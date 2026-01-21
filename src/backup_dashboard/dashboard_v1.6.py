import streamlit as st
import os
import json
import signal
from datetime import datetime
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 0. 컨베이어 스레드 및 시그널 에러 방지 패치 ---
# 시스템 종료 시그널(SIGINT)이 발생했을 때 Streamlit 내부 스레드와 충돌하는 것을 방지하는 핸들러입니다.
def dummy_handler(signum, frame):
    pass

try:
    # 프로그램 종료 신호를 받았을 때 에러 없이 무시하도록 설정합니다.
    signal.signal(signal.SIGINT, dummy_handler)
except ValueError:
    # 메인 스레드가 아닌 곳에서 실행되어 설정이 불가능할 경우를 대비한 예외 처리입니다.
    signal.signal = lambda s, h: None

# 컨베이어 하드웨어 제어를 위한 라이브러리 임포트
import serial.tools.list_ports
from conveyor import ConveyorController

# --- 1. 페이지 설정 ---
# 웹 브라우저의 탭 제목, 아이콘, 그리고 레이아웃(넓게 사용)을 설정합니다.
st.set_page_config(page_title="Data Collection Monitor", page_icon="🦾", layout="wide")

# --- 2. 설정 및 데이터 경로 ---
CONFIG_FILE = "test_dashboard_config.json" # 설정값(목표시간 등)을 저장할 파일 경로
DATA_PATH = os.path.expanduser("~/data_collection/habilis_dataset_manager/data/raw") # 실제 데이터가 쌓이는 경로

# 컨베이어 컨트롤러 초기화 (캐싱 처리)
# @st.cache_resource는 페이지가 새로고침되어도 하드웨어 연결을 끊지 않고 유지하게 해줍니다.
@st.cache_resource
def get_conveyor_controller():
    try:
        # 자동 감지 모드(port 'a')로 컨베이어 장치와 연결을 시도합니다.
        port_config = {'a': None} 
        controller = ConveyorController(port_config)
        return controller
    except Exception as e:
        return None

# 저장된 JSON 설정 파일을 읽어오는 함수
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    # 파일이 없으면 기본값(목표 4시간 등)을 반환합니다.
    return {"target_hours": 4.0, "left_operators": [], "right_operators": [], "task_targets": {}}

# 현재 대시보드 설정을 JSON 파일로 내보내는 함수
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
# 앱이 처음 켜질 때 필요한 변수들을 메모리(session_state)에 등록합니다.
if "test_init" not in st.session_state:
    saved = load_config()
    st.session_state.test_target_input = float(saved.get("target_hours", 4.0))
    st.session_state.test_left_input = saved.get("left_operators", [])
    st.session_state.test_right_input = saved.get("right_operators", [])
    st.session_state.task_targets = saved.get("task_targets", {})
    st.session_state.test_init = True
    st.session_state.processed_folders = set() # 처리된 폴더 기록
    st.session_state.task_stats = {} # 작업별 누적 시간
    st.session_state.task_counts = {} # 작업별 수집 개수
    st.session_state.total_sec = 0.0 # 전체 누적 초
    st.session_state.conveyor_speed_val = 30 # 기본 속도(Hz)

# --- 3. 데이터 추출 함수 ---
# 폴더 내의 YAML(수집시간)과 JSON(작업명) 파일을 분석하여 데이터를 가져옵니다.
def get_folder_data(folder_path):
    duration, task_name = 0, "Unknown"
    yaml_path = os.path.join(folder_path, "metadata.yaml")
    json_path = os.path.join(folder_path, "metacard.json")
    if os.path.exists(yaml_path) and os.path.exists(json_path):
        try:
            # metadata.yaml에서 나노초 단위의 수집 시간을 읽어 초 단위로 변환합니다.
            with open(yaml_path, "r") as f:
                for line in f:
                    if "nanoseconds:" in line:
                        duration = int(line.split(":")[-1].strip()) / 1e9
                        break
            # metacard.json에서 현재 수행 중인 작업 이름을 읽어옵니다.
            with open(json_path, "r", encoding="utf-8") as f:
                task_name = json.load(f).get("task_name", "Unknown")
        except: pass
    return task_name, duration

