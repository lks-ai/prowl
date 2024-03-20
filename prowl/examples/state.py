from lib.stack import ProwlStack

story = """
# Li Ming's Quest for Hope.

**A Short Story for Li Ming**

## Act 1

The sun had long since set, casting the land in an eerie orange glow. Li Ming trudged through the fields, his clothes worn and tattered, his body weary from the long day's labor. He had worked tirelessly, from dawn to dusk, his every waking moment dedicated to the endless toil required to survive in the Chinese Empire.

As he made his way back to his small hut, he stumbled upon something unexpected. Nestled among the ruins of a burned-down library, he found an old, tattered book. Its pages were yellowed with age, its cover worn and battered. Li Ming's curiosity piqued, he carefully opened the book and began to read.

The words on the page transported him to another world, a world filled with hope and redemption, a world that seemed light years away from the despair and hopelessness of Fuhrer's Reign. Li Ming read on, his spirit lifting with every page, his heart filled with a renewed sense of purpose.

## Act 2

The days turned into weeks, and weeks into months. Li Ming continued to work in the fields, his spirit buoyed by the words he had read in the old book. He began to dream of a better world, a world where hope and redemption were not just empty words, but a reality.

But the world of Fuhrer's Reign was not so easily swayed. The Chinese Empire continued to oppress its people, crushing their spirits and their dreams. Li Ming knew that he could not remain in this world forever, that he needed to take action if he was to make a difference.

He began to secretly share the words of the book with his fellow laborers, inspiring them with tales of hope and redemption. Together, they began to plan a rebellion against the Chinese Empire, a rebellion that would shake the foundations of this desolate world.

But the Chinese Empire was not about to let go of its power easily. The ruling class, sensing a threat to their power, began to crack down on any signs of dissent. Li Ming and his fellow rebels were forced to go into hiding, their every move shrouded in secrecy and fear.

Despite the danger, Li Ming refused to give up. He knew that the fate of the world rested on their shoulders, and that they could not fail. He continued to read the book, its words a beacon of hope in the darkest of times.

## Act 3

The rebellion had been planned for months, and the day had finally come. Li Ming and his fellow rebels had gathered in the ruins of an old factory, their hearts filled with a renewed sense of purpose. They knew that the odds were against them, that they were outnumbered and outgunned. But they also knew that they had nothing to lose.

The battle raged on for hours, with the rebels fighting valiantly against the Chinese Empire's forces. Li Ming, at the forefront of the battle, fought with a fierce determination, his every move calculated and precise. But despite their best efforts, the rebels were eventually overpowered.

Li Ming lay on the ground, his body battered and bruised, his spirit crushed. He looked around at the bodies of his comrades, their dreams and aspirations now nothing more than a distant memory. He knew that this was not the end, that there would be more rebellions, more fights for freedom. But he also knew that he would not be a part of it.

As the Chinese Empire's forces closed in, Li Ming closed his eyes, the words of the old book echoing in his mind. He thought of the world that once was, a world filled with hope and redemption. And as the darkness closed in, he knew that he had not fought in vain.

But just as all hope seemed lost, a strange thing happened. The ground beneath Li Ming began to tremble, and the sky turned a brilliant shade of red. From the distance, the sound of engines roared, and the earth shook with the impact of explosions. The Chinese Empire's forces were being attacked from an unexpected direction.

Li Ming opened his eyes, his spirit renewed. He looked around, and saw that the rebels had not been defeated after all. A new force had arrived, one that was determined to bring hope and redemption to this desolate world. And as the sun rose on a new day, Li Ming knew that he would fight once more, for a world that was worth fighting for.

"""

import asyncio

stack = ProwlStack(["prompts/extract/"])

blocks = ['ee', 'se']

r = asyncio.run(stack.run(blocks, inputs={'story': story}, atomic=True))

print(r.get())
print(r.completion)