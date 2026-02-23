# tab2_total.py
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import base64
import os

from utils import run_query, get_dashboard_charts_data

# 로컬 이미지를 웹에서 깨지지 않게 띄우기 위한 Base64 변환 함수
def get_local_image_as_base64(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
            
    fallback_path = image_path.split("TDD/")[-1] if "TDD/" in image_path else image_path
    if os.path.exists(fallback_path):
        with open(fallback_path, "rb") as f:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
            
    return "https://cdn-icons-png.flaticon.com/512/2042/2042462.png"

def render_total_statistics():
    st.markdown(f"## 🏛️ 통합 데이터 통계")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 라디오 버튼 우측 정렬
    st.markdown("""
        <style>
        div[role="radiogroup"] {
            justify-content: flex-end;
        }
        </style>
    """, unsafe_allow_html=True)

    try:
        col_left, col_center, col_right = st.columns([2.5, 5, 2.5], gap="large")

        # =========================================================
        # ■ 왼쪽 영역: Project Oversight & Positioning Map
        # =========================================================
        with col_left:
            st.subheader("■ 프로젝트 진행 현황")
            
            list_query = """
                SELECT 
                    p.project_name, p.status, p.end_date, p.target_hour,
                    COALESCE(SUM(sl.duration), 0) / 3600.0 as current_hours
                FROM projects p
                LEFT JOIN tasks t ON p.project_id = t.project_id
                LEFT JOIN subtasks s ON t.task_id = s.task_id
                LEFT JOIN subtask_logs sl ON s.subtask_id = sl.subtask_id
                WHERE p.status != 'Done' OR (p.status = 'Done' AND p.end_date >= CURRENT_DATE - INTERVAL '3 days')
                GROUP BY p.project_id, p.project_name, p.status, p.end_date, p.target_hour
                ORDER BY p.end_date ASC;
            """
            rows = run_query(list_query)
            
            if not rows:
                st.info("표시할 프로젝트가 없습니다.")
            else:
                for i, row in enumerate(rows):
                    p_name, p_status, p_end, p_target, p_current = row
                    
                    try:
                        safe_target = float(p_target) if p_target is not None else 0.0
                        safe_current = float(p_current) if p_current is not None else 0.0
                    except (ValueError, TypeError):
                        safe_target = 0.0
                        safe_current = 0.0

                    progress = (safe_current / safe_target * 100) if safe_target > 0 else 0.0
                    progress = min(progress, 100.0)
                    
                    if p_status == 'Done': 
                        card_border_color = "#32D74B"
                        badge_bg = "rgba(50, 215, 75, 0.2)"
                    elif p_status == 'Delayed': 
                        card_border_color = "#FF3B30"
                        badge_bg = "rgba(255, 59, 48, 0.2)"
                    elif p_status in ['On Track', 'In Progress']: 
                        card_border_color = "#FFD60A"
                        badge_bg = "rgba(255, 214, 10, 0.2)"
                    else: 
                        card_border_color = "#007AFF"
                        badge_bg = "rgba(0, 122, 255, 0.2)"

                    target_color = "#FFD60A" if p_status in ['On Track', 'In Progress'] else "#5AC8FA"

                    with st.container(border=True):
                        c_text, c_chart = st.columns([0.7, 0.3])
                        with c_text:
                            st.markdown(f"""
                                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                                    <span style="font-size: 26px; font-weight: 800; color: white;">{p_name}</span>
                                    <span style="background-color: {badge_bg}; padding: 4px 10px; border-radius: 6px; font-size: 14px; font-weight: bold; color: {card_border_color}; border: 1px solid {card_border_color}; white-space: nowrap;">
                                        {p_status}
                                    </span>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            d_day = 0
                            end_str = "-"
                            if p_end:
                                try:
                                    if isinstance(p_end, str):
                                        p_end = datetime.strptime(p_end.split()[0], '%Y-%m-%d')
                                    d_day = (p_end.date() - datetime.now().date()).days
                                    end_str = p_end.strftime('%Y.%m.%d')
                                except:
                                    pass

                            d_day_str = f"D-{d_day}" if d_day >= 0 else f"D+{abs(d_day)}"
                            
                            st.markdown(f"""
                                <div style="font-size: 20px; color: #CCCCCC; line-height: 1.6;">
                                    Deadline: <span style="color: {target_color}; font-weight: bold;">{end_str}</span> <span style="color: #FFFFFF; font-size: 18px;">({d_day_str})</span><br>
                                    Target: <span style="color: {target_color}; font-weight: 800;">{safe_target}h</span> &nbsp;|&nbsp; 
                                    Current: <span style="color: #32D74B; font-weight: 800;">{safe_current:.1f}h</span>
                                </div>
                            """, unsafe_allow_html=True)

                        with c_chart:
                            st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True) 
                            fig_mini = go.Figure(go.Pie(
                                values=[progress, 100-progress], hole=0.7,
                                marker=dict(colors=[card_border_color, "rgba(255,255,255,0.1)"]), textinfo="none", sort=False
                            ))
                            fig_mini.add_annotation(
                                text=f"<b>{int(progress)}%</b>", showarrow=False,
                                font=dict(size=16, color="white"), x=0.5, y=0.5
                            )
                            fig_mini.update_layout(
                                showlegend=False, margin=dict(t=0, b=0, l=0, r=0),
                                height=90, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
                            )
                            st.plotly_chart(fig_mini, use_container_width=True, config={'displayModeBar': False}, key=f"donut_{i}_{p_name}")

            st.divider()

            st.subheader("■ 데이터 포지셔닝 맵")
            map_query = """
                SELECT 
                    p.project_name, AVG(sl.quality_score) as avg_quality,
                    AVG(sl.duration) as avg_duration, COUNT(sl.subtask_log_id) as data_count
                FROM projects p JOIN tasks t ON p.project_id = t.project_id
                JOIN subtasks s ON t.task_id = s.task_id JOIN subtask_logs sl ON s.subtask_id = sl.subtask_id
                GROUP BY p.project_name HAVING count(sl.subtask_log_id) > 0;
            """
            map_data = run_query(map_query)
            if map_data:
                df_map = pd.DataFrame(map_data, columns=['Project', 'Quality', 'Duration', 'Count'])
                
                df_map['Duration'] = pd.to_numeric(df_map['Duration'], errors='coerce')
                df_map['Quality'] = pd.to_numeric(df_map['Quality'], errors='coerce')

                fig_map = px.scatter(df_map, x="Duration", y="Quality", size="Count", color="Project", text="Project")
                
                avg_x = df_map['Duration'].mean()
                avg_y = df_map['Quality'].mean()
                if pd.notna(avg_y): fig_map.add_hline(y=avg_y, line_width=1, line_dash="dot", line_color="gray")
                if pd.notna(avg_x): fig_map.add_vline(x=avg_x, line_width=1, line_dash="dot", line_color="gray")
                
                fig_map.update_traces(textposition='top center', textfont_size=12)
                fig_map.update_layout(
                    height=300, margin=dict(t=10, b=10, l=10, r=10),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.05)",
                    font=dict(color="white"), showlegend=False,
                    xaxis=dict(title="Avg Time (s)", showgrid=False), yaxis=dict(title="Avg Quality", showgrid=False)
                )
                st.plotly_chart(fig_map, use_container_width=True, key="pos_map")
            else:
                st.info("데이터 부족")

        # =========================================================
        # 📊 중앙 영역: 간트 차트 및 파이 차트
        # =========================================================
        with col_center:
            header_col1, header_col2 = st.columns([0.45, 0.55])
            with header_col1:
                st.markdown("<h4 style='margin-top:0px; margin-bottom:0px;'>■ 데이터팀 수집 일정 및 현황</h4>", unsafe_allow_html=True)
            with header_col2:
                view_mode = st.radio(
                    "View Mode", 
                    ["1달 단위", "전체 기간"], 
                    horizontal=True, 
                    label_visibility="collapsed"
                )
                
            df_gantt, df_progress, df_primitive = get_dashboard_charts_data()

            if not df_gantt.empty:
                df_gantt['Start'] = pd.to_datetime(df_gantt['Start'], errors='coerce')
                df_gantt['Finish'] = pd.to_datetime(df_gantt['Finish'], errors='coerce')
                df_gantt = df_gantt.dropna(subset=['Start', 'Finish'])
                
                today_dt = pd.Timestamp.now().normalize()
                
                if view_mode == "1달 단위":
                    min_date = today_dt.replace(day=1)
                    max_date = min_date + pd.offsets.MonthEnd(1) + pd.Timedelta(days=1)
                    mask = (df_gantt['Start'] <= max_date) & (df_gantt['Finish'] >= min_date)
                    df_gantt = df_gantt[mask]

                df_gantt = df_gantt.sort_values(by='Finish', ascending=False)
                
                inner_chart_height = max(350, len(df_gantt) * 45)

                df_gantt['Task_Bold'] = df_gantt['Task'].apply(lambda x: f"<b>{x}</b>")

                fig_gantt = px.timeline(
                    df_gantt, x_start="Start", x_end="Finish", y="Task_Bold", hover_name="Task"
                )
                fig_gantt.update_yaxes(autorange="reversed")
                
                fig_gantt.update_traces(
                    marker_color="#579DFF",       
                    marker_cornerradius=12,       
                    opacity=0.9
                )
                
                # 🧩 [수정 완벽 반영] bargap을 0.3 -> 0.5로 늘려 막대를 살짝 얇고 세련되게!
                fig_gantt.update_layout(
                    height=inner_chart_height, bargap=0.5, margin=dict(l=0, r=0, t=10, b=0),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", 
                    font=dict(color="white", size=15), 
                    yaxis_title=None, xaxis_title=None
                )
                
                fig_gantt.update_xaxes(
                    tickformat="%m월 %d일", 
                    showgrid=True, 
                    gridwidth=1, 
                    gridcolor="rgba(255, 255, 255, 0.15)", 
                    griddash="dot",
                    tickfont=dict(size=14, color="white", family="Arial Black, sans-serif")
                )
                fig_gantt.update_yaxes(tickfont=dict(size=15, color="white", weight="bold"))

                today_str = datetime.now().strftime('%Y-%m-%d')
                
                fig_gantt.add_shape(
                    type="line", x0=today_str, x1=today_str, y0=0, y1=1, yref="paper",
                    line=dict(color="#FA114F", width=2, dash="dash")
                )
                fig_gantt.add_annotation(
                    x=today_str, y=1.02, yref="paper",
                    text="<b>오늘</b>", showarrow=False,
                    font=dict(color="#FA114F", size=14),
                    xanchor="left", yanchor="bottom"
                )

                if view_mode == "1달 단위" and 'min_date' in locals():
                    fig_gantt.update_xaxes(range=[min_date, max_date])

                # 높이 320 고정 유지 (왼쪽 카드와 라인 맞춤)
                with st.container(height=320, border=False):
                    st.plotly_chart(fig_gantt, use_container_width=True)
            else:
                st.info("간트 차트용 데이터가 없습니다.")

            st.divider()

            better_palette = [
                "#FF2D55", "#FF9500", "#FFD60A", "#30D158", "#00E5FF",
                "#5856D6", "#AF52DE", "#FF375F", "#64D2FF", "#A3E635"
            ]

            c_pie1, c_pie2 = st.columns([0.65, 0.35])

            with c_pie1:
                st.markdown("##### ■ 프로젝트별 수집 진행률")
                if not df_progress.empty:
                    df_progress['collected_hours'] = pd.to_numeric(df_progress['collected_hours'], errors='coerce').fillna(0.0)
                    df_progress = df_progress[df_progress['collected_hours'] > 0]
                    df_progress = df_progress.sort_values(by='collected_hours', ascending=False)
                    
                    total_prog_hours = df_progress['collected_hours'].sum()

                    fig_prog = px.pie(
                        df_progress, names='project_name', values='collected_hours', hole=0.65,
                        color_discrete_sequence=better_palette
                    )
                    
                    fig_prog.update_traces(
                        textposition='inside', 
                        texttemplate='<b>%{value:.1f}h</b>',
                        textfont=dict(color="white"),
                        marker=dict(line=dict(color="#0E1117", width=0.8)), 
                        hovertemplate="<b>%{label}</b><br>수집량: %{value:.1f}h<extra></extra>",
                        sort=False
                    )
                    
                    fig_prog.update_layout(
                        height=330, 
                        showlegend=True, 
                        legend=dict(
                            orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.0,
                            font=dict(size=12, color="white"), title=None
                        ),
                        margin=dict(t=10, b=10, l=10, r=10),
                        paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white")
                    )
                    
                    fig_prog.add_annotation(
                        text=f"<span style='font-size: 24px; font-weight: bold; color: white;'>{total_prog_hours:.1f}h</span><br><span style='font-size: 14px; color: #888;'>Total</span>",
                        showarrow=False, x=0.5, y=0.5
                    )
                    
                    st.plotly_chart(fig_prog, use_container_width=True)

            with c_pie2:
                st.markdown("##### ■ Primitive Data & Task 비율")
                if not df_primitive.empty:
                    df_primitive['collected_hours'] = pd.to_numeric(df_primitive['collected_hours'], errors='coerce').fillna(0.0)
                    total_prim_hours = df_primitive['collected_hours'].sum()
                    
                    fig_prim = px.pie(
                        df_primitive, names='data_type', values='collected_hours', hole=0.65,
                        color='data_type', 
                        color_discrete_map={'Primitive Data':'#30D158', 'Task Data':'#00E5FF'}
                    )
                    
                    fig_prim.update_traces(
                        textposition='inside', 
                        texttemplate='<b>%{value:.1f}h</b>',
                        textfont=dict(color="white"),
                        marker=dict(line=dict(color="#0E1117", width=0.8)),
                        hovertemplate="<b>%{label}</b><br>비율: %{value:.1f}h<extra></extra>",
                        sort=False
                    )
                    
                    fig_prim.update_layout(
                        height=330, 
                        showlegend=True, 
                        legend=dict(
                            orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.0,
                            font=dict(size=13, color="white"), title=None
                        ),
                        margin=dict(t=10, b=10, l=10, r=10),
                        paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white")
                    )
                    
                    fig_prim.add_annotation(
                        text=f"<span style='font-size: 24px; font-weight: bold; color: white;'>{total_prim_hours:.1f}h</span><br><span style='font-size: 14px; color: #888;'>Total</span>",
                        showarrow=False, x=0.5, y=0.5
                    )
                    
                    st.plotly_chart(fig_prim, use_container_width=True)

        # =========================================================
        # 🤖 오른쪽 영역: Robot Lab 상태 모니터링
        # =========================================================
        with col_right:
            st.subheader("■ 로봇 상태 현황")
            
            robot_query = """
                SELECT 
                    r.model_name,
                    r.status,
                    COALESCE(
                        (SELECT p.project_name
                         FROM subtask_logs sl
                         JOIN subtasks s ON sl.subtask_id = s.subtask_id
                         JOIN tasks t ON s.task_id = t.task_id
                         JOIN projects p ON t.project_id = p.project_id
                         WHERE sl.robot_id = r.robot_id
                         ORDER BY s.subtask_date DESC, sl.subtask_log_id DESC
                         LIMIT 1), '대기중'
                    ) as current_project
                FROM robots r
                ORDER BY r.robot_id ASC;
            """
            
            robot_data = run_query(robot_query)
            
            robot_images = {
                "RB-Y1": get_local_image_as_base64("tomo_dashboard/TDD/img/RAINBOW_rby1.png"), 
                "AI-Worker": get_local_image_as_base64("tomo_dashboard/TDD/img/ROBOTIS_aiworker.png"), 
                "ROBROS": get_local_image_as_base64("tomo_dashboard/TDD/img/ROBROS_igris.png") 
            }
            default_robot_img = "https://cdn-icons-png.flaticon.com/512/2042/2042462.png"
            
            if not robot_data:
                st.info("등록된 로봇 장비가 없습니다.")
            else:
                for row in robot_data:
                    r_name = row[0]
                    r_status_str = str(row[1]).strip().lower() if row[1] else "ready"
                    r_project = row[2]
                    
                    if r_status_str == 'active':
                        border_color = "#30D158" 
                        bg_color = "rgba(48, 209, 88, 0.1)"
                        display_status = "Active"
                    elif r_status_str == 'error':
                        border_color = "#FF2D55" 
                        bg_color = "rgba(255, 45, 85, 0.1)"
                        display_status = "Error"
                    elif r_status_str == 'attention':
                        border_color = "#FFD60A" 
                        bg_color = "rgba(255, 214, 10, 0.1)"
                        display_status = "Attention"
                    else:
                        border_color = "#00E5FF" 
                        bg_color = "rgba(0, 229, 255, 0.1)"
                        display_status = "Ready"
                        
                    current_robot_img = robot_images.get(r_name, default_robot_img)
                        
                    html_str = (
                        f'<div style="border: 2px solid {border_color}; border-radius: 12px; padding: 12px; margin-bottom: 20px; background-color: {bg_color}; display: flex; align-items: center; gap: 20px;">'
                        f'<div style="flex-shrink: 0; width: 65px; height: 65px; background-color: rgba(255,255,255,0.05); border-radius: 8px; display: flex; justify-content: center; align-items: center; overflow: hidden; border: 1px solid rgba(255,255,255,0.1);">'
                        f'<img src="{current_robot_img}" style="width: 50px; height: 50px; object-fit: contain;">'
                        f'</div>'
                        f'<div style="flex-grow: 1; display: flex; flex-direction: column; justify-content: center;">'
                        f'<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">'
                        f'<span style="height: 14px; width: 14px; background-color: {border_color}; border-radius: 50%; display: inline-block; box-shadow: 0 0 8px {border_color};"></span>'
                        f'<strong style="font-size: 18px; color: {border_color}; text-shadow: 0 0 5px rgba(0,0,0,0.5);">{display_status}</strong>'
                        f'</div>'
                        f'<div style="font-size: 15px; color: #E0E0E0; font-weight: bold;">'
                        f'<span style="color: #666;">&gt;&gt;</span> {r_name} '
                        f'<span style="color: #666; margin-left: 8px;">&gt;&gt;</span> {r_project}'
                        f'</div>'
                        f'</div>'
                        f'</div>'
                    )
                    st.markdown(html_str, unsafe_allow_html=True)

        # =========================================================
        # 🚧 하단 영역: QA/QC Labeling Status (내일 작업용 공간)
        # =========================================================
        st.divider()
        st.subheader("■ QA/QC & Labeling Status")
        
        with st.container(border=True):
            st.markdown("""
                <div style="height: 150px; display: flex; flex-direction: column; justify-content: center; align-items: center; background-color: rgba(255,255,255,0.02); border-radius: 8px;">
                    <h3 style="color: #888; margin-bottom: 8px;">🚧 데이터 연동 및 UI 업데이트 예정 (Next Step)</h3>
                    <p style="color: #666; font-size: 16px; margin: 0;">이 공간에 QA/QC 상태 및 라벨링 진행률 현황판이 구성됩니다.</p>
                </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.exception(e)