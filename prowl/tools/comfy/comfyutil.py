# !pip install aiohttp websockets
import aiohttp
import websockets
import asyncio
import uuid
import json
import urllib.parse

class ComfyAsync:
    def __init__(self, host="127.0.0.1:8188"):
        self.host = host
        self.client_id = str(uuid.uuid4())
        self.prompt_id = None
        self.output_images = {}

    async def on_message(self, message):
        if isinstance(message, str):
            print(message)
            data = json.loads(message)
            print(data)
            if data['type'] == 'executing':
                if 'prompt_id' in data['data']:
                    prompt_id = data['data']['prompt_id']
                    if self.prompt_id == prompt_id:
                        return True  # Indicate that message processing is complete
        return False

    async def queue_prompt(self, prompt):
        async with aiohttp.ClientSession() as session:
            p = {"prompt": prompt, "client_id": self.client_id}
            uri = f"http://{self.host}/prompt"
            print('QUEUE', p, uri, flush=True)
            async with session.post(uri, json=p) as response:
                return await response.json()

    async def get_image(self, filename, subfolder, folder_type):
        url_values = urllib.parse.urlencode({"filename": filename, "subfolder": subfolder, "type": folder_type})
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{self.host}/view?{url_values}") as response:
                return await response.read()

    async def get_history(self, prompt_id):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{self.host}/history/{prompt_id}") as response:
                return await response.json()

    async def get_images(self, prompt):
        r = await self.queue_prompt(prompt)
        print(r)
        self.prompt_id = r['prompt_id']
        print('PID', self.prompt_id)

        async with websockets.connect(f"ws://{self.host}/ws?clientId={self.client_id}") as websocket:
            while True:
                message = await websocket.recv()
                if await self.on_message(message):
                    break

        # Attempt to retrieve history, retry if not available
        max_retries = 10
        history = None
        for _ in range(max_retries):
            history_data = await self.get_history(self.prompt_id)
            print('search', self.prompt_id)
            if self.prompt_id in history_data:
                history = history_data[self.prompt_id]
                break
            await asyncio.sleep(2)  # Wait for 2 seconds before retrying

        if history is None:
            raise Exception("History for prompt_id not found after retries")

        for node_id, node_output in history['outputs'].items():
            if 'images' in node_output:
                print('IMAGES')
                images_output = [await self.get_image(image['filename'], image['subfolder'], image['type'])
                                 for image in node_output['images']]
                self.output_images[node_id] = images_output
        print('Image Keys:', list(self.output_images.keys()))
        return self.output_images

    async def generate(self, prompt):
        images = await self.get_images(prompt)
        print('tools.comfy.comfyutil.generate:', len(images))
        return images
