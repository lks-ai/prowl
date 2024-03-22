from prowl.lib.tool import ProwlTool
import os

class IncludeTool(ProwlTool):
    # this is the easy way to get a prowl script's contents within a ```prowl block
    def __init__(self, stack):
        super().__init__(
            name="include",
            description="Runs any prowl task script and outputs into the calling script"
        )
        self.stack = stack
        
    def run(self, task, **kwargs):
        # Concatenate all arguments into a single string
        if task in self.stack.tasks:
            script = self.stack.tasks[task]['code']
            r = self.stack.fill(script, **self.stack.kwargs)
        return ProwlTool.Return(r.completion, r)