from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("AVALAI_API_KEY"),
    base_url="https://api.avalai.ir/v1"
)

response = client.chat.completions.create(
    model="qwen3.6-flash",
    messages=[
        {"role": "user", "content": "سلام! یه جمله فارسی بنویس."}
    ]
)

print(response.choices[0].message.content)