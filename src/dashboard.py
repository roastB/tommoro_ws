import streamlit as st
import os
from datetime import datetime
import time
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(page_title="Cell4 Data Monitor", page_icon="📊", layout="wide")

# 2. CSS 설정
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #1E2130 !important; }
    header[data-testid="stHeader"] { background-color: #000000 !important; }
    [data-testid="stToolbar"] { background-color: #000000 !important; color: white !important; }
    
    h1, h2, h3, p, span, div, label { color: white !important; }
    span[data-baseweb="tag"] { background-color: #007AFF !important; color: white !important; }
    
    .operator-container {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 8px;
        margin-top: 15px;
    }
    .arm-tag {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid #5AC8FA;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 14px;
        font-weight: 500;
    }
    .arm-label { color: #5AC8FA !important; font-weight: bold; margin-right: 5px; }

    /* 메인 시간 폰트 - 상단 배너를 위해 마진 조정 */
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

    /* 축하 메시지 스타일 (상단용) */
    .congrats-banner-top {
        background: linear-gradient(90deg, rgba(48, 209, 88, 0.2), rgba(48, 209, 88, 0.8));
        padding: 10px;
        border-radius: 15px;
        text-align: center;
        font-weight: bold;
        font-size: 24px;
        margin: 10px auto 20px auto;
        width: 60%;
        border: 2px solid #30D158;
        box-shadow: 0 0 20px rgba(48, 209, 88, 0.4);
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 세션 상태 초기화
if 'celebrated' not in st.session_state:
    st.session_state.celebrated = False

# 3. 사이드바 설정
with st.sidebar:
    st.header("⚙️ 대시보드 설정")
    target_hours = st.number_input("오늘의 목표 시간 (Hour)", min_value=0.0, value=0.0, step=0.1, format="%.1f")
    
    st.subheader("👥 수집 담당자")
    operator_list = ["황수범", "정재현", "김민기", "허재훈"]
    
    left_operators = st.multiselect("왼팔(Left Arm) 담당", options=operator_list, default=[])
    right_operators = st.multiselect("오른팔(Right Arm) 담당", options=operator_list, default=[])
    
    left_display = ", ".join(left_operators) if left_operators else "미지정"
    right_display = ", ".join(right_operators) if right_operators else "미지정"
    
    st.divider()
    st.subheader("🕒 수집 시간 기록")
    sidebar_placeholder = st.empty()

# 4. 메인 타이틀 및 담당자 레이아웃
col_t1, col_t2 = st.columns([0.6, 0.4])
with col_t1:
    st.title("🚀 Cell 4 실시간 수집 현황")
with col_t2:
    st.markdown(f"""
        <div class="operator-container">
            <div class="arm-tag"><span class="arm-label">L-Arm:</span> {left_display}</div>
            <div class="arm-tag"><span class="arm-label">R-Arm:</span> {right_display}</div>
        </div>
    """, unsafe_allow_html=True)

st.divider()
main_placeholder = st.empty()

DATA_PATH = os.path.expanduser("~/data_collection/habilis_dataset_manager/data/raw")

def get_duration_from_yaml(file_path):
    try:
        with open(file_path, 'r') as f:
            for line in f:
                if 'nanoseconds:' in line:
                    return int(line.split(':')[-1].strip())
    except: pass
    return 0

# 메인 루프
while True:
    try:
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
        target_seconds = target_hours * 3600
        progress_val = min(total_seconds / target_seconds, 1.0) if target_seconds > 0 else 0.0

        # 사이드바 업데이트
        with sidebar_placeholder.container():
            st.markdown(f'<div class="sidebar-time">🔥 최근 수집: {last_time_str[:2]}:{last_time_str[2:4] if last_time_str else "--"}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="sidebar-time">📊 평균 수집: {int(avg_duration_sec//60):02d}:{int(avg_duration_sec%60):02d}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="sidebar-time">🛫 첫 수집: {start_time_str[:2]}:{start_time_str[2:4] if start_time_str else "--"}</div>', unsafe_allow_html=True)

        # 시스템 정보
        df_output = os.popen("df -h / | tail -1").read().split()
        avail_gb = df_output[3] if len(df_output) > 3 else "N/A"
        used_percent = int(df_output[4].replace('%','')) if len(df_output) > 4 else 0

        # 메인 영역
        with main_placeholder.container():
            # 1. 상단 축하 배너 (달성 시 최상단 노출)
            if progress_val >= 1.0 and target_hours > 0:
                st.markdown('<div class="congrats-banner-top">🎉 오늘 목표 달성! 모두 고생하셨습니다!</div>', unsafe_allow_html=True)
                if not st.session_state.celebrated:
                    st.balloons()
                    st.session_state.celebrated = True
            elif progress_val < 1.0:
                st.session_state.celebrated = False

            # 2. 메인 수집 시간
            st.markdown(f'<p class="huge-font">{duration_str} <span class="goal-font">/ {target_hours:.1f}h 목표</span> <span class="count-font">({folder_count} 개)</span></p>', unsafe_allow_html=True)
            
            # Gauge Chart
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge",
                value = total_seconds / 3600,
                gauge = {
                    'axis': {'range': [None, max(target_hours, 1)], 'tickcolor': "white"},
                    'bar': {'color': "#5AC8FA"},
                    'bgcolor': "rgba(255,255,255,0.05)",
                    'threshold': {'line': {'color': "#FF3B30", 'width': 5}, 'value': target_hours if target_hours > 0 else 0.001}
                }
            ))
            fig_gauge.update_layout(height=280, margin=dict(t=0, b=10, l=100, r=100), paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_gauge, width='stretch', key=f"gauge_{current_ts}")

            col_left, col_right = st.columns(2)
            with col_left:
                st.subheader("💾 디스크 상태 (Storage)")
                fig_disk = go.Figure(go.Pie(values=[used_percent, 100-used_percent], hole=.78, marker_colors=['#FF453A', '#2C2C2E'], textinfo='none', sort=False))
                fig_disk.add_annotation(text=f"<span style='color:#FF453A; font-size:35px; font-weight:bold;'>{used_percent}%</span><br><span style='font-size:12px; color:gray;'>{avail_gb} 여유</span>", showarrow=False)
                fig_disk.update_layout(showlegend=False, height=350, margin=dict(t=20, b=20), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_disk, width='stretch', key=f"disk_{current_ts}")

            with col_right:
                st.subheader("📈 시간 달성률")
                pct = int(progress_val * 100)
                fig_prog = go.Figure(go.Pie(values=[pct, 100-pct], hole=.78, marker_colors=['#30D158', '#1C1C1E'], textinfo='none', sort=False))
                fig_prog.add_annotation(text=f"<span style='color:#30D158; font-size:50px; font-weight:bold;'>{pct}%</span>", showarrow=False)
                fig_prog.update_layout(showlegend=False, height=350, margin=dict(t=20, b=20), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_prog, width='stretch', key=f"prog_{current_ts}")
            
            st.markdown(f"<p style='text-align:right; color:#8E8E93; font-size:12px; margin-top:20px;'>최종 동기화: {datetime.now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {e}")
    
    time.sleep(2.5)