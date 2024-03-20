import sys, os, asyncio, re
from lib.prowl import prowl
from lib.stack import ProwlStack
from tools.out.tool import OutputTemplateTool
from tools.file.tool import FileTool
from tools.time.tool import TimeTool
from tools.include.tool import IncludeTool
from tools.list.tool import ListTool
from tools.script.tool import ScriptTool
from tools.comfy.tool import ComfyTool
from tools.each.tool import EachTool

version = "0.1 beta"

def parse_scripts(scripts:list[str]):
    sc, flags = [], {}
    for s in scripts:
        if s.startswith('-'):
            k = s[1:]
            if '=' in k:
                var, val = k.split('=', 1)
                print(val)
                if ',' in val:
                    print('HAS ,')
                    flags[var] = [v.encode().decode('unicode_escape') for v in val.split(',')]
                else:
                    print('NO,')
                    flags[var] = val.encode().decode('unicode_escape')
            else:
                flags[k] = True
        else:
            sc.append(s)
    return sc, flags


def main():
	if len(sys.argv) > 1:
	    title = f"Prompt Owl (PrOwl) version {version}"
	    border = "-" * len(title)
	    # Run a stack given by the input order in command line args
	    folder = ['prompts/']
	    # get scripts and flags separately
	    scripts, flags = parse_scripts(sys.argv[1:])
	    print(flags)
	    working_dir = os.getcwd()
	    
	    # Set stops from flags 
	    default_stop = ["\n\n"]
	    if 'stop' in flags:
		default_stop = flags['stop']
		print(default_stop)
		
	    # extra folders
	    if 'folder' in flags:
		folder.extend([flags['folder']] if isinstance(flags['folder'], str) else flags['folder'])
	    
	    print(title)
	    print(border)
	    print(f"Working From {working_dir}")
	    print(f"Folder: {folder}")
	    print(f"Scripts: {scripts}")
	    print(border)

	    stack = ProwlStack(folder=folder) #, files=scripts)
	    stack.add_tools(OutputTemplateTool(stack), FileTool(), IncludeTool(stack), ScriptTool(stack), ComfyTool(), TimeTool(), ListTool(stack), EachTool(stack))

	    loop = False
	    pattern = r'\.\.(?:\d+|\.{1})'
	    st = ' '.join(scripts)
	    matches = re.findall(pattern, st)
	    integers = [int(match[2:]) for match in matches if match.startswith('..') and match[2:].isdigit()]
	    if len(matches) > 0:
		loop = True
		split_pattern = r'(\.\.(?:\d+|\.{1}))'
		splitted = re.split(split_pattern, st)
		splitted = [s.strip() for s in splitted if s]
		loops = [(element.split(' '), integers[i]) for i, element in enumerate(splitted) if element not in matches]
		print(loops)

	    async def once(scripts, variables={}, prefix=""):
		inputs = {}
		if 'input' in scripts:
		    print("\nYou included an `input` block. Enter a value for `{user_request}`...")
		    request = input("@>> User Request> ")
		    inputs['user_request'] = request
		result = await stack.run(scripts, inputs=inputs, stops=default_stop, variables=variables, prefix=prefix, atomic='atomic' in flags)
		return result
		
	    if loop:
		for l in loops:
		    blocks, runs = l
		    vars, pre = {}, ""
		    for i in range(0, runs):
		        result = asyncio.run(once(blocks, variables=vars, prefix=pre))
		        vars = result.variables
		        prefix = result.completion
	    else:
		result = asyncio.run(once(scripts))

	    print('\n[[OUTPUT VARS]]\n')
	    print(result.to_dict())
	    print('\n[[COMPLETION PROMPT]]\n')
	    print(result.completion)
	    print('\n[[USAGE]]\n')
	    print(result.usage.dict())
	    print('\n[[OUTPUT FROM TEMPLATES]]\n')
	    for out in result.output:
		print(f"\n[[[{out['task']}]]]\n")
		print(out['output'])
		
	else:
	    from tools.prowl.tool import ProwlProwlTool
	    # Prowl Augmented Prompt Engineering
	    title = f"PrOwl: Augmented Prompt Composer version {version}"
	    border = "-" * len(title)
	    print(title)
	    print(border)
	    # let person write a query and prowl will create a prompt
	    stack = ProwlStack('prompts/world/')
	    stack.add_tools(ProwlProwlTool(stack), ScriptTool(stack))
	    print(border)
	    request = input("> ")
	    r = asyncio.run(stack.run(['prowl'], inputs={
		'user_request': request,
		'example_script': 'creative',
		'variable_name': "{variable_name}",
	    }, stops=["```"]))
	    print(r.completion)
	    
if __name__ == "__main__":
	main()
