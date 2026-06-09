import os
import json
import time
import random
import re
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from tqdm import tqdm

from prompts import SYSTEM_PROMPT, MULTI_PAIR_GENERATION_PROMPT

# -------------------------------------------------------
# Config
# -------------------------------------------------------
load_dotenv()

client = OpenAI(
    api_key=os.getenv("AvvalAI_API_KEY"),
    base_url="https://api.avalai.ir/v1"
)

CONFIG = {
    "model": "gapgpt-qwen-3.5",
    "pairs_per_call": 3,
    "calls_per_subtopic": 2,
    "delay_between_calls": 0.3,
    "output_dir": "output",
    "max_retries": 3,
    "max_tokens": 1500,
}

# Load topic tree
def load_topic_tree(path: str = "topic_tree.json") -> list:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["domains"]


# Try to extract JSON array from raw string
def extract_json(raw: str) -> list:
    # Remove markdown fences
    raw = raw.replace("```json", "").replace("```", "").strip()

    # Try direct parse first
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Try to find JSON array with regex
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return []


# Generate pairs via API
def generate_pairs(topic: str, subtopic: str, count: int) -> list[dict]:
    prompt = MULTI_PAIR_GENERATION_PROMPT.format(
        topic=topic,
        subtopic=subtopic,
        count=count
    )

    for attempt in range(CONFIG["max_retries"]):
        try:
            response = client.chat.completions.create(
                model=CONFIG["model"],
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=CONFIG["max_tokens"],
            )

            raw = response.choices[0].message.content.strip()
            pairs = extract_json(raw)

            if not pairs:
                print(f"  [WARNING] Could not parse JSON - attempt {attempt + 1}/{CONFIG['max_retries']}")
                time.sleep(1)
                continue

            valid = []
            for p in pairs:
                if "instruction" in p and "output" in p:
                    if len(p["instruction"].strip()) > 10 and len(p["output"].strip()) > 50:
                        valid.append({
                            "instruction": p["instruction"].strip(),
                            "input": "",
                            "output": p["output"].strip(),
                            "topic": topic,
                            "subtopic": subtopic
                        })
            return valid

        except Exception as e:
            print(f"  [ERROR] {e} - attempt {attempt + 1}/{CONFIG['max_retries']}")
            time.sleep(2)

    return []



# Save batch to per-topic JSONL file
def save_to_jsonl(pairs: list[dict], topic: str):
    output_dir = Path(CONFIG["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = output_dir / f"{topic}_dataset.jsonl"
    with open(filename, "a", encoding="utf-8") as f:
        for pair in pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")


# Print stats
def print_stats():
    output_dir = Path(CONFIG["output_dir"])
    if not output_dir.exists():
        print("Output directory not found.")
        return

    files = sorted(output_dir.glob("*_dataset.jsonl"))
    if not files:
        print("No dataset files found.")
        return

    total = 0
    print(f"\n{'='*50}")
    for f in files:
        with open(f, "r", encoding="utf-8") as fh:
            count = sum(1 for _ in fh)
        total += count
        print(f"  {f.name}: {count} pairs")

    print(f"{'='*50}")
    print(f"Total: {total} pairs across {len(files)} files")
    print(f"{'='*50}\n")


# Main pipeline
def run(domains: list = None, max_domains: int = None):
    all_domains = load_topic_tree()

    if domains:
        all_domains = [d for d in all_domains if d["name"] in domains]
    if max_domains:
        all_domains = all_domains[:max_domains]

    total_subtopics = sum(len(d["subtopics"]) for d in all_domains)
    total_calls = total_subtopics * CONFIG["calls_per_subtopic"]
    expected = total_calls * CONFIG["pairs_per_call"]

    print(f"Starting Persian synthetic data generation")
    print(f"Domains: {len(all_domains)} | Subtopics: {total_subtopics} | API calls: {total_calls}")
    print(f"Expected output: ~{expected} pairs")
    print(f"{'='*50}\n")

    for domain in all_domains:
        topic = domain["name"]
        subtopics = domain["subtopics"]
        random.shuffle(subtopics)

        print(f"\n[Domain] {topic} ({len(subtopics)} subtopics)")

        for subtopic in tqdm(subtopics, desc=f"  {topic}"):
            for _ in range(CONFIG["calls_per_subtopic"]):
                pairs = generate_pairs(
                    topic=topic,
                    subtopic=subtopic,
                    count=CONFIG["pairs_per_call"]
                )

                if pairs:
                    save_to_jsonl(pairs, topic)

                time.sleep(CONFIG["delay_between_calls"])

    print_stats()
    print(f"Files saved in: {CONFIG['output_dir']}/")


# Entry point
if __name__ == "__main__":

    # Full run - all domains
    run()

    # Test mode - 2 domains only
    # run(max_domains=2)

    # Specific domains
    # run(domains=["فناوری و دیجیتال", "سلامت و پزشکی"])