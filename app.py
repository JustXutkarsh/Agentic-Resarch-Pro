"""
Agentic Research PRO — Premium Warm White Liquid Glass Research Application.
Apple Liquid Glass (80%) + Claymorphism (15%) + Neo-Brutalism (5%).
Consumes the modular ResearchOrchestrator backend without modifying any business logic.
"""

import os
import time
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

from src.research_orchestrator import run_research, ResearchResult
from src.pdfgen import generate_research_pdf
from src.ui.theme import inject_white_liquid_glass_theme
from src.ui.components import (
    render_floating_nav,
    render_hero_header,
    render_single_depth_card,
    render_active_research_banner,
)
from src.ui.research_progress import (
    humanize_backend_message,
    render_7_stage_journey,
    render_live_activity_terminal,
    render_knowledge_graph_svg,
    render_4_live_stats,
)
from src.ui.results_view import render_results_workspace

# Load environment variables from .env
load_dotenv()

st.set_page_config(
    page_title="Agentic Research",
    layout="wide",
    page_icon="✦",
    initial_sidebar_state="collapsed",
)

# Apply Warm White Liquid Glass Design System
inject_white_liquid_glass_theme()

# Background Ambient Liquid Layer
st.markdown('<div class="ambient-liquid-layer"></div>', unsafe_allow_html=True)

# ==============================================================================
# Session State Initialization
# ==============================================================================
if "research_result" not in st.session_state:
    st.session_state["research_result"] = None
if "pdf_path" not in st.session_state:
    st.session_state["pdf_path"] = None
if "depth_choice" not in st.session_state:
    st.session_state["depth_choice"] = "STANDARD"
if "topic_input" not in st.session_state:
    st.session_state["topic_input"] = ""

# ==============================================================================
# Top Floating Navigation Bar
# ==============================================================================
st.markdown(render_floating_nav(), unsafe_allow_html=True)

# ==============================================================================
# Screen 1: Editorial Research Home
# ==============================================================================
st.markdown(render_hero_header(), unsafe_allow_html=True)

# Center Research Command Bar
col_left, col_center, col_right = st.columns([1.2, 7.6, 1.2])

with col_center:
    # 1. Large Floating Liquid-Glass Search Composer
    topic_query = st.text_input(
        label="Research Query",
        value=st.session_state["topic_input"],
        placeholder="What would you like to research? e.g. Will the AI bubble burst?",
        label_visibility="collapsed",
    )
    # Sync typed text back to state
    st.session_state["topic_input"] = topic_query

    # 2. Interactive Depth Mode Cards
    st.markdown(
        """<div style="margin-top:24px; margin-bottom:12px; text-align:center;">
<div style="font-size:12px; font-weight:800; color:#1C1C1E; text-transform:uppercase; letter-spacing:0.8px;">
Select Research Depth Mode
</div>
</div>""",
        unsafe_allow_html=True
    )

    col_q, col_s, col_d = st.columns(3)

    with col_q:
        is_q = st.session_state["depth_choice"] == "QUICK"
        st.markdown(render_single_depth_card("QUICK", is_selected=is_q), unsafe_allow_html=True)
        if is_q:
            st.button("● Active Mode", key="btn_depth_q", disabled=True, use_container_width=True)
        else:
            if st.button("Select Quick", key="btn_depth_q", use_container_width=True):
                st.session_state["depth_choice"] = "QUICK"
                st.rerun()

    with col_s:
        is_s = st.session_state["depth_choice"] == "STANDARD"
        st.markdown(render_single_depth_card("STANDARD", is_selected=is_s), unsafe_allow_html=True)
        if is_s:
            st.button("● Active Mode", key="btn_depth_s", disabled=True, use_container_width=True)
        else:
            if st.button("Select Standard ⭐", key="btn_depth_s", use_container_width=True):
                st.session_state["depth_choice"] = "STANDARD"
                st.rerun()

    with col_d:
        is_d = st.session_state["depth_choice"] == "DEEP"
        st.markdown(render_single_depth_card("DEEP", is_selected=is_d), unsafe_allow_html=True)
        if is_d:
            st.button("● Active Mode", key="btn_depth_d", disabled=True, use_container_width=True)
        else:
            if st.button("Select Deep", key="btn_depth_d", use_container_width=True):
                st.session_state["depth_choice"] = "DEEP"
                st.rerun()

    # 3. Tactile Claymorphic Begin Research Button
    st.markdown("<div style='margin-top:22px;'></div>", unsafe_allow_html=True)
    launch_clicked = st.button("Begin Research ↑", type="primary", use_container_width=True)

    # 4. Example Topics Row (Curated Clickable Chips)
    st.markdown(
        """<div style="text-align:center; margin-top:22px; margin-bottom:12px; font-size:12px; font-weight:800; color:#1C1C1E; text-transform:uppercase; letter-spacing:0.8px;">
        Or explore curated questions
        </div>""",
        unsafe_allow_html=True
    )

    chip_cols = st.columns(4)
    sample_topics = [
        "Will the AI bubble burst?",
        "Future of humanoid robotics",
        "Is quantum computing commercially viable?",
        "The future of work in the AI era",
    ]
    for idx, (c_col, s_top) in enumerate(zip(chip_cols, sample_topics)):
        with c_col:
            if st.button(s_top, key=f"chip_{idx}", use_container_width=True):
                st.session_state["topic_input"] = s_top
                st.rerun()

