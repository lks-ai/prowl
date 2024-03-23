import asyncio
from prowl import ProwlStack

stack = ProwlStack(folder=['prowl/prompts/digest/', 'prowl/prompts/thought/', 'prowl/prompts/'])

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
    
    question = 'How does a tree grow?'
    summary = '[No current summary]'
    for i in range(1, 30):
        _summary, _title, crit = await aggsum(question, summary)
        # TODO Save all this shit

asyncio.run(main())