from lib.stack import ProwlStack

import asyncio

async def main():
    
    context = "Albert Einstein, the renowned theoretical physicist known for his theory of relativity, was born in Ulm, Germany. His groundbreaking work earned him the Nobel Prize in Physics in 1921, awarded by the Royal Swedish Academy of Sciences."
    
    stack = ProwlStack(folder=['prompts/', 'prompts/thought/'], silent=True)
    
    r = await stack.run(['kgraph'], inputs={'context': context})
    print(r.completion)
    print(r.usage.dict())

asyncio.run(main())