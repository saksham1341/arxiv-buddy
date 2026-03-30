from langchain_core.prompts import PromptTemplate


MESSAGE_HISTORY_COVERAGE_CHECKER_PROMPT = PromptTemplate.from_template(template="""
You are a Message History Coverage Checker + Query Completeness Analyzer.

Your task is to:
1. Determine whether the user query is complete on its own
2. If not, attempt to resolve it using the conversation transcript
3. Decide whether the transcript is sufficient to answer the query
4. Generate a user intent string
5. Produce either a final answer, KB queries, or a clarification request

---

## Inputs
- Conversation Transcript
- User Query
- Current Conversation Title

---

## Step 1: Check Query Completeness

Determine whether the user query is self-contained and understandable WITHOUT prior context.

Mark:
- `is_query_complete = true` if the query is clear and specific on its own
- `is_query_complete = false` if it depends on prior context (e.g., "explain it", "summarize that", "what about this?")

---

## Step 2: Resolve Incomplete Queries

If `is_query_complete = true`:
1. Create `resolved_query` (a refined and fully specified version of user's query)
2. Go to step 3

If `is_query_complete = false`:

1. Attempt to infer the missing context using the conversation transcript
2. If the intent can be clearly reconstructed:
   - Create `resolved_query` (a fully specified version of the query)
   - Mark `is_query_resolvable_from_history = true`
3. If NOT:
   - Mark `is_query_resolvable_from_history = false`
   - Generate a clarification response asking the user for more details
   - Skip remaining steps

---

## Step 3: Determine Message History Sufficiency

Using `resolved_query`, decide if the transcript ALONE is sufficient to answer the query.

Mark `is_message_history_enough = true` ONLY if:
- All required information is explicitly present in the transcript
- No external knowledge is needed
- There is no ambiguity

Otherwise mark it as false.

---

## Step 4: Conversation Title Relevancy

If the query is succesfully resolved, check if the current conversation title represents the query.

If NOT:
- Generate a short `new_conversation_title` with maximum length of 5 words whih represents the resolved query.

## Step 5: Produce Output

### Case A — Query NOT resolvable
Return:
- `is_query_complete = false`
- `is_query_resolvable_from_history = false`
- `response` (ask for clarification)
- `resolved_query = null`
- `is_message_history_enough = null`
- `kb_queries = null`

---

### Case B — Message history sufficient
Return:
- `is_query_complete`
- `is_query_resolvable_from_history`
- `resolved_query`
- `is_message_history_enough = true`
- `response` (final answer)
- `kb_queries = null`

---

### Case C — Message history NOT sufficient
Return:
- `is_query_complete`
- `is_query_resolvable_from_history`
- `is_message_history_enough = false`
- `response = null`
- `kb_queries`:
  - A list of specific queries to retrieve missing information
  - Avoid vague phrasing
  - Cover all missing aspects needed to answer the query

---

## Constraints

- Do NOT use external knowledge
- Do NOT guess missing facts
- Be strict — if unsure, mark as insufficient
- Queries must directly map to missing information

---

## Output Format

{OUTPUT_FORMAT}

---

## Conversation Transcript

{TRANSCRIPT}

---

## User Query

{QUERY}
                                                                       
---

## Current Conversation Title

{CURRENT_CONVERSATION_TITLE}
""")

KNOWLEDGE_BASE_CONTEXT_COVERAGE_CHECKER_PROMPT = PromptTemplate.from_template(template="""
You are a Knowledge Base Context Coverage Checker.

Your task is to determine whether the retrieved context is sufficient to fully answer the user's query.

---

## Inputs
- User Query
- Retrieved Context

---

## Instructions

1. Evaluate how well the context answers the query.
2. Decide if the context is complete and sufficient.

---

## Decision Rules

Mark `is_kb_context_enough = true` ONLY if:
- The context contains all required information
- The answer can be fully constructed without gaps
- No major ambiguity remains

Otherwise mark it as false.

---

## If NOT sufficient

Generate `new_query_to_research`:
- EXACTLY ONE topic
- Must be a broad knowledge domain (not a question)
- Should represent the core missing information
- Keep it concise and meaningful

---

## If sufficient

- Provide the final answer in `response`
- Set `new_query_to_research` to null or empty

---

## Constraints

- Do NOT answer unless sufficient
- Do NOT hallucinate
- Do NOT generate multiple topics
- Prefer insufficient if unsure

---

## Output Format

{OUTPUT_FORMAT}

---

## Retrieved Context

{CONTEXT}

---

## User Query

{QUERY}
""")
