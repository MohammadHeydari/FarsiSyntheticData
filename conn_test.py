from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("AvvalAI_API_KEY"), #you can change llm service provider
    base_url="https://api.avalai.ir/v1"
)

response = client.chat.completions.create(
    model="gapgpt-qwen-3.5", # choose your desired llm model
    messages=[
        {"role": "user", "content": "سلام رفیق، یه جمله به زبان شیرین پارسی برام بنویس."}
    ]
)

print(response.choices[0].message.content)