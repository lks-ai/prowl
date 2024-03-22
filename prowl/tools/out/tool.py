from prowl.lib.tool import ProwlTool
import os

class OutputTemplateTool(ProwlTool):
    # this is the easy way to get a prowl script's contents within a ```prowl block
    def __init__(self, stack):
        super().__init__(
            name="out",
            description="Loads a file output template `.prout` for any `.prowl` script which has variables previously declared."
        )
        self.stack = stack
        
    async def run(self, script_name, **kwargs):
        # check if .prout exists... if so fill contents and return completion
        contents = None
        if script_name in self.stack.tasks:
            t = self.stack.tasks[script_name]
            fc = self.read(t['folder'], script_name) # get template file contents
            if fc:
                # Fill into contents of the output template
                variables:dict = self.variables(kwargs)
                r = await self.stack.fill(fc, variables=variables)
                contents = r.completion
        return ProwlTool.Return(contents, None)
    
    # def inspect_callback(self, script_name):
    #     # TODO Add the callback system to stack.inspect
    #     # use this for stack.inspect and return any variables present in
    #     # the output template for the given script
    #     # then inspect will handle the rest of variable requirement validation
    #     # your tool should use `stack` as an argument like the script tool in order to just use
    #     # stack.inspect_vars > passing whatever, if tht is the case
    #     t = self.stack.tasks[script_name]
    #     fc = self.read(t['folder'], script_name)
    #     r = self.stack.inspect_vars(fc)
    #     return r
    
    def read(self, folder, script_name):
        fn = folder + script_name + ".prout"
        if os.path.exists(fn):
            with open(fn, 'r') as f:
                fc = f.read()
            return fc

    def ns_update(self):
        # on stack.validate() return all of the script names into the stack
        return {k: k for k in self.stack.tasks.keys()}
    
    def validate_callback(self, calling_script, reference_script, var_state, script_state):
        # since we are getting vars from a reference script we are effectively including, we require all declared variables in that script
        scinsp = self.stack.tasks[reference_script]['inspect']
        scd = [(reference_script, v) for v in scinsp[0]['declared']]
        var_state['required'].extend(scd)