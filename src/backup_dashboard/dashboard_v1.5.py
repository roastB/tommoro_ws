import streamlit as st
import os
import json
from datetime import datetime
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="[β] Data Collection Monitor", page_icon="🧪", layout="wide")

# --- 2. 설정 및 데이터 경로 ---
CONFIG_FILE = "test_dashboard_config.json"
DATA_PATH = os.path.expanduser("~/data_collection/habilis_dataset_manager/data/raw")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {"target_hours": 4.0, "left_operators": [], "right_operators": [], "task_targets": {}}

def save_config():
    new_conf = {
        "target_hours": st.session_state.test_target_input,
        "left_operators": st.session_state.test_left_input,
        "right_operators": st.session_state.test_right_input,
        "task_targets": st.session_state.get("task_targets", {})
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(new_conf, f, ensure_ascii=False)

# --- 세션 초기화 ---
if "test_init" not in st.session_state:
    saved = load_config()
    st.session_state.test_target_input = float(saved.get("target_hours", 4.0))
    st.session_state.test_left_input = saved.get("left_operators", [])
    st.session_state.test_right_input = saved.get("right_operators", [])
    st.session_state.task_targets = saved.get("task_targets", {})
    st.session_state.test_init = True
    st.session_state.processed_folders = set()
    st.session_state.task_stats = {} 
    st.session_state.task_counts = {} 
    st.session_state.task_times = {}  
    st.session_state.total_sec = 0.0

# --- 3. 데이터 추출 함수 ---
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

def safe_extract_time(folder_name: str) -> str:
    try:
        parts = folder_name.split("_")
        if len(parts) >= 2 and len(parts[1]) >= 4:
            return f"{parts[1][:2]}:{parts[1][2:4]}"
    except: pass
    return "--:--"

# --- 4. CSS 스타일 ---
st.markdown("""
<style>
    .stApp { background-color: #000000 !important; color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #1E2130 !important; }
    span[data-baseweb="tag"] { background-color: #007AFF !important; color: white !important; }
    [data-testid="stVerticalBlockBorderWrapper"] > div:has(div[data-testid="stVerticalBlock"]) {
        background-color: #161A25; border: 1px solid #2D3341; border-radius: 20px !important;
        padding: 20px !important; box-shadow: 0 8px 16px rgba(0,0,0,0.4);
    }
    .huge-font { font-size: 85px !important; font-weight: bold; text-align: center; line-height: 1.1; color: #FFFFFF; }
    .goal-font { font-size: 30px !important; color: #FFFFFF !important; opacity: 0.6; }
    .count-font { font-size: 20px !important; color: #8E8E93 !important; text-align: center; margin-bottom: 5px; }
    .focus-label { font-size: 13px; color: #5AC8FA; font-weight: bold; text-align: center; margin-bottom: 10px; opacity: 0.8; }
    
    .sidebar-time {
        padding: 10px; background-color: #F2F2F7; color: #000000 !important;
        border-radius: 8px; margin-bottom: 10px; font-size: 14px; font-weight: bold; border-left: 5px solid #007AFF;
    }
    .operator-row { display: flex; justify-content: flex-end; gap: 10px; margin-top: 10px; }
    .arm-tag {
        background-color: #FFFFFF !important; color: #000000 !important;
        padding: 6px 16px; border-radius: 14px; font-size: 13px; font-weight: bold; border: 1px solid rgba(0,0,0,0.1);
    }

    /* 우측 상세 카드 중앙 정렬 */
    .right-task-card {
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px; padding: 20px; text-align: center; margin-bottom: 15px;
    }
    .card-name { font-size: 14px; color: #8E8E93; margin-bottom: 8px; font-weight: 500; }
    .card-value-container { display: flex; justify-content: center; align-items: baseline; gap: 8px; margin-bottom: 8px; }
    .card-value { font-size: 32px; font-weight: bold; color: #FFFFFF; }
    .card-percent { font-size: 18px; color: #007AFF; font-weight: bold; }
    .card-badge {
        display: inline-block; background-color: rgba(50, 215, 75, 0.15);
        color: #32D74B; padding: 4px 12px; border-radius: 8px; font-size: 13px; font-weight: 600;
    }

    div[data-testid="stPopover"] > button {
        background-color: #007AFF !important; color: white !important; width: 100% !important; border-radius: 10px !important; font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 5. 사이드바 ---
with st.sidebar:
    st.header("🦾 Dashboard Setting")
    st.number_input("전체 목표 시간 (Overall Target)", min_value=0.0, step=0.1, key="test_target_input", on_change=save_config)
    ops_list = ["황수범", "정재현", "김민기", "허재훈"]
    st.multiselect("Left Arm Operator", options=ops_list, key="test_left_input", on_change=save_config)
    st.multiselect("Right Arm Operator", options=ops_list, key="test_right_input", on_change=save_config)
    
    st.divider()
    st.subheader("🎯 Task별 목표 설정")
    for task_name in list(st.session_state.task_stats.keys()):
        current_target = st.session_state.task_targets.get(task_name, 1.0)
        new_target = st.number_input(f"Target: {task_name}", min_value=0.1, value=float(current_target), step=0.5, key=f"target_{task_name}")
        if new_target != current_target:
            st.session_state.task_targets[task_name] = new_target
            save_config()

    st.divider()
    sidebar_placeholder = st.empty()
    
    with st.popover("📋 금일 수집 최종 요약"):
        if st.session_state.task_stats:
            total_h = st.session_state.total_sec / 3600
            st.info(f"**총 수집 시간:** {total_h:.2f}h / {st.session_state.test_target_input}h")
            st.divider()
            for task, sec in st.session_state.task_stats.items():
                t_h = sec / 3600
                st.write(f"📍 **{task}**: {t_h:.2f}h ({st.session_state.task_counts.get(task, 0)}개)")
        else: st.write("데이터가 없습니다.")

# --- 6. 데이터 로직 ---
try:
    today = datetime.now().strftime("%Y%m%d")
    all_folders = sorted([f for f in os.listdir(DATA_PATH) if f.startswith(today)]) if os.path.exists(DATA_PATH) else []
    unprocessed = [f for f in all_folders if f not in st.session_state.processed_folders]
    
    for f_name in unprocessed:
        task, sec = get_folder_data(os.path.join(DATA_PATH, f_name))
        if task != "Unknown":
            st.session_state.task_stats[task] = st.session_state.task_stats.get(task, 0) + sec
            st.session_state.task_counts[task] = st.session_state.task_counts.get(task, 0) + 1
            st.session_state.total_sec += sec
            st.session_state.processed_folders.add(f_name)

    processed_total_count = sum(st.session_state.task_counts.values())

    # 메인 헤더
    col_h1, col_h2 = st.columns([0.65, 0.35])
    with col_h1: st.title("🦾 Data Dashboard (v1.5)")
    with col_h2: 
        l_ops, r_ops = ", ".join(st.session_state.test_left_input) or "미지정", ", ".join(st.session_state.test_right_input) or "미지정"
        st.markdown(f'<div class="operator-row"><div class="arm-tag">L: {l_ops}</div><div class="arm-tag">R: {r_ops}</div></div>', unsafe_allow_html=True)

    # 사이드바 업데이트
    avg_sec = (st.session_state.total_sec / processed_total_count) if processed_total_count > 0 else 0.0
    start_t = safe_extract_time(all_folders[0]) if all_folders else "--:--"
    last_t = safe_extract_time(all_folders[-1]) if all_folders else "--:--"
    sidebar_placeholder.markdown(f'<div class="sidebar-time">🔥 Last Collect Time: {last_t}</div><div class="sidebar-time">📊 Avg Collect Time: {int(avg_sec//60):02d}:{int(avg_sec%60):02d}</div><div class="sidebar-time">🌞 First Collect Time: {start_t}</div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([0.7, 0.3], gap="medium")
    
    with col_left:
        task_options = ["전체 합계 (Overall)"] + sorted(list(st.session_state.task_stats.keys()))
        selected_focus = st.selectbox("Task Selector", options=task_options, index=0, label_visibility="collapsed")
        
        if selected_focus == "전체 합계 (Overall)":
            display_sec, display_count, display_target = st.session_state.total_sec, processed_total_count, st.session_state.test_target_input
        else:
            display_sec, display_count, display_target = st.session_state.task_stats.get(selected_focus, 0), st.session_state.task_counts.get(selected_focus, 0), st.session_state.task_targets.get(selected_focus, 1.0)

        with st.container(border=True):
            h_f, m_f, s_f = int(display_sec // 3600), int((display_sec % 3600) // 60), int(display_sec % 60)
            st.markdown(f'<p class="focus-label">MONITORING: {selected_focus.upper()}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="huge-font">{h_f:02d}:{m_f:02d}:{s_f:02d} <span class="goal-font">/ {display_target}h</span></p>', unsafe_allow_html=True)
            st.markdown(f'<p class="count-font">현재 {display_count}개 데이터 수집 완료</p>', unsafe_allow_html=True)
            
            # Gauge Chart: use_container_width=True -> width='stretch'
            fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=display_sec/3600, number={"font": {"color": "#FFFFFF", "size": 20}, "suffix": "h"},
                gauge={"axis": {"range": [0, max(display_target, 1)], "tickcolor": "white"}, "bar": {"color": "#5AC8FA"}, "bgcolor": "rgba(255,255,255,0.05)",
                "threshold": {"line": {"color": "white", "width": 4}, "value": display_target if display_target > 0 else 0.001}}))
            fig_gauge.update_layout(height=280, margin=dict(t=0, b=0, l=50, r=50), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_gauge, width='stretch', key="main_gauge")

        col_s1, col_s2 = st.columns(2)
        with col_s1:
             with st.container(border=True):
                st.subheader("💾 Disk Usage")
                df_out = os.popen("df -h / | tail -1").read().split()
                used_p = int(df_out[4].replace("%", "")) if len(df_out) > 4 else 0
                fig_disk = go.Figure(go.Pie(values=[used_p, 100-used_p], hole=0.75, marker_colors=["#FF3B30", "#1C1C1E"], textinfo="none"))
                fig_disk.add_annotation(text=f"{used_p}%", showarrow=False, font=dict(size=30, color="#FF3B30", weight="bold"))
                fig_disk.update_layout(height=180, margin=dict(t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
                st.plotly_chart(fig_disk, width='stretch', key="disk")
        with col_s2:
            with st.container(border=True):
                st.subheader("📈 Overall Achievement")
                overall_pct = int((st.session_state.total_sec / (st.session_state.test_target_input * 3600)) * 100) if st.session_state.test_target_input > 0 else 0
                fig_prog = go.Figure(go.Pie(values=[min(overall_pct, 100), max(0, 100-overall_pct)], hole=0.75, marker_colors=["#32D74B", "#1C1C1E"], textinfo="none"))
                fig_prog.add_annotation(text=f"{overall_pct}%", showarrow=False, font=dict(size=30, color="#32D74B", weight="bold"))
                fig_prog.update_layout(height=180, margin=dict(t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
                st.plotly_chart(fig_prog, width='stretch', key="overall")

    with col_right:
        with st.container(border=True):
            st.markdown("### 📊 Task Ratio")
            sorted_tasks = sorted(st.session_state.task_stats.items(), key=lambda x: x[1], reverse=True)
            if sorted_tasks:
                # Donut Chart: use_container_width=True -> width='stretch'
                fig_donut = go.Figure(go.Pie(labels=[t[0] for t in sorted_tasks], values=[t[1] for t in sorted_tasks], hole=0.55,
                    marker=dict(colors=["#FF2D55", "#32D74B", "#5AC8FA"]), textinfo="percent", sort=False))
                fig_donut.update_layout(height=300, margin=dict(t=20, b=20, l=10, r=10), showlegend=True, 
                                        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_donut, width='stretch', key="donut")
                
                st.divider()
                for name, sec in sorted_tasks:
                    count = st.session_state.task_counts.get(name, 0)
                    target_h = float(st.session_state.task_targets.get(name, 1.0))
                    pct = (sec / 3600) / target_h * 100
                    st.markdown(f"""
                        <div class="right-task-card">
                            <div class="card-name">📍 {name}</div>
                            <div class="card-value-container">
                                <span class="card-value">{sec/3600:.2f}h</span>
                                <span class="card-percent">{pct:.1f}%</span>
                            </div>
                            <div class="card-badge">↑ {int(sec//60)}m · {count}개</div>
                        </div>
                    """, unsafe_allow_html=True)

except Exception as e: st.error(f"Error: {e}")

st_autorefresh(interval=3000, key="refresh")