"""Step 1: get every model's answer to every prompt. Resumable: done (prompt, model) pairs are skipped."""
import time
from concurrent.futures import ThreadPoolExecutor

from common import append_jsonl, chat, latest_by_key, load_config, load_prompts, read_jsonl


def main():
    cfg = load_config()
    prompts = load_prompts(cfg)
    out = cfg["run_dir"] / "responses.jsonl"
    done = latest_by_key(read_jsonl(out), lambda r: r.get("response") is not None)
    todo = [(p, m) for p in prompts.values() for m in cfg["models"] if (p["id"], m) not in done]
    print(f"{len(todo)} generations to run ({len(done)} already done)")

    def run(job):
        p, model = job
        # No system prompt: the eval measures the model's defaults.
        t0 = time.time()
        try:
            text, usage = chat(model, [{"role": "user", "content": p["prompt"]}], cfg["max_tokens"])
            row = {"prompt_id": p["id"], "model": model, "response": text, "usage": usage}
        except Exception as e:
            row = {"prompt_id": p["id"], "model": model, "response": None, "error": str(e)}
        row["latency_s"] = round(time.time() - t0, 1)
        row["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        append_jsonl(out, row)
        print(("ok  " if row["response"] is not None else "ERR ") + f"{p['id']} {model}")

    with ThreadPoolExecutor(cfg.get("concurrency", 8)) as pool:
        list(pool.map(run, todo))


if __name__ == "__main__":
    main()
