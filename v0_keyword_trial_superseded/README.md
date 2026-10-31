# v0 keyword trial (superseded)

The first 3-item trial. Its items were picked with a keyword rule (research question and gold hypothesis both mention AI/ML),
which was then dropped in favour of a hand-made shortlist (`../ai_selection/`). This run used the first version of the client
patch (`clients_local_patch_v0.diff`): thinking on, but **no call log**, so the model's hidden thinking and token usage were not
recorded; only the visible replies are in `ranking_qwen3.8-27b_trial3.jsonl`.

- `ranking_trial3.jsonl` – the three input items; `ranking_qwen3.8-27b_trial3.jsonl` – run-rank output;
  `ranking_qwen3.8-27b_trial3.score.json` – score-rank output; `READABLE.md` – readable view; `run.log`; `select_ai_items.py` – the keyword rule.
- Result: 90 comparisons, all in the expected format; gold won in 3 of the 6 item/order runs (overall accuracy 50%), see `ranking_qwen3.8-27b_trial3.score.json`.
- Cost was not measured per call; the account's daily counter read $0.298 afterwards (includes one smoke call).
