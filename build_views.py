"""Builds the readable views from what the runs recorded (no model calls). Idempotent; safe to re-run after every batch.

Per item folder (outputs/items/*/ with a ranking.jsonl):  summary.json  (requests, tokens, cost, time, result)
                                                           READABLE.md   (question, gold, every negative, the model's reply and thinking)
Top level (outputs/):  ALL_ranking.jsonl + ALL_ranking.score.json (all items through ResearchBench's own score-rank), SUMMARY.md
"""
import json, subprocess, sys
from pathlib import Path

from researchbench.ranking import SELECTION_RE  # the pattern run-rank looks for before it falls back to a looser one

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "outputs" / "items"


def read_jsonl(path: Path) -> list:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def message_of(call: dict) -> dict:
    return call["response"]["choices"][0]["message"]


def summarize(folder: Path, prediction: dict, calls: list) -> dict:
    usage = [c["response"].get("usage") or {} for c in calls]
    empty = sum(1 for c in calls if not (message_of(c).get("content") or "").strip())
    replies = [comp["raw_response"] for v in prediction["orders"].values() for comp in v["comparisons"]]
    start = min((c["started_at"] for c in calls), default=0)
    end = max((c["started_at"] + c["elapsed_s"] for c in calls), default=0)
    return {
        "sample_id": prediction["sample_id"], "model": prediction.get("model"),
        "comparisons": len(replies), "replies_in_the_expected_format": sum(1 for r in replies if SELECTION_RE.search(r)),
        "requests_logged": len(calls), "retried_attempts": sum(1 for c in calls if c["attempt"] > 1), "empty_replies": empty,
        "prompt_tokens": sum(u.get("prompt_tokens", 0) for u in usage),
        "completion_tokens": sum(u.get("completion_tokens", 0) for u in usage),
        "reasoning_tokens": sum((u.get("completion_tokens_details") or {}).get("reasoning_tokens", 0) for u in usage),
        "cost_usd": round(sum(u.get("cost", 0) or 0 for u in usage), 6),
        "wall_seconds": round(end - start), "sum_request_seconds": round(sum(c["elapsed_s"] for c in calls)),
        "providers": sorted({c["response"].get("provider") or "?" for c in calls}),
        "result": {order: {"rank": v["rank"], "gold_wins": v["gold_wins"]} for order, v in prediction["orders"].items()},
    }


def readable(item: dict, paper: dict, prediction: dict, calls: list) -> str:
    by_reply = {}
    for call in calls:
        by_reply.setdefault((message_of(call).get("content") or ""), []).append(call)
    negatives = [("fake", n) for n in item["fake_negative_hypotheses"]] + [("model", n) for n in item["model_negative_hypotheses"]]
    out = [f"# {paper.get('title')}\n", f"`{item['sample_id']}` | {item['discipline']} | {item['source_variant']} | doi {item.get('doi')}\n",
           f"**Abstract:** {paper.get('abstract')}\n", f"**Research question:** {item['research_question']}\n",
           f"**Gold hypothesis** ({len(item['gold_hypothesis'].split())} words): {item['gold_hypothesis']}\n",
           "`res` = gold is candidate 1; `fan_1_res` = gold is candidate 2. Gold wins an order if it beats at least 8 of the 15 negatives.\n"]
    for order, v in prediction["orders"].items():
        out.append(f"\n## Order `{order}`: rank {v['rank']}, gold wins = {v['gold_wins']}\n")
        for comp in v["comparisons"]:
            kind, text = negatives[comp["negative_index"]]
            matches = by_reply.get(comp["raw_response"]) or [None]
            call = matches.pop(0)
            think = (message_of(call).get("reasoning") or "").strip() if call else ""
            cost = (call["response"].get("usage") or {}).get("cost") if call else None
            out.append(f"\n### Negative {comp['negative_index']} ({kind}, {len(text.split())} words): model chose **{comp['selected']}** "
                       f"(candidate {comp['selection']})" + (f", ${cost:.4f}" if cost is not None else "") + f"\n\n> {text}\n")
            out.append(f"<details><summary>reply</summary>\n\n{comp['raw_response'].strip()}\n\n</details>\n")
            if think:
                out.append(f"<details><summary>thinking</summary>\n\n{think}\n\n</details>\n")
    return "\n".join(out)


def scrub_local_paths(folder: Path) -> None:
    """run-rank prints absolute paths into run.log; replace the clone's location so no local path is published."""
    log = folder / "run.log"
    if log.exists():
        log.write_text(log.read_text(encoding="utf-8").replace(str(ROOT), "<clone>"), encoding="utf-8")


def build_item(folder: Path) -> dict:
    scrub_local_paths(folder)
    item = read_jsonl(folder / "item.jsonl")[0]
    paper = json.loads((folder / "paper.json").read_text(encoding="utf-8"))
    prediction = read_jsonl(folder / "ranking.jsonl")[0]
    calls = read_jsonl(folder / "calls.jsonl") if (folder / "calls.jsonl").exists() else []
    summary = summarize(folder, prediction, calls)
    (folder / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    (folder / "READABLE.md").write_text(readable(item, paper, prediction, calls), encoding="utf-8")
    return {**summary, "title": paper.get("title"), "discipline": item["discipline"]}


def build_top(rows: list, folders: list) -> None:
    pred = ROOT / "outputs" / "ALL_ranking.jsonl"
    pred.write_text("".join((f / "ranking.jsonl").read_text(encoding="utf-8") for f in folders), encoding="utf-8")
    subprocess.run([str(ROOT / ".venv" / "bin" / "researchbench"), "score-rank", "--pred", str(pred)], check=True,
                   stdout=subprocess.DEVNULL)
    lines = ["# Summary of all items run so far\n", "| item | discipline | gold first (`res`) | gold second (`fan_1_res`) | requests | cost USD | wall s |",
             "|---|---|---|---|---|---|---|"]
    for r in rows:
        cell = lambda o: f"rank {r['result'][o]['rank']} ({'win' if r['result'][o]['gold_wins'] else 'loss'})"
        lines.append(f"| {r['sample_id']} | {r['discipline']} | {cell('res')} | {cell('fan_1_res')} | {r['requests_logged']} | "
                     f"{r['cost_usd']:.4f} | {r['wall_seconds']} |")
    lines.append(f"| **total ({len(rows)} items)** | | | | {sum(r['requests_logged'] for r in rows)} | "
                 f"{sum(r['cost_usd'] for r in rows):.4f} | |")
    lines.append(f"\nTokens: prompt {sum(r['prompt_tokens'] for r in rows)}, completion {sum(r['completion_tokens'] for r in rows)} "
                 f"(of which reasoning {sum(r['reasoning_tokens'] for r in rows)}). Retried attempts: {sum(r['retried_attempts'] for r in rows)}. "
                 f"Empty replies: {sum(r['empty_replies'] for r in rows)}.\n")
    lines.append("Scores from ResearchBench's own `score-rank` over all items: `ALL_ranking.score.json`.\n")
    (ROOT / "outputs" / "SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    folders = sorted(f for f in ITEMS.iterdir() if (f / "ranking.jsonl").exists())
    rows = [build_item(f) for f in folders]
    if rows:
        build_top(rows, folders)
    print(f"built views for {len(rows)} items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
