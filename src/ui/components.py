"""
Reusable Components for Agentic Research PRO.
Apple Liquid Glass (80%) + Claymorphism (15%) + Neo-Brutalism (5%).
Strict Light Contrast System:
- Primary text: #1C1C1E (near-black charcoal)
- Secondary text: #4A4A4F
- Muted text: #6E6E73
- Disabled text: #9A9AA0
All HTML strings are left-aligned at column 0 to prevent Markdown 4-space code block bugs.
"""

import html
from typing import Dict, Any, List, Optional


def escape(text: Any) -> str:
    """Safely escape text for HTML output."""
    if text is None:
        return ""
    return html.escape(str(text))


def render_floating_nav() -> str:
    """Render the minimal floating liquid glass navigation bar."""
    return """<div class="floating-nav">
<div class="nav-brand">
<span style="color:#0066FF; font-size:18px;">✨</span>
<span style="color:#1C1C1E; font-weight:800;">Agentic Research</span>
</div>
<div class="nav-links">
<span class="nav-link-item">Research History</span>
<span class="nav-link-item">Saved Reports</span>
<span class="nav-link-item">Settings</span>
</div>
<div style="display:flex; align-items:center; gap:10px;">
<span class="nav-pill-badge">v2.0 PRO</span>
<div style="width:34px; height:34px; border-radius:50%; background:#1C1C1E; color:#FFFFFF; display:flex; align-items:center; justify-content:center; font-size:13px; font-weight:750; box-shadow:0 2px 6px rgba(0,0,0,0.2);">
U
</div>
</div>
</div>"""


def render_hero_header() -> str:
    """Render the editorial hero section."""
    return """<div class="hero-box">
<div class="hero-pill-badge">✨ AUTONOMOUS RESEARCH</div>
<div class="hero-title">
Research beyond<br><em>the obvious.</em>
</div>
<div class="hero-subtitle">
Multi-perspective AI research that explores evidence, contradictions, risks, and insights.
</div>
</div>"""


def render_single_depth_card(mode: str, is_selected: bool) -> str:
    """
    Renders an individual tactile depth card for Quick, Standard, or Deep mode.
    High contrast text on liquid glass.
    """
    m = mode.upper()
    sel_class = "selected" if is_selected else ""
    check_html = '<div class="depth-check-icon">✓</div>' if is_selected else '<div class="depth-uncheck-icon">○</div>'

    if m == "QUICK":
        return f"""<div class="depth-card {sel_class}">
<div class="depth-header-row">
<div class="depth-icon-title">
<span>⚡</span>
<span>QUICK</span>
</div>
{check_html}
</div>
<div class="depth-tagline">Fast clarity</div>
<div class="depth-desc">A focused overview for understanding the essentials quickly.</div>
<div class="depth-features-list">
&bull; ~1 research pass<br>
&bull; Fast synthesis<br>
&bull; Best for quick understanding
</div>
</div>"""

    elif m == "STANDARD":
        return f"""<div class="depth-card {sel_class}">
<div class="depth-badge-recommended">⭐ RECOMMENDED</div>
<div class="depth-header-row">
<div class="depth-icon-title">
<span>🔍</span>
<span>STANDARD</span>
</div>
{check_html}
</div>
<div class="depth-tagline">Balanced investigation</div>
<div class="depth-desc">Explore multiple perspectives, key evidence, and important gaps.</div>
<div class="depth-features-list">
&bull; Multiple research angles<br>
&bull; Evidence comparison<br>
&bull; Best for most research
</div>
</div>"""

    else:  # DEEP
        return f"""<div class="depth-card {sel_class}">
<div class="depth-header-row">
<div class="depth-icon-title">
<span>🧠</span>
<span>DEEP</span>
</div>
{check_html}
</div>
<div class="depth-tagline">Autonomous investigation</div>
<div class="depth-desc">Comprehensive research exploring contradictions, risks, and gaps.</div>
<div class="depth-features-list">
&bull; Deep evidence exploration<br>
&bull; Contradiction detection<br>
&bull; Best for serious analysis
</div>
</div>"""


def render_depth_cards(current_depth: str = "STANDARD") -> str:
    """Renders 3 large tactile selectable depth cards in a responsive grid container."""
    is_q = current_depth.upper() == "QUICK"
    is_s = current_depth.upper() == "STANDARD"
    is_d = current_depth.upper() == "DEEP"

    card_q = render_single_depth_card("QUICK", is_q)
    card_s = render_single_depth_card("STANDARD", is_s)
    card_d = render_single_depth_card("DEEP", is_d)

    return f"""<div class="depth-cards-container">
{card_q}
{card_s}
{card_d}
</div>"""


