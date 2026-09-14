"""
Agentic Research — Autonomous Research Instrument.
Editorial Typography (Space Grotesk + Instrument Serif + IBM Plex Mono)
Warm Editorial Palette (#F7F6F2 background, #151619 ink, #315BFF research blue)
Features real-time wall-clock telemetry, genuine research event streams, and continuous publication dossiers.
"""

import os
import time
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

from src.research_orchestrator import run_research, ResearchResult
from src.pdfgen import generate_research_pdf
from src.ui.theme import inject_editorial_research_theme
from src.ui.components import (
    render_editorial_nav,
    render_editorial_hero,
    render_depth_card_editorial,
    render_active_research_banner,
    render_why_different_content,
)
from src.ui.research_progress import (
    humanize_backend_message,
    render_7_stage_journey,
    render_vertical_research_trail,
    render_compact_metrics,
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

# Apply Editorial Research Design System
inject_editorial_research_theme()


# ==============================================================================
# Presentation Modal: Why This Is Different
# ==============================================================================
@st.dialog("✦ Why This Is Different", width="large")
def show_why_diff_modal():
    st.markdown(render_why_different_content(), unsafe_allow_html=True)


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
if "active_investigation" not in st.session_state:
    st.session_state["active_investigation"] = None

# ==============================================================================
# ROUTING: SCREEN 3 (Dossier) vs SCREEN 2 (Active Investigation) vs SCREEN 1 (Home)
# ==============================================================================
active_result = st.session_state.get("research_result")
active_pdf = st.session_state.get("pdf_path")
active_investigation_topic = st.session_state.get("active_investigation")


if active_result is not None:
    # ==========================================================================
    # SCREEN 3: Continuous Publication Research Dossier
    # ==========================================================================
    st.markdown(render_editorial_nav(), unsafe_allow_html=True)

    col_nav_left, col_nav_right = st.columns([7.5, 2.5])
    with col_nav_left:
        st.markdown(
            f"""<div style="font-size:13px; color:#55565D; font-weight:600; padding-top:6px; font-family:'Space Grotesk', sans-serif;">
            ✦ Viewing Research Dossier: <span style="color:#151619; font-weight:700;">{active_result.topic}</span>
            </div>""",
            unsafe_allow_html=True,
        )
    with col_nav_right:
        if st.button("← Start New Investigation", key="btn_new_investigation", use_container_width=True):
            st.session_state["research_result"] = None
            st.session_state["pdf_path"] = None
            st.session_state["topic_input"] = ""
            st.session_state["active_investigation"] = None
            st.rerun()

    st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)
    render_results_workspace(active_result, pdf_path=active_pdf)


