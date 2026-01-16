import streamlit as st
import os
import json
from datetime import datetime
import time
import plotly.graph_objects as go

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Cell4 Data Monitor", page_icon="📊", layout="wide")

# --- 2. 설정값 동기화 관리 함수 ---
CONFIG_FILE = "dashboard_config.json"

def load_config():
    """파일에서 설정 로드"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"target_hours": 0.0, "left_operators": [], "right_operators": []}

def save_config():
    """세션 상태의 값을 파일에 저장 (콜백 함수용)"""
    new_conf = {
        "target_hours": st.session_state.target_input,
        "left_operators": st.session_state.left_input,
        "right_operators": st.session_state.right_input
    }
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_conf, f, ensure_ascii=False)

# 초기 로드 및 세션 상태 동기화
if 'init' not in st.session_state:
    saved = load_config()
    st.session_state.target_input = float(saved.get("target_hours", 0.0))
    st.session_state.left_input = saved.get("left_operators", [])
    st.session_state.right_input = saved.get("right_operators", [])
    st.session_state.init = True

# --- 3. CSS 설정 ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #1E2130 !important; }
    header[data-testid="stHeader"] { background-color: #000000 !important; }
    [data-testid="stToolbar"] { background-color: #000000 !important; color: white !important; }
    
    h1, h2, h3, p, span, div, label { color: white !important; }
    span[data-baseweb="tag"] { background-color: #007AFF !important; color: white !important; }
    
    .operator-container {
        display: flex; flex-direction: column; align-items: flex-end;
        gap: 8px; margin-top: 15px;
    }
    .arm-tag {
        background-color: rgba(255, 255, 255, 0.05); border: 1px solid #5AC8FA;
        padding: 4px 12px; border-radius: 15px; font-size: 14px; font-weight: 500;
    }
    .arm-label { color: #5AC8FA !important; font-weight: bold; margin-right: 5px; }

    .huge-font {
        font-size: 140px !important; font-weight: bold; color: #FFFFFF !important;
        text-align: center; margin-top: 0px; margin-bottom: 0px; line-height: 1;
    }
    .goal-font { font-size: 45px !important; color: #FFFFFF !important; vertical-align: middle; }
    .count-font { font-size: 32px !important; color: #8E8E93 !important; vertical-align: middle; margin-left: 15px; }
    
    .sidebar-time {
        padding: 12px; background-color: #F2F2F7; color: #000000 !important; 
        border-radius: 8px; margin-bottom: 12px; font-size: 15px; font-weight: bold;
        border-left: 5px solid #007AFF;
    }
    .sidebar-time * { color: #000000 !important; }

    .congrats-banner-top {
        background: linear-gradient(90deg, rgba(48, 209, 88, 0.2), rgba(48, 209, 88, 0.8));
        padding: 10px; border-radius: 15px; text-align: center; font-weight: bold;
        font-size: 24px; margin: 10px auto 20px auto; width: 60%;
        border: 2px solid #30D158; box-shadow: 0 0 20px rgba(48, 209, 88, 0.4);
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 세션 상태 초기화 (축하용)
if 'celebrated' not in st.session_state:
    st.session_state.celebrated = False

# --- 4. 사이드바 설정 ---
with st.sidebar:
    st.header("⚙️ 대시보드 설정")
    
    # on_change를 사용하여 입력 즉시 파일에 저장
    st.number_input("오늘의 목표 시간 (Hour)", 
                    min_value=0.0, step=0.1, format="%.1f",
                    key="target_input", on_change=save_config)
    
    operator_list = ["황수범", "정재현", "김민기", "허재훈"]
    st.multiselect("왼팔(Left Arm) 담당", options=operator_list, 
                   key="left_input", on_change=save_config)
    st.multiselect("오른팔(Right Arm) 담당", options=operator_list, 
                   key="right_input", on_change=save_config)
    
    st.info("수정 시 모든 PC에 실시간 반영됩니다.")
    
    st.divider()
    st.subheader("🕒 수집 시간 기록")
    sidebar_placeholder = st.empty()

# --- 5. 데이터 처리 함수 ---
DATA_PATH = os.path.expanduser("~/data_collection/habilis_dataset_manager/data/raw")

def get_duration_from_yaml(file_path):
    try:
        with open(file_path, 'r') as f:
            for line in f:
                if 'nanoseconds:' in line:
                    return int(line.split(':')[-1].strip())
    except: pass
    return 0

# --- 6. 메인 레이아웃 및 루프 ---
main_placeholder = st.empty()

while True:
    try:
        # 파일에서 최신 설정 다시 읽기 (다른 PC가 변경했을 수도 있음)
        current_conf = load_config()
        t_hours = float(current_conf.get("target_hours", 0.0))
        l_display = ", ".join(current_conf.get("left_operators", [])) or "미지정"
        r_display = ", ".join(current_conf.get("right_operators", [])) or "미지정"

        current_ts = int(time.time())
        today = datetime.now().strftime("%Y%m%d")
        all_folders = sorted([f for f in os.listdir(DATA_PATH) if f.startswith(today)]) if os.path.exists(DATA_PATH) else []
        folder_count = len(all_folders)
        
        start_time_str = all_folders[0].split('_')[1] if all_folders else None
        last_time_str = all_folders[-1].split('_')[1] if all_folders else None

        durations = [get_duration_from_yaml(os.path.join(DATA_PATH, f, "metadata.yaml")) for f in all_folders if os.path.exists(os.path.join(DATA_PATH, f, "metadata.yaml"))]
        total_seconds = sum(durations) / 1e9
        avg_duration_sec = (total_seconds / len(durations)) if durations else 0
        
        duration_str = f"{int(total_seconds//3600):02d}:{int((total_seconds%3600)//60):02d}:{int(total_seconds%60):02d}"
        target_seconds = t_hours * 3600
        progress_val = min(total_seconds / target_seconds, 1.0) if target_seconds > 0 else 0.0

        with sidebar_placeholder.container():
            st.markdown(f'<div class="sidebar-time">🔥 최근 수집: {last_time_str[:2] if last_time_str else "--"}:{last_time_str[2:4] if last_time_str else "--"}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="sidebar-time">📊 평균 수집: {int(avg_duration_sec//60):02d}:{int(avg_duration_sec%60):02d}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="sidebar-time">🛫 첫 수집: {start_time_str[:2] if start_time_str else "--"}:{start_time_str[2:4] if start_time_str else "--"}</div>', unsafe_allow_html=True)

        df_output = os.popen("df -h / | tail -1").read().split()
        avail_gb = df_output[3] if len(df_output) > 3 else "N/A"
        used_percent = int(df_output[4].replace('%','')) if len(df_output) > 4 else 0

        with main_placeholder.container():
            col_t1, col_t2 = st.columns([0.6, 0.4])
            with col_t1:
                st.title("🚀 Cell 4 실시간 수집 현황")
            with col_t2:
                st.markdown(f"""
                    <div class="operator-container">
                        <div class="arm-tag"><span class="arm-label">L-Arm:</span> {l_display}</div>
                        <div class="arm-tag"><span class="arm-label">R-Arm:</span> {r_display}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.divider()

            if progress_val >= 1.0 and t_hours > 0:
                st.markdown('<div class="congrats-banner-top">🎉 오늘 목표 달성! 모두 고생하셨습니다!</div>', unsafe_allow_html=True)
                if not st.session_state.celebrated:
                    st.balloons()
                    st.session_state.celebrated = True
            else:
                st.session_state.celebrated = False

            # 메인 시간 표시 (t_hours 적용)
            st.markdown(f'<p class="huge-font">{duration_str} <span class="goal-font">/ {t_hours:.1f}h 목표</span> <span class="count-font">({folder_count} 개)</span></p>', unsafe_allow_html=True)
            
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge",
                value = total_seconds / 3600,
                gauge = {
                    'axis': {'range': [None, max(t_hours, 1)], 'tickcolor': "white"},
                    'bar': {'color': "#5AC8FA"},
                    'bgcolor': "rgba(255,255,255,0.05)",
                    'threshold': {'line': {'color': "#FF3B30", 'width': 5}, 'value': t_hours if t_hours > 0 else 0.001}
                }
            ))
            fig_gauge.update_layout(height=280, margin=dict(t=0, b=10, l=100, r=100), paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_gauge, width='stretch', key=f"gauge_{current_ts}")

            col_left, col_right = st.columns(2)
            with col_left:
                st.subheader("💾 디스크 상태")
                fig_disk = go.Figure(go.Pie(values=[used_percent, 100-used_percent], hole=.78, marker_colors=['#FF453A', '#2C2C2E'], textinfo='none', sort=False))
                fig_disk.add_annotation(text=f"<span style='color:#FF453A; font-size:35px; font-weight:bold;'>{used_percent}%</span><br><span style='font-size:12px; color:gray;'>{avail_gb} 여유</span>", showarrow=False)
                fig_disk.update_layout(showlegend=False, height=300, margin=dict(t=20, b=20), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_disk, width='stretch', key=f"disk_{current_ts}")

            with col_right:
                st.subheader("📈 시간 달성률")
                pct = int(progress_val * 100)
                fig_prog = go.Figure(go.Pie(values=[pct, 100-pct], hole=.78, marker_colors=['#30D158', '#1C1C1E'], textinfo='none', sort=False))
                fig_prog.add_annotation(text=f"<span style='color:#30D158; font-size:50px; font-weight:bold;'>{pct}%</span>", showarrow=False)
                fig_prog.update_layout(showlegend=False, height=300, margin=dict(t=20, b=20), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_prog, width='stretch', key=f"prog_{current_ts}")
            
            st.markdown(f"<p style='text-align:right; color:#8E8E93; font-size:12px; margin-top:20px;'>최종 동기화: {datetime.now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {e}")
    
    time.sleep(3.0)
