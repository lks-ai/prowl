from prowl.lib.tool import ProwlTool
import os, random

class CollectTool(ProwlTool):
    # callback to collect a variable into a semantic vector store
    def __init__(self, stack, collect_callback=None):
        super().__init__(
            name="collect",
            description="Collect a variable to a document vector store using callbacks"
        )
        self.stack = stack
        self.collect_callback = collect_callback
        
    async def run(self, variable, *args, **kwargs):
        # pass the first arg in as a required variable to store
        # every other arg after that goes into a dict for supporting metadata for the document
        if self.collect_callback:
            var_name = self.arg_name(kwargs, 0)
            data = {}
            for i, arg in enumerate(args):
                vn = self.arg_name(kwargs, i + 1)
                print(vn)
                data[vn] = arg
            # Yes, your callback must be async, it's 2024.
            await self.collect_callback(var_name, variable, data)
        return ProwlTool.Return(None, None)