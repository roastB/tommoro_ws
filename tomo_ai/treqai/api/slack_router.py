from fastapi import APIRouter, Request
from datetime import datetime
from treqai.ai.llama_client import ask_llama #✨
from treqai.ai.prompts import build_summary_prompt
from treqai.core.tommoro_team import USER_TEAM_MAP, detect_request_type
from treqai.core.req_counter import get_next_request_id
from treqai.api.slack_sender import send_to_req_channel

router = APIRouter()

@router.post("/t-req")
async def t_req_handler(request: Request):
    form = await request.form()

    req_id = get_next_request_id()
    req_text = form.get("text")
    now_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    user_id = form.get("user_id")
    user_team = USER_TEAM_MAP.get(user_id, "unassigned_team")
    req_type = detect_request_type(req_text)
    channel_id = form.get("channel_id")
    
    if not req_text:
        return {
            "response_type": "ephemeral",
            "text": (
                "😅 요청 내용을 찾을 수 없습니다. "
                "/t-req 뒤에 `요청 내용`을 입력해주세요!\n\n"
                "예시: /t-req `Habilis-beta 데이터 수집 진행상황 요청드립니다.`"
            )
        }

    # ----------------------------
    # 0) Server Command Check
    # ----------------------------
    print("User:", user_id, "| Channel:", channel_id)
    print("Req_text:", req_text)

    # ----------------------------
    # 1) LLM 요약 생성
    # ---------------------------- 
    try:
        summary_prompt = build_summary_prompt(req_text)
        return_summary = await ask_llama(summary_prompt) #✨


    except Exception as error:
        return_summary = f"( ❌ LLM 요약 중 오류 발생: {error} )"
    
    # ----------------------------
    # 2) Slack Block Kit 메시지 구성
    # ----------------------------
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📌 Request Received",
                "emoji": True
            }
        },
        { "type": "divider" },
        {
            "type": "section",
            "fields": [
                { "type": "mrkdwn", "text": f"*Request ID*\n: {req_id}" },
                { "type": "mrkdwn", "text": f"*Requester & Team*\n: <@{user_id}> & {user_team}" },
                { "type": "mrkdwn", "text": f"*Request Type*\n: {req_type}" },
                { "type": "mrkdwn", "text": f"*Request Time*\n: {now_date}" },
            ]
        },
        { "type": "divider" },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Original Request Content*\n```{req_text}```"
            }
        },
        # LLM 요약
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Summary (Llama-3.3)*\n```{return_summary}```"}
        }, 
        {
            "type": "context",
            "elements": [
                { "type": "mrkdwn", "text": "🧬 [MVP version] T-ReqAI automatically processed this request." }
            ]
        }
    ]

    # ----------------------------
    # 3) -> t-req-hub으로 전송!
    # ----------------------------
    send_to_req_channel(
        blocks=blocks,
        fallback_text=f"T-ReqAI 요청이 접수되었습니다!: {req_text}"
    )

    # ----------------------------
    # 4) Slash command 응답 (사용자에게만 보임)
    # ----------------------------
    return {
        "response_type": "ephemeral",
        "text": "📨 요청이 `#tommoro-req-hub`으로 자동 전송되었습니다! 담당자가 확인 후 직접 찾아갈게요!"
    }

    # [테스트용]
    # return {
    #     "response_type": "in_channel",  # 채널 전체에 보이게
    #     "blocks": blocks,
    #     # fallback 텍스트 (모바일/옛 클라이언트용)
    #     "text": f"T-ReqAI 요청이 접수되었습니다: {req_text}"
    # }