# 현재는 당장 사용하진 않지만... 기능이 늘어나면 사용해야함!

import requests
from treqai.core.config import settings


def send_to_req_channel(blocks: list, fallback_text: str = "New T-ReqAI request"):
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {settings.SLACK_BOT_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "channel": settings.REQ_TARGET_CHANNEL,
        "text": fallback_text,
        "blocks": blocks
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()
