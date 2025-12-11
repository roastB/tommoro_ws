import os
from datetime import datetime

# 현재 파일(req_counter.py)의 절대 경로
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# storage/req_counter.txt의 절대 경로
COUNTER_FILE = os.path.join(BASE_DIR, "storage", "req_counter.txt")


def get_next_request_id() -> str:
    current_month = datetime.now().strftime("%Y-%m")

    # 파일 없으면 기본 세팅
    if not os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "w") as f:
            f.write(f"{current_month}\n0")

    # 파일 읽기
    with open(COUNTER_FILE, "r") as f:
        saved_month = f.readline().strip()
        saved_count = int(f.readline().strip())

    # 월이 바뀌었는지 확인 → 새달이면 카운트 리셋
    if saved_month != current_month:
        next_count = 1
        saved_month = current_month
    else:
        next_count = saved_count + 1

    # 값 저장
    with open(COUNTER_FILE, "w") as f:
        f.write(f"{saved_month}\n{next_count}")

    return f"REQ_{next_count:04d}"
