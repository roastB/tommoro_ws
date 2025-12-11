# llm/llama_client.py
import os
from groq import Groq
from treqai.core.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

MODEL = "llama-3.3-70b-versatile"   # ★ Slack 요약에 가장 추천되는 모델

async def ask_llama(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.4,
        )
        return response.choices[0].message.content

    except Exception as error:
        return f"(LLaMA 요약 중 오류 발생 : {error})"
