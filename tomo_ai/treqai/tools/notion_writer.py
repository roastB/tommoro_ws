#tomo_ai/treqai/tools/notion_writer.py

import httpx
from treqai.core.config import settings

NOTION_BASE_URL = "https://api.notion.com/v1/pages"

VALID_REQUEST_TYPES = [
    "Bug Report",
    "Data Request",
    "Console UI / Control",
    "Model / AI Request",
    "Habilis / Architecture",
    "Field Request / Deployment",
    "Enhancement / Feature Request",
    "# General Inquiry"
]

VALID_TEAMS = [
    "Architecture Team",
    "Data Division Team",
    "Habilis Console Team",
    "Edge-AI Team"
]

class NotionWriter:
    def __init__(self):
        if not settings.NOTION_API_KEY:
            raise ValueError("NOTION_API_KEY is not set.")
        if not settings.NOTION_REQUEST_DB_ID:
            raise ValueError("NOTION_REQUEST_DB_ID is not set.")

        self.headers = {
            "Authorization": f"Bearer {settings.NOTION_API_KEY}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        }
        self.db_id = settings.NOTION_REQUEST_DB_ID

    async def create_request_log(
        self,
        req_id: str,
        request_name: str,
        request_type: str,
        team: str,
        ai_summary: str,
    ):

        # select 옵션 보정
        request_type_fixed = (
            request_type if request_type in VALID_REQUEST_TYPES else "# General Inquiry"
        )
        team_fixed = team if team in VALID_TEAMS else "Architecture Team"

        payload = {
            "parent": {"database_id": self.db_id},
            "properties": {
                "Request Name": {
                    "title": [{"text": {"content": request_name}}]
                },
                "Request ID": {
                    "rich_text": [{"text": {"content": req_id}}]
                },
                "Request Type": {
                    "select": {"name": request_type_fixed}
                },
                "Requesting Team": {
                    "select": {"name": team_fixed}
                },
                "AI Summary": {
                    "rich_text": [{"text": {"content": ai_summary}}]
                },
            }
        }

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(NOTION_BASE_URL, json=payload, headers=self.headers)
            #print("🚨 Notion Response:", resp.status_code, resp.text)  # debug
            resp.raise_for_status()
            return resp.json()