# 폴더명(예: 20240119_123045)에서 시각(12:30)만 가독성 있게 추출합니다.
def safe_extract_time(folder_name: str) -> str:
    try:
        parts = folder_name.split("_")
        if len(parts) >= 2 and len(parts[1]) >= 4:
            return f"{parts[1][:2]}:{parts[1][2:4]}"
    except: pass
    return "--:--"

# --- 4. CSS 스타일 ---
# 대시보드의 다크 테마 디자인과 폰트 크기, 카드 형태의 레이아웃을 정의합니다.
st.markdown("""
<style>
    .stApp { background-color: #000000 !important; color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #1E2130 !important; }
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
</style>
""", unsafe_allow_html=True)

# --- 5. 사이드바 ---
# 작업 목표 설정 및 컨베이어 제어를 수행하는 왼쪽 바 영역입니다.
with st.sidebar:
    st.header("🦾 Dashboard Setting")
    # 목표 시간 입력창 (값이 바뀌면 자동으로 save_config 실행)
    st.number_input("전체 목표 시간 (Overall Target)", min_value=0.0, step=0.1, key="test_target_input", on_change=save_config)
    ops_list = ["황수범", "정재현", "김민기", "허재훈"]
    st.multiselect("Left Arm Operator", options=ops_list, key="test_left_input", on_change=save_config)
    st.multiselect("Right Arm Operator", options=ops_list, key="test_right_input", on_change=save_config)
    
    st.divider()
    
    # 동적으로 변하는 정보를 담기 위한 컨테이너
    sidebar_info_area = st.container()

    st.divider()
    
    # 금일 수집 최종 요약을 보여줄 팝오버 위치 고정
    summary_placeholder = st.empty()

    # --- 사이드바 최하단 컨베이어 제어 패널 ---
    st.divider()
    st.subheader("⚙️ Conveyor Control")
    
    # 컨베이어 UI가 들어갈 빈 공간 예약
    conveyor_area = st.empty()

    # 컨베이어 컨트롤러 객체를 가져와 실시간 제어 버튼 생성
    ctrl = get_conveyor_controller()
    with conveyor_area.container(): 
        if ctrl and len(ctrl.conveyor) > 0:
            active_belt = list(ctrl.conveyor.keys())[0]

            # 컨베이어 속도 조절 (Hz 단위)
            speed_input = st.number_input("Speed (Hz)", 1, 196, st.session_state.conveyor_speed_val, key="side_speed_input")
            if speed_input != st.session_state.conveyor_speed_val:
                st.session_state.conveyor_speed_val = speed_input
                ctrl.command(active_belt, speed=speed_input)
                
            # 역방향 회전 버튼
            if st.button("◀️ BWD", width='stretch', key="btn_bwd_side"):
                ctrl.command(active_belt, direction='backward', speed=st.session_state.conveyor_speed_val)
            
            # 정지 버튼
            if st.button("⏹ STOP", type="primary", width='stretch', key="btn_stop_side"):
                ctrl.command(active_belt, direction='stop')
                
            st.caption(f"Connected: {ctrl.conveyor[active_belt].ser.port}")
        else:
            st.error("⚠️ 컨베이어 연결 없음")

