from lib.stack import ProwlStack
from tools.file.tool import FileTool

import sys, asyncio

stack = ProwlStack('prompts/code/')
stack.add_tool(FileTool())

r = asyncio.run(stack.run(tasks=['codetodo'], inputs={
    'filename': sys.argv[1],
    'language': 'python' if len(sys.argv) <= 2 else sys.argv[2],
}, stops=["```"]))

print(r.completion)
print(r.variables)
print(r.usage.dict())