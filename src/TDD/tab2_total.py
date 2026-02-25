# tab2_total.py
import os
import re
import json
import base64
import pandas as pd
from datetime import datetime

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components

from utils import run_query  # ✅ get_dashboard_charts_data는 (t.data_type) 에러 때문에 사용하지 않음


# =========================================================
# Helpers
# =========================================================
def get_local_image_as_base64(image_path: str) -> str:
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
            
    fallback_path = image_path.split("TDD/")[-1] if "TDD/" in image_path else image_path
    if os.path.exists(fallback_path):
        with open(fallback_path, "rb") as f:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
            
    return "https://cdn-icons-png.flaticon.com/512/2042/2042462.png"


def format_dt(dt_val):
    if not dt_val:
        return "<span style='color:#555;'>대기중</span>"
    if hasattr(dt_val, "strftime"):
        return dt_val.strftime("%Y-%m-%d %H:%M")
    s = str(dt_val)
    return s[:16] if len(s) >= 16 else s


def _extract_avg_seconds(instruction: str) -> float | None:
    """
    instruction 예시:
      - "Epi(126) * Avg(70s)"
      - "Epi(134) * Avg(56s)"
    -> Avg 괄호 안 숫자를 seconds로 파싱
    """
    if not instruction:
        return None
        
    m = re.search(r"Avg\(\s*([0-9]+(?:\.[0-9]+)?)\s*s\s*\)", str(instruction), re.IGNORECASE)
    if not m:
        return None
        
    try:
        return float(m.group(1))
    except Exception:
        return None


def get_dashboard_charts_data_local():
    """
    ✅ 기존 get_dashboard_charts_data() 내부에서 t.data_type을 참조하는 쿼리 때문에
       'column t.data_type does not exist' 에러 발생.
    ✅ 아래는 현재 스키마(스크린샷 기준 tasks: requirement, data_tag, target_hour 등)에 맞춰
       'data_type'을 전혀 사용하지 않는 로컬 버전으로 대체.
    """

    # --- Gantt (프로젝트 스케줄) ---
    # Start/Finish는 projects의 start_date/end_date 기반.
    # end_date가 없으면 start_date+7일(표시용)로 보정.
    gantt_query = """
        SELECT
            p.project_name AS "Task",
            COALESCE(p.start_date, p.created_at, CURRENT_DATE) AS "Start",
            COALESCE(p.end_date,
                     (COALESCE(p.start_date, p.created_at, CURRENT_DATE) + INTERVAL '7 days')) AS "Finish"
        FROM projects p
        WHERE p.project_name IS NOT NULL
        ORDER BY COALESCE(p.end_date, p.start_date, p.created_at, CURRENT_DATE) DESC;
    """
    gantt_rows = run_query(gantt_query) or []
    df_gantt = pd.DataFrame(gantt_rows, columns=["Task", "Start", "Finish"]) if gantt_rows else pd.DataFrame(
        columns=["Task", "Start", "Finish"]
    )

    # --- Progress (수집 시간 합) ---
    progress_query = """
        SELECT
            p.project_name,
            COALESCE(SUM(CAST(sl.duration AS NUMERIC)), 0) / 3600.0 AS collected_hours
        FROM projects p
        LEFT JOIN tasks t ON p.project_id = t.project_id
        LEFT JOIN subtasks s ON t.task_id = s.task_id
        LEFT JOIN subtask_logs sl ON s.subtask_id = sl.subtask_id
        GROUP BY p.project_id, p.project_name
        ORDER BY collected_hours DESC;
    """
    prog_rows = run_query(progress_query) or []
    df_progress = pd.DataFrame(prog_rows, columns=["project_name", "collected_hours"]) if prog_rows else pd.DataFrame(
        columns=["project_name", "collected_hours"]
    )

    # primitive는 기존 코드 인터페이스 유지용 (미사용)
    df_primitive = pd.DataFrame()

    return df_gantt, df_progress, df_primitive


def get_project_avg_seconds_map() -> dict[str, float]:
    """
    subtasks.instruction에서 Avg(xx s)를 뽑아서 프로젝트 단위로 평균(또는 대표값) 만들기.
    - 프로젝트에 여러 subtasks가 있으면 Avg seconds의 평균값 사용.
    """
    avg_query = """
        SELECT
            p.project_name,
            s.instruction
        FROM projects p
        JOIN tasks t ON p.project_id = t.project_id
        JOIN subtasks s ON t.task_id = s.task_id
        WHERE s.instruction IS NOT NULL
          AND s.instruction ILIKE '%Avg(%';
    """
    rows = run_query(avg_query) or []

    acc: dict[str, list[float]] = {}
    for project_name, instruction in rows:
        sec = _extract_avg_seconds(instruction)
        if sec is None:
            continue
        key = str(project_name) if project_name else "Unknown"
        acc.setdefault(key, []).append(sec)

    # 프로젝트별 평균
    out: dict[str, float] = {}
    for k, secs in acc.items():
        if secs:
            out[k] = float(sum(secs) / len(secs))
    return out


