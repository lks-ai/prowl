""" Prowl Self Writer

Uses `prowl.prowl` to write out a prowl script at user request.
This leads to self-guided task execution and prompt generation.
Since it is using variable based generation, you get everything back
"""
import sys

from lib.prowl import prowl
from lib.stack import ProwlStack
import asyncio
# Tooling
from tools.script.tool import ScriptTool

# Load ProwlStack to the prompts folder
stack = ProwlStack(folder=['prompts/world/', 'prompts/code/'])
stack.add_tool(ScriptTool(stack))

# Run the `prowl` task with inputs, stopping at three backticks
# outputs the script 
user_request = " ".join(sys.argv[1:])
# find an example script that is semantically closest to user request
s = stack.search(user_request)
# get back example script... we get 2 results... if 0 is prowl, use the second
# problem arises if only 1 search result, and actually no fix because no example to use!
print(s)
example_script = s[0]['id']
if example_script == 'prowl':
    example_script = s[1]['id']

r = asyncio.run(stack.run(tasks=['prowl'], inputs={
    'user_request': user_request,
    'example_script': example_script,
    'variable_name': '{variable_name}',
}, stops=["```"]))
#stops=[])#, stops=["```"])

# Fill the resulting generated prowl script using prowl
# there could be an easy way in the near future to map generated inputs and ask the user through @ask tool
r2 = asyncio.run(prowl.fill(r.val('prowl_script') + "\n"))

# So how to complete?

# Show the entire completed prompt and usage stats
print(">> User Request >>\n", r.val('user_request'))
print("\n>> Generated Prowl Script >>")
print(r.val('prowl_script'))
print("\n>> Script Completion >>")
print(r2.completion)

print(r2.get())

print(r.usage.dict())
print(r2.usage.dict())