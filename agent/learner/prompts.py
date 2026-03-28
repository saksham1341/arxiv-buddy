from langchain_core.prompts import PromptTemplate


ARTICLE_DESCRIPTION_GENERATOR_PROMPT = PromptTemplate.from_template(template="""
You are an expert research assistant.

Given the abstract of a research paper, generate a concise 1–2 sentence description that captures:
- The main topic or problem addressed
- The key contribution, method, or finding
- Any important context (domain, application, or significance)

Guidelines:
- Be precise, factual, and neutral (no speculation or exaggeration)
- Do not repeat the abstract verbatim
- Avoid jargon where possible, but preserve important technical terms
- Make it useful for semantic search and retrieval (include meaningful keywords)
- Keep it within 40–60 words total

Output Instructions:
{OUTPUT_FORMAT}

Abstract:
{ABSTRACT}
""")
