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

## Second pass (for the next batch of items)

The first 40 came from the title reading above. For more, a second pass was made:

1. **The 28 reserve items' abstracts were read.** 25 were confirmed (`selected_extra`); 3 were rejected after reading
   (`rejected_after_reading_abstract`, with the reason in `kind`).
2. **A recall check.** A keyword search (AI/ML terms in the abstract or research question) was run **only to surface papers the title
   reading might have missed**; it did not select anything. It found 46 papers that had not been flagged. Each was then read
   (the snippet around the match, and for doubtful ones more of the abstract) and judged by hand; every decision, with a reason, is in
   `second_pass_recall.csv`. 13 were added (`selected_extra`); 11 are `tier2_ml_as_tool_not_run` (ML is used as a tool inside a paper
   that is about something else, e.g. a wearable sensor with a classifier); the rest were rejected (the term was incidental).
   Eight more title-only borderlines were also put in tier 2. **Tier 2 was run as `selected_tier2_ml_as_tool`** (19 items); these are
   papers where ML is a tool, not the subject, so read their results separately from the AI-subject items.
3. **Other dataset rows of the same paper.** A paper can appear in two disciplines, and those rows have a different research
   question, gold hypothesis and negatives (checked: none of the 10 pairs found is identical). They are separate benchmark
   items, so the second rows of selected papers are included as `selected_extra_other_row_of_same_paper`.

## Non-AI control sample

To reach 100 new items beyond the first 40, 33 items were drawn at random, **labelled `selected_non_ai_random_sample`**. Pool: the
1,156 ranking rows whose paper is not in `shortlist.csv` in any status and whose abstract and research question contain none of a broad
list of AI/ML terms (including 'algorithm', 'data-driven', 'classifier'). `draw_non_ai_sample.py` reproduces the draw (seed 20261101,
plain random, not stratified by discipline).

Counts in `shortlist.csv`: `selected_40` 40, `selected_extra` 38, `selected_extra_other_row_of_same_paper` 10, `selected_tier2_ml_as_tool` 19,
`selected_non_ai_random_sample` 33, `rejected_after_reading_abstract` 3. That is 140 selected rows: the first 40, then 100 new ones
(48 AI-related, 19 ML-as-tool, 33 non-AI). As before, the judgement is Claude's, not a domain expert's.
