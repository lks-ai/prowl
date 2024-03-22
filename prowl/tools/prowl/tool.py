from prowl.lib.tool import ProwlTool
import os

class ProwlProwlTool(ProwlTool):
    def __init__(self, stack):
        # note that the stack is required to avoid circular imports
        # example usage in a prowl script: {@prowl(user_request)}
        super().__init__(
            name="prowl",
            description="Generate and run a prowl script. Use for more conditioned completion, returning generated variables.",
            stack=stack,
        )
        
    async def run(self, user_request, **kwargs):
        # This is where we'd actually choose the included file
        # This is where to use chromadb search from the stack so like
        # stack.search(user_request) ... obviously search excludes ./prowl.prowl cause that is too much recursion
        # and we still need ```prowl checking on the pattern so it leaves the example vars alone
        # in order to make prowl use this tool we just need examples 
        s = self.stack.search(user_request)
        # get back example script from this and stick it in
        example_script = s[0]['id']
        if example_script == 'prowl':
            example_script = s[1]['id']
        # Generate a prowl script and then run it, returning it's completion and variables
        r = self.stack.run(tasks=['prowl'], inputs={
            'user_request': user_request,
            'example_script': example_script,
            'variable_name': '{variable_name}',
        }, stops=["```"], continue_ratio=0.5)
        generated_script = r.var('prowl_script')
        r2 = self.stack.fill(generated_script + "\n")
        return ProwlTool.Return(r2.completion, r2.variables)