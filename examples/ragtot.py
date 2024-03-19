from lib.stack import ProwlStack
from tools.collect.tool import CollectTool
from tools.recall.tool import RecallTool
from tools.each.tool import EachTool

import chromadb
from chromadb import QueryResult

import asyncio
    
"""
    Example of how to perform RAG and ToT in one script
    Uses chroma to hook into the Collect and Recall tools 
    for prowl script based use of chroma or any other vectordb
"""

# Start

stack = ProwlStack('prompts/thought/')

chroma = chromadb.Client()
collection = chroma.create_collection(name="stories")

## Define callbacks

async def collect(id, text, data=None):
    print('Adding to ChromaDB:', id)
    collection.add(
        documents=text,
        metadatas=data,
        ids=id
    )

async def recall(query, limit=3, **kwargs):
    """Query the database and return (content:str, data:dict[str, Any])"""
    #print(limit, query)
    r:QueryResult = collection.query(query_texts=query, n_results=limit)
    content, data = "", []
    #print(r)
    if len(r['ids'][0]) > 0:
        #print(len(r['documents']))
        for i, id in enumerate(r['ids'][0]):
            m = {
                'id': id,
                'document': r['documents'][0][i],
                'metadata': r['metadatas'][0][i],
                'distance': r['distances'][0][i]
            }
            #print(m)
            #await asyncio.sleep(4)
            data.append(m)
        
        content = "\n- ".join([v.replace("\n", '\\n').strip() for v in r['documents'][0]])
        #print(content)
    return content, data
    

# Now for fun

## Generate some stories to collect

async def main():
    stack = ProwlStack(folder=["prompts/rag/", "prompts/thought/"])
    stack.add_tool(EachTool(stack))
    stack.add_tool(RecallTool(stack, recall_callback=recall))
    stack.add_tool(CollectTool(stack, collect_callback=collect))
    
    with open('/home/osiris/Projects/lorekeeper/prowl/examples/output/the-divided-realm_output.md', 'r') as f:
        co = f.read()
    docs = co.split("\n#")
    for i, doc in enumerate(docs):
        ee = "#" if i > 0 else ""
        #print(ee + doc)
        #await asyncio.sleep(4)
        await collect(str(i), ee + doc)
    
    r = await stack.run(['input', 'tottest'], inputs={
        'user_request': 'How would Allistair and Jasper meet?',
        'num_questions': 'three',
    })
    #print(r.to_dict())
    print(r.completion)
    print(r.var('critical_answer').hist())

asyncio.run(main())