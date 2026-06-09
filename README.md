# Farsi Synthetic Data

Generating high-quality Farsi instruction-following synthetic datasets using LLMs.

## Overview

This project provides a pipeline for generating diverse, realistic Farsi instruction-response pairs across a wide range of topics. The output is structured as JSONL files suitable for fine-tuning language models.

Each generated sample follows the standard instruction-tuning format:

```json
{
  "instruction": "چطور می‌تونم برای کنکور ریاضی آماده بشم؟",
  "input": "",
  "output": "برای آمادگی کنکور ریاضی...",
  "topic": "آموزش و تحصیل",
  "subtopic": "کنکور و آزمون"
}
```

## Project Structure

```
.
├── topic_tree.json       # Topic hierarchy (10 domains, 150 subtopics)
├── prompts.py            # Prompt templates for the LLM
├── generator.py          # Main data generation pipeline
├── output/               # Generated JSONL datasets (one file per domain)
└── requirements.txt
```

## Setup

**1. Clone the repository**

```bash
git clone https://github.com/MohammadHeydari/FarsiSyntheticData
cd PersianSyntheticData
```

**2. Create a virtual environment and install dependencies**

```bash
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

**3. Configure your API key**

Copy the sample env file and add your API key:

```bash
cp .env.sample .env
```

```env
GAPGPT_API_KEY=your_api_key_here
```

This project uses the [GapGPT API](https://gapgpt.app/platform-v2/docs/quickstart), which is compatible with the OpenAI SDK.

## Usage

**Full run — all domains:**

```bash
python generator.py
```

**Test run — 2 domains only:**

```python
# In generator.py
run(max_domains=2)
```

**Specific domains:**

```python
run(domains=["فناوری و دیجیتال", "سلامت و پزشکی"])
```

## Configuration

All settings are in the `CONFIG` dictionary inside `generator.py`:

| Parameter | Default | Description |
|---|---|---|
| `model` | `gapgpt-qwen-3.5` | LLM model to use |
| `pairs_per_call` | `3` | Pairs generated per API call |
| `calls_per_subtopic` | `2` | API calls per subtopic |
| `delay_between_calls` | `0.3` | Seconds between calls |
| `max_tokens` | `1500` | Max tokens per response |

## Output

Each domain gets its own JSONL file under `output/`:

```
output/
├── آموزش و تحصیل_dataset.jsonl
├── سلامت و پزشکی_dataset.jsonl
├── فناوری و دیجیتال_dataset.jsonl
└── ...
```

With default settings the pipeline generates approximately **900 instruction-response pairs** across **10 domain files** in roughly **90 minutes**.

## Topic Coverage

10 domains, 150 subtopics, including:

- Education & Learning
- Health & Medicine
- Technology & Digital
- Business & Entrepreneurship
- Daily Life
- Travel & Tourism
- Art & Culture
- Sports
- Science & Nature
- Society & Philosophy