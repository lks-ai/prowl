from prowl.lib.tool import ProwlTool
import os, random

class ListTool(ProwlTool):
    # get list elements back out of prowl variables
    def __init__(self, stack):
        super().__init__(
            argmap=[
                {'arg': 0, 'label': 'variable', 'required': True},
                {'kwarg': 'index', 'label': 'index'},
            ],
            name="list",
            description="Access elements by index on a variable which has a list in it, if no index given, returns a random element"
        )
        self.stack = stack
        
    async def run(self, variable, index=None, **kwargs):
        # Access index of list or a random one if index is None
        print("@>>list", variable, index)
        value = None
        # Get the name of the variable from self.argname by passing kwargs an an index
        var_name = self.arg_name(kwargs, 0)
        if self.stack.has(var_name):
            # Load in the Variable object for this variable from the stack
            var = self.stack.var(var_name)
            # Now give a return value with or without index
            print(var.list)
            if var.list is not None:
                list_ = var.list
                if index:
                    value = var.list[int(index - 1)]
                else:
                    value = random.choice(var.list)
            print("value", value)
        return ProwlTool.Return(value, None)