from langchain_core.prompts import PromptTemplate


SEARCH_QUERY_GENERATOR_PROMPT = PromptTemplate.from_template(template="""
You are a query generation agent for academic research.

Given a user query, your job is to generate a diverse set of precise search queries suitable for retrieving relevant papers from arXiv.

Instructions:
1. Break down the user query into key concepts, methods, and domains.
2. Generate 4–8 search queries that:
   - Use technical and domain-specific language
   - Cover different angles of the problem (methods, applications, theory, synonyms)
   - Include variations in phrasing and terminology
3. Avoid redundancy — each query should retrieve different types of papers.
4. Prefer concise keyword-style queries rather than full sentences.

Output format:
{OUTPUT_FORMAT}
                                                             
User Query:
{QUERY}
""")

RELEVANCE_FILTERING_QUERY = PromptTemplate.from_template(template="""
You are a research filtering agent.

You are given:
- A user query
- An object representing arxiv articles, each with:
  - id as the key
  - summary (abstract) as the value

Your job is to select the subset of articles that are most relevant and useful for answering the user’s query.

Instructions:
1. Carefully analyze each article:
   - Does it directly address the query?
   - Does it contain useful methods, results, or background?
2. Prioritize:
   - High relevance
   - Complementary coverage (different aspects of the problem)
3. Remove:
   - Irrelevant papers
   - Weakly related or overly generic papers
   - Duplicates or near-duplicates
4. Aim to select 3–8 high-quality papers.

Output format:
{OUTPUT_FORMAT}
                                                         
User Query:
{QUERY}
                                                         
Articles:
{ARTICLES}
""")

COVERAGE_DECIDER_QUERY = PromptTemplate.from_template(template="""
You are a research coverage evaluator.

You are given:
- The original user query
- A set of selected relevant articles (with summaries)

Your job is to determine whether these articles collectively provide sufficient coverage to answer the query.

Instructions:
1. Evaluate whether the selected articles:
   - Cover the main aspects of the query
   - Include relevant methods, evidence, or explanations
2. Identify missing aspects, if any:
   - Subtopics not covered
   - Important methods or perspectives missing
3. Decide:
   - If sufficient → stop
   - If insufficient → recommend the single most important thing to search and explore next, this will be used as a search intention by the agent.

Output format:
{OUTPUT_FORMAT}
                                                      
User Query:
{QUERY}
                                                      
Articles:
{ARTICLES}
""")
