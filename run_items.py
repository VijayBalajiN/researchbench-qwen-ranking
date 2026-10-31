"""Runs ResearchBench's own ranking pipeline (run-rank, then score-rank) on chosen items: one process and one folder per item.

Usage:  run_items.py [--parallel N] [--max-calls M] <sample_id> [<sample_id> ...]
Per item, outputs/items/<sample_id with / -> __>/ gets:
  item.jsonl         the dataset row, as run-rank reads it           ranking.jsonl        run-rank's output
  paper.json         title / abstract / doi of the source paper       ranking.score.json   score-rank's output
  calls.jsonl        every request: prompt + the provider's whole reply (answer, thinking, tokens, cost)
  run.log            what the run-rank process printed
An item whose ranking.jsonl already exists is skipped; a calls.jsonl left by a crashed attempt is kept as calls.partial-<time>.jsonl.
"""
import argparse, json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODEL = "qwen/qwen3.8-27b"


def folder_for(sample_id: str) -> Path:
    return ROOT / "outputs" / "items" / sample_id.replace("/", "__")


def load_rows(path: Path) -> dict:
    return {r["sample_id"]: r for r in map(json.loads, path.read_text(encoding="utf-8").splitlines()) if r}


def prepare(sample_id: str, ranking: dict, papers: dict) -> Path:
    folder = folder_for(sample_id)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "item.jsonl").write_text(json.dumps(ranking[sample_id], ensure_ascii=False) + "\n", encoding="utf-8")
    paper = papers[sample_id]
    (folder / "paper.json").write_text(json.dumps({k: paper.get(k) for k in ("sample_id", "doi", "title", "abstract")},
                                                  ensure_ascii=False, indent=1), encoding="utf-8")
    calls = folder / "calls.jsonl"
    if calls.exists():
        calls.rename(folder / f"calls.partial-{int(time.time())}.jsonl")
    return folder


def run_one(sample_id: str, folder: Path, max_calls: int) -> int:
    env = {**os.environ, "RESEARCHBENCH_CALL_LOG": str(folder / "calls.jsonl")}
    cli = str(ROOT / ".venv" / "bin" / "researchbench")
    run = [sys.executable, str(ROOT / "outputs" / "qwen_env.py"), "--max-calls", str(max_calls), "--", cli, "run-rank",
           "--data", str(folder / "item.jsonl"), "--model-name", MODEL, "--order", "both", "--concurrency", "1",
           "--out", str(folder / "ranking.jsonl")]
    with open(folder / "run.log", "w") as log:
        code = subprocess.run(run, env=env, stdout=log, stderr=subprocess.STDOUT).returncode
        if code == 0:
            code = subprocess.run([cli, "score-rank", "--pred", str(folder / "ranking.jsonl")], stdout=log,
                                  stderr=subprocess.STDOUT).returncode
    return code


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parallel", type=int, default=3)
    parser.add_argument("--max-calls", type=int, default=80, help="hard cap on requests per item (30 are expected)")
    parser.add_argument("ids", nargs="+")
    args = parser.parse_args()
    ranking = load_rows(ROOT / "data" / "ranking" / "ranking.jsonl")
    papers = load_rows(ROOT / "data" / "papers" / "papers.jsonl")
    todo = []
    for sample_id in args.ids:
        if (folder_for(sample_id) / "ranking.jsonl").exists():
            print(f"skip (done): {sample_id}", flush=True)
        else:
            todo.append((sample_id, prepare(sample_id, ranking, papers)))

    def job(pair):
        started = time.time()
        code = run_one(pair[0], pair[1], args.max_calls)
        print(f"{'ok  ' if code == 0 else 'FAIL'} {pair[0]}  exit={code}  {time.time() - started:.0f}s", flush=True)
        return code

    with ThreadPoolExecutor(max_workers=args.parallel) as pool:
        codes = list(pool.map(job, todo))
    return 1 if any(codes) else 0


if __name__ == "__main__":
    sys.exit(main())
