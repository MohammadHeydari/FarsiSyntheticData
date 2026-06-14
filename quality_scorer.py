import os
import json
import time
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("AVALAI_API_KEY"),
    base_url="https://api.avalai.ir/v1"
)

SCORER_SYSTEM = """You are a quality evaluator for Persian instruction-following datasets.
Given an instruction-response pair in Persian, score it on three criteria.
Return ONLY a JSON object, no explanation."""

SCORER_PROMPT = """Evaluate this Persian instruction-response pair:

INSTRUCTION: {instruction}

RESPONSE: {output}

Score each criterion from 1 to 5:
- fluency: Is the Persian natural and fluent? (1=broken, 5=native-level)
- relevance: Does the response actually answer the instruction? (1=irrelevant, 5=perfectly on-topic)
- quality: Is the response accurate, complete, and useful? (1=useless, 5=excellent)

Return ONLY this JSON:
{{"fluency": <1-5>, "relevance": <1-5>, "quality": <1-5>}}"""

CONFIG = {
    "model": "gpt-4.1-nano", #gpt-4.1-mini
    "min_score": 3.5,
    "delay": 0.3,
    "max_retries": 3,
    "output_dir": "output",
    "sample_mode": True,   # True = preview only, does NOT modify files
    "sample_size": 10,
}


def score_pair(instruction: str, output: str) -> dict | None:
    prompt = SCORER_PROMPT.format(instruction=instruction, output=output)

    for attempt in range(CONFIG["max_retries"]):
        try:
            response = client.chat.completions.create(
                model=CONFIG["model"],
                messages=[
                    {"role": "system", "content": SCORER_SYSTEM},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=100,
            )
            raw = response.choices[0].message.content.strip()
            raw = raw.replace("```json", "").replace("```", "").strip()
            scores = json.loads(raw)

            if all(k in scores for k in ["fluency", "relevance", "quality"]):
                avg = sum(scores.values()) / 3
                scores["avg"] = round(avg, 2)
                return scores

        except Exception as e:
            print(f"  [ERROR] {e} - attempt {attempt + 1}")
            time.sleep(2)

    return None


def process_file(filepath: Path) -> tuple[int, int]:
    with open(filepath, "r", encoding="utf-8") as f:
        items = [json.loads(l) for l in f if l.strip()]

    # sample mode: only preview scores, never modify the file
    if CONFIG["sample_mode"]:
        sample = items[:CONFIG["sample_size"]]
        for item in sample:
            scores = score_pair(item["instruction"], item["output"])
            if scores:
                print(f"    {scores['avg']:.1f} | {item['instruction'][:60]}")
            time.sleep(CONFIG["delay"])
        return len(sample), 0

    # full mode: score everything and remove low-quality pairs
    kept = []
    removed = 0

    for item in items:
        scores = score_pair(item["instruction"], item["output"])

        if scores is None:
            kept.append(item)
            continue

        item["scores"] = scores
        print(f"    {scores['avg']:.1f} | {item['instruction'][:60]}")

        if scores["avg"] >= CONFIG["min_score"]:
            kept.append(item)
        else:
            removed += 1

        time.sleep(CONFIG["delay"])

    # only write back in full mode
    with open(filepath, "w", encoding="utf-8") as f:
        for item in kept:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    return len(items), removed


def run():
    files = sorted(Path(CONFIG["output_dir"]).glob("*_dataset.jsonl"))
    if not files:
        print("No dataset files found.")
        return

    mode = "SAMPLE (preview only - files unchanged)" if CONFIG["sample_mode"] else "FULL (will modify files)"
    print(f"Quality scoring — {mode}")
    print(f"Min avg score: {CONFIG['min_score']}")
    print(f"{'='*50}")

    total_before = 0
    total_removed = 0

    for f in files:
        print(f"\n  Scoring: {f.name}")
        before, removed = process_file(f)
        total_before += before
        total_removed += removed
        if not CONFIG["sample_mode"]:
            print(f"  {before} -> {before - removed} ({removed} removed)")

    if not CONFIG["sample_mode"]:
        print(f"\n{'='*50}")
        print(f"Total: {total_before} -> {total_before - total_removed} ({total_removed} removed)")
        print(f"{'='*50}")


if __name__ == "__main__":
    run()