# treqai/ai/llama_client.py

from groq import Groq
from treqai.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

MODEL = "llama-3.3-70b-versatile"

async def ask_llama(prompt: str, max_tokens: int = 300, temp: float = 0.4) -> str:
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,     # 모델이 생성할 수 있는 최대 출력 길이
            temperature=temp,   # 0: 규칙 잘지킴, 반복적, 안정적 | 1: 창의적, 문장 다양
        )
        # message는 ChatCompletionMessage 객체!
        return response.choices[0].message.content

    except Exception as error:
        return f"(❌ LLaMA 요약 중 오류 발생: {error})"
