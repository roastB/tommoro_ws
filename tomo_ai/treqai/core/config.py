# API Key 관리
import os
from dotenv import load_dotenv

load_dotenv()

# API
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# API Key 체크
if GROQ_API_KEY is None:
    print("❌ Warning: GROQ_API_KEY not found. (Llama 기능은 비활성화될 수 있음)")
