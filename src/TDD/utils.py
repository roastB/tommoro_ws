# utils.py
import os
import json
import psycopg2
import pandas as pd  # 🧩 [추가] 차트 데이터를 다루기 위한 pandas 임포트
import streamlit as st

# 🧩 [추가] 공통으로 사용될 경로 및 설정 파일 정의
CONFIG_FILE = "dashboard_config.json"
DATA_PATH = os.path.expanduser("~/data_collection/habilis_dataset_manager/data/raw")

# 🧩 [이동] DB 연결 함수 분리
@st.cache_resource
def init_connection():
    return psycopg2.connect(
        host="localhost",
        database="tommoro_db",
        user="tommoro",
        password="tommoro4011"
    )

# 🧩 [이동] 쿼리 실행 함수 분리
def run_query(query):
    with init_connection().cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

# 🧩 [이동] 설정 로드 함수 분리
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {"target_hours": 4.0, "left_operators": [], "right_operators": [], "task_targets": {}}

# 🧩 [이동] 설정 저장 함수 분리
def save_config():
    new_conf = {
        "target_hours": st.session_state.test_target_input,
        "left_operators": st.session_state.test_left_input,
        "right_operators": st.session_state.test_right_input,
        "task_targets": st.session_state.get("task_targets", {})
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(new_conf, f, ensure_ascii=False)

# 🧩 [이동] 폴더 데이터 추출 함수 분리
def get_folder_data(folder_path):
    duration, task_name = 0, "Unknown"
    yaml_path = os.path.join(folder_path, "metadata.yaml")
    json_path = os.path.join(folder_path, "metacard.json")
    if os.path.exists(yaml_path) and os.path.exists(json_path):
        try:
            with open(yaml_path, "r") as f:
                for line in f:
                    if "nanoseconds:" in line:
                        duration = int(line.split(":")[-1].strip()) / 1e9
                        break
            with open(json_path, "r", encoding="utf-8") as f:
                task_name = json.load(f).get("task_name", "Unknown")
        except: pass
    return task_name, duration

# 🧩 [이동] 시간 포맷팅 함수 분리
def safe_extract_time(folder_name: str) -> str:
    try:
        parts = folder_name.split("_")
        if len(parts) >= 2 and len(parts[1]) >= 4:
            return f"{parts[1][:2]}:{parts[1][2:4]}"
    except: pass
    return "--:--"

# 🧩 [이동] 시간 포맷팅 함수 분리
def format_h_m(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    if h > 0:
        return f"{h}시간 {m}분"
    return f"{m}분"

# 🧩 [추가] 누락되었던 컨베이어 컨트롤러 생성 함수
def get_conveyor_controller():
    try:
        # 포트 설정 (필요에 따라 수정 가능)
        port_config = {'a': None} 
        # ConveyorController가 정의/임포트되어 있어야 동작합니다.
        controller = ConveyorController(port_config)
        return controller
    except Exception as e:
        # 연결 실패 시 None 반환 (대시보드가 멈추지 않도록)
        return None

# -------------------------------------------------------------------
# 📊 대시보드 중앙 차트용 데이터 로드 함수 (utils.py 하단)
# -------------------------------------------------------------------
@st.cache_data(ttl=60)
def get_dashboard_charts_data():
    """간트 차트 및 파이 차트용 데이터 로드"""
    
    # 🧩 [수정 3] "전체 기간"에 모든 프로젝트가 뜨도록 WHERE 필터 조건 해제
    gantt_query = """
        SELECT 
            project_name AS "Task",
            start_date AS "Start",
            end_date AS "Finish"
        FROM projects
        WHERE start_date IS NOT NULL AND end_date IS NOT NULL;
    """
    
    # 2. 프로젝트별 진행률 데이터 쿼리
    progress_query = """
        SELECT 
            p.project_name, 
            p.status,
            SUM(CAST(sl.duration AS NUMERIC)) / 3600.0 AS collected_hours
        FROM projects p
        JOIN tasks t ON p.project_id = t.project_id
        JOIN subtasks s ON t.task_id = s.task_id
        JOIN subtask_logs sl ON s.subtask_id = sl.subtask_id
        GROUP BY p.project_name, p.status
        HAVING SUM(CAST(sl.duration AS NUMERIC)) > 0;
    """
    
    # 3. Primitive Data 비율 쿼리
    primitive_query = """
        SELECT 
            CASE 
                WHEN p.project_name ILIKE '%Picking%' OR p.project_name ILIKE '%Play%' OR p.project_name ILIKE '%BI%' THEN 'Primitive Data'
                ELSE 'Task Data'
            END AS data_type,
            SUM(CAST(sl.duration AS NUMERIC)) / 3600.0 AS collected_hours
        FROM projects p
        JOIN tasks t ON p.project_id = t.project_id
        JOIN subtasks s ON t.task_id = s.task_id
        JOIN subtask_logs sl ON s.subtask_id = sl.subtask_id
        GROUP BY 1;
    """
    
    gantt_rows = run_query(gantt_query)
    progress_rows = run_query(progress_query)
    primitive_rows = run_query(primitive_query)
    
    df_gantt = pd.DataFrame(gantt_rows, columns=["Task", "Start", "Finish"])
    df_progress = pd.DataFrame(progress_rows, columns=["project_name", "status", "collected_hours"])
    df_primitive = pd.DataFrame(primitive_rows, columns=["data_type", "collected_hours"])
    
    # 파이썬 코드단에서 안전하게 타입 변환
    df_gantt['Start'] = pd.to_datetime(df_gantt['Start'], errors='coerce')
    df_gantt['Finish'] = pd.to_datetime(df_gantt['Finish'], errors='coerce')
    
    df_progress['collected_hours'] = pd.to_numeric(df_progress['collected_hours'], errors='coerce').fillna(0.0)
    df_primitive['collected_hours'] = pd.to_numeric(df_primitive['collected_hours'], errors='coerce').fillna(0.0)
    
    return df_gantt, df_progress, df_primitive