from datetime import date
from treqai.core.exp_cal_date import get_next_business_day

def build_exp_json_prompt(exp_text: str) -> str:
    today = date.today()
    next_bd = get_next_business_day(today)

    today_str = today.isoformat()
    next_bd_str = next_bd.isoformat()

    return f"""
당신은 회사 지출결의서 작성을 위한 정보 추출 AI입니다.

아래 사용자 입력을 분석하여
지출결의서 작성을 위한 정보를 JSON 형식으로 추출하세요.

[핵심 규칙]
- 반드시 JSON만 출력하세요.
- 설명, 주석, 문장은 절대 포함하지 마세요.
- 추론할 수 없는 값은 null로 설정하세요.

[필드 규칙]
- original_text에는 아래 [사용자 입력]을 그대로 복사하세요.

[날짜 규칙]
- 오늘 날짜는 {today_str} 입니다.
- 사용자가 결제 희망일을 명시하지 않았다면, payment_date 필드는 반드시 "{next_bd_str}" 로 설정하세요.
- payment_date는 YYYY-MM-DD 형식으로 작성하세요. 
- 날짜를 알 수 없으면 null로 설정하세요.

[출력 JSON 스키마]
{{
  "original_text": string,
  "purpose": string,
  "items": [
    {{
      "name": string,
      "quantity": number
    }}
  ],
  "purchase_place": string,
  "payment_method": string,
  "payment_date": string
}}

[사용자 입력]
\"\"\"
{exp_text}
\"\"\"
"""
