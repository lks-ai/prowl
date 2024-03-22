from prowl.lib.tool import ProwlTool
import os

class ConcatTool(ProwlTool):
    def __init__(self):
        # note that no argmap is used here because we want a 1 to 1 sequential arg input
        super().__init__(
            name="concat",
            description="Concatenates any number of variables"
        )
        
    async def run(self, *args, **kwargs):
        # Concatenate all arguments into a single string
        contents = '\n'.join(args)
        return ProwlTool.Return(contents, None)