from prowl.lib.tool import ProwlTool
import os, random

class RecallTool(ProwlTool):
    # callback to recall information using a semantic vector db like chroma
    def __init__(self, stack, recall_callback=None):
        super().__init__(
            argmap=[
                {'arg': 0, 'label': 'query', 'required': True},
                {'kwarg': 'limit', 'label': 'limit'},
            ],
            name="recall",
            description="Recall documents from a document vector store passing the query and limit through a callback"
        )
        self.stack = stack
        self.recall_callback = recall_callback
        
    async def run(self, query, limit=3, **kwargs):
        # pass the first arg in as a required variable to store
        # every other arg after that goes into a dict for supporting metadata for the document
        if self.recall_callback:
            #var_name = self.arg_name(kwargs, 0)
            # Yes, your callback must be async, it's 2024.
            #print(kwargs)
            result, data = await self.recall_callback(query, limit=limit, **kwargs)
        return ProwlTool.Return(str(result), data)
    
    # def inspect_callback(self, script_name):
