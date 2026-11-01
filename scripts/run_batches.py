"""Runs the items of ai_selection/shortlist.csv (kept locally, not in the published repo) whose status starts with `selected` in batches.
After each batch: build the views, commit, push.
Stops (after publishing what finished) if an item fails or the logged cost passes --max-cost-usd.
Usage: run_batches.py [--batch 10] [--parallel 10] [--max-cost-usd 8]      (needs OPENROUTER_ENV_FILE, see qwen_env.py)
"""
import argparse, csv, json, subprocess, sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
OUT = SCRIPTS.parent
TRAILER = "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"


def item_dir(sample_id: str) -> Path:
    return OUT / "items" / sample_id.replace("/", "__")


def selected_ids() -> list:
    with open(OUT / "ai_selection" / "shortlist.csv", newline="", encoding="utf-8") as handle:
        return [row["sample_id"] for row in csv.DictReader(handle) if row["status"].startswith("selected")]


def total_cost() -> float:
    return sum(json.loads(p.read_text())["cost_usd"] for p in (OUT / "items").glob("*/summary.json"))


def finished_count() -> int:
    return len(list((OUT / "items").glob("*/ranking.jsonl")))


def run(cmd: list, log=None) -> int:
    return subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT if log else None).returncode


def publish(message: str) -> None:
    run(["git", "-C", str(OUT), "add", "-A"])
    run(["git", "-C", str(OUT), "commit", "-q", "-m", message, "-m", TRAILER])
    if run(["git", "-C", str(OUT), "push", "-q", "origin", "main"]):
        print("WARNING: push failed; it will be retried after the next batch", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=int, default=10)
    parser.add_argument("--parallel", type=int, default=10)
    parser.add_argument("--max-cost-usd", type=float, default=8.0)
    args = parser.parse_args()
    todo = [i for i in selected_ids() if not (item_dir(i) / "ranking.jsonl").exists()]
    print(f"{len(todo)} items to run, batches of {args.batch}, {args.parallel} at a time", flush=True)
    for number, start in enumerate(range(0, len(todo), args.batch), 1):
        chunk = todo[start:start + args.batch]
        with open(OUT / "items" / f"_batch_{finished_count()}_done_before.log", "w") as log:
            code = run([sys.executable, str(SCRIPTS / "run_items.py"), "--parallel", str(args.parallel), "--max-calls", "80", *chunk], log)
        run([sys.executable, str(SCRIPTS / "build_views.py")])
        publish(f"Add batch {number}: {finished_count()} of {len(selected_ids())} selected items done, logged cost so far ${total_cost():.2f}")
        print(f"batch {number}: exit={code}; {finished_count()} items done; logged cost ${total_cost():.2f}", flush=True)
        if code:
            print("STOP: an item failed; see its run.log", flush=True)
            return 1
        if total_cost() > args.max_cost_usd:
            print(f"STOP: logged cost passed ${args.max_cost_usd}", flush=True)
            return 2
    print("all done", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
