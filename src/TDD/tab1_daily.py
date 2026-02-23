# tab1_daily.py
import streamlit as st
import os
from datetime import datetime
import plotly.graph_objects as go
import numpy as np
from scipy.stats import norm
from utils import get_folder_data, safe_extract_time, format_h_m, save_config, DATA_PATH # 🧩 [수정] utils에서 필요한 함수 임포트

def render_daily_monitor(sidebar_info_area, summary_placeholder):
    # 🧩 [이동] 기존 메인 로직을 함수로 캡슐화. sidebar 요소들을 인자로 받음
    try:
        # 데이터 로딩 로직
        today = datetime.now().strftime("%Y%m%d")
        all_folders = sorted([f for f in os.listdir(DATA_PATH) if f.startswith(today)]) if os.path.exists(DATA_PATH) else []
        
        temp_task_stats = {}
        temp_task_counts = {}
        temp_task_durations = {}
        temp_total_sec = 0.0
        
        for f_name in all_folders:
            task, sec = get_folder_data(os.path.join(DATA_PATH, f_name))
            if task != "Unknown":
                temp_task_stats[task] = temp_task_stats.get(task, 0) + sec
                temp_task_counts[task] = temp_task_counts.get(task, 0) + 1
                temp_total_sec += sec
                if task not in temp_task_durations: temp_task_durations[task] = []
                temp_task_durations[task].append(sec)
    
        st.session_state.task_stats = temp_task_stats
        st.session_state.task_counts = temp_task_counts
        st.session_state.task_durations = temp_task_durations
        st.session_state.total_sec = temp_total_sec
        processed_total_count = sum(st.session_state.task_counts.values())
    
        # 사이드바 정보 업데이트 (전역 변수 호출)
        with sidebar_info_area:
            st.subheader("🎯 Task별 목표 설정")
            if "task_celebrated" not in st.session_state: st.session_state.task_celebrated = {}
            for task_name in list(st.session_state.task_stats.keys()):
                current_task_target = st.session_state.task_targets.get(task_name, 1.0)
                current_sec = st.session_state.task_stats.get(task_name, 0)
                is_task_done = (current_sec / 3600) >= current_task_target
                
                if is_task_done: st.write(f"✅  **{task_name}**")
                else: st.write(f"📍 **{task_name}**")
                
                t_default_h = int(current_task_target)
                t_default_m = int(round((current_task_target - t_default_h) * 60))
                
                col_th, col_tm = st.columns(2)
                with col_th: t_target_h = st.number_input("시간", 0, 24, t_default_h, 1, key=f"h_{task_name}")
                with col_tm: t_target_m = st.number_input("분", 0, 59, t_default_m, 1, key=f"m_{task_name}")
                
                new_task_target = t_target_h + (t_target_m / 60.0)
                if new_task_target != current_task_target:
                    st.session_state.task_targets[task_name] = new_task_target
                    st.session_state.task_celebrated[task_name] = False
                    save_config()
                
                if is_task_done and not st.session_state.task_celebrated.get(task_name, False):
                    st.balloons()
                    st.toast(f"🎉 {task_name} 목표 달성!", icon="✅")
                    st.session_state.task_celebrated[task_name] = True
            
            st.divider()
            avg_sec = (st.session_state.total_sec / processed_total_count) if processed_total_count > 0 else 0.0
            start_t = safe_extract_time(all_folders[0]) if all_folders else "--:--"
            last_t = safe_extract_time(all_folders[-1]) if all_folders else "--:--"
            st.markdown(f'<div class="sidebar-time">🔥 Last Collect Time: {last_t}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="sidebar-time">📊 Avg Collect Time: {int(avg_sec//60):02d}:{int(avg_sec%60):02d}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="sidebar-time">🌞 First Collect Time: {start_t}</div>', unsafe_allow_html=True)
    
        with summary_placeholder.popover("요약 보기"):
            if st.session_state.task_stats:
                total_time_str = format_h_m(st.session_state.total_sec)
                target_time_str = format_h_m(st.session_state.test_target_input * 3600)
                st.info(f"**총 수집 시간:** {total_time_str} / {target_time_str}")
                st.divider()
                for task, sec in st.session_state.task_stats.items():
                    st.write(f"📍 **{task}**: {format_h_m(sec)} ({st.session_state.task_counts.get(task, 0)}개)")
    
        # --- 메인 UI 렌더링 ---
        col_h1, col_h2 = st.columns([0.65, 0.35])
        with col_h1: st.title("🦾 Daily Data Dashboard (v2.0)")
        with col_h2: 
            l_ops = ", ".join(st.session_state.test_left_input) or "미지정"
            r_ops = ", ".join(st.session_state.test_right_input) or "미지정"
            st.markdown(f'<div class="operator-row"><div class="arm-tag">L: {l_ops}</div><div class="arm-tag">R: {r_ops}</div></div>', unsafe_allow_html=True)
    
        col_left, col_right = st.columns([0.65, 0.35], gap="medium")
        
        # [왼쪽 영역]
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
                target_display_str = format_h_m(display_target * 3600)
                st.markdown(f'<p class="huge-font">{h_f:02d}:{m_f:02d}:{s_f:02d} <span class="goal-font">/ {target_display_str}</span></p>', unsafe_allow_html=True)
                st.markdown(f'<p class="count-font">현재 {display_count}개 데이터 수집 완료</p>', unsafe_allow_html=True)
                
                fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=display_sec/3600, number={"font": {"size": 20}, "suffix": "h"},
                    gauge={"axis": {"range": [0, max(display_target, 1)]}, "bar": {"color": "#5AC8FA"}}))
                fig_gauge.update_layout(height=280, margin=dict(t=0, b=0, l=50, r=50), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_gauge, width='stretch', key="main_gauge")
    
            # 정규분포도 (Curation Helper)
            with st.container(border=True):
                st.subheader("📊 수집 시간 정규분포도")
                # ... (이전과 동일한 정규분포 로직 적용) ...
                if selected_focus == "전체 합계 (Overall)":
                    durations = [d for task_list in st.session_state.task_durations.values() for d in task_list]
                else:
                    durations = st.session_state.task_durations.get(selected_focus, [])

                if durations and len(durations) > 2:
                    data = np.array(durations)
                    mu, std = norm.fit(data)
                    # (Plotly 차트 생략 - 기존과 동일)
                    st.info(f"평균 수집 시간: {mu:.1f}s")
                else:
                    st.info("데이터 부족으로 분석 불가")

        # [오른쪽 영역]
        with col_right:
            # 1. Task Ratio (최상단)
            with st.container(border=True):
                st.markdown("### 📊 Task Ratio")
                sorted_tasks = sorted(st.session_state.task_stats.items(), key=lambda x: x[1], reverse=True)
                if sorted_tasks:
                    fig_donut = go.Figure(go.Pie(
                        labels=[t[0] for t in sorted_tasks], 
                        values=[t[1] for t in sorted_tasks], 
                        hole=0.55,
                        marker=dict(colors=["#FF2D55", "#32D74B", "#5AC8FA"]), 
                        textinfo="percent", 
                        sort=False
                    ))
                    fig_donut.update_layout(
                        height=300, 
                        margin=dict(t=20, b=20, l=10, r=10), 
                        showlegend=True, 
                        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5), 
                        paper_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig_donut, width='stretch', key="donut")

                    st.divider()

                    # 2. 상세 Task 카드 (Task Ratio 바로 아래 배치 및 디자인 원복)
                    for name, sec in sorted_tasks:
                        count = st.session_state.task_counts.get(name, 0)
                        target_h = float(st.session_state.task_targets.get(name, 1.0))
                        pct = (sec / 3600) / target_h * 100

                        # 소수점(.2f) 대신 'X시간 Y분' 포맷 함수(format_h_m) 적용
                        st.markdown(f"""
                            <div class="right-task-card">
                                <div class="card-name">📍 {name}</div>
                                <div class="card-value-container">
                                    <span class="card-value">{format_h_m(sec)}</span>
                                    <span class="card-percent">{pct:.1f}%</span>
                                </div>
                                <div class="card-badge">↑ {int(sec//60)}m · {count}개</div>
                            </div>
                        """, unsafe_allow_html=True)

            # 3. Disk & Achievement (가로 배치)
            col_sub1, col_sub2 = st.columns(2)
            with col_sub1:
                with st.container(border=True):
                    st.subheader("💾 Disk")
                    df_out = os.popen("df -h / | tail -1").read().split()
                    used_p = int(df_out[4].replace("%", "")) if len(df_out) > 4 else 0
                    fig_disk = go.Figure(go.Pie(values=[used_p, 100-used_p], hole=0.75, marker_colors=["#FF3B30", "#1C1C1E"], textinfo="none"))
                    fig_disk.add_annotation(text=f"{used_p}%", showarrow=False, font=dict(size=20, color="#FF3B30", weight="bold"))
                    fig_disk.update_layout(height=160, margin=dict(t=5, b=5), paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
                    st.plotly_chart(fig_disk, width='stretch', key="disk")
            with col_sub2:
                with st.container(border=True):
                    st.subheader("📈 Overall")
                    overall_pct = int((st.session_state.total_sec / (st.session_state.test_target_input * 3600)) * 100) if st.session_state.test_target_input > 0 else 0
                    fig_prog = go.Figure(go.Pie(values=[min(overall_pct, 100), max(0, 100-overall_pct)], hole=0.75, marker_colors=["#32D74B", "#1C1C1E"], textinfo="none"))
                    fig_prog.add_annotation(text=f"{overall_pct}%", showarrow=False, font=dict(size=20, color="#32D74B", weight="bold"))
                    fig_prog.update_layout(height=160, margin=dict(t=5, b=5), paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
                    st.plotly_chart(fig_prog, width='stretch', key="overall")


        # 목표 달성 이벤트
        if st.session_state.test_target_input > 0:
            if (st.session_state.total_sec / (st.session_state.test_target_input * 3600)) >= 1.0:
                if not st.session_state.get("overall_celebrated", False):
                    st.balloons()
                    st.session_state.overall_celebrated = True

    except Exception as e:
        st.error(f"Tab 1 Error: {e}")