import requests
import json
import time
import os
import traceback

import aiohttp

PROWL_COMPLETIONS_ENDPOINT = os.getenv('PROWL_COMPLETIONS_ENDPOINT') or "/v1/completions"
API_KEY = os.getenv('PROWL_VENDOR_API_KEY') or None

class VLLM:
    def __init__(self, base_url, model="mistralai/Mistral-7B-Instruct-v0.2"):
        self.url = f"{base_url}{PROWL_COMPLETIONS_ENDPOINT}"
        print(f"[INFO] Endpoint URL: {self.url}, model: {model}")
        self.headers = {"Content-Type": "application/json"}
        # If provided, add the API key to the Authorization header.
        if API_KEY:
            self.headers["Authorization"] = f"Bearer {API_KEY}"
        self.data = {"model": model, "max_tokens": 512, "temperature": 0.0}
        self.usage = {}

    class Usage:
        # For use with calculating and aggregating usage from outside this module.
        def __init__(self):
            self.prompt_tokens: int = 0
            self.total_tokens: int = 0
            self.completion_tokens: int = 0
            self.elapsed: float = 0

        def cost(self, prompt_multiplier, completion_multiplier):
            return (float(self.prompt_tokens) * prompt_multiplier) + (float(self.completion_tokens) * completion_multiplier)

        def add(self, ref):
            if isinstance(ref, dict):
                self.prompt_tokens += ref.get('prompt_tokens', 0)
                self.completion_tokens += ref.get('completion_tokens', 0)
                self.total_tokens += ref.get('total_tokens', 0)
                if 'elapsed' in ref:
                    self.elapsed += ref['elapsed']
            else:
                self.prompt_tokens += ref.prompt_tokens
                self.total_tokens += ref.total_tokens
                self.completion_tokens += ref.completion_tokens
                self.elapsed += ref.elapsed

        def dict(self):
            return {
                'prompt_tokens': self.prompt_tokens,
                'total_tokens': self.total_tokens,
                'completion_tokens': self.completion_tokens,
                'elapsed': self.elapsed
            }

    def get_usage(self):
        return self.usage

    def run(self, prompt, **kwargs):
        """
        Synchronous request method with enhanced error handling.
        """
        data = self.data.copy()
        data.update({"prompt": prompt})
        data.update(kwargs)
        st = time.time()
        try:
            response = requests.post(self.url, headers=self.headers, data=json.dumps(data))
            # Raise an error for bad HTTP status codes
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            print(f"[ERROR] HTTP error occurred during run(): {http_err}")
            print(f"Response content: {response.text if 'response' in locals() else 'No response'}")
            raise
        except Exception as e:
            print(f"[ERROR] Error during run() request: {e}")
            traceback.print_exc()
            raise

        en = time.time()
        try:
            r = response.json()
        except json.JSONDecodeError as jde:
            print(f"[ERROR] Failed to decode JSON response: {jde}")
            print(f"Response text: {response.text}")
            raise
        # Update usage with elapsed time
        if "usage" in r:
            self.usage = r["usage"]
            self.usage['elapsed'] = en - st
        else:
            print("[WARNING] No 'usage' key in response.")
        return r

    async def run_async(self, prompt, streaming=False, stream_callback=None, variable_name=None, **kwargs):
        """
        Asynchronous request method with enhanced error handling.
        """
        data = self.data.copy()
        data.update({"prompt": prompt})
        data.update(kwargs)
        n = kwargs.get('n', 1)
        if streaming:
            data['stream'] = True
        st = time.time()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, headers=self.headers, data=json.dumps(data)) as response:
                    if response.status >= 400:
                        content = await response.text()
                        error_msg = f"[ERROR] HTTP error {response.status} during run_async(): {content}"
                        print(error_msg)
                        raise aiohttp.ClientResponseError(
                            status=response.status,
                            message=error_msg,
                            request_info=response.request_info,
                            history=response.history
                        )

                    if streaming and stream_callback:
                        tokens, choices, finish_reason = 0, [{} for _ in range(n)], None
                        async for line in response.content:
                            try:
                                decoded_line = line.decode('utf-8').strip()
                                if decoded_line.startswith('data:'):
                                    decoded_line = decoded_line[5:].strip()
                                if decoded_line:  # Ensure line is not empty
                                    try:
                                        r = json.loads(decoded_line)
                                    except json.JSONDecodeError:
                                        print(f"[WARNING] Skipping non-JSON line: {decoded_line}")
                                        continue
                                    tokens += 1
                                    for i, v in enumerate(r.get('choices', [])):
                                        if len(choices[i]) == 0:
                                            choices[i] = {'index': i, 'text': '', 'logprobs': None, 'finish_reason': None}
                                        choices[i]['text'] += v.get('text', '')
                                        choices[i]['finish_reason'] = v.get('finish_reason')
                                    await stream_callback(r['choices'][0]['text'], finish_reason=choices[0]['finish_reason'], variable_name=variable_name)
                            except Exception as inner_e:
                                print(f"[ERROR] Error processing streaming data: {inner_e}")
                                traceback.print_exc()
                                continue
                        el = time.time() - st
                        u = VLLM.Usage()
                        u.add({'prompt_tokens': 0, 'completion_tokens': tokens, 'total_tokens': tokens, 'elapsed': el})
                        return {'choices': choices, 'usage': u.dict()}
                    else:
                        resp_text = await response.text()
                        try:
                            r = json.loads(resp_text)
                        except json.JSONDecodeError as jde:
                            print(f"[ERROR] Failed to decode JSON in run_async(): {jde}")
                            print(f"Response text: {resp_text}")
                            raise
                        # Add elapsed time to usage data
                        if 'usage' in r:
                            r['usage']['elapsed'] = time.time() - st
                        else:
                            print("[WARNING] No 'usage' key in asynchronous response.")
                        return r
        except aiohttp.ClientError as client_err:
            print(f"[ERROR] AIOHTTP ClientError during run_async(): {client_err}")
            traceback.print_exc()
            raise
        except Exception as e:
            print(f"[ERROR] General error during run_async(): {e}")
            traceback.print_exc()
            raise

if __name__ == "__main__":
    import asyncio
    import os
    PROWL_MODEL = os.getenv('PROWL_MODEL')
    PROWL_VLLM_ENDPOINT = os.getenv('PROWL_VLLM_ENDPOINT')
    llm = VLLM(
        f"{PROWL_VLLM_ENDPOINT}",
        model=PROWL_MODEL,
    )

    async def sample_callback(text, finish_reason=None, variable_name=None):
        print(text, end="", flush=True)

    try:
        r = asyncio.run(llm.run_async("Monty Python Sketch:\n\nPriest: What do we do with witches?\nAngry Crowd:",
                                      streaming=True,
                                      stream_callback=sample_callback))
    except Exception as ex:
        print(f"[CRITICAL] Exception occurred in main: {ex}")
        traceback.print_exc()
