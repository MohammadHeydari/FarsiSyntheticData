import json
from pathlib import Path
from difflib import SequenceMatcher


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def deduplicate_file(filepath: Path, threshold: float = 0.75) -> tuple[int, int]:
    with open(filepath, "r", encoding="utf-8") as f:
        lines = [json.loads(l) for l in f if l.strip()]

    original_count = len(lines)
    kept = []

    for item in lines:
        instruction = item["instruction"]
        is_duplicate = False
        for existing in kept:
            if similarity(instruction, existing["instruction"]) > threshold:
                is_duplicate = True
                break
        if not is_duplicate:
            kept.append(item)

    with open(filepath, "w", encoding="utf-8") as f:
        for item in kept:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    return original_count, len(kept)


def run(output_dir: str = "output", threshold: float = 0.75):
    files = sorted(Path(output_dir).glob("*_dataset.jsonl"))
    if not files:
        print("No dataset files found.")
        return

    total_before = 0
    total_after = 0

    print(f"Deduplicating with similarity threshold: {threshold}")
    print(f"{'='*50}")

    for f in files:
        before, after = deduplicate_file(f, threshold)
        removed = before - after
        total_before += before
        total_after += after
        print(f"  {f.name}: {before} -> {after} ({removed} removed)")

    print(f"{'='*50}")
    print(f"Total: {total_before} -> {total_after} ({total_before - total_after} removed)")
    print(f"{'='*50}")


if __name__ == "__main__":
    run()