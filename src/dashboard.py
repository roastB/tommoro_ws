import streamlit as st
import os
from datetime import datetime, timedelta
import time
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(page_title="Cell4 Data Monitor", page_icon="📊", layout="wide")

# 2. CSS 설정
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    [data-testid="stSidebar"] { background-color: #1E2130 !important; }
    header[data-testid="stHeader"] { background-color: rgba(0, 0, 0, 0) !important; }
    [data-testid="stToolbar"] { background-color: #000000 !important; }

    .huge-font {
        font-size: 200px !important; font-weight: bold; color: #FFFFFF;
        text-align: center; margin-top: -100px; margin-bottom: -10px; line-height: 1;
    }
    .goal-font { font-size: 50px !important; color: #FFFFFF; vertical-align: middle; }
    
    .stProgress > div > div > div > div { background-color: #3B82F6 !important; }
    
    .detail-container { margin-top: 60px; }

    /* 수집 시간 상세: 왼쪽 정렬로 수정 */
    .time-box-orange {
        background-color: #FF9500; color: #000000 !important; padding: 18px 25px;
        border-radius: 12px; margin-bottom: 15px; font-weight: bold; 
        text-align: left; font-size: 22px;
    }
    .time-box-green {
        background-color: #34C759; color: #000000 !important; padding: 18px 25px;
        border-radius: 12px; margin-bottom: 15px; font-weight: bold; 
        text-align: left; font-size: 22px;
    }
    .time-box-skyblue {
        background-color: #5AC8FA; color: #000000 !important; padding: 18px 25px;
        border-radius: 12px; margin-bottom: 15px; font-weight: bold; 
        text-align: left; font-size: 22px;
    }
    
    h1, h2, h3, p, span { color: white !important; }
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 { color: white !important; }

    .status-line {
        display: flex; justify-content: center; align-items: center; gap: 80px;
        margin-top: 20px; color: #FFFFFF !important;
    }
    .status-label { font-size: 24px; font-weight: normal; margin-right: 15px; }
    .status-value { font-size: 42px; font-weight: bold; }
    
    .calc-info {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 10px;
        font-size: 14px;
        color: #AAAAAA !important;
        margin-top: 20px;
        border-left: 4px solid #00BFFF;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Cell 4 실시간 수집 현황")

with st.sidebar:
    st.header("⚙️ 대시보드 설정")
    target_goal = st.number_input("오늘의 수집 목표", min_value=1, value=300, step=10)
    st.divider()
    st.info("목표값을 변경하면 실시간으로 반영됩니다.")

st.divider()

DATA_PATH = os.path.expanduser("~/data_collection/habilis_dataset_manager/data/raw")
main_placeholder = st.empty()

def get_duration_from_yaml(file_path):
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if 'duration:' in line:
                    for next_line in lines[i+1:i+3]:
                        if 'nanoseconds:' in next_line:
                            return int(next_line.split(':')[-1].strip())
    except:
        pass
    return 0

while True:
    try:
        today = datetime.now().strftime("%Y%m%d")
        all_folders = sorted([f for f in os.listdir(DATA_PATH) if f.startswith(today)])
        count = len(all_folders)
        
        total_duration_ns = 0
        start_time_str, last_time_str = None, None
        estimated_finish_time = "--:--:--"
        
        if all_folders:
            start_time_str = all_folders[0].split('_')[1]
            last_time_str = all_folders[-1].split('_')[1]
            
            try:
                t_now = datetime.now()
                fmt = "%H%M%S"
                folder_times = [datetime.strptime(f.split('_')[1], fmt).replace(year=t_now.year, month=t_now.month, day=t_now.day) for f in all_folders]
                
                net_working_sec = 0
                for i in range(len(folder_times)-1):
                    diff = (folder_times[i+1] - folder_times[i]).total_seconds()
                    if diff < 300:
                        net_working_sec += diff
                
                last_diff = (t_now - folder_times[-1]).total_seconds()
                if last_diff < 300:
                    net_working_sec += last_diff

                if count > 1 and count < target_goal:
                    avg_sec_per_item = net_working_sec / count
                    remaining_items = target_goal - count
                    pure_remaining_sec = avg_sec_per_item * remaining_items
                    
                    t_finish = t_now + timedelta(seconds=pure_remaining_sec)
                    
                    lunch_start = t_now.replace(hour=12, minute=0, second=0)
                    lunch_end = t_now.replace(hour=13, minute=0, second=0)
                    if t_now < lunch_end and t_finish > lunch_start:
                        t_finish += timedelta(hours=1)
                    
                    break_sec = (pure_remaining_sec / 3600) * 600
                    t_finish += timedelta(seconds=break_sec)
                    
                    estimated_finish_time = t_finish.strftime("%H:%M:%S")
                elif count >= target_goal:
                    estimated_finish_time = "목표 달성 완료"
            except:
                pass

            for folder in all_folders:
                yaml_path = os.path.join(DATA_PATH, folder, "metadata.yaml")
                if os.path.exists(yaml_path):
                    total_duration_ns += get_duration_from_yaml(yaml_path)

        total_seconds = total_duration_ns / 1e9
        hours, remainder = divmod(int(total_seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        def format_t(t):
            return f"{t[:2]}:{t[2:4]}:{t[4:]}" if t and len(t) >= 6 else "--:--:--"

        df_output = os.popen("df -h / | tail -1").read().split()
        avail_gb = df_output[3]
        used_percent = int(df_output[4].replace('%',''))
        free_percent = 100 - used_percent

        with main_placeholder.container():
            st.markdown(f'<p class="huge-font">{count} <span class="goal-font">/ {target_goal} 목표</span></p>', unsafe_allow_html=True)
            
            progress_val = min(count / target_goal, 1.0)
            st.progress(progress_val)
            
            st.markdown(f"""
                <div class="status-line">
                    <div><span class="status-label">총 누적 수집 시간</span><span class="status-value">{duration_str}</span></div>
                    <div><span class="status-label">현재 달성률</span><span class="status-value">{int(progress_val*100)}%</span></div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="detail-container">', unsafe_allow_html=True)
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.subheader("💾 시스템 상태 (Disk Usage)")
                fig = go.Figure(go.Pie(
                    values=[used_percent, free_percent], labels=['Used', 'Free'], hole=.85,
                    marker_colors=['#FF5554', '#1A1A1A'], textinfo='none'
                ))
                fig.add_annotation(
                    text=f"<span style='font-size:38px; font-weight:bold; color:#FF5554;'>{free_percent}%</span><br><br><span style='font-size:18px; color:#AAAAAA;'>({avail_gb})</span>",
                    x=0.5, y=0.5, showarrow=False
                )
                # 차트 크기를 약 20% 축소 (height를 380에서 300으로 조정)
                fig.update_layout(showlegend=False, height=300, margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True, key=f"disk_{int(time.time())}")

            with col_right:
                st.subheader("🕒 수집 시간 상세")
                st.write("")
                # 텍스트가 왼쪽 정렬된 박스들
                st.markdown(f'<div class="time-box-orange">🔥 실시간 최근 수집 시간 : {format_t(last_time_str)}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="time-box-skyblue">⏳ 예상 목표 달성 시각 : {estimated_finish_time}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="time-box-green">✔️ 금일 첫 수집 시작 시간 : {format_t(start_time_str)}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown(f"""
                <div class="calc-info">
                    <strong>💡 예상 시각 계산 방식:</strong><br>
                    1. 5분 이상의 수집 공백(점심/휴식)을 제외한 <strong>순수 수집 속도</strong>를 계산합니다.<br>
                    2. (순수 평균 속도 × 남은 개수) + 점심시간(1h) + 정기 휴게시간(시간당 10분)을 더하여 최종 시각을 예측합니다.
                </div>
                <p style='text-align:right; color:#555555 !important; font-size:13px; margin-top:20px;'>
                    Updated by <strong>roastB</strong> ☕ | 최종 동기화: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </p>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.warning(f"데이터 처리 중 알림: {e}")
        
    time.sleep(2.5)