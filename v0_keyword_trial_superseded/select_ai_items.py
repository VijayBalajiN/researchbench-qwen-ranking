"""Pick AI-related items from the full ResearchBench ranking file (it has no AI/CS discipline, so this is a keyword rule).
Rule: the research question AND the gold hypothesis both mention AI/ML. Usage: select_ai_items.py <out.jsonl> <n> [seed]
(n = 0 writes all matches; otherwise a reproducible random sample of n, sorted by sample_id.)"""
import json, random, re, sys
ci = re.compile(r"\b(machine learning|deep learning|neural networks?|artificial intelligence|large language models?|language models?|"
                r"reinforcement learning|transformers?|convolutional|generative models?|supervised learning|LLMs?)\b", re.I)
cs = re.compile(r"\b(AI|LLMs?|GPT)\b")
hit = lambda t: bool(ci.search(t) or cs.search(t))
rows = [json.loads(l) for l in open("data/ranking/ranking.jsonl")]
match = sorted((r for r in rows if hit(r["research_question"]) and hit(r["gold_hypothesis"])), key=lambda r: r["sample_id"])
out, n = sys.argv[1], int(sys.argv[2]); seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
pick = match if n == 0 else sorted(random.Random(seed).sample(match, n), key=lambda r: r["sample_id"])
with open(out, "w") as f:
    for r in pick: f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(f"{len(match)} AI-related items match; wrote {len(pick)} to {out}")
for r in pick: print(r["sample_id"], "|", r["research_question"][:150])
