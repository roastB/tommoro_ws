# tomo_ai/treqai/api/slack_router.py

from fastapi import APIRouter, Request
from datetime import datetime
from treqai.ai.llama_client import ask_llama
from treqai.ai.req_prompts import build_summary_prompt
from treqai.core.tommoro_team import USER_TEAM_MAP
from treqai.core.req_type_detector import detect_request_type
from treqai.core.req_counter import get_next_request_id
from treqai.api.slack_sender import send_to_req_channel
from treqai.tools.notion_writer import NotionWriter

router = APIRouter()


# =======================================================
#                Slash Command Entry Point
# =======================================================

@router.post("/t-req")
async def t_req_handler(request: Request):
    form = await request.form()

    # Data Load
    req_id = get_next_request_id()
    req_text = form.get("text")
    req_type = detect_request_type(req_text)
    req_time = datetime.now().strftime("%Y-%m-%d %H:%M") 
    user_id = form.get("user_id")
    user_team = USER_TEAM_MAP.get(user_id, "-")
    channel_id = form.get("channel_id")
    
    if not req_text:
        return {
            "response_type": "ephemeral",
            "text": "😅 `/t-req 요청내용` 형식으로 입력해주세요!"
        }

    print("User:", user_id, "| Channel:", channel_id)
    print("Req_text:", req_text)

    try:
        llama_prompt = build_summary_prompt(req_text)
        ai_summary = await ask_llama(llama_prompt, max_tokens=400, temp=0.4)
    except Exception as error:
        ai_summary = f"( ❌ LLM 요약 중 오류 발생: {error} )"
    
    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": "📌 Request Received", "emoji": True}},
        {"type": "divider"},
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Request ID*\n: {req_id}"},
                {"type": "mrkdwn", "text": f"*Requester & Team*\n: <@{user_id}> & {user_team}"},
                {"type": "mrkdwn", "text": f"*Request Type*\n: {req_type}"},
                {"type": "mrkdwn", "text": f"*Request Time*\n: {req_time}"},
            ]
        },
        {"type": "divider"},
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*Original Request Content*\n```{req_text}```"}},
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*Summary (Llama-3.3)*\n```{ai_summary}```"}},
        {
            "type": "context",
            "elements": [{"type": "mrkdwn", "text": "🧬 T-ReqAI automatically processed this request."}]
        }
    ]

    send_to_req_channel(
        blocks=blocks,
        fallback_text=f"T-ReqAI 요청이 접수되었습니다!: {req_text}"
    )

    try:
        notion = NotionWriter()
        await notion.create_request_log(
            req_id=req_id,
            request_name=req_text,
            request_type=req_type,
            team=user_team,
            ai_summary=ai_summary,
        )
    except Exception as e:
        print(f"[Notion 기록 실패] {e}")

    return {
        "response_type": "ephemeral",
        "text": "📨 요청이 `#t-req-hub` 으로 자동 전송되었습니다!"
    }
