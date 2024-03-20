from lib.stack import ProwlStack

input_data = {
    'monster_name': 'Cheese Demon',
    'monster_strengths': 'Stronger Defense',
    'monster_cr': '9',
    'monster_instructions': 'Has an explosive AOE cheese fart',
}

import asyncio

stack = ProwlStack("prompts/monster/")

r = asyncio.run(stack.run(['monster'], inputs=input_data))

print(r.completion)
print(r.to_dict())