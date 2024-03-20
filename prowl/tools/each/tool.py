# {@each(list_var, script_name)}
# runs script for each item in the list
# passes through the completion as well as variables to a run

from lib.tool import ProwlTool
from lib.stack import ProwlStack, prowl
import os, random

class EachTool(ProwlTool):
    # get list elements back out of prowl variables
    def __init__(self, stack:ProwlStack):
        super().__init__(
            argmap=[
                {'arg': 0, 'label': 'variable', 'required': True},
                {'arg': 1, 'label': 'script_name', 'required': True},
            ],
            name="each",
            description="Run a script for each item in a variable's list or history"
        )
        self.stack:ProwlStack = stack
        
    async def run(self, *args, **kwargs):
        var_name:str = self.arg_name(kwargs, 0)
        script_name:str = self.arg_name(kwargs, 1)
        completion:str = self.completion(kwargs)
        variables:dict[str, prowl.Variable] = self.variables(kwargs)
        # print()
        # print(list(variables.keys()))
        # print()
        extra_blocks = [] if len(args) <= 2 else args[1:]
        stream_level = self.stream_level(kwargs)
        # remove the entire call to this tool from completion text
        callback_txt = self.callback_match(kwargs)
        completion = completion.replace(callback_txt, '') 
        value = ""
        #print('\n@>>each:', var_name, script_name, args, kwargs)
        if var_name in variables:
            # Load in the Variable object for this variable from the stack
            var:prowl.Variable = variables[var_name]
            tasks = [script_name]
            tasks.extend(extra_blocks)
            # Go through each variable and perform a stack run
            #print(var.list)
            list_ = None
            if var.list:
                list_ = var.list
            else: # use the hist function of the variable
                # treats current and historical values as a list
                # results in there always being at least one item in the list
                h = var.hist()
                list_ = [v['value'] for v in h]
            #print(list_)
            # each variable in the list_ run it through the given stack
            if list_:
                difference = lambda original, modified: modified[len(original):]
                original = completion
                #_variables = variables.copy()
                for i, v in enumerate(list_):
                    variables['_list_step'] = prowl.Variable('_list_step', value=str(i + 1))
                    variables[var_name] = prowl.Variable(var_name, value=v)
                    #print(completion[-100:])
                    #print(i, var_name, tasks)
                    #print(_variables[var_name].value)
                    #return ProwlTool.Return(None, None)
                    #print(list(_variables.keys()))
                    r = await self.stack.run(tasks, prefix=completion, variables=variables, stream_level=stream_level)
                    modified = r.completion
                    diff = difference(original, modified)
                    #print(diff)
                    value += diff
            #print("value", value)
        return ProwlTool.Return(value, None)
    
    # def inspect_callback(self, script_name):
    #     # TODO Add the callback system to stack.inspect
    #     # use this for stack.inspect and return any variables present in
    #     # the output template for the given script
    #     # then inspect will handle the rest of variable requirement validation
    #     # your tool should use `stack` as an argument like the script tool in order to just use
    #     # stack.inspect_vars > passing whatever, if tht is the case
    #     # t = self.stack.tasks[script_name]
    #     # fc = self.read(t['folder'], script_name)
    #     # r = self.stack.inspect_vars(fc)
    #     return None


    # def ns_update(self):
    #     # on prowl.callback return all of the script names into the stack so they can be used to make a stack!
    #     return {k: k for k in self.stack.tasks.keys()}

    def validate_callback(self, calling_script, reference_script, var_state, script_state):
        # all variables that are declared in this script go in declared, all reference go in referenced
        scinsp = self.stack.tasks[reference_script]['inspect']
        scd = [(reference_script, v) for v in scinsp[0]['declared']]
        var_state['declared'].extend(scd)
        scd = [(reference_script, v) for v in scinsp[0]['referenced']]
        var_state['referenced'].extend(scd)