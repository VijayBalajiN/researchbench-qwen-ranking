# How the AI-related items were chosen

ResearchBench's ranking file has 1,323 items in 12 disciplines (Astronomy, Biology, Business, Cell Biology, Chemistry, Earth Science,
Energy Science, Environmental Science, Law, Material Science, Math, Physics). **None of them is "AI" or "CS"**, so AI-related items
have to be found by reading. No keyword filter was used for the selection.

1. **Every title was read.** `reviewed_titles.tsv` lists all 1,323 items (index, `sample_id`, title) in the order they were read
   (sorted by discipline, then `sample_id`). Titles come from the dataset's `papers/papers.jsonl`.
2. **Candidates were marked by judgement** on whether the paper's contribution is about developing, applying, evaluating or governing
   AI/ML (deep learning, LLMs, neural networks, AI ethics/law/adoption). Papers that only use a statistical model, an optimiser
   or "intelligent" in a product sense were left out.
3. **The abstracts of the 40 selected items were read** to confirm they are AI-related. The 28 reserve items were judged from the
   title only; their abstracts have not been read.
4. The same paper can appear under several disciplines with different `sample_id`s (e.g. the diabetic-retinopathy deep-learning
   paper, scGPT, "Generative AI in marketing"). Only one copy of each paper was shortlisted.

`shortlist.csv`: `status` is `selected_40` (abstract read) or `reserve`; `kind` says what role AI plays in the paper
(AI method, AI applied to a science, AI adoption, AI ethics/law, AI theory, ...). The 40 cover all 12 disciplines: Business 6,
Math 6, Astronomy 5, Law 5, Biology 4, Earth Science 4, Cell Biology 2, Energy Science 2, Environmental Science 2, Material Science 2,
Chemistry 1, Physics 1 (a spread, not a quota: it is what the reading turned up).

**Caveats.** The selection was made by Claude (an AI model) reading titles and abstracts, not by a human domain expert; the
discipline labels are the dataset's own (for example a COVID-19 machine-learning paper is filed under Physics, and many "Math"
items are not mathematics). "AI-related" is a judgement call at the edges.
