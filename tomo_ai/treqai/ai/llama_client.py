# treqai/ai/llama_client.py

from groq import Groq
from treqai.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

MODEL = "llama-3.3-70b-versatile"

async def ask_llama(prompt: str) -> str:
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.4,
        )
        
        # message는 ChatCompletionMessage 객체!
        return response.choices[0].message.content

    except Exception as error:
        return f"(❌ LLaMA 요약 중 오류 발생: {error})"
