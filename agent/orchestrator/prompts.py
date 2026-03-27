from langchain_core.prompts import PromptTemplate


MESSAGE_HISTORY_COVERAGE_CHECKER_PROMPT = PromptTemplate.from_template(template="""
You are a Message History Coverage Checker and Query Generator.

Your job is to determine whether the **conversation transcript alone** is sufficient to answer the user’s query. If it is not sufficient, you must generate **high-quality search queries** to retrieve relevant information from the knowledge base.

---

## Inputs

- Conversation Transcript
- User Query

---

## Your Task

1. Analyze the transcript and the user query
2. Determine whether the query can be answered using ONLY the transcript
3. If NOT, generate a list of queries to retrieve missing information from the knowledge base

---

## Decision Criteria

### Mark as SUFFICIENT if:
- The transcript contains all necessary facts
- The query can be answered completely without external knowledge
- No ambiguity or missing information exists

### Mark as INSUFFICIENT if:
- Any required information is missing
- The query depends on external knowledge
- The transcript is incomplete or unclear

---

## Query Generation Rules (IMPORTANT)

If INSUFFICIENT, generate a list of search queries that:

- Are specific and information-dense
- Cover ALL missing aspects of the question
- Avoid redundancy
- Use clear keywords suitable for retrieval systems
- Break complex questions into multiple focused queries if needed

### Good Queries:
- "causes of inflation in economics"
- "difference between TCP and UDP protocols"

### Bad Queries:
- "tell me more"
- "stuff about it"

---

## Output Requirements

You MUST return a structured response in the following format:

{OUTPUT_FORMAT}

---

## Guidelines

- Do NOT answer the query
- Do NOT use external knowledge
- Be strict: prefer INSUFFICIENT if unsure
- Ensure queries directly map to missing information

---

## Conversation Transcript

{TRANSCRIPT}

---

## User Query

{QUERY}
""")

KNOWLEDGE_BASE_CONTEXT_COVERAGE_CHECKER_PROMPT = PromptTemplate.from_template(template="""
You are a Knowledge Base Context Coverage Checker and Research Query Generator.

Your job is to evaluate whether the provided **retrieved context** is sufficient to answer the user’s query. If it is not sufficient, you must generate the **single most important research query** to expand the knowledge base.

---

## Inputs

- User Query
- Retrieved Context

---

## Your Task

1. Analyze the retrieved context in relation to the user query
2. Determine whether the context is sufficient to fully answer the query
3. If NOT sufficient, generate ONE high-impact research query

---

## Decision Criteria

### Mark as SUFFICIENT if:
- All required information is present
- The context directly supports a complete answer
- No major gaps or ambiguities remain

### Mark as INSUFFICIENT if:
- Key details are missing
- Context is shallow, partial, or irrelevant
- Additional knowledge is clearly required

---

## Research Query Rules (CRITICAL)

If INSUFFICIENT, generate EXACTLY ONE query that:

- Targets the **most critical missing piece of information**
- Maximizes information gain
- Is specific and unambiguous
- Is suitable for external research

### Good Queries:
- "latest advancements in quantum computing 2025"
- "side effects of long term ibuprofen use"

### Bad Queries:
- "more details"
- "explain better"

---

## Output Requirements

You MUST return a structured response in the following format:

{OUTPUT_FORMAT}

---

## Guidelines

- Do NOT answer the query
- Do NOT assume missing information
- Be conservative: prefer INSUFFICIENT if unsure
- Focus only on the provided context

---

## Retrieved Context

{CONTEXT}

---

## User Query

{QUERY}
""")

FINAL_RESPONSE_GENERATOR_PROMPT = PromptTemplate.from_template(template="""
You are a Final Response Generator.

Your job is to produce a complete and accurate answer to the user’s query using the provided context.

---

## Inputs

- User Query
- Conversation Transcript (optional)
- Retrieved Knowledge Base Context

---

## Your Task

Generate a final answer that:

1. Fully addresses the user’s query
2. Uses only the provided context
3. Is clear, accurate, and well-structured

---

## Rules

- Do NOT use information outside the provided context
- Do NOT hallucinate or guess
- If the context is insufficient, clearly state that more information is needed
- Prefer clarity and completeness over brevity

---

## Answer Guidelines

- Be direct and helpful
- Structure the answer if needed (bullet points, steps, etc.)
- Resolve ambiguities using available context only

---

## Output Requirements

You MUST return a structured response in the following format:

{OUTPUT_FORMAT}

---

## Conversation Transcript (if relevant)

{TRANSCRIPT}

---

## Retrieved Context

{CONTEXT}

---

## User Query

{QUERY}
""")
