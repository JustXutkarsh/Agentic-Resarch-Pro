"""
Agentic Research PRO — Premium Warm White Liquid Glass Research Application.
Minimal editorial interface combining Apple Liquid Glass, soft claymorphism, and subtle neo-brutalism.
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
    render_depth_selector,
)
from src.ui.research_progress import (
    humanize_backend_message,
    render_live_timeline,
    render_live_terminal,
    render_live_metrics_row,
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
col_left, col_center, col_right = st.columns([1.5, 7, 1.5])

with col_center:
    # Topic Input
    topic_query = st.text_input(
        label="Research Query",
        value=st.session_state["topic_input"],
        placeholder="What would you like to research? e.g. State of Solid-State Battery Commercialization...",
        label_visibility="collapsed",
    )
    # Sync typed text back to state
    st.session_state["topic_input"] = topic_query

    # Tactile Segmented Depth Controller & Launch Button
    c_depth, c_btn = st.columns([3, 2])
    with c_depth:
        depth_selected = st.radio(
            "Research Depth Mode",
            options=["Quick", "Standard", "Deep"],
            index=["QUICK", "STANDARD", "DEEP"].index(st.session_state["depth_choice"]),
            horizontal=True,
            label_visibility="collapsed",
        )
        st.session_state["depth_choice"] = depth_selected.upper()

    with c_btn:
        launch_clicked = st.button("Begin Research ↑", use_container_width=True)

    # Tactile Depth Card Descriptions
    st.markdown(render_depth_selector(st.session_state["depth_choice"]), unsafe_allow_html=True)

    # Example Topics Row (Clickable Chips)
    st.markdown(
        """
        <div style="text-align:center; margin-top:16px; margin-bottom:10px; font-size:12px; font-weight:600; color:#8E8E93; text-transform:uppercase; letter-spacing:0.8px;">
            Try exploring
        </div>
        """,
        unsafe_allow_html=True
    )
    
    chip_cols = st.columns(5)
    sample_topics = [
        "AI in Healthcare",
        "Future of Work",
        "Climate Tech",
        "Quantum Computing",
        "Solid-State Batteries",
    ]
    for idx, (c_col, s_top) in enumerate(zip(chip_cols, sample_topics)):
        with c_col:
            if st.button(s_top, key=f"chip_{idx}", use_container_width=True):
                st.session_state["topic_input"] = s_top
                st.rerun()

# ==============================================================================
# Screen 2: Live Research Experience (Warm White Command Center)
# ==============================================================================
if launch_clicked:
    clean_topic = topic_query.strip()
    if not clean_topic:
        st.error("Please enter a research topic into the command bar before initiating research.")
        st.stop()

    st.markdown("---")
    st.markdown(f"""
    <div class="glass-panel" style="margin-top:16px; margin-bottom:20px; border-left: 4px solid #1C1C1E; padding: 20px 28px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
                <div style="font-size:11.5px; font-weight:700; color:#8E8E93; text-transform:uppercase; letter-spacing:0.8px;">Active Research Session</div>
                <div style="font-size:20px; font-weight:700; color:#1C1C1E; margin-top:2px;">
                    "{clean_topic}"
                </div>
            </div>
            <div style="display:flex; align-items:center; gap:8px; background:rgba(28,28,30,0.06); padding:5px 14px; border-radius:9999px;">
                <div class="live-dot"></div>
                <span style="font-size:11.5px; font-weight:700; color:#1C1C1E; text-transform:uppercase; letter-spacing:0.6px;">INVESTIGATING</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Telemetry containers
    timeline_container = st.empty()
    live_metrics_container = st.empty()
    terminal_container = st.empty()

    event_logs = []
    start_time = time.time()
    tracked_metrics = {"sources": 0, "perspectives": 3, "iterations": 1}

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

        # Track sources from event messages
        if "source" in details.lower() or "sources" in details.lower():
            for w in details.split():
                if w.isdigit():
                    tracked_metrics["sources"] = max(tracked_metrics["sources"], int(w))
        if "iteration" in step_name.lower():
            parts = step_name.split("_")
            if len(parts) > 1 and parts[1].isdigit():
                tracked_metrics["iterations"] = int(parts[1])

        # Render stage timeline
        timeline_container.markdown(render_live_timeline(step_name), unsafe_allow_html=True)

        # Render simple metrics
        live_metrics_container.markdown(
            render_live_metrics_row(
                sources=tracked_metrics["sources"],
                perspectives=tracked_metrics["perspectives"],
                iterations=tracked_metrics["iterations"],
            ),
            unsafe_allow_html=True,
        )

        # Render typewriter terminal
        terminal_container.markdown(render_live_terminal(event_logs, current_message=friendly_text), unsafe_allow_html=True)

    try:
        # Initial render of command center
        timeline_container.markdown(render_live_timeline("PLANNER"), unsafe_allow_html=True)
        live_metrics_container.markdown(render_live_metrics_row(0, 3, 1), unsafe_allow_html=True)
        terminal_container.markdown(render_live_terminal([], current_message="Formulating inquiry and understanding topic..."), unsafe_allow_html=True)

        # Run backend orchestrator without modifying any logic
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

        # Final terminal update
        timeline_container.markdown(render_live_timeline("COMPLETE"), unsafe_allow_html=True)
        live_metrics_container.markdown(
            render_live_metrics_row(
                sources=len(result.accepted_sources),
                perspectives=len(result.plan.research_dimensions) if result.plan else 3,
                iterations=result.metrics.research_iterations if result.metrics else tracked_metrics["iterations"],
            ),
            unsafe_allow_html=True,
        )
        terminal_container.markdown(render_live_terminal(event_logs, current_message="Research completed & dossier verified."), unsafe_allow_html=True)

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
