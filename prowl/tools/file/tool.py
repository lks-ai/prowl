from prowl.lib.tool import ProwlTool
import os

class FileTool(ProwlTool):
    def __init__(self):
        super().__init__(
            argmap=[{'arg': 0}],
            name="file",
            description="Reads out a file's contents"
        )
        
    async def run(self, path, **kwargs):
        data = {
            'size': os.path.getsize(path),
            'created': os.path.getctime(path),
            'modified': os.path.getmtime(path),
            'type': os.path.splitext(path)[1][1:]
        }
        with open(path, 'r') as f:
            contents = f.read()
        print(contents)
        return ProwlTool.Return(contents, data)