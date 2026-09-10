"""
Live Research Activity & Stage Monitor for Agentic Research.
Apple Liquid Glass + Tactile Claymorphism live research command center.
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
    ("01", "UNDERSTAND", "Understand Question"),
    ("02", "EXPLORE", "Explore Angles"),
    ("03", "SEARCH", "Search Sources"),
    ("04", "EVIDENCE", "Extract Evidence"),
    ("05", "DEBATE", "Analyze Debate"),
    ("06", "VERIFY", "Verify Claims"),
    ("07", "DOSSIER", "Synthesize Dossier"),
]


def humanize_backend_message(step_name: str, raw_msg: str) -> str:
    """
    Translates raw backend engineering events into human-readable research actions
    while preserving genuine real pipeline counts and details.
    """
    msg = raw_msg or ""
    step = step_name.upper()

    # Step 1: Initialization
    if "INIT" in step:
        return "Understanding question..."

    # Step 2: Research Planner
    if "PLAN" in step:
        if "generated" in msg.lower():
            return msg.replace("targeted search queries", "investigative queries across research angles")
        return "Exploring research angles..."

    # Step 3: Multi-query Search
    if "SEARCH" in step:
        if "searching" in msg.lower():
            return "Searching authoritative sources..."
        if "found" in msg.lower():
            return msg.replace("Tavily", "authoritative search index").replace("duplicates", "duplicate sources consolidated")
        return "Searching authoritative sources..."

    # Step 4: Source Evaluation
    if "EVAL" in step:
        if "evaluating" in msg.lower():
            return "Evaluating evidence..."
        if "accepted" in msg.lower():
            return msg.replace("Rejected:", "Filtered lower-credibility:")
        return "Evaluating evidence..."

    # Step 5: Content Scraping & Extraction
    if "SCRAP" in step:
        if "scraping" in msg.lower():
            return "Scraping content & primary citations from verified sources..."
        if "parsed" in msg.lower():
            return msg.replace("Successfully parsed", "Extracted primary evidence from")
        return "Scraping content & primary citations..."

    # Step 6: Vector Embeddings
    if "EMBED" in step:
        return "Generating dense semantic vector embeddings..."

    # Step 7: Evidence Retrieval
    if "RETR" in step:
        return "Retrieving evidence passages from isolated vector collection..."

    # Step 8: Research Gap Detection
    if "GAP" in step:
        if "discovered" in msg.lower():
            return "Research gap detected..."
        if "sufficient" in msg.lower():
            return "Sufficient dimension coverage verified across angles."
        return "Analyzing dimension coverage to detect research gaps..."

    # Iteration follow-up
    if "ITERATION" in step:
        return "Expanding follow-up search..."

    # Step 9: Contradiction Detection
    if "CONTRA" in step:
        if "identified" in msg.lower():
            return "Conflicting evidence identified..."
        return "Clustering vector evidence to detect divergent viewpoints..."

    # Step 10: Claim Verification
    if "CLAIM" in step:
        if "extracting" in msg.lower():
            return "Extracting atomic factual claims for evidentiary verification..."
        if "judging" in msg.lower():
            return "Verifying claims..."
        if "verified" in msg.lower():
            return msg.replace("Verified", "Grounded").replace("claims", "factual claims against primary vector passages")
        return "Verifying claims..."

    # Step 11: Dossier Synthesis
    if "SYNTH" in step:
        if "completed" in msg.lower():
            return "Synthesizing dossier completed."
        return "Synthesizing dossier..."

    # Step 12: Research Confidence & Completion
    if "CONF" in step:
        if "calculated" in msg.lower():
            return msg.replace("Confidence calculated:", "Evidence confidence score:")
        return "Computing research confidence heuristic across evidence components..."

    if "COMPLETE" in step:
        return "Research complete: Final dossier verified."

    # Clean out internal library mentions if any remain
    return (
        msg.replace("Tavily", "Research Index")
        .replace("ChromaDB", "Vector Store")
        .replace("all-MiniLM-L6-v2", "Semantic Embedder")
        .replace("GPT-4o", "Synthesizer")
    )


def render_7_stage_journey(current_stage: str) -> str:
    """
    Renders the 7-stage research journey timeline with clear active focus and high contrast.
    UNDERSTAND ─ EXPLORE ─ SEARCH ─ EVIDENCE ─ DEBATE ─ VERIFY ─ DOSSIER
    """
    stage_upper = current_stage.upper()
    active_idx = 0

    if "INIT" in stage_upper:
        active_idx = 0  # UNDERSTAND
    elif "PLAN" in stage_upper:
        active_idx = 1  # EXPLORE
    elif "SEARCH" in stage_upper or "EVAL" in stage_upper:
        active_idx = 2  # SEARCH
    elif "SCRAP" in stage_upper or "EMBED" in stage_upper or "RETR" in stage_upper:
        active_idx = 3  # EVIDENCE
    elif "GAP" in stage_upper or "CONTRA" in stage_upper or "ITERATION" in stage_upper:
        active_idx = 4  # DEBATE (Gap detection, follow-up search, contradiction detection)
    elif "CLAIM" in stage_upper:
        active_idx = 5  # VERIFY
    elif "SYNTH" in stage_upper or "CONF" in stage_upper or "COMPLETE" in stage_upper:
        active_idx = 6  # DOSSIER

    steps_html = []
    for idx, (num, short_code, label) in enumerate(STAGES):
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
<div class="stage-node-num">{short_code}</div>
<div class="stage-node-name">{label}</div>
</div>""")

    joined_steps = "".join(steps_html)
    return f"""<div class="stage-journey-panel">
<div class="stage-journey-flow">
{joined_steps}
</div>
</div>"""


def render_live_activity_terminal(event_logs: List[Dict[str, Any]], current_message: str = "") -> str:
    """
    Renders live real-time research activity lines in warm white liquid glass.
    Completed lines settle into place cleanly; active line has blinking cursor ▌.
    Strictly left-aligned HTML elements prevent Markdown pre/code block parsing.
    """
    lines_html = []
    # Show last 8 events for comfortable reading without layout jumping
    for log in event_logs[-8:]:
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
<span>Executing autonomous research pipeline</span>
<span class="activity-cursor">▌</span>
</div>"""

    joined_lines = "".join(lines_html)

    return f"""<div class="live-activity-card">
<div class="live-activity-header">
<div class="activity-status-tag">
<div class="activity-live-pulse"></div>
<span>Autonomous Pipeline Activity</span>
</div>
<div style="font-size:12px; font-weight:700; color:#4A4A4F; font-family:'JetBrains Mono', monospace;">
Live Event Telemetry
</div>
</div>
<div>
{joined_lines}
{active_line_html}
</div>
</div>"""


def render_4_live_stats(sources: int = 0, perspectives: int = 3, evidence_count: int = 0, iterations: int = 1) -> str:
    """Renders 4 floating research metric cards with clean typography."""
    return f"""<div class="metrics-row">
<div class="metric-glass-box">
<div class="metric-glass-number">{sources:02d}</div>
<div class="metric-glass-label">Sources Discovered</div>
</div>
<div class="metric-glass-box">
<div class="metric-glass-number">{perspectives:02d}</div>
<div class="metric-glass-label">Research Angles</div>
</div>
<div class="metric-glass-box">
<div class="metric-glass-number">{evidence_count:02d}</div>
<div class="metric-glass-label">Evidence Passages</div>
</div>
<div class="metric-glass-box">
<div class="metric-glass-number">{iterations:02d}</div>
<div class="metric-glass-label">Research Iterations</div>
</div>
</div>"""
