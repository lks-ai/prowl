from prowl.lib.tool import ProwlTool
import os

class ScriptTool(ProwlTool):
    # this is the easy way to get a prowl script's contents within a ```prowl block
    def __init__(self, stack):
        super().__init__(
            name="script",
            description="Loads any prowl task script into the completion prompt"
        )
        self.stack = stack
        
    async def run(self, task, **kwargs):
        # Concatenate all arguments into a single string
        if task in self.stack.tasks:
            contents = self.stack.tasks[task]['code']
            inspect = self.stack.tasks[task]['inspect']
        return ProwlTool.Return(contents, inspect)