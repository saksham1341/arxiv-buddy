from langchain_core.prompts import PromptTemplate


SEMANTICALLY_SPLIT_CONTENT_PROMPT = PromptTemplate.from_template(template="""
You are given raw text extracted from a PDF. This text will be used in a **retrieval-augmented generation (RAG)** system to answer user questions.

The pipeline works as follows:

* The text will be split into sections.
* Each section will be converted into a concise semantic description.
* These descriptions will be embedded and used for retrieval.
* Retrieved sections will be used to answer questions.

### Your Goal:

Split the text into **semantic sections that maximize retrieval quality** for question answering.

### Guidelines for Splitting:

1. Each section should contain a **self-contained, meaningful unit of information** that can answer or contribute to answering a question.
2. Keep together content that belongs to the same concept, even if it spans multiple paragraphs.
3. Split when there is a **clear topic shift, heading change, or conceptual boundary**.
4. Avoid sections that are:

   * Too small (lack context for answering questions)
   * Too large (contain multiple unrelated ideas that hurt retrieval precision)
5. Prefer splits that would allow a generated description to clearly capture:

   * What the section is about
   * What questions it could answer

### Instructions:

* Do NOT modify, rewrite, or summarize the text.
* Use the **original character indices** of the input text.
* Only determine the split boundaries.

### Output Format:

Return a JSON array of integers representing the **end index (exclusive)** of each section **EXCEPT the final section**.

### Constraints:

* Indices must be strictly increasing.
* Do NOT include 0 as a boundary.
* Do NOT include the final index (i.e., the length of the text).
* Sections must be contiguous and cover the text when combined with the implicit final section.
* Each section should be semantically meaningful and useful for retrieval.
* If the entire text forms a single coherent semantic unit, you MAY return an empty list `[]`.

### Example:

Input text:
"Introduction\nThis is a paper.\nMethods\nWe did experiments."

Output:
{SAMPLE_OUTPUT}

(Here, the final section from index 24 to the end is implicit and omitted.)

### Output Format Instructions

{OUTPUT_INSTRUCTIONS}

### Text to process:

{TEXT}

""")

EMBEDDABLE_STRINGS_GENERATOR_PROMPT = PromptTemplate.from_template(template="""
You are given a section of text extracted from a PDF. This will be used in a **retrieval-augmented generation (RAG)** system.

The pipeline works as follows:

* This section represents a semantically coherent chunk of the original document.
* You will generate one or more **concise semantic descriptions** of this section.
* These descriptions will be embedded and used for retrieval.
* Retrieved sections will be used to answer user questions.

### Your Goal:

Generate **high-quality, retrieval-optimized embedding strings** that maximize the chances of this section being retrieved for relevant user queries.

### Key Principles:

1. Each string should capture:

   * The **main topic**
   * The **key facts, concepts, or claims**
   * The **types of questions this section can answer**
2. Write strings as if they are **searchable knowledge entries**, not summaries.
3. Use **natural language phrasing similar to how a user might ask questions**.
4. Include **important keywords, terminology, and entities** from the text.
5. Prefer **specificity over vagueness**.

### Multiple Strings:

* You MAY generate multiple strings per section.
* Do this when the section contains **multiple distinct ideas or query angles**.
* Each string should focus on a **different retrieval angle** (e.g., definition, process, comparison, use-case).

### Style Guidelines:

* Each string should be **1–2 sentences max**.
* Avoid fluff, filler, or meta language.
* Do NOT refer to “this section” or “the text”.
* Do NOT include irrelevant details.
* Do NOT repeat the same idea across multiple strings.

### Examples of Good Strings:

* "How does gradient descent work in machine learning and what problem does it solve?"
* "Definition of photosynthesis and the role of chlorophyll in energy conversion"
* "Steps involved in the HTTP request-response cycle and how servers process requests"

### Output Format:

{OUTPUT_FORMAT}

### Constraints:

* Each string must be self-contained and understandable without additional context.
* Avoid redundancy across strings.
* Prefer fewer high-quality strings over many low-quality ones (typically 1–5).

### Text to process:

{TEXT}
""")