# --- 6. 데이터 로직 (전체 합산 버전) ---
# 오늘 날짜의 폴더들을 전수 조사하여 실시간 통계를 계산합니다.
try:
    today = datetime.now().strftime("%Y%m%d")
    # 오늘 날짜로 시작하는 폴더 목록 생성
    all_folders = sorted([f for f in os.listdir(DATA_PATH) if f.startswith(today)]) if os.path.exists(DATA_PATH) else []
    
    temp_task_stats = {}
    temp_task_counts = {}
    temp_total_sec = 0.0
    
    # 각 폴더별로 작업명과 걸린 시간을 합산합니다.
    for f_name in all_folders:
        task, sec = get_folder_data(os.path.join(DATA_PATH, f_name))
        if task != "Unknown":
            temp_task_stats[task] = temp_task_stats.get(task, 0) + sec
            temp_task_counts[task] = temp_task_counts.get(task, 0) + 1
            temp_total_sec += sec

    # 계산 결과를 세션 상태에 업데이트
    st.session_state.task_stats = temp_task_stats
    st.session_state.task_counts = temp_task_counts
    st.session_state.total_sec = temp_total_sec
    
    processed_total_count = sum(st.session_state.task_counts.values())

    # 사이드바 정보 영역에 작업별 목표 설정과 수집 시간 정보 출력
    with sidebar_info_area:
        st.subheader("🎯 Task별 목표 설정")
        for task_name in list(st.session_state.task_stats.keys()):
            current_target = st.session_state.task_targets.get(task_name, 1.0)
            new_target = st.number_input(f"Target: {task_name}", 0.1, 10.0, float(current_target), 0.5, key=f"side_target_{task_name}")
            if new_target != current_target:
                st.session_state.task_targets[task_name] = new_target
                save_config()

        st.divider()
        # 평균 수집 시간, 첫 수집 시각, 마지막 수집 시각 계산
        avg_sec = (st.session_state.total_sec / processed_total_count) if processed_total_count > 0 else 0.0
        start_t = safe_extract_time(all_folders[0]) if all_folders else "--:--"
        last_t = safe_extract_time(all_folders[-1]) if all_folders else "--:--"
        
        st.markdown(f'<div class="sidebar-time">🔥 Last Collect Time: {last_t}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sidebar-time">📊 Avg Collect Time: {int(avg_sec//60):02d}:{int(avg_sec%60):02d}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sidebar-time">🌞 First Collect Time: {start_t}</div>', unsafe_allow_html=True)

    # 팝오버 메뉴를 통해 금일 수집 요약 리포트 제공
    with summary_placeholder.popover("📋 금일 수집 최종 요약"):
        if st.session_state.task_stats:
            total_h = st.session_state.total_sec / 3600
            st.info(f"**총 수집 시간:** {total_h:.2f}h / {st.session_state.test_target_input}h")
            st.divider()
            for task, sec in st.session_state.task_stats.items():
                t_h = sec / 3600
                st.write(f"📍 **{task}**: {t_h:.2f}h ({st.session_state.task_counts.get(task, 0)}개)")

    # --- 메인 대시보드 화면 ---
    col_h1, col_h2 = st.columns([0.65, 0.35])
    with col_h1: st.title("🦾 Data Dashboard (v1.6)")
    with col_h2: 
        # 선택된 좌/우 작업자 이름을 상단에 표시
        l_ops, r_ops = ", ".join(st.session_state.test_left_input) or "미지정", ", ".join(st.session_state.test_right_input) or "미지정"
        st.markdown(f'<div class="operator-row"><div class="arm-tag">L: {l_ops}</div><div class="arm-tag">R: {r_ops}</div></div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([0.7, 0.3], gap="medium")
    
    # [왼쪽 영역] 메인 시계 및 달성률 게이지
    with col_left:
        # 특정 작업을 선택하여 모니터링할 수 있는 선택창
        task_options = ["전체 합계 (Overall)"] + sorted(list(st.session_state.task_stats.keys()))
        selected_focus = st.selectbox("Task Selector", options=task_options, index=0, label_visibility="collapsed")
        
        if selected_focus == "전체 합계 (Overall)":
            display_sec, display_count, display_target = st.session_state.total_sec, processed_total_count, st.session_state.test_target_input
        else:
            display_sec, display_count, display_target = st.session_state.task_stats.get(selected_focus, 0), st.session_state.task_counts.get(selected_focus, 0), st.session_state.task_targets.get(selected_focus, 1.0)

        # 현재 수집된 시간을 시:분:초 형태로 크게 표시
        with st.container(border=True):
            h_f, m_f, s_f = int(display_sec // 3600), int((display_sec % 3600) // 60), int(display_sec % 60)
            st.markdown(f'<p class="focus-label">MONITORING: {selected_focus.upper()}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="huge-font">{h_f:02d}:{m_f:02d}:{s_f:02d} <span class="goal-font">/ {display_target}h</span></p>', unsafe_allow_html=True)
            st.markdown(f'<p class="count-font">현재 {display_count}개 데이터 수집 완료</p>', unsafe_allow_html=True)
            
            # 목표 달성률을 나타내는 게이지 차트 (Plotly)
            fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=display_sec/3600, number={"font": {"color": "#FFFFFF", "size": 20}, "suffix": "h"},
                gauge={"axis": {"range": [0, max(display_target, 1)], "tickcolor": "white"}, "bar": {"color": "#5AC8FA"}, "bgcolor": "rgba(255,255,255,0.05)",
                "threshold": {"line": {"color": "white", "width": 4}, "value": display_target if display_target > 0 else 0.001}}))
            fig_gauge.update_layout(height=280, margin=dict(t=0, b=0, l=50, r=50), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_gauge, width='stretch', key="main_gauge")

        # 하단 두 칸: 디스크 용량 및 전체 달성률 차트
        col_s1, col_s2 = st.columns(2)
        with col_s1:
             with st.container(border=True):
                st.subheader("💾 Disk Usage")
                # 리눅스 df 명령어로 하드 용량 확인
                df_out = os.popen("df -h / | tail -1").read().split()
                used_p = int(df_out[4].replace("%", "")) if len(df_out) > 4 else 0
                fig_disk = go.Figure(go.Pie(values=[used_p, 100-used_p], hole=0.75, marker_colors=["#FF3B30", "#1C1C1E"], textinfo="none"))
                fig_disk.add_annotation(text=f"{used_p}%", showarrow=False, font=dict(size=30, color="#FF3B30", weight="bold"))
                fig_disk.update_layout(height=180, margin=dict(t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
                st.plotly_chart(fig_disk, width='stretch', key="disk")
        with col_s2:
            with st.container(border=True):
                st.subheader("📈 Overall Achievement")
                # 전체 누적 초를 목표 시간(초 단위)으로 나누어 달성률 계산
                overall_pct = int((st.session_state.total_sec / (st.session_state.test_target_input * 3600)) * 100) if st.session_state.test_target_input > 0 else 0
                fig_prog = go.Figure(go.Pie(values=[min(overall_pct, 100), max(0, 100-overall_pct)], hole=0.75, marker_colors=["#32D74B", "#1C1C1E"], textinfo="none"))
                fig_prog.add_annotation(text=f"{overall_pct}%", showarrow=False, font=dict(size=30, color="#32D74B", weight="bold"))
                fig_prog.update_layout(height=180, margin=dict(t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
                st.plotly_chart(fig_prog, width='stretch', key="overall")

    # --- [오른쪽 영역] 작업별 비율 및 상세 카드 ---
    with col_right:
        with st.container(border=True):
            st.markdown("### 📊 Task Ratio")
            # 어떤 작업의 비중이 높은지 파이 차트로 표시
            sorted_tasks = sorted(st.session_state.task_stats.items(), key=lambda x: x[1], reverse=True)
            if sorted_tasks:
                fig_donut = go.Figure(go.Pie(labels=[t[0] for t in sorted_tasks], values=[t[1] for t in sorted_tasks], hole=0.55,
                    marker=dict(colors=["#FF2D55", "#32D74B", "#5AC8FA"]), textinfo="percent", sort=False))
                fig_donut.update_layout(height=300, margin=dict(t=20, b=20, l=10, r=10), showlegend=True, 
                                        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_donut, width='stretch', key="donut")
                
                st.divider()
                # 하단에 개별 작업의 달성 정보 카드 생성
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

# 3초마다 페이지를 자동으로 새로고침하여 최신 수집 현황을 반영합니다.
st_autorefresh(interval=3000, key="refresh")
