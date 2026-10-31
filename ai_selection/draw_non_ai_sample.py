"""Draws the seeded random sample of NON-AI items used to fill the count up to 100 new items, and adds them to shortlist.csv.
Pool = ranking rows whose paper is not in shortlist.csv (any status) and whose abstract and research question contain no AI/ML term
(broad list incl. 'algorithm', 'data-driven', 'classifier'). Run from the ResearchBench clone: python outputs/ai_selection/draw_non_ai_sample.py <n> [seed]"""
import csv, json, random, re, sys
n = int(sys.argv[1]); seed = int(sys.argv[2]) if len(sys.argv) > 2 else 20261101
papers = {r["sample_id"]: r for r in map(json.loads, open("data/papers/papers.jsonl"))}
rank = [json.loads(l) for l in open("data/ranking/ranking.jsonl")]
path = "outputs/ai_selection/shortlist.csv"
rows = list(csv.DictReader(open(path)))
flagged_ids = {r["sample_id"] for r in rows}
flagged_titles = {papers[s]["title"].strip().lower() for s in flagged_ids}
rx = re.compile(r"machine learning|deep learning|neural network|artificial intelligence|\bAI\b|\bLLMs?\b|language model|ChatGPT|\bGPT|transformer|"
                r"reinforcement learning|support vector|random forest|XGBoost|convolutional|physics-informed|\bPINNs?\b|\bANN\b|\bCNN\b|generative|"
                r"foundation model|AlphaFold|data-driven|supervised|classifier|autoencoder|federated learning|chatbot|computer vision|natural language|algorithm", re.I)
pool = [r["sample_id"] for r in rank if r["sample_id"] not in flagged_ids and papers[r["sample_id"]]["title"].strip().lower() not in flagged_titles
        and not rx.search(papers[r["sample_id"]]["abstract"] + " " + r["research_question"])]
pick = sorted(random.Random(seed).sample(pool, n))
index_of = {line.split("\t")[1]: int(line.split("\t")[0]) for line in open("outputs/ai_selection/reviewed_titles.tsv").read().splitlines()[1:]}
cols = ["index_in_reviewed_titles", "sample_id", "discipline", "title", "status", "kind"]
with open(path, "a", newline="") as f:
    w = csv.writer(f)
    for sid in pick:
        w.writerow([index_of[sid], sid, sid.split("/")[0], papers[sid]["title"][:115], "selected_non_ai_random_sample", f"NON-AI control: seed {seed}, random draw of {n} from a pool of {len(pool)}"])
print(f"pool {len(pool)}, drew {n} with seed {seed}")
