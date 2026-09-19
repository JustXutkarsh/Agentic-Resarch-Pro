"""
Live Research Activity & Stage Monitor for Agentic Research.
Editorial Research Instrument Design:
- Real local wall-clock event timestamps (HH:MM:SS AM/PM)
- Real wall-clock elapsed duration (MM:SS elapsed)
- 7-Stage Progressive Research Journey:
  UNDERSTAND ─ EXPLORE ─ SEARCH ─ EVIDENCE ─ DEBATE ─ VERIFY ─ DOSSIER
- Vertical Research Trail with active blinking cursor ▌ on current event only
- Compact live metrics (Sources, Perspectives, Evidence, Iterations)
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
    Translates raw backend engineering events into human-readable research actions.
    Eliminates internal library names, API calls, raw telemetry, and developer noise.
    """
    msg = raw_msg or ""
    step = step_name.upper()

    # Step 1: Initialization
    if "INIT" in step:
        return "Understanding the research question & scope"

    # Step 2: Research Planner
    if "PLAN" in step:
        if "generated" in msg.lower():
            return "Formulated investigative queries across research dimensions"
        return "Exploring relevant research angles & hypotheses"

    # Step 3: Multi-query Search
    if "SEARCH" in step:
        if "found" in msg.lower():
            return "Retrieved candidate literature & deduplicated source references"
        return "Searching authoritative sources across dimensions"

    # Step 4: Source Evaluation
    if step.startswith("EVAL") or "EVALUAT" in step:
        if "accepted" in msg.lower():
            return "Completed source authority & credibility scoring"
        return "Evaluating source relevance and institutional authority"


    # Step 5: Content Scraping & Browser Agent
    if "PLAYWRIGHT" in step or "ACQUISITION" in step or "BROWSER" in step:
        if "detect" in step.lower() or "detect" in msg.lower():
            return "Dynamic source detected; activating Playwright browser agent"
        if "init" in step.lower() or "opening" in msg.lower():
            return "Opening interactive source in headless browser session"
        if "expand" in step.lower() or "inspect" in msg.lower():
            return "Inspecting dynamic DOM, expandable sections & data tables"
        if "page" in step.lower() or "pagin" in msg.lower():
            return "Navigating multi-page evidence repository"
        if "table" in msg.lower():
            return "Extracting structured data tables preserving row relationships"
        if "pdf" in msg.lower() or "pdf" in step.lower():
            return "Extracting and parsing academic PDF document"
        if "success" in step.lower() or "acquired" in msg.lower():
            return "Extracted interactive evidence via browser agent"
        return "Acquiring dynamic evidence via browser agent"

    if "SCRAP" in step:
        if "parsed" in msg.lower():
            return "Extracted primary evidence passages and citations"
        return "Scraping verified content & literature passages"

    # Step 6: Vector Embeddings
    if "EMBED" in step:
        return "Generating dense semantic representations for evidence passages"

    # Step 7: Evidence Retrieval
    if "RETR" in step:
        return "Retrieving evidence passages from session vector collection"

    # Step 8: Research Gap Detection
    if "GAP" in step:
        if "discovered" in msg.lower():
            return "Evidence gap detected; scheduling autonomous follow-up queries"
        if "sufficient" in msg.lower():
            return "Sufficient dimension coverage verified across all angles"
        return "Analyzing dimension coverage to detect research gaps"

    # Iteration follow-up
    if "ITERATION" in step:
        parts = step.split("_")
        num = parts[1] if len(parts) > 1 else "2"
        return f"Expanding follow-up investigation (Iteration {num})"

    # Step 9: Contradiction Detection
    if "CONTRA" in step:
        if "identified" in msg.lower():
            return "Reconciled conflicting viewpoints and empirical trade-offs"
        return "Comparing conflicting evidence across opposing perspectives"

    # Step 10: Claim Verification
    if "CLAIM" in step:
        if "extracting" in msg.lower():
            return "Extracting atomic factual assertions from synthesized evidence"
        if "verified" in msg.lower() or "judging" in msg.lower():
            return "Grounded factual claims against verified primary citations"
        return "Verifying empirical claims against retrieved passages"

    # Step 11: Dossier Synthesis
    if "SYNTH" in step:
        if "completed" in msg.lower():
            return "Synthesizing research findings into structured dossier"
        return "Synthesizing comprehensive research dossier"

    # Step 12: Research Confidence & Completion
    if "CONF" in step:
        return "Computing research confidence heuristic across evidence components"

    if "COMPLETE" in step:
        return "Research complete: Final dossier verified"

    # Clean out internal library mentions if any remain
    cleaned = (
        msg.replace("Tavily", "Research Index")
        .replace("ChromaDB", "Vector Store")
        .replace("all-MiniLM-L6-v2", "Semantic Embedder")
        .replace("GPT-4o", "Synthesizer")
        .replace("Nemotron", "Synthesizer")
        .replace("NVIDIA", "Synthesizer")
    )
    return cleaned


