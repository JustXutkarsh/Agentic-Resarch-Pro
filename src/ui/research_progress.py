"""
Live Research Activity & Stage Monitor for Agentic Research PRO.
Apple Liquid Glass + Soft Claymorphism live research command center.
Strict Light Contrast System:
- Primary text: #1C1C1E
- Secondary text: #4A4A4F
- Muted text: #6E6E73
- Active accent: #0066FF / #E85D4A
All HTML strings are left-aligned at column 0 to prevent Markdown 4-space code block bugs.
"""

import html
from typing import List, Dict, Any

STAGES = [
    ("01", "Understanding", "Understanding the question"),
    ("02", "Angles", "Exploring research angles"),
    ("03", "Searching", "Searching authoritative sources"),
    ("04", "Evidence", "Extracting evidence"),
    ("05", "Perspectives", "Comparing perspectives"),
    ("06", "Contradictions", "Detecting contradictions"),
    ("07", "Synthesis", "Synthesizing findings"),
]


def humanize_backend_message(step_name: str, raw_msg: str) -> str:
    """Translates raw backend engineering events into human-readable research actions."""
    msg = raw_msg or ""
    step = step_name.upper()

    if "PLAN" in step or "INIT" in step:
        if "query" in msg.lower() or "queries" in msg.lower():
            return "Mapping possible perspectives, assumptions, and investigative queries..."
        return "Understanding the core research question and framing objectives..."

    if "SEARCH" in step:
        if "found" in msg.lower():
            return msg.replace("Tavily", "authoritative web index").replace("duplicates", "duplicate records consolidated")
        return "Searching authoritative economic analysis, institutional publications, and academic repositories..."

    if "EVAL" in step:
        if "accepted" in msg.lower():
            return msg.replace("Rejected:", "Filtered lower-credibility:")
        return "Evaluating source credibility, institutional domain authority, and evidentiary rigor..."

    if "SCRAP" in step:
        return "Extracting and parsing evidentiary passages from selected primary literature..."

    if "EMBED" in step or "RETR" in step:
        return "Indexing evidence passages and structuring memory for cross-perspective comparison..."

    if "GAP" in step or "ITERATION" in step:
        return "Identifying missing information, boundary constraints, and executing targeted follow-up queries..."

    if "CONTRA" in step:
        return "Comparing optimistic, balanced, and skeptical perspectives across source documents..."

    if "CLAIM" in step:
        return "Detecting contradictions and grounding factual assertions against primary source quotes..."

    if "SYNTH" in step:
        return "Synthesizing comprehensive findings, trade-off matrices, and publication-ready report..."

    if "CONF" in step or "COMPLETE" in step:
        return "Finalizing research dossier, verification metrics, and confidence assessment..."

    return msg.replace("Tavily", "Research Search").replace("ChromaDB", "Evidence Vector Store").replace("all-MiniLM-L6-v2", "Semantic Embedder").replace("GPT-4o", "Research AI")


def render_7_stage_journey(current_stage: str) -> str:
    """
    Renders the 7-stage research journey timeline with clear active focus and high contrast.
    """
    stage_upper = current_stage.upper()
    active_idx = 0
    if "INIT" in stage_upper or "PLAN" in stage_upper:
        active_idx = 0
    elif "SEARCH" in stage_upper:
        active_idx = 1
    elif "EVAL" in stage_upper:
        active_idx = 2
    elif "SCRAP" in stage_upper or "EMBED" in stage_upper:
        active_idx = 3
    elif "GAP" in stage_upper or "RETR" in stage_upper:
        active_idx = 4
    elif "CONTRA" in stage_upper or "CLAIM" in stage_upper:
        active_idx = 5
    elif "SYNTH" in stage_upper or "CONF" in stage_upper or "COMPLETE" in stage_upper:
        active_idx = 6

    steps_html = []
    for idx, (num, short_name, full_name) in enumerate(STAGES):
        if idx < active_idx:
            status_cls = "done"
            dot_content = "✓"
        elif idx == active_idx:
            status_cls = "active"
            dot_content = "●"
        else:
            status_cls = ""
            dot_content = "○"

        steps_html.append(f"""<div class="stage-node-box {status_cls}">
<div class="stage-node-circle">{dot_content}</div>
<div class="stage-node-num">{num}</div>
<div class="stage-node-name">{full_name}</div>
</div>""")

    joined_steps = "".join(steps_html)
    return f"""<div class="stage-journey-panel">
<div class="stage-journey-flow">
{joined_steps}
</div>
</div>"""


