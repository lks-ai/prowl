import requests
import json
import time

import aiohttp

class VLLM:
    def __init__(self, base_url, model="mistralai/Mistral-7B-Instruct-v0.2"):
        self.url=base_url
        self.headers = {"Content-Type": "application/json"}
        self.data= {"model": model, "max_tokens": 500, "temperature": 0.0}
        self.usage = {}

    class Usage:
        # for use with calculating and aggregating usage from outside this module
        def __init__(self):
            self.prompt_tokens:int = 0
            self.total_tokens:int = 0
            self.completion_tokens:int = 0
            self.elapsed:float = 0
        
        def cost(self, prompt_multiplier, completion_multiplier):
            return (float(self.prompt_tokens) * prompt_multiplier) + (float(self.completion_tokens) * completion_multiplier)

        def add(self, ref):
            d = type(ref) == dict
            if d:
                self.prompt_tokens += ref['prompt_tokens']
                self.completion_tokens += ref['completion_tokens']
                self.total_tokens += ref['total_tokens']
                if 'elapsed' in ref:
                    self.elapsed += ref['elapsed']
            else:
                self.prompt_tokens += ref.prompt_tokens
                self.total_tokens += ref.total_tokens
                self.completion_tokens += ref.completion_tokens
                self.elapsed += ref.elapsed
                
        def dict(self):
            return {'prompt_tokens': self.prompt_tokens, 'total_tokens': self.total_tokens, 'completion_tokens': self.completion_tokens, 'elapsed': self.elapsed}

    def get_usage(self):
        return self.usage

    def run(self, prompt, **kwargs):
        data = self.data.copy()
        data.update({"prompt": prompt})
        data.update(kwargs)
        st = time.time()
        response = requests.post(self.url, headers=self.headers, data=json.dumps(data))
        en = time.time()
        r = json.loads(response.text)
        self.usage = r["usage"]
        self.usage['elapsed'] = en - st
        return r

    async def run_async(self, prompt, streaming=False, stream_callback=None, **kwargs):
        data = self.data.copy()
        data.update({"prompt": prompt})
        data.update(kwargs)
        n = 1 if 'n' not in kwargs else kwargs['n']
        #del data['token_event']
        if streaming:
            data['stream'] = True
        st = time.time()
        # print(streaming, stream_callback)
        # print(data)

        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, headers=self.headers, data=json.dumps(data)) as response:
                if streaming and stream_callback:
                    #print('STREAMING')
                    tokens, choices, finish_reason = 0, [{}] * n, None
                    async for line in response.content:
                        try:
                            # Check for SSE pattern and strip the "data: " part if present
                            decoded_line = line.decode('utf-8').strip()
                            if decoded_line.startswith('data:'):
                                decoded_line = decoded_line[5:].strip()
                            if decoded_line:  # Ensure line is not empty
                                r:dict = json.loads(decoded_line)
                                # elapsed = {'elapsed': time.time() - st}
                                # r['usage'] = r.get('usage', {})  # Ensure 'usage' key exists
                                # r['usage'].update(elapsed)
                                tokens += 1
                                #print(r)
                                for i, v in enumerate(r['choices']):
                                    if len(choices[i]) == 0:
                                        choices[i] = {'index': i, 'text': '', 'logprobs': None, 'finish_reason': None}
                                    choices[i]['text'] += v['text']
                                    choices[i]['finish_reason'] = v['finish_reason']
                                await stream_callback(r['choices'][0]['text']) # can change to send back ALL choices
                        except json.JSONDecodeError:
                            # Handle lines that are not valid JSON, such as heartbeats or empty lines
                            pass
                    el = time.time() - st
                    u = VLLM.Usage()
                    u.add({'prompt_tokens': 0, 'completion_tokens': tokens, 'total_tokens': tokens, 'elapsed': el})
                    return {'choices': choices, 'usage': u.dict()}  # Return None or appropriate response to indicate streaming completion
                else:
                    resp_text = await response.text()
                    r = json.loads(resp_text)
                    elapsed = {'elapsed': time.time() - st}
                    r['usage'].update(elapsed)
                    return r


if __name__ == "__main__":
    import asyncio, os
    PROWL_MODEL = os.getenv('PROWL_MODEL')
    PROWL_VLLM_ENDPOINT = os.getenv('PROWL_VLLM_ENDPOINT')
    llm = VLLM(
        f"{PROWL_VLLM_ENDPOINT}/v1/completions",
        model=PROWL_MODEL,
    )

    async def sample_callback(data):
        print(data['choices'][0]['text'], end="", flush=True)

    r = asyncio.run(llm.run_async("Monty Python Sketch:\n\nPriest: What do we do with witches?\nAngry Crowd:", streaming=True, stream_callback=sample_callback))