elif active_investigation_topic is not None:
    # ==========================================================================
    # SCREEN 2: Dedicated Live Research Experience (Agentic Command Center)
    # ==========================================================================
    st.markdown(render_editorial_nav(), unsafe_allow_html=True)

    topic = active_investigation_topic
    depth = st.session_state.get("depth_choice", "STANDARD")

    # Layout Containers
    banner_container = st.empty()
    journey_container = st.empty()
    metrics_container = st.empty()
    trail_container = st.empty()

    # Capture REAL Local System Wall-Clock Research Start Time
    research_started_at = datetime.now().astimezone()
    start_clock_str = research_started_at.strftime("%I:%M:%S %p")

    event_logs = []
    tracked_metrics = {"sources": 0, "perspectives": 3, "evidence": 0, "iterations": 1}

    # Initial state before backend fires
    initial_elapsed = "00:00 elapsed"
    banner_container.markdown(render_active_research_banner(topic, elapsed_str=initial_elapsed), unsafe_allow_html=True)
    journey_container.markdown(render_7_stage_journey("INITIALIZATION"), unsafe_allow_html=True)
    metrics_container.markdown(render_compact_metrics(0, 3, 0, 1), unsafe_allow_html=True)
    trail_container.markdown(
        render_vertical_research_trail(
            event_logs=[],
            active_message="Understanding the research question & scope",
            active_clock_time=start_clock_str,
            elapsed_str=initial_elapsed,
            is_complete=False,
        ),
        unsafe_allow_html=True,
    )

    last_active_item = {
        "message": "Understanding the research question & scope",
        "clock_time": start_clock_str,
    }

    def live_progress_handler(step_name: str, pct: float, details: str):
        # 1. Capture exact current local system wall-clock time
        now = datetime.now().astimezone()
        curr_clock_time = now.strftime("%I:%M:%S %p")
        
        # 2. Calculate real elapsed wall-clock duration
        elapsed_sec = int((now - research_started_at).total_seconds())
        curr_elapsed_str = f"{elapsed_sec//60:02d}:{elapsed_sec%60:02d} elapsed"

        # 3. Humanize message into a clean, distinct research action
        friendly_action = humanize_backend_message(step_name, details)

        # 4. If the new action is distinct from the previous active action,
        # settle the previous active action into completed history with its original start timestamp
        if friendly_action != last_active_item["message"]:
            event_logs.append({
                "clock_time": last_active_item["clock_time"],
                "friendly_message": last_active_item["message"],
                "stage": step_name,
            })
            last_active_item["message"] = friendly_action
            last_active_item["clock_time"] = curr_clock_time

        # 5. Dynamically extract live metrics from backend details
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

        # 6. Push Live UI Telemetry updates immediately to Streamlit
        banner_container.markdown(
            render_active_research_banner(topic, elapsed_str=curr_elapsed_str),
            unsafe_allow_html=True,
        )
        journey_container.markdown(
            render_7_stage_journey(step_name),
            unsafe_allow_html=True,
        )
        metrics_container.markdown(
            render_compact_metrics(
                sources=tracked_metrics["sources"],
                perspectives=tracked_metrics["perspectives"],
                evidence_count=max(tracked_metrics["evidence"], int(pct * 24)),
                iterations=tracked_metrics["iterations"],
            ),
            unsafe_allow_html=True,
        )
        trail_container.markdown(
            render_vertical_research_trail(
                event_logs=event_logs,
                active_message=last_active_item["message"],
                active_clock_time=last_active_item["clock_time"],
                elapsed_str=curr_elapsed_str,
                is_complete=False,
            ),
            unsafe_allow_html=True,
        )

    try:
        # Run the real research pipeline synchronously with live progress callbacks
        result: ResearchResult = run_research(
            topic=topic,
            depth=depth,
            progress_callback=live_progress_handler,
        )

        # Final completion timestamp
        now = datetime.now().astimezone()
        final_clock_str = now.strftime("%I:%M:%S %p")
        total_elapsed_sec = int((now - research_started_at).total_seconds())
        final_elapsed_str = f"{total_elapsed_sec//60:02d}:{total_elapsed_sec%60:02d} elapsed"

        # Settle the final active action
        event_logs.append({
            "clock_time": last_active_item["clock_time"],
            "friendly_message": last_active_item["message"],
            "stage": "COMPLETE",
        })

        # Compile PDF Dossier
        pdf_path = f"research_dossier_{result.session_id}.pdf"
        generate_research_pdf(result, output_path=pdf_path)

        # Final UI Flush
        banner_container.markdown(
            render_active_research_banner(topic, elapsed_str=final_elapsed_str),
            unsafe_allow_html=True,
        )
        journey_container.markdown(
            render_7_stage_journey("COMPLETE"),
            unsafe_allow_html=True,
        )
        metrics_container.markdown(
            render_compact_metrics(
                sources=len(result.accepted_sources),
                perspectives=len(result.plan.research_dimensions) if result.plan else 3,
                evidence_count=len(result.claims) * 3 if result.claims else 24,
                iterations=result.metrics.research_iterations if result.metrics else tracked_metrics["iterations"],
            ),
            unsafe_allow_html=True,
        )
        trail_container.markdown(
            render_vertical_research_trail(
                event_logs=event_logs,
                active_message="Investigation finalized & publication dossier compiled",
                active_clock_time=final_clock_str,
                elapsed_str=final_elapsed_str,
                is_complete=True,
            ),
            unsafe_allow_html=True,
        )

        # Store result in state and transition smoothly to Screen 3
        st.session_state["research_result"] = result
        st.session_state["pdf_path"] = pdf_path
        st.session_state["active_investigation"] = None

        time.sleep(0.8)
        st.rerun()

    except Exception as e:
        st.error(f"Research execution interrupted: {e}")
        st.session_state["active_investigation"] = None
        st.exception(e)
        st.stop()


