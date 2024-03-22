from prowl.lib.stack import ProwlStack, StreamLevel

import asyncio 

async def token_event(token):
    print(token, end="", flush=True)

stack = ProwlStack(['prowl/prompts/'],
    token_event=token_event,
    stream_level=StreamLevel.TOKEN,
)
print('begin')
r = asyncio.run(stack.run(['input', 'output'], inputs={'user_request': 'How high is Mount Everest?'}, stream_level=StreamLevel.TOKEN))