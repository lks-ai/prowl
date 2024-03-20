from lib.stack import ProwlStack
import sys, os

folder = sys.argv[1]
scripts = sys.argv[2:]
working_dir = os.getcwd()

# dump some variables from the stack into a prout file
stack = ProwlStack(folder=folder, files=scripts)

for task_name in scripts:
    vars, tools = stack.get_inspect(task_name)
    o = ""
    for var in vars['declared']:
        o += '{' + var + '}' + "\n"
    with open(folder + task_name + ".prout", 'w+') as f:
        f.write(o)
