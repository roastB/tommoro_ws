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
    .stApp { background-color: #000000 !important; }
    [data-testid="stSidebar"] { background-color: #1E2130 !important; }
    
    /* 담당자 멀티셀렉트 태그 색상 (Apple Sky Blue) */
    span[data-baseweb="tag"] {
        background-color: #007AFF !important;
        color: white !important;
    }
    
    /* 상단 타이틀 레이아웃 */
    .title-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;
    }
    .operator-tag {
        background-color: rgba(90, 200, 250, 0.1);
        border: 1px solid #5AC8FA;
        color: #5AC8FA !important;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 16px;
        font-weight: 600;
    }

    /* 메인 폰트 스타일 */
    .huge-font {
        font-size: 140px !important; font-weight: bold; color: #FFFFFF;
        text-align: center; margin-top: -30px; margin-bottom: 0px; line-height: 1;
    }
    .goal-font { font-size: 45px !important; color: #FFFFFF; vertical-align: middle; }
    .count-font { font-size: 32px !important; color: #8E8E93; vertical-align: middle; margin-left: 15px; }
    
    .detail-container { margin-top: 30px; }
    h1, h2, h3, p, span { color: white !important; }
    
    .sidebar-time {
        padding: 12px; background-color: rgba(255, 255, 255, 0.08);
        border-radius: 8px; margin-bottom: 12px; font-size: 14px;
        border-left: 4px solid #007AFF;
    }
    </style>
    """, unsafe_allow_html=True)

# 담당자 정보를 사이드바에서 먼저 정의 (타이틀 표시를 위해)
with st.sidebar:
    st.header("⚙️ 대시보드 설정")
    # 1. 오늘의 목표 시간 기본값 0.0 설정
    target_hours = st.number_input("오늘의 목표 시간 (Hour)", min_value=0.0, value=0.0, step=0.1, format="%.1f")
    
    st.subheader("👥 수집 담당자")
    operators = st.multiselect(
        "담당자를 선택하세요",
        options=["황수범", "김재현", "김민기", "허재훈"],
        default=["황수범", "김재현", "김민기", "허재훈"]
    )
    operator_display = ", ".join(operators) if operators else "미지정"

# 2. 메인 타이틀 옆에 담당자 표시
col_t1, col_t2 = st.columns([0.7, 0.3])
with col_t1:
    st.title("🚀 Cell 4 실시간 수집 현황")
with col_t2:
    st.markdown(f'<div style="text-align: right; margin-top: 25px;"><span class="operator-tag">👥 담당: {operator_display}</span></div>', unsafe_allow_html=True)

with st.sidebar:
    st.divider()
    st.subheader("🕒 수집 시간 기록")
    last_time_place = st.empty()
    avg_duration_place = st.empty()
    first_time_place = st.empty()

st.divider()

DATA_PATH = os.path.expanduser("~/data_collection/habilis_dataset_manager/data/raw")
main_placeholder = st.empty()

def get_duration_from_yaml(file_path):
    try:
        with open(file_path, 'r') as f:
            for line in f:
                if 'nanoseconds:' in line:
                    return int(line.split(':')[-1].strip())
    except: pass
    return 0

def format_time_hm(t):
    return f"{t[:2]}:{t[2:4]}" if t and len(t) >= 4 else "--:--"

def format_duration_ms(seconds):
    if seconds <= 0: return "--:--"
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"

def format_full_duration(seconds):
    h, r = divmod(int(seconds), 3600)
    m, s = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

while True:
    try:
        today = datetime.now().strftime("%Y%m%d")
        all_folders = sorted([f for f in os.listdir(DATA_PATH) if f.startswith(today)]) if os.path.exists(DATA_PATH) else []
        folder_count = len(all_folders)
        
        start_time_str = all_folders[0].split('_')[1] if all_folders else None
        last_time_str = all_folders[-1].split('_')[1] if all_folders else None

        durations = [get_duration_from_yaml(os.path.join(DATA_PATH, f, "metadata.yaml")) for f in all_folders if os.path.exists(os.path.join(DATA_PATH, f, "metadata.yaml"))]
        total_seconds = sum(durations) / 1e9
        avg_duration_sec = (total_seconds / len(durations)) if durations else 0
        
        last_time_place.markdown(f'<div class="sidebar-time">🔥 최근 수집: {format_time_hm(last_time_str)}</div>', unsafe_allow_html=True)
        avg_duration_place.markdown(f'<div class="sidebar-time">📊 평균 수집: {format_duration_ms(avg_duration_sec)}</div>', unsafe_allow_html=True)
        first_time_place.markdown(f'<div class="sidebar-time">🛫 첫 수집: {format_time_hm(start_time_str)}</div>', unsafe_allow_html=True)

        duration_str = format_full_duration(total_seconds)
        target_seconds = target_hours * 3600
        progress_val = min(total_seconds / target_seconds, 1.0) if target_seconds > 0 else 0.0

        df_output = os.popen("df -h / | tail -1").read().split()
        avail_gb = df_output[3]
        used_percent = int(df_output[4].replace('%',''))

        with main_placeholder.container():
            st.markdown(f'<p class="huge-font">{duration_str} <span class="goal-font">/ {target_hours:.1f}h 목표</span> <span class="count-font">({folder_count} 개)</span></p>', unsafe_allow_html=True)
            
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge",
                value = total_seconds / 3600,
                domain = {'x': [0, 1], 'y': [0, 1]},
                gauge = {
                    'axis': {'range': [None, max(target_hours, 1)], 'tickwidth': 2, 'tickcolor': "white"},
                    'bar': {'color': "#5AC8FA", 'thickness': 1},
                    'bgcolor': "rgba(255,255,255,0.05)",
                    'threshold': {'line': {'color': "#FF3B30", 'width': 6}, 'thickness': 0.8, 'value': target_hours if target_hours > 0 else 0.001}
                }
            ))
            fig_gauge.update_layout(height=280, margin=dict(t=10, b=10, l=150, r=150), paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_gauge, use_container_width=True, key=f"gauge_{time.time()}")

            st.markdown('<div class="detail-container">', unsafe_allow_html=True)
            col_left, col_right = st.columns(2)
            loop_id = str(time.time())

            with col_left:
                st.subheader("💾 디스크 상태 (Storage)")
                fig_disk = go.Figure(go.Pie(
                    values=[used_percent, 100-used_percent], 
                    hole=.78, 
                    marker_colors=['#FF453A', '#2C2C2E'],
                    textinfo='none',
                    sort=False
                ))
                fig_disk.add_annotation(
                    text=f"<span style='font-size:38px; font-weight:bold; color:#FF453A;'>{used_percent}%</span><br><br><span style='font-size:16px; color:#E5E5EA;'>사용 중</span><br><br><span style='font-size:14px; color:#8E8E93;'>({avail_gb} 여유)</span>", 
                    x=0.5, y=0.5, showarrow=False
                )
                fig_disk.update_layout(showlegend=False, height=380, margin=dict(t=20, b=20, l=20, r=20), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_disk, use_container_width=True, key="disk_" + loop_id)

            with col_right:
                st.subheader("📈 시간 달성률")
                pct = int(progress_val * 100)
                fig_prog = go.Figure(go.Pie(values=[pct, 100-pct], hole=.78, marker_colors=['#30D158', '#1C1C1E'], textinfo='none', sort=False))
                fig_prog.add_annotation(
                    text=f"<span style='font-size:55px; font-weight:bold; color:#30D158;'>{pct}%</span><br><br><span style='font-size:18px; color:#E5E5EA;'>달성 완료</span>", 
                    x=0.5, y=0.5, showarrow=False
                )
                fig_prog.update_layout(showlegend=False, height=380, margin=dict(t=20, b=20, l=20, r=20), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_prog, use_container_width=True, key="prog_" + loop_id)
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:right; color:#8E8E93; font-size:12px; margin-top:20px;'>최종 동기화: {datetime.now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {e}")
        
    time.sleep(2.5)
