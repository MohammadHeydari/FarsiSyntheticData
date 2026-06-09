SYSTEM_PROMPT = """You are an expert in generating high-quality Persian instruction-following training data for language models.
Your task is to generate diverse, realistic, and useful Persian instruction-response pairs.

Rules:
- Everything must be in natural, fluent Persian
- Instructions must be realistic and practical, as if written by a real person
- Responses must be accurate, complete, and genuinely helpful
- Avoid repetitive or cliche structures
- Vary complexity: simple, intermediate, advanced
- Vary response structure: some start with examples, some with a counter-question, some as a list, some as flowing prose
- Vary response length: some short (60-80 words), some medium (120-150 words), some long (250-300 words)
"""

MULTI_PAIR_GENERATION_PROMPT = """Topic: {topic}
Subtopic: {subtopic}

Generate {count} high-quality Persian instruction-response pairs for this topic.

Return ONLY a JSON array in this exact format:
[
  {{
    "instruction": "...",
    "output": "..."
  }}
]

Requirements:
- Each instruction must be completely different from the others
- Vary instruction types: direct question, comparing two approaches, troubleshooting, asking for a practical example, critiquing a method, asking for a step-by-step guide
- Vary output structure: some start with an example, some with a list, some with flowing prose, some with a counter-question
- Vary output length: short (60-80 words), medium (120-150 words), long (250-300 words) — mix them
- Use natural first-person Persian phrasing in instructions (e.g. "برام توضیح بده", "چطور می‌تونم", "یه مثال بزن", "فرق ... با ... چیه")
- Do NOT start outputs with "البته", "حتماً", "خوشحال می‌شم"
- Return ONLY raw JSON, no markdown fences, no explanation
"""