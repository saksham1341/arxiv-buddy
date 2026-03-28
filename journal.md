# Journal 

## March 26, 2026

Arxiv Buddy aims to answer any questions using the extensive research material hosted on [Arxiv](https://arxiv.org).

The main idea is to have a knowledge base which would basically be a map of embeddings to research papers.
When a question is asked, Arxiv Buddy will gather the related research papers from the knowledge base and use them as a context to formulate an answer.
It will also provide the exact references used.

Since it would take a lot of storage to literally chunk-embed every paper, I'm thinking of a slightly different approach:
- To store a research paper in the knowledge base, we will use an LLM to generate "embeddable strings", i.e., efficient descriptions of 
different parts of a research paper (can do multiple embeddable strings for the same part) and then saving embeddings of those, tagged with
the exact research paper and the starting/ending character information.
- When answering a question, the agent will query the knowledge base, collect the list of research paper parts it requires for the context,
then use a tool call to fetch those parts from Arxiv. To handle the Arxiv rate limits we will make the tool call use a SSE (server sent event)
to the cilent which will use the Arxiv API on their part to fetch those papers, extract the exact portion the agent needs, and send them over to
the server which will send it to the LLM as a tool call result.

## March 28, 2026

Initial version of the server has been implemented but the learning method right now is extremely expensive so I'm gonna change it.
Discussed a bit with Gemini, it gave me a couple of ways to go about it:
- Calculate sentence level embeddings -> compare neighbor sentence embedding similarity -> if below a certain threshold, assume topic changed and thus a chunk is created.
- Ask a cheap llm to generate a 1-2 line summary of a research paper (using it's abstract) and prepend it to all of it's chunks.
- Just use recursive text splitters (like the one given by langchain)

I am thinking of merging the last 2 options, creating chunks using text splitter and prepending a 1-2 sentence description of the paper to them and storing the embedding.

Also for retreival I will use a hybrid approach, obtaining high volumne of chunks using BM25 + vector search then do cross-ranking.

Let's see how it goes.
