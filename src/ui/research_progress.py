"""
Live Research Progress & Activity Monitor for Agentic Research PRO.
Warm white liquid glass live command center with typewriter research telemetry,
minimal stage timeline, and clean human-readable metrics.
"""

import html
from typing import List, Dict, Any

STAGES = [
    ("UNDERSTANDING", "Understanding"),
    ("EXPLORING", "Exploring"),
    ("ANALYZING", "Analyzing"),
    ("VERIFYING", "Verifying"),
    ("COMPLETE", "Complete"),
]


def humanize_backend_message(step_name: str, raw_msg: str) -> str:
    """
    Translates raw backend engineering telemetry into clean, product-friendly
    research language as requested by the user.
    """
    msg = raw_msg or ""
    step = step_name.upper()

    if "PLAN" in step:
        if "query" in msg.lower() or "queries" in msg.lower():
            return "Formulating research inquiry and perspective angles..."
        return "Understanding the research question & planning strategic inquiry..."

    if "SEARCH" in step:
        if "found" in msg.lower():
            # e.g., "Found 15 sources (12 new, 3 duplicates)."
            return msg.replace("Tavily", "global literature").replace("duplicates", "duplicate sources filtered")
        return "Finding relevant authoritative sources & literature..."

    if "EVAL" in step:
        if "accepted" in msg.lower():
            return msg.replace("Rejected:", "Filtered low-relevance:")
        return "Evaluating source quality, institutional authority, and credibility..."

    if "SCRAP" in step:
        return "Reading and extracting passages from authoritative sources..."

    if "EMBED" in step or "RETR" in step:
        return "Analyzing and organizing evidence for multi-perspective comparison..."

    if "GAP" in step or "ITERATION" in step:
        return "Identifying missing information & expanding follow-up research..."

    if "SYNTH" in step:
        return "Synthesizing executive findings and multi-perspective insights..."

    if "CLAIM" in step:
        return "Grounding factual claims and verifying empirical evidence..."

    if "CONTRA" in step:
        return "Comparing conflicting viewpoints & analyzing empirical trade-offs..."

    if "CONF" in step or "COMPLETE" in step:
        return "Finalizing research dossier, citations, and confidence assessment..."

    # Generic cleaning
    cleaned = msg.replace("Tavily", "Search Engine").replace("ChromaDB", "Evidence Store").replace("all-MiniLM-L6-v2", "Neural Embedder").replace("GPT-4o", "AI Engine")
    return cleaned


def render_live_timeline(current_stage: str) -> str:
    """
    Renders a minimal editorial timeline for active research.
    Understanding -> Exploring -> Analyzing -> Verifying -> Complete
    """
    stage_upper = current_stage.upper()
    active_idx = 0
    if "PLAN" in stage_upper or "INIT" in stage_upper:
        active_idx = 0
    elif "SEARCH" in stage_upper or "EVAL" in stage_upper:
        active_idx = 1
    elif "SCRAP" in stage_upper or "EMBED" in stage_upper or "GAP" in stage_upper:
        active_idx = 2
    elif "CLAIM" in stage_upper or "CONTRA" in stage_upper or "SYNTH" in stage_upper:
        active_idx = 3
    elif "CONF" in stage_upper or "COMPLETE" in stage_upper:
        active_idx = 4

    steps_html = []
    for idx, (code, label) in enumerate(STAGES):
        if idx < active_idx:
            status_cls = "done"
            dot_content = "✓"
        elif idx == active_idx:
            status_cls = "active"
            dot_content = "●"
        else:
            status_cls = ""
            dot_content = "○"

        steps_html.append(
            f"""
            <div class="timeline-step {status_cls}">
                <div class="timeline-node">{dot_content}</div>
                <div class="timeline-label">{label}</div>
            </div>
            """
        )

    return f"""
    <div style="background:rgba(255,255,255,0.65); border:1px solid rgba(255,255,255,0.85); border-radius:20px; padding:18px 24px; box-shadow:0 4px 16px rgba(0,0,0,0.02); margin-bottom:20px;">
        <div class="timeline-track">
            {''.join(steps_html)}
        </div>
    </div>
    """


def render_live_terminal(event_logs: List[Dict[str, Any]], current_message: str = "") -> str:
    """
    Renders the live research activity typewriter panel in warm white liquid glass.
    """
    lines_html = []
    for log in event_logs[-6:]:
        t = log.get("time", "00:00")
        msg = html.escape(log.get("friendly_message") or log.get("message", ""))
        lines_html.append(
            f"""
            <div class="terminal-line">
                <span class="line-time">{t}</span>
                <span class="line-bullet">›</span>
                <span>{msg}</span>
            </div>
            """
        )

    active_line_html = ""
    if current_message:
        clean_curr = html.escape(current_message)
        active_line_html = f"""
        <div class="terminal-line" style="margin-top:6px; color:#1C1C1E; font-weight:550;">
            <span class="line-time">now</span>
            <span class="line-bullet">›</span>
            <span>{clean_curr}</span>
            <span class="terminal-cursor"></span>
        </div>
        """
    else:
        active_line_html = """
        <div class="terminal-line" style="margin-top:6px; color:#8E8E93;">
            <span class="line-time">...</span>
            <span class="line-bullet">›</span>
            <span>Investigating topic dimensions</span>
            <span class="terminal-cursor"></span>
        </div>
        """

    return f"""
    <div class="live-terminal-panel">
        <div class="live-terminal-header">
            <div class="live-indicator">
                <div class="live-dot"></div>
                <span>Autonomous Research Activity</span>
            </div>
            <div style="font-size:12px; font-weight:600; color:#8E8E93;">
                Live Telemetry
            </div>
        </div>
        <div>
            {''.join(lines_html)}
            {active_line_html}
        </div>
    </div>
    """


def render_live_metrics_row(sources: int = 0, perspectives: int = 3, iterations: int = 1) -> str:
    """
    Renders 3 simple, user-friendly metric chips:
    Sources reviewed, Perspectives explored, Research iterations.
    """
    return f"""
    <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:14px; margin: 16px 0;">
        <div class="live-metric-card">
            <div class="live-metric-val">{sources:02d}</div>
            <div class="live-metric-lbl">Sources Reviewed</div>
        </div>
        <div class="live-metric-card">
            <div class="live-metric-val">{perspectives:02d}</div>
            <div class="live-metric-lbl">Perspectives Explored</div>
        </div>
        <div class="live-metric-card">
            <div class="live-metric-val">{iterations:02d}</div>
            <div class="live-metric-lbl">Research Iterations</div>
        </div>
    </div>
    """
