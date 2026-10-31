# ResearchBench ranking, run with Qwen3.8-27B (AI-related items)

Outputs of running **ResearchBench's own hypothesis-ranking pipeline** ([paper](https://arxiv.org/abs/2503.21248),
[code](https://github.com/ankitala/ResearchBench), [data](https://huggingface.co/datasets/ankilok/ResearchBench)) with
`qwen/qwen3.8-27b` through OpenRouter, thinking on, on AI-related items of the benchmark. This repo only **records outputs**; it
does not compare the model with anything. It is a work in progress: items are added as they are run. Not affiliated with the
ResearchBench authors.

## What was run

| | |
|---|---|
| Pipeline | upstream `researchbench run-rank --order both` then `score-rank`, unchanged logic: for each item, the gold hypothesis is compared with each of its 15 negatives in both orders (30 requests per item), temperature 0.0, upstream prompt and parser. Gold "wins" an order if it beats at least 8 of the 15 negatives. |
| Upstream | `ankitala/ResearchBench` commit `03873e0` (MIT) plus one small patch, `clients_local_patch.diff` (below) |
| Model | `qwen/qwen3.8-27b` via OpenRouter, `reasoning.effort = high` |
| Data | the full `ranking.jsonl` (1,323 items) from Hugging Face; items chosen by hand, see `ai_selection/` |

**The patch** (one file, `src/researchbench/clients.py`, the OpenAI-compatible client). With none of its environment variables set
the client sends the same request as upstream.
1. `RESEARCHBENCH_REASONING_EFFORT=high` adds OpenRouter's `reasoning` field (thinking on).
2. `RESEARCHBENCH_CALL_LOG=file.jsonl` appends every request: the prompt and the provider's whole reply (answer, thinking, token usage, cost).
3. `RESEARCHBENCH_MAX_CALLS=N` is a hard cap on requests per process.
4. The SDK retries failed requests 6 times instead of 2, and an empty reply is retried (then raises). Upstream would return an empty
   string, which `run-rank` silently turns into "candidate 1".

## Layout

```
items/<discipline>__<doi>/   one folder per item
    item.jsonl            the dataset row exactly as run-rank read it (question, gold, 15 negatives)
    paper.json            title, abstract, doi of the source paper
    ranking.jsonl         run-rank's output: per order, rank, gold_wins and every comparison with the model's reply
    ranking.score.json    score-rank's output for this item
    calls.jsonl           every request: prompt + the provider's whole reply (answer, thinking, tokens, cost)
    summary.json          requests, retries, tokens, cost, time, result
    READABLE.md           the same, as a document: every negative, the reply and the thinking
    run.log
ALL_ranking.jsonl, ALL_ranking.score.json   all items together, through the same score-rank
SUMMARY.md              one table: result, requests, cost and time per item
ai_selection/           how the items were chosen: all 1,323 titles reviewed, shortlist of 40 (+28 reserve)
v0_keyword_trial_superseded/   the first 3-item trial (keyword-picked items, no call log), kept for completeness
build_views.py, run_items.py, qwen_env.py   the scripts that produced the above
clients_local_patch.diff   the patch
```

## Please read before using the numbers

- **Small and early.** A handful of items so far.
- **The items are not a random sample.** The benchmark has no AI/CS discipline; AI-related items were picked by reading titles and
  abstracts (by Claude, an AI model, not a domain expert). `ai_selection/README.md` has the details and the caveats.
- **`calls.jsonl` is the provider's reply as returned.** The thinking is the provider's `reasoning` field. Upstream's client keeps only
  the visible answer; the patch is what makes the rest available.
- **OpenRouter routes each request to one of several upstream providers** (listed per item in `summary.json`), so identical settings can
  still mean different serving stacks.
- **Upstream's parser falls back to "candidate 1"** if a reply has no recognisable choice. `summary.json` reports how many replies were
  in the expected format (`replies_in_the_expected_format` out of `comparisons`).
- Known property of the data (not of this run): in the shipped file the gold hypotheses are much shorter than the negatives.

## Reproduce

```
git clone https://github.com/ankitala/ResearchBench && cd ResearchBench && git checkout 03873e0
git apply <this repo>/clients_local_patch.diff
uv venv .venv && uv pip install --python .venv/bin/python -e ".[openai]"
hf download ankilok/ResearchBench --repo-type dataset --include "ranking/*" --include "papers/*" --local-dir data   # gated dataset
cp -r <this repo> outputs
OPENROUTER_ENV_FILE=/path/to/.env .venv/bin/python outputs/run_items.py --parallel 3 <sample_id> ...   # .env holds OPENROUTER_API_KEY
.venv/bin/python outputs/build_views.py
```

## Licences and credits

- Our scripts and write-up: MIT (`LICENSE`).
- ResearchBench code: MIT. **The dataset text in this repo** (research questions, hypotheses, negatives, titles, abstracts in
  `items/` and `ai_selection/`) is from the ResearchBench dataset, **CC BY-NC 4.0, non-commercial use only** (`DATA_LICENSE.md`);
  titles and abstracts originate from the papers' publishers, whose terms apply. Cite Liu et al., "ResearchBench: Benchmarking LLMs in
  Scientific Discovery via Inspiration-Based Task Decomposition", arXiv 2503.21248.
- Model replies are Qwen3.8-27B output.
