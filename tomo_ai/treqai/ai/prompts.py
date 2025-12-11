def build_summary_prompt(req_text: str) -> str:
    """
    Slack 요약용 Llama Prompt 생성
    """
    return f"""
당신은 회사 내부 요청을 정리하는 Assistant입니다.
아래 요청 내용을 읽고 Slack 메시지용으로 아주 깔끔하고 간단하게 요약해 주세요.

⚠️ 출력 규칙(중요):
- 모든 bullet 목록은 반드시 `-` 하이픈으로 시작해야 합니다. 절대로 `*`(asterisk) bullet을 사용하지 마세요.


요약 형식은 반드시 다음을 따르세요:

📌 요청 요약 

1) 핵심 요약
- 한 문장으로 요약

2) 상세 내용 요약
- bullet 2~4줄로 세부 내용 요약

3) 필요한 조치(있다면)
- 담당자 또는 팀이 해야 할 액션을 bullet로 작성
- 없다면 "특이사항 없음"이라고 작성
---

요청 내용:
\"\"\"{req_text}\"\"\"
"""