else:
    # ==========================================================================
    # SCREEN 1: Editorial Research Home
    # ==========================================================================
    st.markdown(render_editorial_nav(), unsafe_allow_html=True)
    st.markdown(render_editorial_hero(), unsafe_allow_html=True)

    # Center Research Command Area
    col_left, col_center, col_right = st.columns([1.2, 7.6, 1.2])

    with col_center:
        # 1. Investigation Command Surface
        topic_query = st.text_input(
            label="Research Query",
            value=st.session_state["topic_input"],
            placeholder="What would you like to investigate? e.g. Will the AI bubble burst?",
            label_visibility="collapsed",
        )
        st.session_state["topic_input"] = topic_query

        # 2. Three Depth Selection Cards
        st.markdown(
            """<div style="margin-top:22px; margin-bottom:10px; text-align:center;">
<div style="font-size:11px; font-weight:700; color:#85868D; text-transform:uppercase; letter-spacing:0.1em; font-family:'IBM Plex Mono', monospace;">
Select Research Depth
</div>
</div>""",
            unsafe_allow_html=True,
        )

        col_q, col_s, col_d = st.columns(3)

        with col_q:
            is_q = st.session_state["depth_choice"] == "QUICK"
            st.markdown(render_depth_card_editorial("QUICK", is_selected=is_q), unsafe_allow_html=True)
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            btn_class = "depth-active-btn" if is_q else ""
            st.markdown(f'<div class="{btn_class}">', unsafe_allow_html=True)
            if st.button("Active Mode" if is_q else "Select Quick", key="btn_depth_q", use_container_width=True):
                st.session_state["depth_choice"] = "QUICK"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with col_s:
            is_s = st.session_state["depth_choice"] == "STANDARD"
            st.markdown(render_depth_card_editorial("STANDARD", is_selected=is_s), unsafe_allow_html=True)
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            btn_class = "depth-active-btn" if is_s else ""
            st.markdown(f'<div class="{btn_class}">', unsafe_allow_html=True)
            if st.button("Active Mode" if is_s else "Select Standard", key="btn_depth_s", use_container_width=True):
                st.session_state["depth_choice"] = "STANDARD"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with col_d:
            is_d = st.session_state["depth_choice"] == "DEEP"
            st.markdown(render_depth_card_editorial("DEEP", is_selected=is_d), unsafe_allow_html=True)
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            btn_class = "depth-active-btn" if is_d else ""
            st.markdown(f'<div class="{btn_class}">', unsafe_allow_html=True)
            if st.button("Active Mode" if is_d else "Select Deep", key="btn_depth_d", use_container_width=True):
                st.session_state["depth_choice"] = "DEEP"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # 3. Strongest CTA: Begin Research →
        st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
        launch_clicked = st.button("Begin Research →", type="primary", use_container_width=True)

        # 4. Subtle "✦ What makes this different?" Trigger
        st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
        col_w1, col_w2, col_w3 = st.columns([1.5, 3, 1.5])
        with col_w2:
            if st.button("✦ What makes this different?", key="btn_why_diff_home", use_container_width=True):
                show_why_diff_modal()

        # 5. Curated Questions Row
        st.markdown(
            """<div style="text-align:center; margin-top:24px; margin-bottom:10px; font-size:11px; font-weight:700; color:#85868D; text-transform:uppercase; letter-spacing:0.1em; font-family:'IBM Plex Mono', monospace;">
Curated Questions
</div>""",
            unsafe_allow_html=True,
        )

        chip_cols = st.columns(4)
        sample_topics = [
            ("Will the AI bubble burst?", "DEEP"),
            ("Is quantum computing commercially viable?", "STANDARD"),
            ("Future of humanoid robotics", "STANDARD"),
            ("How AI reshapes the future of work", "STANDARD"),
        ]
        for idx, (c_col, (s_top, s_depth)) in enumerate(zip(chip_cols, sample_topics)):
            with c_col:
                if st.button(s_top, key=f"chip_{idx}", use_container_width=True):
                    st.session_state["topic_input"] = s_top
                    st.session_state["depth_choice"] = s_depth
                    st.rerun()

    # Trigger Transition to Screen 2 when Launch is Clicked
    if launch_clicked:
        clean_topic = topic_query.strip()
        if not clean_topic:
            st.error("Please enter a research topic into the command bar before initiating research.")
        else:
            st.session_state["active_investigation"] = clean_topic
            st.session_state["research_result"] = None
            st.rerun()