def render_7_stage_journey(current_stage: str) -> str:
    """
    Renders the 7-stage research journey timeline.
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
        active_idx = 4  # DEBATE
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
<div class="stage-node-name">{short_code}</div>
</div>""")

    joined_steps = "".join(steps_html)
    return f"""<div class="stage-journey-panel">
<div class="stage-journey-flow">
{joined_steps}
</div>
</div>"""


def render_compact_metrics(sources: int = 0, perspectives: int = 3, evidence_count: int = 0, iterations: int = 1) -> str:
    """Renders 4 compact live research metrics."""
    return f"""<div class="metrics-strip">
<div class="metric-cell">
<div class="metric-value">{sources:02d}</div>
<div class="metric-label">Sources Discovered</div>
</div>
<div class="metric-cell">
<div class="metric-value">{perspectives:02d}</div>
<div class="metric-label">Research Angles</div>
</div>
<div class="metric-cell">
<div class="metric-value">{evidence_count:02d}</div>
<div class="metric-label">Evidence Passages</div>
</div>
<div class="metric-cell">
<div class="metric-value">{iterations:02d}</div>
<div class="metric-label">Iterations</div>
</div>
</div>"""


def render_4_live_stats(sources: int = 0, perspectives: int = 3, evidence_count: int = 0, iterations: int = 1) -> str:
    """Backward compatibility wrapper."""
    return render_compact_metrics(sources, perspectives, evidence_count, iterations)


def render_vertical_research_trail(
    event_logs: List[Dict[str, Any]],
    active_message: str = "",
    active_clock_time: str = "",
    elapsed_str: str = "00:00 elapsed",
    is_complete: bool = False,
) -> str:
    """
    Renders the refined vertical research trail.
    Each event shows real local system clock time (HH:MM:SS AM/PM) and research action.
    The active event features the blinking typewriter cursor ▌.
    When an event completes, the cursor is removed.
    """
    trail_items_html = []
    
    # Render historical completed events
    for idx, log in enumerate(event_logs):
        clock_t = html.escape(log.get("clock_time") or "00:00:00 AM")
        msg = html.escape(log.get("friendly_message") or log.get("message", ""))
        
        trail_items_html.append(f"""<div class="trail-node">
<div class="trail-time">{clock_t}</div>
<div class="trail-bullet-col">
<div class="trail-bullet"></div>
<div class="trail-line"></div>
</div>
<div class="trail-content">{msg}</div>
</div>""")

    # Render active in-flight event if not complete
    if not is_complete and active_message:
        act_clock = html.escape(active_clock_time or "00:00:00 AM")
        act_msg = html.escape(active_message)
        
        trail_items_html.append(f"""<div class="trail-node">
<div class="trail-time" style="color:#315BFF; font-weight:600;">{act_clock}</div>
<div class="trail-bullet-col">
<div class="trail-bullet active"></div>
</div>
<div class="trail-content active">
{act_msg}<span class="trail-cursor">▌</span>
</div>
</div>""")
    elif is_complete and active_message:
        # Final complete step without cursor
        act_clock = html.escape(active_clock_time or "00:00:00 AM")
        act_msg = html.escape(active_message)
        
        trail_items_html.append(f"""<div class="trail-node">
<div class="trail-time" style="color:#138A63; font-weight:600;">{act_clock}</div>
<div class="trail-bullet-col">
<div class="trail-bullet" style="background:#138A63;"></div>
</div>
<div class="trail-content" style="color:#151619; font-weight:700;">
{act_msg}
</div>
</div>""")

    joined_trail = "".join(trail_items_html)

    return f"""<div class="trail-card">
<div class="trail-header">
<div class="trail-title">
<span style="color:#315BFF;">✦</span> Autonomous Investigation Trail
</div>
<div class="trail-elapsed">
⏱️ {html.escape(elapsed_str)}
</div>
</div>

<div>
{joined_trail}
</div>
</div>"""


def render_live_activity_terminal(
    event_logs: List[Dict[str, Any]],
    current_message: str = "",
    elapsed_seconds: float = 0.0,
) -> str:
    """Backward compatibility wrapper."""
    elapsed_int = int(elapsed_seconds)
    elapsed_str = f"{elapsed_int//60:02d}:{elapsed_int%60:02d} elapsed"
    return render_vertical_research_trail(
        event_logs=event_logs,
        active_message=current_message,
        elapsed_str=elapsed_str,
    )