def render_active_research_banner(topic: str) -> str:
    """Renders the calm, spacious active research session header."""
    return f"""<div class="active-research-banner">
<div class="banner-text-col">
<div class="banner-sublabel">Researching</div>
<h2 class="banner-headline">"{escape(topic)}"</h2>
</div>
<div class="banner-status-badge">
<span class="banner-pulse-dot"></span>
<span class="banner-status-text">Research in progress</span>
</div>
</div>"""


def render_report_header(topic: str, depth: str, execution_time: float, sources_count: int, dimensions_count: int, summary_one_liner: str) -> str:
    """Renders the top executive header for the research dossier."""
    mins = int(execution_time // 60)
    secs = int(execution_time % 60)
    time_str = f"{mins}m {secs:02d}s" if mins > 0 else f"{secs}s"

    return f"""<div class="report-header-panel">
<div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
<span style="background:#047857; color:#FFFFFF; font-size:11.5px; font-weight:800; padding:4px 12px; border-radius:9999px; letter-spacing:0.5px;">✓ RESEARCH COMPLETE</span>
<span style="font-size:12.5px; color:#4A4A4F; font-family:'JetBrains Mono', monospace; font-weight:600;">Autonomous Dossier</span>
</div>
<h1 class="report-headline">{escape(topic)}</h1>
<div class="report-one-liner">{escape(summary_one_liner)}</div>
<div class="meta-pills-row">
<span class="meta-pill">🔍 {escape(depth.title())} Mode</span>
<span class="meta-pill">📚 {sources_count} Sources</span>
<span class="meta-pill">🧠 {dimensions_count} Perspectives</span>
<span class="meta-pill">⏱ {time_str} Research Time</span>
</div>
</div>"""


def render_exec_summary_card(summary_text: str, confidence_score: int) -> str:
    """Renders the executive summary with visual confidence indicator."""
    if confidence_score >= 80:
        badge_text = "High Empirical Grounding"
        bar_fill = "linear-gradient(90deg, #047857, #10B981)"
    elif confidence_score >= 65:
        badge_text = "Moderate Empirical Evidence"
        bar_fill = "linear-gradient(90deg, #92400E, #F59E0B)"
    else:
        badge_text = "Emerging / Disputed Findings"
        bar_fill = "linear-gradient(90deg, #9F1239, #F43F5E)"

    return f"""<div class="exec-summary-card">
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; flex-wrap:wrap; gap:12px;">
<div>
<div style="font-size:12px; font-weight:750; color:#6E6E73; text-transform:uppercase; letter-spacing:0.8px;">Executive Assessment</div>
<div style="font-size:22px; font-weight:800; color:#1C1C1E; margin-top:3px;">{badge_text}</div>
</div>
<div style="text-align:right;">
<div style="font-size:13px; font-weight:650; color:#4A4A4F;">Confidence Rating: <b style="color:#1C1C1E; font-size:17px; font-weight:800;">{confidence_score}%</b></div>
<div style="width:170px; height:9px; background:rgba(0,0,0,0.08); border-radius:9999px; overflow:hidden; margin-top:6px;">
<div style="width:{confidence_score}%; height:100%; background:{bar_fill}; border-radius:9999px;"></div>
</div>
</div>
</div>
<div style="font-size:15.5px; color:#1C1C1E; line-height:1.75; font-weight:450;">
{escape(summary_text)}
</div>
</div>"""


def render_key_finding_card(index: int, title: str, summary: str, evidence_strength: int = 4, detail_text: str = "") -> str:
    """Renders an interactive key insight card with visual evidence strength indicator."""
    dots_html = []
    for i in range(5):
        if i < evidence_strength:
            dots_html.append('<span style="color:#1C1C1E; font-size:15px;">●</span>')
        else:
            dots_html.append('<span style="color:#9A9AA0; font-size:15px;">○</span>')
    dots_str = " ".join(dots_html)

    detail_html = ""
    if detail_text:
        detail_html = f"""<div style="margin-top:14px; padding-top:12px; border-top:1px solid rgba(0,0,0,0.08); font-size:14px; color:#2C2C2E; line-height:1.65;">
<b style="color:#1C1C1E;">Supporting Evidence:</b> {escape(detail_text)}
</div>"""

    return f"""<div class="insight-card">
<div class="insight-header">
<div style="display:flex; align-items:flex-start;">
<span class="insight-index-num">{index:02d}</span>
<div>
<div style="font-size:17.5px; font-weight:750; color:#1C1C1E; line-height:1.35; margin-bottom:5px;">{escape(title)}</div>
<div style="font-size:14.5px; color:#2C2C2E; line-height:1.6; font-weight:500;">{escape(summary)}</div>
</div>
</div>
<div style="text-align:right; min-width:115px; margin-left:16px;">
<div style="font-size:11px; font-weight:750; color:#4A4A4F; text-transform:uppercase; letter-spacing:0.5px;">Evidence Strength</div>
<div style="margin-top:3px;">{dots_str}</div>
</div>
</div>
{detail_html}
</div>"""


def render_perspectives_section(optimistic: str, balanced: str, skeptical: str) -> str:
    """Renders 3 visually distinct perspective cards (Green, Yellow, Red)."""
    return f"""<div class="perspectives-grid">
<div class="perspective-col-card" style="border-top:3.5px solid #047857;">
<div style="margin-bottom:14px;">
<span class="persp-badge-optimistic">🟢 Optimistic Perspective</span>
</div>
<div style="font-size:14.5px; color:#1C1C1E; line-height:1.65; font-weight:450;">
{escape(optimistic)}
</div>
</div>

<div class="perspective-col-card" style="border-top:3.5px solid #92400E;">
<div style="margin-bottom:14px;">
<span class="persp-badge-balanced">🟡 Balanced Perspective</span>
</div>
<div style="font-size:14.5px; color:#1C1C1E; line-height:1.65; font-weight:450;">
{escape(balanced)}
</div>
</div>

<div class="perspective-col-card" style="border-top:3.5px solid #9F1239;">
<div style="margin-bottom:14px;">
<span class="persp-badge-skeptical">🔴 Skeptical Perspective</span>
</div>
<div style="font-size:14.5px; color:#1C1C1E; line-height:1.65; font-weight:450;">
{escape(skeptical)}
</div>
</div>
</div>"""


def render_contradiction_card(topic: str, arg_a: str, arg_b: str, synthesis: str) -> str:
    """Renders a visually striking divergence card comparing opposing perspectives."""
    return f"""<div style="background:linear-gradient(135deg, rgba(255,255,255,0.90), rgba(255,255,255,0.76)); border:1px solid rgba(255,255,255,0.95); border-radius:18px; padding:24px; box-shadow:var(--clay-card); margin-bottom:20px;">
<div style="display:flex; align-items:center; gap:8px; margin-bottom:16px;">
<span style="color:#D97706; font-size:18px;">⚡</span>
<span style="font-size:17px; font-weight:800; color:#1C1C1E;">Contradiction Analysis: {escape(topic)}</span>
</div>
<div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px; margin-bottom:16px;">
<div style="background:#FFFFFF; border:1px solid rgba(0,0,0,0.08); border-radius:14px; padding:18px;">
<div style="font-size:11.5px; font-weight:750; color:#0052CC; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px;">Perspective A (Bullish Argument)</div>
<div style="font-size:14px; color:#1C1C1E; line-height:1.6;">{escape(arg_a)}</div>
</div>
<div style="background:#FFFFFF; border:1px solid rgba(0,0,0,0.08); border-radius:14px; padding:18px;">
<div style="font-size:11.5px; font-weight:750; color:#BE123C; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px;">Perspective B (Skeptical Argument)</div>
<div style="font-size:14px; color:#1C1C1E; line-height:1.6;">{escape(arg_b)}</div>
</div>
</div>
<div style="background:#F0F6FF; border-left:3.5px solid #0066FF; border-radius:10px; padding:16px 20px; font-size:14px; color:#1C1C1E; line-height:1.65;">
<b style="color:#0052CC;">Synthesis / Reconciliation:</b> {escape(synthesis)}
</div>
</div>"""


def render_source_card_v2(src: Dict[str, Any]) -> str:
    """Renders a clean, uncluttered source card without raw long URLs."""
    url = escape(src.get("url", ""))
    title = escape(src.get("title") or "Research Document")
    snippet = escape(src.get("snippet", ""))[:200]
    score = int(src.get("source_score", 0.5) * 100)

    # Domain extraction
    domain = url.split("//")[-1].split("/")[0].replace("www.", "")

    # Category determination from domain
    cat_tag = "General Analysis"
    if any(k in url.lower() for k in [".edu", "arxiv", "nature", "science", "ieee", "springer"]):
        cat_tag = "Academic & Research"
    elif ".gov" in url.lower():
        cat_tag = "Government / Standards"
    elif any(k in url.lower() for k in ["bloomberg", "reuters", "wsj", "ft.com", "economist", "cnbc"]):
        cat_tag = "Economic & Financial News"

    return f"""<div style="background:linear-gradient(135deg, rgba(255,255,255,0.90), rgba(255,255,255,0.76)); border:1px solid rgba(255,255,255,0.95); border-radius:16px; padding:20px 24px; margin-bottom:14px; box-shadow:var(--clay-card);">
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; flex-wrap:wrap; gap:8px;">
<div style="display:flex; align-items:center; gap:8px;">
<span style="font-size:13px; font-weight:750; color:#1C1C1E;">{domain}</span>
<span style="background:rgba(0,0,0,0.06); color:#3A3A3C; font-size:11.5px; font-weight:600; padding:3px 9px; border-radius:9999px;">{cat_tag}</span>
</div>
<span style="font-size:12px; font-weight:750; color:#047857; background:#E6F7F0; padding:3px 12px; border-radius:9999px; border:1px solid #A7F3D0;">
Authority: {score}%
</span>
</div>
<div style="font-size:16px; font-weight:750; color:#1C1C1E; line-height:1.4; margin-bottom:6px;">
{title}
</div>
<div style="font-size:13.5px; color:#3A3A3C; line-height:1.6; margin-bottom:14px;">
{snippet}...
</div>
<div>
<a href="{url}" target="_blank" style="display:inline-flex; align-items:center; gap:4px; font-size:13px; font-weight:700; color:#0052CC; text-decoration:none; background:#EBF3FF; border:1px solid #BFDBFE; padding:5px 14px; border-radius:9999px; transition:all 0.2s ease;">
Open Source ↗
</a>
</div>
</div>"""


def render_claim_card(claim_dict: Dict[str, Any], index: int) -> str:
    """Renders a factual claim card with support badge and primary evidence quote."""
    claim = escape(claim_dict.get("claim", ""))
    label = claim_dict.get("support_label", "Supported")
    score = int(claim_dict.get("support_score", 0.8) * 100)
    reasoning = escape(claim_dict.get("reasoning", ""))
    urls = claim_dict.get("source_urls", [])
    chunks = claim_dict.get("evidence_chunks", [])

    badge_color = "#047857"
    badge_bg = "#E6F7F0"
    badge_border = "#A7F3D0"
    if "partially" in label.lower():
        badge_color = "#92400E"
        badge_bg = "#FEF3C7"
        badge_border = "#FDE68A"
    elif "weakly" in label.lower() or "unsupported" in label.lower():
        badge_color = "#9F1239"
        badge_bg = "#FFE4E6"
        badge_border = "#FECDD3"

    source_links = " &bull; ".join(
        f"<a href='{escape(u)}' target='_blank' style='color:#0052CC; font-weight:650; text-decoration:none;'>{escape(u.split('//')[-1][:32])} ↗</a>"
        for u in urls[:2]
    ) if urls else "<span style='color:#6E6E73;'>Vector Store Literature</span>"

    quote_html = ""
    if chunks:
        quote_html = f"""<div style="margin-top:12px; padding:12px 16px; background:rgba(0,0,0,0.04); border-left:3.5px solid #1C1C1E; border-radius:8px; font-size:13px; color:#1C1C1E; line-height:1.6;">
<b style="color:#1C1C1E;">Passage Evidence:</b> "{escape(chunks[0][:260])}..."
</div>"""

    return f"""<div style="background:linear-gradient(135deg, rgba(255,255,255,0.90), rgba(255,255,255,0.76)); border:1px solid rgba(255,255,255,0.95); border-radius:16px; padding:20px 24px; margin-bottom:14px; box-shadow:var(--clay-card);">
<div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px; gap:12px;">
<div style="font-size:15.5px; font-weight:750; color:#1C1C1E; line-height:1.4;">
<span style="color:#6E6E73; font-family:'Newsreader', serif; font-size:18px; margin-right:4px;">{index:02d}.</span> {claim}
</div>
<span style="color:{badge_color}; background:{badge_bg}; border:1px solid {badge_border}; font-size:12px; font-weight:750; padding:3px 12px; border-radius:9999px; white-space:nowrap;">
{escape(label)} &bull; {score}%
</span>
</div>
<div style="font-size:13.5px; color:#2C2C2E; line-height:1.55; margin-bottom:8px;">
<b style="color:#1C1C1E;">Verification Rationale:</b> {reasoning}
</div>
<div style="font-size:12px; color:#4A4A4F;">
<b style="color:#1C1C1E;">Citations:</b> {source_links}
</div>
{quote_html}
</div>"""