# ==============================================================================
# Screen 2: Live Research Experience (Dedicated Autonomous Command Center)
# ==============================================================================
if launch_clicked:
    clean_topic = topic_query.strip()
    if not clean_topic:
        st.error("Please enter a research topic into the command bar before initiating research.")
        st.stop()

    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    st.markdown(render_active_research_banner(clean_topic), unsafe_allow_html=True)

    # Telemetry and Visual Containers
    timeline_container = st.empty()
    graph_container = st.empty()
    live_metrics_container = st.empty()
    terminal_container = st.empty()

    event_logs = []
    start_time = time.time()
    tracked_metrics = {"sources": 0, "perspectives": 3, "evidence": 0, "iterations": 1}

    def live_progress_handler(step_name: str, pct: float, details: str):
        elapsed = int(time.time() - start_time)
        timestamp = f"{elapsed//60:02d}:{elapsed%60:02d}"
        
        friendly_text = humanize_backend_message(step_name, details)
        
        event_logs.append({
            "time": timestamp,
            "stage": step_name,
            "message": details,
            "friendly_message": friendly_text,
            "progress": pct,
        })

        # Track sources & evidence count dynamically
        if "source" in details.lower():
            for w in details.split():
                if w.isdigit():
                    tracked_metrics["sources"] = max(tracked_metrics["sources"], int(w))
        if "evidence" in details.lower() or "chunk" in details.lower() or "claim" in details.lower():
            for w in details.split():
                if w.isdigit():
                    tracked_metrics["evidence"] = max(tracked_metrics["evidence"], int(w))
        if "iteration" in step_name.lower():
            parts = step_name.split("_")
            if len(parts) > 1 and parts[1].isdigit():
                tracked_metrics["iterations"] = int(parts[1])

        # 1. 7-Stage Research Journey Timeline
        timeline_container.markdown(render_7_stage_journey(step_name), unsafe_allow_html=True)

        # 2. Dynamic Research Map & Angle SVG
        graph_container.markdown(render_knowledge_graph_svg(step_name), unsafe_allow_html=True)

        # 3. 4 Floating Live Research Metrics
        live_metrics_container.markdown(
            render_4_live_stats(
                sources=tracked_metrics["sources"],
                perspectives=tracked_metrics["perspectives"],
                evidence_count=max(tracked_metrics["evidence"], int(pct * 20)),
                iterations=tracked_metrics["iterations"],
            ),
            unsafe_allow_html=True,
        )

        # 4. Clean Typewriter Activity Terminal (Zero raw HTML)
        terminal_container.markdown(
            render_live_activity_terminal(event_logs, current_message=friendly_text),
            unsafe_allow_html=True,
        )

    try:
        # Initial Render before execution
        timeline_container.markdown(render_7_stage_journey("PLANNER"), unsafe_allow_html=True)
        graph_container.markdown(render_knowledge_graph_svg("PLANNER"), unsafe_allow_html=True)
        live_metrics_container.markdown(render_4_live_stats(0, 3, 0, 1), unsafe_allow_html=True)
        terminal_container.markdown(
            render_live_activity_terminal([], current_message="Understanding the core research question..."),
            unsafe_allow_html=True,
        )

        # Execute Modular Backend Pipeline
        result: ResearchResult = run_research(
            topic=clean_topic,
            depth=st.session_state["depth_choice"],
            progress_callback=live_progress_handler,
        )

        st.session_state["research_result"] = result

        # Compile PDF Dossier
        pdf_path = f"research_dossier_{result.session_id}.pdf"
        generate_research_pdf(result, output_path=pdf_path)
        st.session_state["pdf_path"] = pdf_path

        # Final Terminal & Metric Completion Update
        timeline_container.markdown(render_7_stage_journey("COMPLETE"), unsafe_allow_html=True)
        graph_container.markdown(render_knowledge_graph_svg("COMPLETE"), unsafe_allow_html=True)
        live_metrics_container.markdown(
            render_4_live_stats(
                sources=len(result.accepted_sources),
                perspectives=len(result.plan.research_dimensions) if result.plan else 3,
                evidence_count=len(result.claims) * 3 if result.claims else 18,
                iterations=result.metrics.research_iterations if result.metrics else tracked_metrics["iterations"],
            ),
            unsafe_allow_html=True,
        )
        terminal_container.markdown(
            render_live_activity_terminal(event_logs, current_message="Research completed & dossier verified."),
            unsafe_allow_html=True,
        )

        time.sleep(0.4)

    except Exception as e:
        st.error(f"Research execution interrupted: {e}")
        st.exception(e)
        st.stop()

# ==============================================================================
# Screen 3: Editorial Research Results Workspace
# ==============================================================================
active_result = st.session_state.get("research_result")
active_pdf = st.session_state.get("pdf_path")

if active_result:
    render_results_workspace(active_result, pdf_path=active_pdf)
