import streamlit as st
import os
import json
from datetime import datetime
import time
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="[β 1.3] Data Collection Monitor", page_icon="🧪", layout="wide")

# --- 2. 설정 및 데이터 경로 ---
CONFIG_FILE = "test_dashboard_config.json"
DATA_PATH = os.path.expanduser("~/data_collection/habilis_dataset_manager/data/raw")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {"target_hours": 4.0, "left_operators": [], "right_operators": []}

def save_config():
    new_conf = {
        "target_hours": st.session_state.test_target_input,
        "left_operators": st.session_state.test_left_input,
        "right_operators": st.session_state.test_right_input,
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(new_conf, f, ensure_ascii=False)

# --- 세션 초기화 (데이터 캐싱으로 깜빡임 및 중복 방지) ---
if "test_init" not in st.session_state:
    saved = load_config()
    st.session_state.test_target_input = float(saved.get("target_hours", 4.0))
    st.session_state.test_left_input = saved.get("left_operators", [])
    st.session_state.test_right_input = saved.get("right_operators", [])
    st.session_state.test_init = True
    st.session_state.processed_folders = set()
    st.session_state.task_stats = {}
    st.session_state.total_sec = 0.0
    st.session_state.celebrated = False

# --- 3. 데이터 추출 함수 ---
def get_folder_data(folder_path):
    duration, task_name = 0, "Unknown"
    yaml_path = os.path.join(folder_path, "metadata.yaml")
    if os.path.exists(yaml_path):
        try:
            with open(yaml_path, "r") as f:
                for line in f:
                    if "nanoseconds:" in line:
                        duration = int(line.split(":")[-1].strip()) / 1e9
                        break
        except: pass
    json_path = os.path.join(folder_path, "metacard.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                task_name = json.load(f).get("task_name", "Unknown")
        except: pass
    return task_name, duration

def safe_extract_time(folder_name: str) -> str:
    try:
        parts = folder_name.split("_")
        if len(parts) >= 2 and len(parts[1]) >= 4:
            return f"{parts[1][:2]}:{parts[1][2:4]}"
    except: pass
    return "--:--"

# --- 4. CSS (담당자 색상 및 카드 디자인) ---
st.markdown("""
<style>
    .stApp { background-color: #000000 !important; color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #1E2130 !important; }
    
    /* 사이드바 담당자 태그: 파란색 계열 복구 */
    span[data-baseweb="tag"] { background-color: #007AFF !important; color: white !important; }
    
    /* 카드 디자인: 차트를 감싸는 라운드 박스 */
    [data-testid="stVerticalBlockBorderWrapper"] > div:has(div[data-testid="stVerticalBlock"]) {
        background-color: #161A25;
        border: 1px solid #2D3341;
        border-radius: 20px !important;
        padding: 20px !important;
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
    }
    
    .huge-font { font-size: 85px !important; font-weight: bold; text-align: center; line-height: 1; color: #FFFFFF; }
    .goal-font { font-size: 30px !important; color: #FFFFFF !important; opacity: 0.6; }
    .count-font { font-size: 20px !important; color: #8E8E93 !important; text-align: center; }
    
    .sidebar-time {
        padding: 10px; background-color: #F2F2F7; color: #000000 !important;
        border-radius: 8px; margin-bottom: 10px; font-size: 14px; font-weight: bold;
        border-left: 5px solid #007AFF;
    }
    
    .operator-row { display: flex; justify-content: flex-end; gap: 10px; margin-top: 10px; }
    
    /* 메인 화면 우측 상단 담당자: 흰색 바탕에 검정색 텍스트 */
    .arm-tag {
        background-color: #FFFFFF !important; 
        color: #000000 !important;
        padding: 6px 16px; 
        border-radius: 14px; 
        font-size: 13px; 
        font-weight: bold;
        border: 1px solid rgba(0,0,0,0.1);
        white-space: nowrap;
    }
    .arm-label { color: #000000 !important; margin-right: 5px; opacity: 0.6; }
</style>
""", unsafe_allow_html=True)

# --- 5. 사이드바 ---
with st.sidebar:
    st.header("🧪 테스트 설정")
    st.number_input("Target Hours", min_value=0.0, step=0.1, format="%.1f", key="test_target_input", on_change=save_config)
    ops_list = ["황수범", "정재현", "김민기", "허재훈"]
    st.multiselect("Left Arm Operator", options=ops_list, key="test_left_input", on_change=save_config)
    st.multiselect("Right Arm Operator", options=ops_list, key="test_right_input", on_change=save_config)
    st.divider()
    sidebar_placeholder = st.empty()

# --- 6. 데이터 로직 및 렌더링 ---
try:
    today = datetime.now().strftime("%Y%m%d")
    all_folders = sorted([f for f in os.listdir(DATA_PATH) if f.startswith(today)]) if os.path.exists(DATA_PATH) else []
    
    # 신규 데이터 캐싱 및 Unknown 필터링
    new_folders = [f for f in all_folders if f not in st.session_state.processed_folders]
    for f_name in new_folders:
        task, sec = get_folder_data(os.path.join(DATA_PATH, f_name))
        if task != "Unknown":
            st.session_state.task_stats[task] = st.session_state.task_stats.get(task, 0) + sec
            st.session_state.total_sec += sec
        st.session_state.processed_folders.add(f_name)

    conf = load_config()
    t_hours = float(conf.get("target_hours", 0.0))
    l_ops, r_ops = ", ".join(conf.get("left_operators", [])) or "미지정", ", ".join(conf.get("right_operators", [])) or "미지정"
    total_hours = st.session_state.total_sec / 3600.0
    progress_pct = int((st.session_state.total_sec / (t_hours * 3600)) * 100) if t_hours > 0 else 0

    # 사이드바 텍스트 업데이트 (깜빡임 방지)
    avg_sec = (st.session_state.total_sec / len(all_folders)) if all_folders else 0.0
    start_t = safe_extract_time(all_folders[0]) if all_folders else "--:--"
    last_t = safe_extract_time(all_folders[-1]) if all_folders else "--:--"
    sidebar_html = f"""
        <div class="sidebar-time">🔥 Last Collection: {last_t}</div>
        <div class="sidebar-time">📊 Average Time: {int(avg_sec//60):02d}:{int(avg_sec%60):02d}</div>
        <div class="sidebar-time">🌞 First Collection: {start_t}</div>
    """
    sidebar_placeholder.markdown(sidebar_html, unsafe_allow_html=True)

    # 상단 헤더 (담당자 흰색 태그 적용)
    col_h1, col_h2 = st.columns([0.65, 0.35])
    with col_h1: st.title("🧪 Data Collection Status (v1.3)")
    with col_h2: 
        st.markdown(f'<div class="operator-row"><div class="arm-tag"><span class="arm-label">L-Arm:</span>{l_ops}</div><div class="arm-tag"><span class="arm-label">R-Arm:</span>{r_ops}</div></div>', unsafe_allow_html=True)

    if progress_pct >= 100 and t_hours > 0 and not st.session_state.celebrated:
        st.balloons(); st.session_state.celebrated = True

    # --- 메인 그리드 레이아웃 (좌 7 : 우 3) ---
    col_left, col_right = st.columns([0.7, 0.3], gap="medium")

    with col_left:
        # 섹션 1: 실시간 수집 현황 (라운드 카드 박스)
        with st.container(border=True):
            duration_str = f"{int(st.session_state.total_sec//3600):02d}:{int((st.session_state.total_sec%3600)//60):02d}:{int(st.session_state.total_sec%60):02d}"
            st.markdown(f'<p class="huge-font">{duration_str} <span class="goal-font">/ {t_hours}h</span></p>', unsafe_allow_html=True)
            st.markdown(f'<p class="count-font">현재 {len(all_folders)}개 데이터 수집 완료</p>', unsafe_allow_html=True)
            
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number", value=total_hours,
                number={"font": {"color": "#FFFFFF", "size": 20}, "suffix": "h"},
                gauge={
                    "axis": {"range": [0, max(t_hours, 1)], "tickcolor": "white"},
                    "bar": {"color": "#5AC8FA"},
                    "bgcolor": "rgba(255,255,255,0.05)",
                    "threshold": {"line": {"color": "white", "width": 4}, "value": t_hours if t_hours > 0 else 0.001}
                }
            ))
            fig_gauge.update_layout(height=260, margin=dict(t=0, b=10, l=50, r=50), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_gauge, width='stretch', key="gauge")

        # 섹션 2: 하단 보조 지표 (디스크 & 달성률)
        col_s1, col_s2 = st.columns(2, gap="medium")
        with col_s1:
            with st.container(border=True):
                st.subheader("💾 Disk Usage")
                df_out = os.popen("df -h / | tail -1").read().split()
                used_p = int(df_out[4].replace("%", "")) if len(df_out) > 4 else 0
                fig_disk = go.Figure(go.Pie(values=[used_p, 100-used_p], hole=0.75, marker_colors=["#FF3B30", "#1C1C1E"], textinfo="none"))
                fig_disk.add_annotation(text=f"{used_p}%", showarrow=False, font=dict(size=30, color="#FF3B30", weight="bold")) 
                fig_disk.update_layout(height=200, margin=dict(t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
                st.plotly_chart(fig_disk, width='stretch', key="disk")
        with col_s2:
            with st.container(border=True):
                st.subheader("📈 Overall Achievement")
                prog_val = min(progress_pct, 100)
                fig_prog = go.Figure(go.Pie(values=[prog_val, 100-prog_val], hole=0.75, marker_colors=["#32D74B", "#1C1C1E"], textinfo="none"))
                fig_prog.add_annotation(text=f"{progress_pct}%", showarrow=False, font=dict(size=30, color="#32D74B", weight="bold")) 
                fig_prog.update_layout(height=200, margin=dict(t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
                st.plotly_chart(fig_prog, width='stretch', key="prog")

    with col_right:
        # 섹션 3: Task Breakdown (라운드 카드 박스)
        with st.container(border=True):
            st.markdown("### 📊 Task Breakdown")
            sorted_tasks = sorted(st.session_state.task_stats.items(), key=lambda x: x[1], reverse=True)
            if sorted_tasks:
                # 데이터가 많은 순서대로 빨강 > 녹색 > 하늘색 할당
                rank_colors = ["#FF2D55", "#32D74B", "#5AC8FA", "#AF52DE", "#FF9500"]
                fig_donut = go.Figure(go.Pie(
                    labels=[t[0] for t in sorted_tasks], values=[t[1] for t in sorted_tasks], hole=0.55,
                    marker=dict(colors=rank_colors), textinfo="percent",
                    textfont=dict(size=15, color="white", family="Arial Black"), # 흰색 Bold %
                    sort=False
                ))
                fig_donut.update_layout(height=300, margin=dict(t=20, b=20, l=0, r=0), showlegend=True, 
                                        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
                                        paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_donut, width='stretch', key="donut")
                
                st.divider()
                # 시간이 많은 순서대로 메트릭 정렬 출력
                for name, sec in sorted_tasks:
                    st.metric(label=f"📍 {name}", value=f"{sec/3600:.2f} h", delta=f"{int(sec//60)} min")
            else: st.info("데이터 수집 중...")

except Exception as e: st.error(f"Error: {e}")

# --- 7. 자동 새로고침 ---
st_autorefresh(interval=3000, key="refresh")