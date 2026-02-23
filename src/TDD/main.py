# main.py
import streamlit as st
import signal
from streamlit_autorefresh import st_autorefresh
# 🧩 [추가] 분리된 모듈 임포트
from utils import load_config, save_config, get_conveyor_controller
from tab1_daily import render_daily_monitor
from tab2_total import render_total_statistics
from conveyor import ConveyorController

# --- 0. 컨베이어 스레드 및 시그널 에러 방지 패치 ---
def dummy_handler(signum, frame):
    pass

try:
    signal.signal(signal.SIGINT, dummy_handler)
except ValueError:
    signal.signal = lambda s, h: None

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="TDD", page_icon="🪬", layout="wide")

# --- 4. CSS 스타일 (기존 스타일 유지) ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117 !important; color: #FFFFFF !important; }
    header[data-testid="stHeader"] { background-color: rgba(0,0,0,0) !important; }
    sidebar[data-testid="stSidebar"] { background-color: #1E2130 !important; }
    span[data-baseweb="tag"] { background-color: #007AFF !important; color: white !important; }
    /* 위젯 박스 디자인 */
    [data-testid="stVerticalBlockBorderWrapper"] > div:has(div[data-testid="stVerticalBlock"]) {
        background-color: #161A25; border: 1px solid #2D3341; border-radius: 20px !important;
        padding: 20px !important; box-shadow: 0 8px 16px rgba(0,0,0,0.4);
    }
    .huge-font { font-size: 85px !important; font-weight: bold; text-align: center; line-height: 1.1; color: #FFFFFF; }
    .goal-font { font-size: 30px !important; color: #FFFFFF !important; opacity: 0.6; }
    .count-font { font-size: 20px !important; color: #8E8E93 !important; text-align: center; margin-bottom: 5px; }
    .focus-label { font-size: 13px; color: #5AC8FA; font-weight: bold; text-align: center; margin-bottom: 10px; opacity: 0.8; }
    .sidebar-time { padding: 10px; background-color: #F2F2F7; color: #000000 !important; border-radius: 8px; margin-bottom: 10px; font-size: 14px; font-weight: bold; border-left: 5px solid #007AFF; }
    .operator-row { display: flex; justify-content: flex-end; gap: 10px; margin-top: 10px; }
    .arm-tag { background-color: #FFFFFF !important; color: #000000 !important; padding: 6px 16px; border-radius: 14px; font-size: 13px; font-weight: bold; border: 1px solid rgba(0,0,0,0.1); }
    .right-task-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 20px; text-align: center; margin-bottom: 15px; }
    .card-name { font-size: 14px; color: #8E8E93; margin-bottom: 8px; font-weight: 500; }
    .card-value-container { display: flex; justify-content: center; align-items: baseline; gap: 8px; margin-bottom: 8px; }
    .card-value { font-size: 32px; font-weight: bold; color: #FFFFFF; }
    .card-percent { font-size: 18px; color: #007AFF; font-weight: bold; }
    .card-badge { display: inline-block; background-color: rgba(50, 215, 75, 0.15); color: #32D74B; padding: 4px 12px; border-radius: 8px; font-size: 13px; font-weight: 600; }
    .curation-card { background-color: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 10px; border-left: 5px solid #32D74B; line-height: 1.6; }
    .text-good { color: #32D74B; font-weight: bold; }
    .text-bad { color: #FF3B30; font-weight: bold; }
    .text-highlight { font-weight: bold; color: #FFFFFF; }
</style>
""", unsafe_allow_html=True)

# --- 5. 사이드바 및 세션 초기화 ---
if "test_init" not in st.session_state:
    saved = load_config()
    st.session_state.test_target_input = float(saved.get("target_hours", 0.0))
    st.session_state.test_left_input = saved.get("left_operators", [])
    st.session_state.test_right_input = saved.get("right_operators", [])
    st.session_state.task_targets = saved.get("task_targets", {})
    st.session_state.test_init = True
    st.session_state.task_stats = {} 
    st.session_state.task_counts = {} 
    st.session_state.task_durations = {} 
    st.session_state.total_sec = 0.0 
    st.session_state.conveyor_speed_val = 30 

with st.sidebar:
    st.header("🦾 Dashboard Setting")

    st.subheader("🗃️ 금일 수집 요약")
    summary_placeholder = st.empty()
    st.divider()
    
    st.subheader("🎯 전체 목표 시간 설정")
    current_overall = st.session_state.get("test_target_input", 0.0)
    default_h = int(current_overall)
    default_m = int(round((current_overall - default_h) * 60))

    col_h, col_m = st.columns(2)
    with col_h:
        target_h = st.number_input("시간", min_value=0, max_value=24, value=default_h, step=1, key="input_hour")
    with col_m:
        target_m = st.number_input("분", min_value=0, max_value=59, value=default_m, step=1, key="input_min")

    new_overall_target = target_h + (target_m / 60.0)
    if new_overall_target != current_overall:
        st.session_state.test_target_input = new_overall_target
        save_config()

    st.caption(f"현재 설정: {target_h}시간 {target_m}분")
    ops_list = ["황수범", "정재현", "허재훈"]
    st.multiselect("Left Arm Operator", options=ops_list, key="test_left_input", on_change=save_config)
    st.multiselect("Right Arm Operator", options=ops_list, key="test_right_input", on_change=save_config)
    
    st.divider()
    sidebar_info_area = st.container()

    st.divider()
    st.subheader("⚙️ Conveyor Control")
    conveyor_area = st.empty()
    ctrl = get_conveyor_controller() # 🧩 [수정] utils 또는 main에서 정의된 함수 사용
    with conveyor_area.container(): 
        if ctrl and len(ctrl.conveyor) > 0:
            active_belt = list(ctrl.conveyor.keys())[0]
            speed_input = st.number_input("Speed (Hz)", 1, 196, st.session_state.conveyor_speed_val, key="side_speed_input")
            if speed_input != st.session_state.conveyor_speed_val:
                st.session_state.conveyor_speed_val = speed_input
                ctrl.command(active_belt, speed=speed_input)
            if st.button("◀️ BWD", width='stretch', key="btn_bwd_side"):
                ctrl.command(active_belt, direction='backward', speed=st.session_state.conveyor_speed_val)
            if st.button("⏹ STOP", type="primary", width='stretch', key="btn_stop_side"):
                ctrl.command(active_belt, direction='stop')
            st.caption(f"Connected: {ctrl.conveyor[active_belt].ser.port}")
        else:
            st.error("⚠️ 컨베이어 연결 없음")

# 메인 어플리케이션 실행 루프
def main():
    # 탭 생성: 상단 브라우저 형태의 UI
    tab_daily, tab_total = st.tabs(["🌞 Daily Monitoring (Local)", "🏛️ Total Statistics (PostgreSQL)"])

    with tab_daily:
        # Tab 1: 금일 실시간 모니터링 함수 호출 (인자 전달)
        render_daily_monitor(sidebar_info_area, summary_placeholder) # 🧩 [수정] 사이드바 컨테이너 전달
        
        # 탭 1이 활성화된 상태에서만 3초마다 화면 자동 갱신
        st_autorefresh(interval=3000, key="daily_view_autorefresh")

    with tab_total:
        # Tab 2: PostgreSQL 통합 통계 함수 호출
        render_total_statistics()
        
        # 참고: Tab 2는 DB 부하를 위해 자동 갱신을 넣지 않거나, 필요시 아주 긴 주기로 설정하는 것을 추천합니다.

if __name__ == "__main__":
    # 프로젝트 실행
    main()