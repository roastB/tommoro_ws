# tomo_ai/treqai/api/slack_exp_router.py
from fastapi import APIRouter, Request
from treqai.ai.llama_client import ask_llama
from treqai.ai.exp_json_prompts import build_exp_json_prompt
from treqai.ai.exp_doc_prompts import build_exp_doc_prompt

router = APIRouter()

# =======================================================
#                Slash Command Entry Point
# =======================================================

@router.post("/t-exp")
async def t_exp_handler(request: Request):
    form = await request.form()
    exp_text = form.get("text")

    if not exp_text:
        return {
            "response_type": "ephemeral",
            "text": "😅 지출 내용을 자연어로 입력해주세요.\n예: RealSense 2개 구매 예정이며 내일 중으로 네이버스토어 결제되었으면 좋겠습니다."
        }
    
    try:
        # JSON 추출 (구조화는 최대한 안정적으로)
        json_prompt = build_exp_json_prompt(exp_text)
        exp_json = await ask_llama(json_prompt, max_tokens=350, temp=0.1) 

        # 결의서 문서 (조금 더 길게/유연하게)
        doc_prompt = build_exp_doc_prompt(exp_json)
        exp_doc = await ask_llama(doc_prompt, max_tokens=500, temp=0.3)

    except Exception as e:
        return {
            "response_type": "ephemeral",
            "text": f"❌ 지출결의서 문서 생성 중 오류 발생:\n{e}"
        }

    # -----------------------------------------
    # 3) Slack 출력 (문서 + JSON 참고)
    # -----------------------------------------
    return {
        "response_type": "ephemeral",
        "text": (
            "1️⃣ *지출결의서 초안*\n\n"
            f"```{exp_doc}```\n\n"
            "2️⃣ *추출된 구조화 데이터(JSON)*\n"
            f"```json\n{exp_json}\n```"
        )
    }
