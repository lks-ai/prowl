import asyncio
from lib.stack import ProwlStack

stack = ProwlStack(folder=['prompts/digest/', 'prompts/thought/'])

async def aggsum(question, summary):
    q_orig = question
    summaries = []
    summary_last = summary
    crit = ''
    for i in range(1, 8):
        # generate some text
        r1 = await stack.run(['input', 'intent', 'output'], 
            inputs={'user_request': question, 'num_questions': 'two'}, 
            prefix=f"# Original Request\n{q_orig}\n\n# Current Summary:\n{summary}\n\n\n", 
            stops=['\n\n\n'],
            continue_ratio = 0.0,
        )
        crit += "# Intent\n" + r1.val('user_intent') + "\n\n#Output\n" + r1.val('output_text') + "\n\n"
        # get some next quesions using ToT
        r1a = await stack.run(['ntot'], 
            prefix=r1.completion, 
            inputs={'num_questions': 'four'}
        )
        # generate summary
        r2 = await stack.run(['sum_recursive'], 
            inputs={'summary': summary, 'text': r1.completion},
            stops=['\n\n\n', '```']
        )
        # set new summary value
        summary = f"# Question {i}\n{question}\n\n" + r2.val('summary')
        summaries.append(summary)
        summary_last = r2.val('summary')
        # use crit questions as new question
        question = r1a.val('crit_questions')

    r3 = await stack.run(['sumtitle'], inputs={'summary': summary_last})
    return summary_last, r3.val('summary_title'), crit


async def main():
    
    def slugify(text:str) -> str:
        return text.strip(' #`-"*').lower().replace(' ', '-')
    
    all_fp = "examples/output/summaries/all.md"
    
    question = 'Create a plan to programatically protect an end user by categorizing all types of government, globalist and mainstream media propaganda. It should see every piece of data as a potential result of some larger agenda until proven otherwise. The user should control what is deemed misinformation. It should be open source, use local models and not leak any data back to the internet. I will start out using Large Language Models to train a categorizer but I do not know the categories or some good set of parameters to judge incoming data by. The user should be considered an adult, with no protection needed by a higher authority like a government or globalist organization. This is a psychological shield against the massive psychological warfare which is rampant in 2024.'
    summary = '[No current summary]'
    for i in range(1, 30):
        _summary, _title, crit = await aggsum(question, summary)
        title = slugify(_title)
        fp = f"examples/output/summaries/{title}.md"
        with open(fp, 'w+') as f:
            f.write(crit + _summary)
        with open(all_fp, 'a') as f:
            f.write(f"{_summary}\n\n\n")

asyncio.run(main())