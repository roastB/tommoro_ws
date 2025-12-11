import os
import requests

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
REQ_TARGET_CHANNEL = os.getenv("REQ_TARGET_CHANNEL", "t-req-hub")

def send_to_req_channel(blocks: list, fallback_text: str = "New T-ReqAI request"):
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "channel": REQ_TARGET_CHANNEL,
        "text": fallback_text,
        "blocks": blocks
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()
