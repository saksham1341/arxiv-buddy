from langchain_core.prompts import PromptTemplate


SEMANTICALLY_SPLIT_CONTENT_PROMPT = PromptTemplate.from_template(template="""
You are given raw text extracted from a PDF. This text will be used in a **retrieval-augmented generation (RAG)** system to answer user questions.

The pipeline works as follows:

* The text will be split into sections.
* Each section will be converted into a concise semantic description.
* These descriptions will be embedded and used for retrieval.
* Retrieved sections will be used to answer questions.

### Your Goal:

Select and extract **high-value semantic sections** that maximize retrieval quality for question answering.

You are allowed to **skip irrelevant or low-value content** that is unlikely to help answer user questions.

---

### What to INCLUDE:

Include sections that:
- Contain **definitions, explanations, concepts, or descriptions**
- Provide **factual, instructional, or technical information**
- Contain **arguments, insights, or reasoning**
- Would help answer likely user questions

---

### What to SKIP:

Do NOT include sections that are not useful for retrieval, such as:
- References / bibliography
- Citations or citation lists
- Acknowledgments
- Table of contents
- Headers/footers
- Page numbers
- Repeated boilerplate text
- Copyright notices
- Purely decorative or formatting content
- Lists of names without explanatory context

If a portion of text contains both useful and useless content, include only the useful part.

---

### Guidelines for Splitting:

1. Each section should contain a **self-contained, meaningful unit of information**.
2. Keep together content that belongs to the same concept, even across multiple paragraphs.
3. Split when there is a **clear topic shift, heading change, or conceptual boundary**.
4. Avoid sections that are:
   - Too small (lack context)
   - Too large (contain multiple unrelated ideas)
5. Each section should be suitable for generating a semantic description that clearly answers:
   - What is this about?
   - What questions could it answer?

---

### Instructions:

* Do NOT modify, rewrite, or summarize the text.
* Use the **original character indices** of the input text.
* Return only sections that you decide to KEEP.
* Skipped content should simply not appear in the output.

---

### Output Format:

Return a JSON array of `[start, end)` index pairs representing the selected sections.

Example:
[[0, 120], [240, 560], [800, 1020]]

---

### Constraints:

* Indices must be:
  - Valid character offsets
  - Strictly increasing
  - Non-overlapping
* Each pair must follow: start < end
* Do NOT include empty sections
* Sections do NOT need to cover the entire text (skipping is allowed)
* If no useful content exists, return an empty list `[]`

---

### Output Format Instructions

{OUTPUT_INSTRUCTIONS}

---

### Text to process:

{TEXT}""")

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
