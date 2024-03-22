from prowl.lib.tool import ProwlTool
import os, random

class NavigateTool(ProwlTool):
    # callback to recall information using a semantic vector db like chroma
    def __init__(self, navigate_callback=None):
        super().__init__(
            argmap=[
                {'arg': 0, 'label': 'URL', 'required': True},
            ],
            name="navigate",
            description="Navigates to a URL using a browser through the navigate_callback function"
        )
        self.navigate_callback = navigate_callback
        
    async def run(self, url, **kwargs):
        if self.navigate_callback:
            result, data = await self.navigate_callback(url, **kwargs)
        return ProwlTool.Return(str(result), data)
    
