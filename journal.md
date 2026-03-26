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
