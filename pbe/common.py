"""Shared helpers: config, prompts, run files and the OpenRouter client."""
import argparse
import json
import os
import re
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def load_config():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "config.json"))
    cfg = json.loads(Path(ap.parse_args().config).read_text())
    cfg["run_dir"] = ROOT / "runs" / cfg["run_id"]
    cfg["run_dir"].mkdir(parents=True, exist_ok=True)
    return cfg


def read_jsonl(path):
    path = Path(path)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def append_jsonl(path, row):
    with open(path, "a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_prompts(cfg):
    """{id: prompt}, filtered by the optional `series` list and `ids` list in the config."""
    rows = read_jsonl(ROOT / cfg["prompts"])
    if cfg.get("series"):
        rows = [p for p in rows if p["series"] in cfg["series"]]
    if cfg.get("ids"):
        rows = [p for p in rows if p["id"] in cfg["ids"]]
    return {p["id"]: p for p in rows}


def latest_by_key(rows, ok):
    """Last row per (prompt_id, model) that passes `ok`; later rows win, so reruns replace."""
    return {(r["prompt_id"], r["model"]): r for r in rows if ok(r)}


def chat(model, messages, max_tokens=4000, json_mode=False):
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        sys.exit("OPENROUTER_API_KEY is not set")
    body = {"model": model, "messages": messages, "max_tokens": max_tokens}
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    r = httpx.post(OPENROUTER_URL, json=body, timeout=300,
                   headers={"Authorization": f"Bearer {key}", "X-Title": "Propaganda-Bait-Eval"})
    r.raise_for_status()
    data = r.json()
    if "choices" not in data:
        raise RuntimeError(f"no choices in response: {json.dumps(data)[:300]}")
    choice = data["choices"][0]
    usage = dict(data.get("usage", {}), finish_reason=choice.get("finish_reason"),
                 provider=data.get("provider"))
    return choice["message"].get("content") or "", usage


def parse_json(text):
    """Judge output as a dict; tolerates a ```json fence around it."""
    m = re.search(r"\{.*\}", text, re.S)
    return json.loads(m.group(0) if m else text)
