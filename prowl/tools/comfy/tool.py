from prowl.lib.tool import ProwlTool
import time
from string import Template
import random, sys, json, traceback

from prowl.tools.comfy.comfyutil import ComfyAsync

import base64
from PIL import Image
from io import BytesIO

import os
PROWL_COMFY_ENDPOINT = os.getenv("PROWL_COMFY_ENDPOINT")

class ComfyTool(ProwlTool):
    def __init__(self, forgive_errors=False, output_path='prowl/tools/comfy/output/', workflow_path='prowl/tools/comfy/workflows/', save=True):
        super().__init__(
            argmap=[
                {'arg': 0, 'label': 'prompt'},
                {'kwarg': 'workflow'},
                {'kwarg': 'width'},
                {'kwarg': 'height'},
            ],
            name="comfy",
            description="Generate an image with ComfyUI"
        )
        self.comfy_output_path = output_path
        self.comfy_workflow_path = workflow_path
        self.forgive_errors = forgive_errors
        self.headers = {"Content-Type": "application/json"}
        self.counter = 0
        self.save = save
        
    async def run(self, prompt, workflow="sdxl", seed=0, prefix="prowl", width=1024, height=1024, **kwargs):
        # how to get an image back
        with open(f"{self.comfy_workflow_path}{workflow}.jsont", 'r') as f:
            template = f.read()
        t = Template(template)
        t_data = {
            'seed': seed if seed > 0 else random.randint(1, sys.maxsize),
            'prompt': prompt.replace('"', "'").replace("\n", "\\n"),
            'prefix': prefix,
            'width': width,
            'height': height,
        }
        print(t_data)
        print(t.template)
        comfy_prompt = t.substitute(t_data)
        print(comfy_prompt)
        jp = json.loads(comfy_prompt)
        st = time.time()
        try:
            print(PROWL_COMFY_ENDPOINT, flush=True)
            comfy = ComfyAsync(host=PROWL_COMFY_ENDPOINT)
            images = await comfy.generate(jp) # returns list of binary image strings
            data = {'images': []}
            print(images.keys())
            for i, (k, v) in enumerate(images.items()):
                image = v[0]
                if self.save:
                    ii = i + self.counter
                    stt = random.randint(10000, 99999)
                    fpath = f"{self.comfy_output_path}{prefix}_{ii}_{stt}.jpg"
                    print('>>> Saving', fpath)
                    self.save_image(image, fpath)
                    data['images'].append(fpath)
                else:
                    data['images'].append(base64.b64encode(self.convert_png_to_jpg(image)).decode('utf-8'))
            self.counter += len(images)
        except Exception as e:
            print(e, flush=True)
            #traceback.format_exc(e)
            if self.forgive_errors:
                data = {'error': str(e)}
            else:
                raise e
        en = time.time()

        data['elapsed'] = en - st
        return ProwlTool.Return(None, data)
            
    def save_image(self, image_data, output_filename):
        try:
            print('@>> comfy: Image Data Received. Length:', len(image_data))
            image = Image.open(BytesIO(image_data))
            image.save(output_filename, 'JPEG', quality=75)
        except Exception as e:
            print("Error saving image:", e)
                    

    def convert_png_to_jpg(self, png_bytes):
        # Load the PNG image from bytes
        with Image.open(BytesIO(png_bytes)) as img:
            # Convert the image to RGB mode in case it's in a different mode
            img = img.convert("RGB")
            # # Calculate the new dimensions (half the original size)
            # new_dimensions = (img.width // 2, img.height // 2)
            # # Resize the image to half its size
            # img = img.resize(new_dimensions)
            # Create a bytes buffer for the converted image
            jpg_buffer = BytesIO()
            # Save the image in JPEG format to the bytes buffer
            img.save(jpg_buffer, format="JPEG", quality=75)
            # Get the JPEG bytes
            jpg_bytes = jpg_buffer.getvalue()
            return jpg_bytes