"""Runs a command with Qwen3.8-27B on OpenRouter wired into ResearchBench's OpenAI-compatible client, thinking on.
The key (OPENROUTER_API_KEY) is read from the file named by $OPENROUTER_ENV_FILE (default ./.env), split on the first "=";
the file is never sourced or printed, and the key goes only into the child's environment.
Usage: qwen_env.py [--max-calls N] -- <command ...>      e.g.  qwen_env.py --max-calls 150 -- .venv/bin/researchbench run-rank ..."""
import os, sys
ENV_FILE = os.environ.get("OPENROUTER_ENV_FILE", ".env")
args = sys.argv[1:]
max_calls = "0"
if args[:1] == ["--max-calls"]:
    max_calls, args = args[1], args[2:]
assert args[:1] == ["--"] and len(args) > 1, __doc__
env = {}
for line in open(ENV_FILE).read().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        env[k.strip()] = v.split(" #")[0].strip().strip("'\"")
if not env.get("OPENROUTER_API_KEY"):
    sys.exit("STOP: OPENROUTER_API_KEY is not set in the project .env")
os.environ.update(OPENAI_API_KEY=env["OPENROUTER_API_KEY"], OPENAI_BASE_URL="https://openrouter.ai/api/v1",
                  RESEARCHBENCH_REASONING_EFFORT="high", RESEARCHBENCH_MAX_CALLS=max_calls)
print(f"[qwen_env] OPENROUTER_API_KEY found; model qwen/qwen3.8-27b, thinking high, call cap {max_calls or 'none'}", flush=True)
os.execvp(args[1], args[1:])