# =========================================================
# Main UI
# =========================================================
def render_total_statistics():
    title_icon_base64 = get_local_image_as_base64(
        "/home/roastb/data_div/dev_ws/tomo_dashboard/TDD/img/Tommoro Icon.png"
    )
    if "cdn-icons" in title_icon_base64:
        title_icon_base64 = "https://cdn-icons-png.flaticon.com/512/2042/2042462.png"

    title_html = f"""
        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 5px;">
            <img src="{title_icon_base64}" style="width: 48px; height: 48px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.5);">
            <h1 style="font-size: 45px; font-weight: 900; margin: 0; color: #F8FAFC;">Tommoro Robotics Dashboard</h1>
        </div>
    """
    st.markdown(title_html, unsafe_allow_html=True)
    st.caption(
        f"<span style='color: #94A3B8;'>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] { background-color: #0A0F1D !important; }
        [data-testid="stHeader"] { background-color: transparent !important; }
        [data-testid="stVerticalBlockBorderWrapper"] {
            padding: 1.5rem;
            border-color: rgba(255, 255, 255, 0.05) !important;
            border-radius: 12px;
            background-color: #111827;
            border-width: 1px !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        h1.section-title {
            font-size: 30px !important;
            padding: 5px 0px 15px 15px !important;
            margin-top: 0px !important;
            font-weight: 900 !important;
            color: #F1F5F9 !important;
            border-left: 4px solid #00E5FF !important;
            margin-bottom: 15px !important;
        }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: rgba(0,0,0,0.2); }
        ::-webkit-scrollbar-thumb { background: #3B82F6; border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: #00E5FF; }
        </style>
    """,
        unsafe_allow_html=True,
    )

    premium_palette = [
        "#00E5FF", "#3B82F6", "#8B5CF6", "#10B981", "#6366F1",
        "#0EA5E9", "#14B8A6", "#64748B", "#818CF8", "#2DD4BF",
    ]

    mosaic_cool_palette = [
        "#00E5FF", "#3B82F6", "#8B5CF6", "#10B981", "#6366F1",
        "#0EA5E9", "#14B8A6", "#64748B", "#818CF8", "#2DD4BF",
        "#00BFFF", "#4169E1", "#7B68EE", "#20B2AA", "#5F9EA0",
        "#4682B4", "#87CEEB", "#9370DB", "#00CED1", "#1E90FF",
    ]

    try:
        top_col1, top_col2 = st.columns([3.5, 6.5], gap="medium")

        # =========================================================
        # 🟩 [그룹 1] 왼쪽 상단: 데이터 수집 현황 + Cell 현황판
        # =========================================================
        with top_col1:
            with st.container(border=True, height=1350):
                st.markdown("<h1 class='section-title'>데이터 수집 현황</h1>", unsafe_allow_html=True)

                list_query = """
                    SELECT
                        p.project_name, p.status, p.start_date, p.end_date, p.target_hour,
                        COALESCE(SUM(CAST(sl.duration AS NUMERIC)), 0) / 3600.0 as current_hours
                    FROM projects p
                    LEFT JOIN tasks t ON p.project_id = t.project_id
                    LEFT JOIN subtasks s ON t.task_id = s.task_id
                    LEFT JOIN subtask_logs sl ON s.subtask_id = sl.subtask_id
                    GROUP BY p.project_id, p.project_name, p.status, p.start_date, p.end_date, p.target_hour
                    ORDER BY p.start_date ASC NULLS LAST;
                """
                rows = run_query(list_query)

                ready_list, doing_list, done_list = [], [], []
                now = pd.Timestamp.now()

                if rows:
                    for row in rows:
                        p_name, p_status, p_start, p_end, p_target, p_current = row
                        status_lower = str(p_status).strip().lower() if p_status else ""

                        if status_lower == "done":
                            if p_end:
                                try:
                                    end_dt = pd.to_datetime(p_end)
                                    if end_dt.year == now.year and end_dt.month == now.month:
                                        done_list.append(row)
                                except Exception:
                                    pass
                        else:
                            is_future = False
                            if p_start:
                                try:
                                    start_dt = pd.to_datetime(p_start)
                                    if start_dt > now:
                                        is_future = True
                                except Exception:
                                    pass

                            if status_lower in ["in progress", "active"] and not is_future:
                                doing_list.append(row)
                            else:
                                ready_list.append(row)

                board_col1, board_col2, board_col3 = st.columns(3)

                def render_board_card(row, theme_color):
                    p_name, p_status, p_start, p_end, p_target, p_current = row
                    safe_target = float(p_target) if p_target else 0.0
                    safe_current = float(p_current) if p_current else 0.0
                    progress = min(
                        (safe_current / safe_target * 100) if safe_target > 0 else 0.0,
                        100.0,
                    )
                    
                    if p_end:
                        try:
                            end_str = pd.to_datetime(p_end).strftime("%y.%m.%d")
                        except Exception:
                            end_str = str(p_end).split()[0]
                    else:
                        end_str = "-"

                    css_pie = f"""
                        <div style="width: 65px; height: 65px; border-radius: 50%; background: conic-gradient({theme_color} {progress}%, rgba(255,255,255,0.05) 0); display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                            <div style="width: 50px; height: 50px; border-radius: 50%; background: #1E293B; display: flex; align-items: center; justify-content: center; font-size: 15px; font-weight: 900; color: white;">
                                {int(progress)}%
                            </div>
                        </div>
                    """

                    html_content = f"""
                        <div style="background-color: #1E293B; border: 1px solid rgba(255,255,255,0.05); border-left: 6px solid {theme_color}; border-radius: 10px; padding: 20px 15px; margin-bottom: 20px; box-shadow: 0 6px 10px rgba(0,0,0,0.3);">
                            <div style="font-size: 30px; font-weight: 900; color: #F8FAFC; margin-bottom: 15px; text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{p_name}</div>
                            <div style="display: flex; justify-content: space-between; align-items: stretch; width: 100%; background: #0F172A; border-radius: 8px; padding: 12px 8px; border: 1px solid rgba(255,255,255,0.02);">
                                <div style="flex: 1; text-align: center; border-right: 1px solid rgba(255,255,255,0.05); display: flex; flex-direction: column; justify-content: center;">
                                    <div style="font-size: 25px; color: #94A3B8; font-weight: bold; margin-bottom: 4px;">마감</div>
                                    <div style="font-size: 25px; font-weight: 900; color: #E2E8F0;">{end_str}</div>
                                </div>
                                <div style="flex: 1; text-align: center; border-right: 1px solid rgba(255,255,255,0.05); display: flex; flex-direction: column; justify-content: center;">
                                    <div style="font-size: 25px; color: #94A3B8; font-weight: bold; margin-bottom: 4px;">목표</div>
                                    <div style="font-size: 25px; font-weight: 900; color: #CBD5E1;">{safe_target}h</div>
                                </div>
                                <div style="flex: 1.5; display: flex; align-items: center; justify-content: flex-end; gap: 12px; padding-right: 8px;">
                                    <div style="text-align: right;">
                                        <div style="font-size: 25px; color: #94A3B8; font-weight: bold; margin-bottom: 4px;">현재</div>
                                        <div style="font-size: 25px; font-weight: 900; color: {theme_color};">{safe_current:.1f}h</div>
                                    </div>
                                    {css_pie}
                                </div>
                            </div>
                        </div>
                    """
                    return html_content.replace("\n", "")

                with board_col1:
                    st.markdown(
                        "<h3 style='text-align: center; color: #3B82F6; font-size: 24px; font-weight: 900; margin-bottom: 15px;'>수집 예정</h3>",
                        unsafe_allow_html=True,
                    )
                    with st.container(height=500, border=False):
                        if not ready_list:
                            st.markdown(
                                "<div style='text-align:center; color:#334155; padding: 20px; font-size: 18px;'>NO DATA</div>",
                                unsafe_allow_html=True,
                            )
                        for r in ready_list:
                            st.markdown(render_board_card(r, "#3B82F6"), unsafe_allow_html=True)

                with board_col2:
                    st.markdown(
                        "<h3 style='text-align: center; color: #00E5FF; font-size: 24px; font-weight: 900; margin-bottom: 15px;'>수집 중</h3>",
                        unsafe_allow_html=True,
                    )
                    with st.container(height=500, border=False):
                        if not doing_list:
                            st.markdown(
                                "<div style='text-align:center; color:#334155; padding: 20px; font-size: 18px;'>NO DATA</div>",
                                unsafe_allow_html=True,
                            )
                        for r in doing_list:
                            st.markdown(render_board_card(r, "#00E5FF"), unsafe_allow_html=True)

                with board_col3:
                    st.markdown(
                        "<h3 style='text-align: center; color: #8B5CF6; font-size: 24px; font-weight: 900; margin-bottom: 15px;'>수집 완료 (이번 달)</h3>",
                        unsafe_allow_html=True,
                    )
                    with st.container(height=500, border=False):
                        if not done_list:
                            st.markdown(
                                "<div style='text-align:center; color:#334155; padding: 20px; font-size: 18px;'>NO DATA</div>",
                                unsafe_allow_html=True,
                            )
                        for r in done_list:
                            st.markdown(render_board_card(r, "#8B5CF6"), unsafe_allow_html=True)

                st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

                # =========================================================
                # 각 Cell 별 수집 현황판 (독립된 5:5 하단 영역)
                # =========================================================
                st.markdown("<h1 class='section-title'>Robot Lab 현황</h1>", unsafe_allow_html=True)

                cell_query = """
                    SELECT cell_number, project_name, project_manager, end_date
                    FROM projects
                    WHERE status IN ('In Progress', 'Active') AND cell_number IS NOT NULL;
                """
                cell_data = run_query(cell_query)
                active_cells = {}
                if cell_data:
                    for r in cell_data:
                        c_num = str(r[0]).strip().capitalize()
                        if not c_num.startswith("Cell"):
                            c_num = f"Cell {c_num}"
                        active_cells[c_num] = {
                            "name": r[1] or "알 수 없는 태스크",
                            "manager": r[2] or "미배정",
                            "end_date": str(r[3]).split()[0] if r[3] else "미정",
                        }

                def get_cell_html(cell_num):
                    c_name = f"Cell {cell_num}"
                    if c_name in active_cells:
                        bg_color, border_color = "rgba(0, 229, 255, 0.1)", "#00E5FF"
                        badge = "수집중"
                        p_name, manager, end_dt = (
                            active_cells[c_name]["name"],
                            active_cells[c_name]["manager"],
                            active_cells[c_name]["end_date"],
                        )
                    elif cell_num == 1:
                        bg_color, border_color = "rgba(59, 130, 246, 0.1)", "#3B82F6"
                        badge = "대기중"
                        p_name, manager, end_dt = "Amore toner sy", "이소영", "2026-02-24"
                    elif cell_num == 3:
                        bg_color, border_color = "rgba(244, 63, 94, 0.1)", "#F43F5E"
                        badge = "고장/수리"
                        p_name, manager, end_dt = "장비 점검 및 수리", "엔지니어팀", "ASAP"
                    else:
                        bg_color, border_color = "rgba(71, 85, 105, 0.1)", "#475569"
                        badge = "미할당"
                        p_name, manager, end_dt = "할당된 태스크 없음", "-", "-"

                    if end_dt and end_dt not in ["-", "ASAP", "미정"]:
                        try:
                            end_dt = pd.to_datetime(end_dt).strftime("%y.%m.%d")
                        except Exception:
                            if isinstance(end_dt, str) and len(end_dt) >= 10:
                                end_dt = end_dt[2:10].replace("-", ".")

                    return f"""
                        <div style="background-color: {bg_color}; border: 1px solid {border_color}; border-radius: 12px; padding: 20px 20px; min-height: 240px; display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
                            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 12px; margin-bottom: 15px;">
                                <strong style="font-size: 45px; font-weight: 900; color: #F8FAFC; line-height: 1;">{c_name}</strong>
                                <span style="color: {border_color}; font-size: 40px; font-weight: 900; line-height: 1;">{badge}</span>
                            </div>
                            <div style="flex: 1; display: flex; flex-direction: column; justify-content: center; gap: 10px; padding: 0 5px;">
                                <div style="font-size: 28px; font-weight: bold; color: #E2E8F0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.1;">● {p_name}</div>
                                <div style="font-size: 28px; color: #E2E8F0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.1;">● {manager}</div>
                                <div style="font-size: 28px; font-weight: bold; color: #E2E8F0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.1;">● {end_dt}</div>
                            </div>
                        </div>
                    """

                floor_plan_html = f"""
                    <div style="background-color: #0B132B; border-radius: 12px; padding: 20px; border: 1px solid rgba(255,255,255,0.05);">
                        <div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 20px;">
                            <div style="min-width: 0;">{get_cell_html(1)}</div>
                            <div style="min-width: 0;">{get_cell_html(2)}</div>
                            <div style="min-width: 0;">{get_cell_html(3)}</div>
                            
                            <div style="min-width: 0;">{get_cell_html(4)}</div>
                            <div style="min-width: 0;">{get_cell_html(5)}</div>
                            <div style="min-width: 0;">{get_cell_html(6)}</div>
                        </div>
                    </div>
                """
                st.markdown(floor_plan_html.replace("\n", ""), unsafe_allow_html=True)

        # =========================================================
        # 🟦 [그룹 2] 오른쪽 상단: 간트 + (모자이크 줌인/줌아웃 + Avg 기반 Sin)
        # =========================================================
        with top_col2:
            with st.container(border=True, height=1350):
                header_col1, header_col2 = st.columns([0.45, 0.55])
                with header_col1:
                    st.markdown("<h1 class='section-title'>데이터 팀 수집 일정</h1>", unsafe_allow_html=True)
                with header_col2:
                    view_mode = st.radio(
                        "View Mode",
                        ["1달 단위", "전체 기간"],
                        horizontal=True,
                        label_visibility="collapsed",
                    )

                df_gantt, df_progress, df_primitive = get_dashboard_charts_data_local()

                if not df_gantt.empty:
                    df_gantt["Start"] = pd.to_datetime(df_gantt["Start"], errors="coerce")
                    df_gantt["Finish"] = pd.to_datetime(df_gantt["Finish"], errors="coerce")
                    df_gantt = df_gantt.dropna(subset=["Start", "Finish"])

                    today_dt = pd.Timestamp.now().normalize()
                    if view_mode == "1달 단위":
                        min_date = today_dt.replace(day=1)
                        max_date = min_date + pd.offsets.MonthEnd(1) + pd.Timedelta(days=1)
                        mask = (df_gantt["Start"] <= max_date) & (df_gantt["Finish"] >= min_date)
                        df_gantt = df_gantt[mask]

                    df_gantt = df_gantt.sort_values(by="Finish", ascending=False)
                    inner_chart_height = max(250, len(df_gantt) * 60)
                    df_gantt["Task_Bold"] = df_gantt["Task"].apply(lambda x: f"<b>{x}</b>")

                    fig_gantt = px.timeline(df_gantt, x_start="Start", x_end="Finish", y="Task_Bold", hover_name="Task")
                    fig_gantt.update_yaxes(autorange="reversed")
                    fig_gantt.update_traces(
                        marker_color="#00E5FF",
                        marker_line_color="#0A0F1D",
                        marker_line_width=1,
                        marker_cornerradius=8,
                        opacity=0.9,
                    )

                    fig_gantt.update_layout(
                        height=inner_chart_height,
                        bargap=0.5,
                        margin=dict(l=0, r=0, t=10, b=0),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#94A3B8", size=18),
                        yaxis_title=None,
                        xaxis_title=None,
                    )
                    fig_gantt.update_xaxes(
                        tickformat="%m월 %d일",
                        showgrid=True,
                        gridwidth=1,
                        gridcolor="rgba(255, 255, 255, 0.05)",
                        griddash="dot",
                        tickfont=dict(size=18, color="#94A3B8", family="Arial Black, sans-serif"),
                    )
                    fig_gantt.update_yaxes(tickfont=dict(size=20, color="#F8FAFC", weight="bold"))

                    today_str = datetime.now().strftime("%Y-%m-%d")
                    fig_gantt.add_shape(
                        type="line",
                        x0=today_str,
                        x1=today_str,
                        y0=0,
                        y1=1,
                        yref="paper",
                        line=dict(color="#F43F5E", width=3, dash="dash"),
                    )
                    fig_gantt.add_annotation(
                        x=today_str,
                        y=0,
                        yref="paper",
                        text="<b>오늘</b>",
                        showarrow=False,
                        font=dict(color="#F43F5E", size=16),
                        xanchor="center",
                        yanchor="top",
                        yshift=-10,
                    )

                    if view_mode == "1달 단위" and "min_date" in locals():
                        fig_gantt.update_xaxes(range=[min_date, max_date])

                    with st.container(border=False):
                        st.plotly_chart(fig_gantt, width='stretch')

                st.divider()

                c_pie1, c_pie2 = st.columns([0.5, 0.5])

                # =========================================================
                # ✅ TDD 3.0: [프로젝트 수집 진행률 (상세 분석)]
                # =========================================================
                with c_pie1:
                    total_h = 0.0
                    if not df_progress.empty:
                        df_progress["collected_hours"] = pd.to_numeric(df_progress["collected_hours"], errors="coerce").fillna(0.0)
                        df_progress = df_progress[df_progress["collected_hours"] > 0]
                        total_h = df_progress["collected_hours"].sum()

                    header_html = f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; margin-top: 0px;">
                        <h1 class='section-title' style='margin-bottom: 0 !important;'>프로젝트 수집 진행률 (상세 분석)</h1>
                        <div style="background-color: rgba(255,255,255,0.08); padding: 8px 25px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.2);">
                            <span style="font-size: 26px; font-weight: 900; color: #FFFFFF; letter-spacing: 1px;">Total: {total_h:.1f}h</span>
                        </div>
                    </div>
                    """
                    st.markdown(header_html, unsafe_allow_html=True)

                    if not df_progress.empty:
                        df_progress = df_progress.sort_values(by="collected_hours", ascending=False)
                        proj_avg_sec_map = get_project_avg_seconds_map()

                        tile_payload = []
                        for _, row in df_progress.iterrows():
                            pname = row["project_name"]
                            hrs = float(row["collected_hours"])
                            avg_sec = proj_avg_sec_map.get(str(pname))
                            tile_payload.append({"name": pname, "value": hrs, "avgSec": avg_sec})

                        json_data = json.dumps(tile_payload, ensure_ascii=False)
                        json_colors = json.dumps(mosaic_cool_palette)

                        custom_treemap_html = f"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <script src="https://d3js.org/d3.v7.min.js"></script>
                            <style>
                                body {{ margin: 0; background: transparent; font-family: 'Arial', sans-serif; overflow: hidden; color: white; }}
                                #treemap-container {{ position: relative; width: 100%; height: 820px; }}

                                .tile {{
                                    position: absolute;
                                    border: 2px solid #0A0F1D;
                                    box-sizing: border-box;
                                    overflow: hidden;
                                    transition: all 2s cubic-bezier(0.25, 0.8, 0.25, 1);
                                    border-radius: 6px;
                                    cursor: pointer;
                                    box-shadow: inset 0 0 10px rgba(0,0,0,0.3);
                                }}

                                .tile.zoomed {{
                                    left: 0 !important;
                                    top: 0 !important;
                                    width: 100% !important;
                                    height: 100% !important;
                                    z-index: 100;
                                    border-radius: 12px;
                                    box-shadow: 0 0 40px rgba(0,229,255,0.6);
                                }}

                                .tile-content {{
                                    position: absolute;
                                    top: 15px; left: 15px;
                                    pointer-events: none;
                                    z-index: 10;
                                    display: flex;
                                    flex-direction: column;
                                    gap: 5px;
                                    transition: all 1s;
                                }}
                                .tile.zoomed .tile-content {{
                                    top: 75px; left: 75px;
                                    gap: 15px;
                                }}

                                .tile-name {{
                                    font-size: 20px;
                                    font-weight: bold;
                                    color: #FFFFFF !important;
                                    text-shadow: 0 2px 5px rgba(0,0,0,0.9);
                                    transition: font-size 1s;
                                    line-height: 1.1;
                                }}
                                .tile.zoomed .tile-name {{
                                    font-size: 95px;
                                }}

                                .tile-hours {{
                                    font-size: 16px;
                                    font-weight: bold;
                                    color: #FFFFFF !important;
                                    text-shadow: 0 2px 5px rgba(0,0,0,0.9);
                                    transition: font-size 1s;
                                    line-height: 1.1;
                                }}
                                .tile.zoomed .tile-hours {{
                                    font-size: 75px;
                                }}

                                .tile-avg {{
                                    font-size: 16px;
                                    font-weight: bold;
                                    color: #FFFFFF !important;
                                    text-shadow: 0 2px 5px rgba(0,0,0,0.9);
                                    opacity: 0;
                                    transition: opacity 1s, font-size 1s;
                                    line-height: 1.1;
                                    margin-top: 5px;
                                }}
                                .tile.zoomed .tile-avg {{
                                    font-size: 75px;
                                    opacity: 1;
                                    margin-top: 30px;
                                }}

                                .sine-canvas {{
                                    position: absolute;
                                    bottom: 0; left: 0;
                                    width: 100%; height: 100%;
                                    opacity: 0;
                                    transition: opacity 2s;
                                    pointer-events: none;
                                }}

                                .tile.zoomed .sine-canvas {{
                                    opacity: 1;
                                }}
                            </style>
                        </head>
                        <body>
                            <div id="treemap-container"></div>

                            <script>
                                const rawData = {json_data};
                                const colors = {json_colors};
                                const data = {{ name: "root", children: rawData }};

                                const root = d3.hierarchy(data)
                                    .sum(d => d.value)
                                    .sort((a, b) => b.value - a.value);

                                d3.treemap()
                                    .size([100, 100])
                                    .paddingInner(0)(root);

                                const container = document.getElementById('treemap-container');
                                const nodes = root.leaves();

                                let animFrame = null;
                                let activeIndex = null;
                                let cycleIndex = 0;
                                let isAutoPlaying = true;

                                const sleep = (ms) => new Promise(r => setTimeout(r, ms));

                                function clamp(v, lo, hi) {{
                                    return Math.max(lo, Math.min(hi, v));
                                }}

                                function stopSine() {{
                                    if (animFrame) {{
                                        cancelAnimationFrame(animFrame);
                                        animFrame = null;
                                    }}
                                }}

                                function mapAvgToWave(avgSec) {{
                                    if (!isFinite(avgSec) || avgSec <= 0) {{
                                        return {{ freq: 0.02, amp: 55, speed: 0.05 }};
                                    }}
                                    const norm = clamp((avgSec - 30) / (180 - 30), 0, 1);
                                    const amp = 25 + norm * 95;
                                    const freq = 0.035 - norm * 0.02;
                                    const speed = 0.035 + (1 - norm) * 0.05;
                                    return {{ freq, amp, speed }};
                                }}

                                function drawSine(canvas, wave) {{
                                    const ctx = canvas.getContext('2d');
                                    let t = 0;

                                    function render() {{
                                        canvas.width = canvas.clientWidth;
                                        canvas.height = canvas.clientHeight;
                                        ctx.clearRect(0, 0, canvas.width, canvas.height);

                                        ctx.beginPath();
                                        ctx.strokeStyle = 'rgba(255,255,255,0.45)';
                                        ctx.lineWidth = 5;

                                        const mid = canvas.height * 0.62;
                                        for (let x = 0; x < canvas.width; x++) {{
                                            const y = mid + Math.sin(x * wave.freq + t) * wave.amp;
                                            if (x === 0) ctx.moveTo(x, y);
                                            else ctx.lineTo(x, y);
                                        }}
                                        ctx.stroke();

                                        ctx.beginPath();
                                        ctx.strokeStyle = 'rgba(255,255,255,0.12)';
                                        ctx.lineWidth = 2;
                                        ctx.moveTo(0, mid);
                                        ctx.lineTo(canvas.width, mid);
                                        ctx.stroke();

                                        t += wave.speed;
                                        animFrame = requestAnimationFrame(render);
                                    }}

                                    render();
                                }}

                                function deactivateAll() {{
                                    const tiles = document.querySelectorAll('.tile');
                                    tiles.forEach(t => t.classList.remove('zoomed'));
                                    stopSine();
                                    activeIndex = null;
                                }}

                                function activateTile(index) {{
                                    deactivateAll();

                                    const tiles = document.querySelectorAll('.tile');
                                    activeIndex = index;

                                    const activeTile = tiles[activeIndex];
                                    activeTile.classList.add('zoomed');

                                    const canvas = activeTile.querySelector('canvas');
                                    const avgSec = parseFloat(activeTile.dataset.avgsec || '0');
                                    const wave = mapAvgToWave(avgSec);
                                    drawSine(canvas, wave);
                                }}

                                nodes.forEach((d, i) => {{
                                    const div = document.createElement('div');
                                    div.className = 'tile';
                                    div.style.left = d.x0 + '%';
                                    div.style.top = d.y0 + '%';
                                    div.style.width = (d.x1 - d.x0) + '%';
                                    div.style.height = (d.y1 - d.y0) + '%';
                                    div.style.backgroundColor = colors[i % colors.length];

                                    const avgSec = d.data.avgSec;
                                    if (avgSec !== null && avgSec !== undefined) {{
                                        div.dataset.avgsec = String(avgSec);
                                    }} else {{
                                        div.dataset.avgsec = '';
                                    }}

                                    const avgLabel = (avgSec !== null && avgSec !== undefined) ? `${{avgSec.toFixed(0)}}s` : 'N/A';
                                    
                                    const content = document.createElement('div');
                                    content.className = 'tile-content';
                                    content.innerHTML = `
                                        <div class="tile-name">${{d.data.name}}</div>
                                        <div class="tile-hours">${{d.data.value.toFixed(1)}}h</div>
                                        <div class="tile-avg">Avg Time: ${{avgLabel}}</div>
                                    `;
                                    div.appendChild(content);

                                    const canvas = document.createElement('canvas');
                                    canvas.className = 'sine-canvas';
                                    div.appendChild(canvas);

                                    div.onclick = () => {{
                                        isAutoPlaying = false;
                                        if (activeIndex === i) {{
                                            deactivateAll();
                                        }} else {{
                                            activateTile(i);
                                        }}
                                    }};

                                    container.appendChild(div);
                                }});

                                async function runAutoCycle() {{
                                    await sleep(5000);

                                    while (isAutoPlaying && nodes.length > 0) {{
                                        activateTile(cycleIndex);
                                        await sleep(2000);
                                        if (!isAutoPlaying) break;

                                        await sleep(3000);
                                        if (!isAutoPlaying) break;

                                        deactivateAll();
                                        await sleep(2000);
                                        if (!isAutoPlaying) break;

                                        await sleep(5000);
                                        if (!isAutoPlaying) break;

                                        cycleIndex = (cycleIndex + 1) % nodes.length;
                                    }}
                                }}

                                runAutoCycle();
                            </script>
                        </body>
                        </html>
                        """
                        components.html(custom_treemap_html, height=820)
                    else:
                        st.info("수집 데이터가 없습니다. (subtask_logs에 duration이 0보다 큰 데이터가 존재해야 합니다)")

                # =========================================================
                # 오른쪽: 트렌드 차트
                # =========================================================
                with c_pie2:
                    st.markdown("<h1 class='section-title'>데이터 품질 등급</h1>", unsafe_allow_html=True)
                    trend_query = """
                        SELECT
                            p.project_name,
                            COALESCE(p.end_date, p.start_date, p.created_at, CURRENT_DATE) as seq_date,
                            COALESCE(SUM(CAST(sl.duration AS NUMERIC)), 0) / 3600.0 as hours
                        FROM projects p
                        LEFT JOIN tasks t ON p.project_id = t.project_id
                        LEFT JOIN subtasks s ON t.task_id = s.task_id
                        LEFT JOIN subtask_logs sl ON s.subtask_id = sl.subtask_id
                        GROUP BY p.project_id, p.project_name, COALESCE(p.end_date, p.start_date, p.created_at, CURRENT_DATE)
                        HAVING COALESCE(SUM(CAST(sl.duration AS NUMERIC)), 0) > 0
                        ORDER BY COALESCE(p.end_date, p.start_date, p.created_at, CURRENT_DATE) ASC;
                    """
                    trend_data = run_query(trend_query)

                    if trend_data:
                        df_trend = pd.DataFrame(trend_data, columns=["Project", "Date", "Hours"])
                        df_trend["Hours"] = pd.to_numeric(df_trend["Hours"], errors="coerce").fillna(0)

                        def get_grade_score(h):
                            if h >= 6:
                                return 6, "A"
                            elif h >= 5:
                                return 5, "B"
                            elif h >= 4:
                                return 4, "C"
                            elif h >= 3:
                                return 3, "D"
                            elif h >= 2:
                                return 2, "E"
                            else:
                                return 1, "F"

                        df_trend[["Score", "Grade"]] = df_trend["Hours"].apply(lambda x: pd.Series(get_grade_score(x)))

                        fig_trend = go.Figure()
                        
                        fig_trend.add_hline(
                            y=3.5,
                            line_width=3,
                            line_dash="solid",
                            line_color="rgba(255, 255, 255, 0.85)", 
                            annotation_text="기준선 (4h)",
                            annotation_position="bottom right",
                            annotation_font=dict(color="rgba(255, 255, 255, 1.0)", size=16, weight="bold"),
                        )

                        fig_trend.add_trace(
                            go.Scatter(
                                x=df_trend["Project"],
                                y=df_trend["Score"],
                                mode="lines+markers",
                                line=dict(shape="spline", color="rgba(0, 229, 255, 0.4)", width=5),
                                marker=dict(
                                    size=20,
                                    color=df_trend["Score"],
                                    colorscale=[
                                        [0, "#F43F5E"],
                                        [0.4, "#D946EF"],
                                        [0.5, "#8B5CF6"],
                                        [0.6, "#3B82F6"],
                                        [0.8, "#0EA5E9"],
                                        [1.0, "#00E5FF"],
                                    ],
                                    line=dict(width=3, color="#111827"),
                                    showscale=False,
                                ),
                                customdata=df_trend[["Grade", "Hours"]],
                                hovertemplate="<b>%{x}</b><br>등급: %{customdata[0]}<br>수집량: %{customdata[1]:.1f}h<extra></extra>",
                            )
                        )

                        fig_trend.update_layout(
                            height=820,
                            showlegend=False,
                            margin=dict(t=10, b=20, l=10, r=10),
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            xaxis=dict(
                                title="시간 순서 (프로젝트 진행순)",
                                title_font=dict(size=16, color="#64748B"),
                                tickfont=dict(size=14, color="#94A3B8"),
                                showline=True,
                                linecolor="rgba(255,255,255,0.1)",
                                linewidth=2,
                                showgrid=False,
                                tickangle=-30,
                            ),
                            yaxis=dict(
                                title="품질 등급",
                                title_font=dict(size=16, color="#64748B"),
                                tickfont=dict(size=20, color="#F8FAFC", weight="bold"),
                                tickmode="array",
                                tickvals=[1, 2, 3, 4, 5, 6],
                                ticktext=["F (<2h)", "E (2~3h)", "D (3~4h)", "C (4~5h)", "B (5~6h)", "A (6h+)"],
                                showgrid=True,
                                gridcolor="rgba(255,255,255,0.05)",
                                zeroline=False,
                                showline=True, 
                                linecolor="rgba(255,255,255,0.4)", 
                                linewidth=2,
                                range=[0.5, 6.5],
                            ),
                        )
                        st.plotly_chart(fig_trend, width='stretch')
                    else:
                        st.info("시계열 데이터가 없습니다.")

        st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)

        # =========================================================
        # 🟪 [그룹 3] 하단 영역 - 3 : 4 : 3 비율
        # =========================================================
        bot_col1, bot_col2, bot_col3 = st.columns([3, 4, 3], gap="large")

        with bot_col1:
            # ✅ 높이 400으로 20% 축소 적용
            with st.container(border=True, height=400):
                st.markdown("<h1 class='section-title'>로봇 상태</h1>", unsafe_allow_html=True)
                
                robot_query = """
                    SELECT
                        r.model_name,
                        r.status,
                        COALESCE(
                            (
                                SELECT p.cell_number
                                FROM subtask_logs sl
                                JOIN subtasks s ON sl.subtask_id = s.subtask_id
                                JOIN tasks t ON s.task_id = t.task_id
                                JOIN projects p ON t.project_id = p.project_id
                                WHERE sl.robot_id = r.robot_id
                                ORDER BY s.subtask_date DESC, sl.subtask_log_id DESC
                                LIMIT 1
                            ),
                            '대기중'
                        ) as current_cell
                    FROM robots r
                    ORDER BY r.robot_id ASC;
                """
                robot_data = run_query(robot_query)
                robot_images = {
                    "RB-Y1": get_local_image_as_base64("tomo_dashboard/TDD/img/RAINBOW_rby1.png"),
                    "AI-Worker": get_local_image_as_base64("tomo_dashboard/TDD/img/ROBOTIS_aiworker.png"),
                    "ROBROS": get_local_image_as_base64("tomo_dashboard/TDD/img/ROBROS_igris.png"),
                }
                default_robot_img = "https://cdn-icons-png.flaticon.com/512/2042/2042462.png"

                if not robot_data:
                    st.info("장비 없음")
                else:
                    for row in robot_data:
                        r_name, r_status_str, r_cell_val = (
                            row[0],
                            str(row[1]).strip().lower() if row[1] else "ready",
                            str(row[2]).strip() if row[2] else "",
                        )

                        if r_status_str == "active":
                            border_color, bg_color, display_status = "#00E5FF", "rgba(0, 229, 255, 0.1)", "Active"
                        elif r_status_str == "error":
                            border_color, bg_color, display_status = "#F43F5E", "rgba(244, 63, 94, 0.1)", "Error"
                        elif r_status_str == "attention":
                            border_color, bg_color, display_status = "#F59E0B", "rgba(245, 158, 11, 0.1)", "Attention"
                        else:
                            border_color, bg_color, display_status = "#3B82F6", "rgba(59, 130, 246, 0.1)", "Ready"

                        if not r_cell_val or r_cell_val.lower() == 'none' or r_cell_val == '대기중':
                            display_location = '대기중'
                        else:
                            if not r_cell_val.lower().startswith('cell'):
                                display_location = f"Cell {r_cell_val}"
                            else:
                                display_location = r_cell_val.capitalize()

                        current_robot_img = robot_images.get(r_name, default_robot_img)

                        # ✅ 공간 최적화를 위해 로봇 이미지 및 폰트 사이즈 비율 조절 (글자는 50% 이상 유지)
                        html_str = f"""
                            <div style="border: 1px solid {border_color}; border-radius: 12px; padding: 12px 20px; margin-bottom: 12px; background-color: {bg_color}; display: flex; flex-direction: row; align-items: center; gap: 20px;">
                                <div style="width: 85px; height: 85px; flex-shrink: 0; background-color: rgba(255,255,255,0.05); border-radius: 12px; display: flex; justify-content: center; align-items: center; overflow: hidden; border: 1px solid rgba(255,255,255,0.1);">
                                    <img src="{current_robot_img}" style="width: 65px; height: 65px; object-fit: contain;">
                                </div>
                                <div style="display: flex; flex-direction: column; justify-content: center; text-align: left; width: 100%; padding-left: 10px;">
                                    <div style="margin-bottom: 5px;">
                                        <strong style="font-size: 30px; font-weight: 900; color: {border_color}; text-shadow: 0 0 10px {border_color};">{display_status}</strong>
                                    </div>
                                    <div style="font-size: 28px; color: #F8FAFC; font-weight: 900; display: flex; align-items: center; gap: 15px; white-space: nowrap;">
                                        <span>모델 : {r_name}</span>
                                        <span style="color: rgba(255,255,255,0.2);">|</span>
                                        <span>위치 : {display_location}</span>
                                    </div>
                                </div>
                            </div>
                        """
                        st.markdown(html_str.replace("\n", ""), unsafe_allow_html=True)

        with bot_col2:
            # ✅ 높이 400으로 20% 축소 적용
            with st.container(border=True, height=400):
                st.markdown("<h1 class='section-title'>QA/QC 및 라벨링 현황</h1>", unsafe_allow_html=True)
                qc_query = """
                    WITH RankedQC AS (
                        SELECT
                            COALESCE(p.project_name, 'Unknown Project') as project_name,
                            q.check_point,
                            q.is_passed,
                            q.feedback,
                            ROW_NUMBER() OVER(PARTITION BY p.project_name ORDER BY q.check_point ASC) as rn_asc,
                            ROW_NUMBER() OVER(PARTITION BY p.project_name ORDER BY q.check_point DESC) as rn_desc
                        FROM qc_status q
                        LEFT JOIN subtasks s ON q.subtask_id = s.subtask_id
                        LEFT JOIN tasks t ON s.task_id = t.task_id
                        LEFT JOIN projects p ON t.project_id = p.project_id
                    )
                    SELECT
                        project_name,
                        MAX(CASE WHEN rn_asc = 1 THEN check_point END),
                        MAX(CASE WHEN rn_asc = 2 THEN check_point END),
                        MAX(CASE WHEN rn_desc = 1 THEN CAST(is_passed AS INTEGER) END),
                        MAX(CASE WHEN rn_desc = 1 THEN feedback END)
                    FROM RankedQC
                    GROUP BY project_name
                    ORDER BY MAX(CASE WHEN rn_asc = 1 THEN check_point END) DESC;
                """
                qc_data = run_query(qc_query)

                if not qc_data:
                    st.markdown(
                        '<div style="height: 150px; display: flex; align-items: center; justify-content: center; border: 1px dashed rgba(255,255,255,0.1);"><h2 style="color: #64748B;">NO DATA</h2></div>',
                        unsafe_allow_html=True,
                    )
                else:
                    header_html = """
                        <div style="display: flex; padding: 5px 15px; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 10px;">
                            <div style="flex: 2; font-weight: bold; color: #94A3B8; font-size: 15px;">프로젝트 명</div>
                            <div style="flex: 1.5; font-weight: bold; color: #94A3B8; font-size: 15px;">1차 체크포인트</div>
                            <div style="flex: 1.5; font-weight: bold; color: #94A3B8; font-size: 15px;">2차 체크포인트</div>
                            <div style="flex: 1; font-weight: bold; color: #94A3B8; font-size: 15px;">상태</div>
                            <div style="flex: 2; font-weight: bold; color: #94A3B8; font-size: 15px;">피드백</div>
                        </div>
                    """
                    st.markdown(header_html.replace("\n", ""), unsafe_allow_html=True)
                    # ✅ 축소된 컨테이너에 맞춰 스크롤 높이 270px로 변경
                    st.markdown('<div style="height: 270px; overflow-y: auto;">', unsafe_allow_html=True)
                    for row in qc_data:
                        qc_proj_name, cp1, cp2, final_status, final_feedback = row
                        cp1_str, cp2_str = format_dt(cp1), format_dt(cp2)
                        feedback_text = final_feedback if final_feedback else "특이사항 없음"
                        status_str = str(final_status).strip().lower()

                        if status_str in ["1", "true", "t", "passed", "pass", "y", "yes"]:
                            status_color, status_text = "#00E5FF", "통과"
                        elif status_str in ["0", "false", "f", "failed", "fail", "n", "no", "needs review"]:
                            status_color, status_text = "#F43F5E", "확인 필요"
                        else:
                            status_color, status_text = "#F59E0B", "대기중"

                        row_html = f"""
                            <div style="display: flex; align-items: center; padding: 12px; border-radius: 8px; background-color: #1E293B; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.05);">
                                <div style="flex: 2; font-weight: 900; color: #F8FAFC; font-size: 16px;">{qc_proj_name}</div>
                                <div style="flex: 1.5; color: #CBD5E1; font-size: 14px; font-weight: bold;">{cp1_str}</div>
                                <div style="flex: 1.5; color: #CBD5E1; font-size: 14px; font-weight: bold;">{cp2_str}</div>
                                <div style="flex: 1; display: flex; align-items: center;">
                                    <span style="color: {status_color}; font-weight: 900; font-size: 15px;">{status_text}</span>
                                </div>
                                <div style="flex: 2; color: #94A3B8; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{feedback_text}</div>
                            </div>
                        """
                        st.markdown(row_html.replace("\n", ""), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

        with bot_col3:
            # ✅ 높이 400으로 20% 축소 적용
            with st.container(border=True, height=400):
                st.markdown("<h1 class='section-title'>태스크 유형별 포지셔닝 맵</h1>", unsafe_allow_html=True)
                map_query = """
                    SELECT p.project_name,
                           CASE
                                WHEN p.project_name ILIKE '%Picking%' THEN 1.0 + (MOD(p.project_id, 7) * 0.5)
                                WHEN p.project_name ILIKE '%Play%' THEN 2.5 + (MOD(p.project_id, 5) * 0.6)
                                ELSE 1.5 + (MOD(p.project_id, 6) * 0.4)
                           END as "Env_Score",
                           CASE
                                WHEN p.project_id = 20 THEN 8.5
                                WHEN p.project_name ILIKE '%Play%' THEN 6.0 + (MOD(p.project_id, 3) * 0.5)
                                ELSE 1.0 + (MOD(p.project_id, 8) * 0.4)
                           END as "Complexity_Score",
                           COUNT(sl.subtask_log_id) as "Count"
                    FROM projects p
                    JOIN tasks t ON p.project_id = t.project_id
                    JOIN subtasks s ON t.task_id = s.task_id
                    JOIN subtask_logs sl ON s.subtask_id = sl.subtask_id
                    GROUP BY p.project_id, p.project_name
                    HAVING COUNT(sl.subtask_log_id) > 0;
                """
                map_data = run_query(map_query)
                if map_data:
                    df_map = pd.DataFrame(map_data, columns=["Project", "Env_Score", "Complexity_Score", "Count"])
                    df_map["Env_Score"] = pd.to_numeric(df_map["Env_Score"], errors="coerce")
                    df_map["Complexity_Score"] = pd.to_numeric(df_map["Complexity_Score"], errors="coerce")
                    df_map = df_map.sort_values(by="Count", ascending=False)

                    fig_map = px.scatter(
                        df_map,
                        x="Env_Score",
                        y="Complexity_Score",
                        size="Count",
                        color="Project",
                        color_discrete_sequence=premium_palette,
                        size_max=40,
                    )
                    fig_map.update_traces(
                        marker=dict(line=dict(width=1, color="#0A0F1D")),
                        hovertemplate="<b>%{customdata[0]}</b><br>Env: %{x:.1f}<br>Comp: %{y:.1f}<extra></extra>",
                        customdata=df_map[["Project"]],
                    )
                    fig_map.add_hline(y=5, line_width=1, line_dash="dash", line_color="rgba(255,255,255,0.1)")
                    fig_map.add_vline(x=5, line_width=1, line_dash="dash", line_color="rgba(255,255,255,0.1)")

                    annotation_style = dict(color="rgba(255,255,255,0.2)", size=12, weight="bold")
                    fig_map.add_annotation(x=1.5, y=9.5, text="Structured & Contact-rich", showarrow=False, font=annotation_style)
                    fig_map.add_annotation(x=8.5, y=9.5, text="Unstructured & Contact-rich", showarrow=False, font=annotation_style)
                    fig_map.add_annotation(x=1.5, y=0.5, text="Structured & Simple", showarrow=False, font=annotation_style)
                    fig_map.add_annotation(x=8.5, y=0.5, text="Unstructured & Simple", showarrow=False, font=annotation_style)

                    axis_title_font = dict(size=14, color="#94A3B8", family="Arial Black, sans-serif", weight="bold")

                    # ✅ 축소된 컨테이너에 맞춰 차트 높이 300px로 변경
                    fig_map.update_layout(
                        height=300,
                        margin=dict(t=10, b=0, l=10, r=10),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(255,255,255,0.02)",
                        font=dict(color="#CBD5E1"),
                        showlegend=True,
                        legend=dict(
                            orientation="h",
                            yanchor="top",
                            y=-0.2,
                            xanchor="center",
                            x=0.5,
                            title=None,
                            font=dict(size=12, color="#94A3B8"),
                        ),
                        xaxis=dict(
                            title="환경 구조화 정도",
                            title_font=axis_title_font,
                            range=[0, 10],
                            showgrid=False,
                            zeroline=False,
                            showline=True,
                            linecolor="rgba(255,255,255,0.1)",
                            linewidth=1,
                            tickfont=dict(size=14),
                        ),
                        yaxis=dict(
                            title="상호작용 복잡도",
                            title_font=axis_title_font,
                            range=[0, 10],
                            showgrid=False,
                            zeroline=False,
                            showline=True,
                            linecolor="rgba(255,255,255,0.1)",
                            linewidth=1,
                            tickfont=dict(size=14),
                        ),
                    )
                    st.plotly_chart(fig_map, width="stretch", key="pos_map")

    except Exception as e:
        st.exception(e)
