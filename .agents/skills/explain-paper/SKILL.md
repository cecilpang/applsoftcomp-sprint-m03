---
name: explain-paper
description: Explains a paper comprehensively and concisely.
---

Read the paper by running `tools/extract_pdf.py` to extract text from PDF files.

```
uv run python3 tools/extract_pdf.py <input.pdf>
```
(Use `python` instead of `python3` if that's what your environment provides.)


When explaining a paper, always include:

1. Motivation: Why was this research conducted? What problem does it solve or question does it answer?

2. Diff of ideas: How does it differ from previous research? Why is this difference crucial? Why not use existing methods/theories?

3. Method: What approach/methodology addresses the research question? (experimental design, data collection, analysis techniques, theoretical frameworks)

4. Results: What are the key findings? How do they contribute to the field? Any surprising/significant results?

5. Significance: How does it advance understanding? What are potential applications/implications?

Draw from abstract, intro, and conclusion for a well-rounded explanation, with quotes and references to specific sections for clarity. Accessible to general audience while maintaining depth of original research.

**Style:**

- Use clear, concise language
- Avoid jargon unless necessary. Define when used. 
- Use LaTeX for equations.
- Display mode for key equations. 
- Max 3 sentences/paragraph. 
- Prefer narrative over bullet points/lists for conversational tone.



