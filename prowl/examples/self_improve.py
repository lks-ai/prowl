from lib.stack import ProwlStack
import asyncio

stack = ProwlStack('prompts/code/')

with open('lib/prowl.py', 'r') as f:
    prowl_code = f.read()

with open('lib/prowlstack.py', 'r') as f:
    prowlstack_code = f.read()
    
# Note, in the future, make that `{$metadata_key=value, meta2=value2}` syntax in prowl
# If I have that plus `{@tool(args)}`` and `{%include}`` + `%}`` that will complete prowl
r = asyncio.run(stack.run(tasks=['codedit'], inputs={
    'code': prowl_code + prowlstack_code,
    'language': 'python',
}, stops=["```"]))

print(r.completion)
print(r.usage.dict())