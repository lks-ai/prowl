from prowl.lib.tool import ProwlTool
import os, random

class SearchTool(ProwlTool):
    # callback to recall information using a semantic vector db like chroma
    def __init__(self, search_callback=None):
        super().__init__(
            argmap=[
                {'arg': 0, 'label': 'query', 'required': True},
                {'kwarg': 'limit', 'label': 'limit'},
            ],
            name="search",
            description="Uses a Search callback function to perform any type of search"
        )
        self.search_callback = search_callback
        
    async def run(self, query, limit=10, **kwargs):
        if self.search_callback:
            result, data = await self.search_callback(query, limit=limit, **kwargs)
        return ProwlTool.Return(str(result), data)
    
    # def inspect_callback(self, script_name):
