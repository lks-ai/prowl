from prowl.lib.stack import ProwlStack

# Image Generation

# Let's use the `image` scripts: `scene` and `comfy` to create a scene that turns 
# into a prompt for an Image model hosted on a locally running comfyui service

stack4 = ProwlStack(folder=['prowl/prompts/image/', 'prowl/prompts/'])

# Add the comfy tool
from prowl.tools.comfy.tool import ComfyTool
stack4.add_tool(ComfyTool(
    output_path='/home/osiris/Pictures/sd/'
))

# Make the run: here you see the comfy script is on it's own, that is just for modularity
#  since we commonly use the same input variables, let's set them here. {@comfy(prompt, workflow)}
#  As a note: we could probably make a script that just generates these values, might be a fun challenge for you
comfy_inputs = {
    'workflow': 'sdxl',
    'width_background': 1024,
    'height_background': 640,
    'user_request': 'A cyberpunk giraffe'
}

import asyncio
r4 = asyncio.run(stack4.run(['input', 'scene', 'comfy'], inputs=comfy_inputs))

print(r4.var('comfy').data['images'][0])

print(r4.get()) # return json of variables

print(r4.completion)