def render_knowledge_graph_svg(current_stage: str) -> str:
    """
    Renders an elegant animated knowledge graph SVG representing
    the research flow (Query -> Angles -> Sources -> Evidence -> Debate -> Dossier).
    Labels are placed below nodes instead of inside circles to guarantee clean readability.
    """
    stage_upper = current_stage.upper()
    act = 0
    if "SEARCH" in stage_upper:
        act = 1
    elif "SCRAP" in stage_upper or "EMBED" in stage_upper:
        act = 2
    elif "GAP" in stage_upper:
        act = 3
    elif "CONTRA" in stage_upper or "CLAIM" in stage_upper:
        act = 4
    elif "SYNTH" in stage_upper or "COMPLETE" in stage_upper:
        act = 5

    labels = ["Query", "Angles", "Sources", "Evidence", "Debate", "Dossier"]
    xs = [50, 164, 278, 392, 506, 620]

    node_elements = []
    for i, (name, x) in enumerate(zip(labels, xs)):
        # Connecting line to next node
        if i < len(xs) - 1:
            next_x = xs[i + 1]
            if i < act:
                line_stroke = "#1C1C1E"
                line_dash = ""
                line_w = "2.5"
            elif i == act:
                line_stroke = "#0066FF"
                line_dash = 'stroke-dasharray="4 4"'
                line_w = "2.5"
            else:
                line_stroke = "#D1D1D6"
                line_dash = 'stroke-dasharray="4 4"'
                line_w = "2"
            node_elements.append(f'<line x1="{x+16}" y1="26" x2="{next_x-16}" y2="26" stroke="{line_stroke}" stroke-width="{line_w}" {line_dash} />')

        # Node Circle
        if i < act:
            # Completed
            circle_svg = f"""<circle cx="{x}" cy="26" r="13" fill="#1C1C1E" />
<text x="{x}" y="30" text-anchor="middle" fill="#FFFFFF" font-family="Plus Jakarta Sans" font-size="11" font-weight="800">✓</text>"""
            label_fill = "#1C1C1E"
            label_weight = "750"
            label_size = "12.5"
        elif i == act:
            # Active (Pulse ring & glowing blue)
            circle_svg = f"""<circle cx="{x}" cy="26" r="18" fill="rgba(0,102,255,0.18)" stroke="#0066FF" stroke-width="2" />
<circle cx="{x}" cy="26" r="12" fill="#0066FF" />
<circle cx="{x}" cy="26" r="4" fill="#FFFFFF" />"""
            label_fill = "#0066FF"
            label_weight = "800"
            label_size = "13"
        else:
            # Future
            circle_svg = f"""<circle cx="{x}" cy="26" r="12" fill="#FFFFFF" stroke="#D1D1D6" stroke-width="2.5" />
<circle cx="{x}" cy="26" r="3" fill="#D1D1D6" />"""
            label_fill = "#6E6E73"
            label_weight = "600"
            label_size = "12.5"

        # Label placed below the node
        label_svg = f'<text x="{x}" y="56" text-anchor="middle" fill="{label_fill}" font-family="Plus Jakarta Sans" font-size="{label_size}" font-weight="{label_weight}">{name}</text>'

        node_elements.append(circle_svg)
        node_elements.append(label_svg)

    joined_svg = "\n".join(node_elements)

    return f"""<div style="background:linear-gradient(135deg, rgba(255,255,255,0.88), rgba(255,255,255,0.70)); border:1px solid rgba(255,255,255,0.95); border-radius:20px; padding:20px 24px; box-shadow:var(--clay-card); margin-bottom:20px;">
<div style="font-size:12px; font-weight:750; color:#1C1C1E; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:12px; text-align:center;">
Dynamic Research Map & Perspective Pipeline
</div>
<div style="display:flex; justify-content:center;">
<svg width="670" height="70" viewBox="0 0 670 70" fill="none" xmlns="http://www.w3.org/2000/svg">
{joined_svg}
</svg>
</div>
</div>"""


def render_live_activity_terminal(event_logs: List[Dict[str, Any]], current_message: str = "") -> str:
    """
    Renders live typewriter activity lines in warm white liquid glass.
    High contrast text: #3A3A3C for completed logs, #1C1C1E for active log.
    Strictly left-aligned HTML elements prevent Markdown pre/code block parsing.
    """
    lines_html = []
    for log in event_logs[-7:]:
        t = log.get("time", "00:00")
        msg = html.escape(log.get("friendly_message") or log.get("message", ""))
        lines_html.append(f"""<div class="activity-line">
<span class="activity-time">{t}</span>
<span style="color:#6E6E73; font-weight:700;">●</span>
<span>{msg}</span>
</div>""")

    active_line_html = ""
    if current_message:
        clean_curr = html.escape(current_message)
        active_line_html = f"""<div class="activity-line active-line" style="margin-top:6px;">
<span class="activity-time" style="color:#0066FF; font-weight:700;">now</span>
<span style="color:#0066FF; font-weight:800;">●</span>
<span>{clean_curr}</span>
<span class="activity-cursor">▌</span>
</div>"""
    else:
        active_line_html = """<div class="activity-line" style="margin-top:6px; color:#6E6E73;">
<span class="activity-time">...</span>
<span style="color:#6E6E73;">●</span>
<span>Investigating topic dimensions</span>
<span class="activity-cursor">▌</span>
</div>"""

    joined_lines = "".join(lines_html)

    return f"""<div class="live-activity-card">
<div class="live-activity-header">
<div class="activity-status-tag">
<div class="activity-live-pulse"></div>
<span>Autonomous Research Intelligence</span>
</div>
<div style="font-size:12px; font-weight:700; color:#4A4A4F;">
Live Real-Time Activity
</div>
</div>
<div>
{joined_lines}
{active_line_html}
</div>
</div>"""


def render_4_live_stats(sources: int = 0, perspectives: int = 3, evidence_count: int = 0, iterations: int = 1) -> str:
    """Renders 4 floating research metric cards with strong typography."""
    return f"""<div class="metrics-row">
<div class="metric-glass-box">
<div class="metric-glass-number">{sources:02d}</div>
<div class="metric-glass-label">Sources Reviewed</div>
</div>
<div class="metric-glass-box">
<div class="metric-glass-number">{perspectives:02d}</div>
<div class="metric-glass-label">Perspectives Explored</div>
</div>
<div class="metric-glass-box">
<div class="metric-glass-number">{evidence_count:02d}</div>
<div class="metric-glass-label">Evidence Extracted</div>
</div>
<div class="metric-glass-box">
<div class="metric-glass-number">{iterations:02d}</div>
<div class="metric-glass-label">Research Iterations</div>
</div>
</div>"""
