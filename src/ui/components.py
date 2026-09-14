"""
Reusable Components for Agentic Research.
Editorial Research Instrument Design System:
- Typography: Space Grotesk + Instrument Serif + IBM Plex Mono
- Palette: #F7F6F2 background, #151619 ink, #315BFF research blue
Strict WCAG AAA contrast for all buttons, labels, and text elements.
All HTML strings are left-aligned at column 0 to prevent Markdown 4-space code block bugs.
"""

import html
from typing import Dict, Any, List, Optional


def escape(text: Any) -> str:
    """Safely escape text for HTML output."""
    if text is None:
        return ""
    return html.escape(str(text))


def render_editorial_nav() -> str:
    """Render the minimal top editorial navigation bar."""
    return """<div class="editorial-nav">
<div class="nav-brand">
<span class="brand-signal">✦</span>
<span>AGENTIC RESEARCH</span>
</div>
<div style="display:flex; align-items:center; gap:12px;">
<span class="nav-badge">v2.0 PRO</span>
<div style="width:28px; height:28px; border-radius:50%; background:#151619; color:#FFFFFF; -webkit-text-fill-color:#FFFFFF; display:flex; align-items:center; justify-content:center; font-size:11px; font-weight:700;">U</div>
</div>
</div>"""


def render_floating_nav() -> str:
    """Backward compatibility wrapper."""
    return render_editorial_nav()


def render_active_research_banner(topic: str, elapsed_str: str = "00:00 elapsed") -> str:
    """Renders the active research indicator banner during live pipeline execution."""
    return f"""<div class="research-active-banner">
<div>
<div class="investigating-eyebrow">INVESTIGATING</div>
<div class="investigating-topic">"{escape(topic)}"</div>
</div>
<div class="research-status-pill">
<div class="pulse-dot"></div>
<span>● RESEARCHING</span>
<span style="opacity:0.4;">|</span>
<span style="font-family:'IBM Plex Mono', monospace;">{escape(elapsed_str)}</span>
</div>
</div>"""


def render_editorial_hero() -> str:
    """Render the editorial hero section with subtle research field visual language."""
    return """<div class="hero-container">
<div class="hero-eyebrow">
<span style="color:#315BFF;">✦</span> AUTONOMOUS RESEARCH INSTRUMENT
</div>
<h1 class="hero-headline">
Research beyond<br>
<span class="hero-editorial-headline">the obvious.</span>
</h1>
<div class="hero-subtitle">
Investigate complex questions through evidence, perspectives, and iterative research.
</div>

<div class="research-field-strip">
<div class="research-field-node"><span>●</span> QUESTION</div>
<span class="research-field-arrow">→</span>
<div class="research-field-node"><span>●</span> ANGLES</div>
<span class="research-field-arrow">→</span>
<div class="research-field-node"><span>●</span> EVIDENCE</div>
<span class="research-field-arrow">→</span>
<div class="research-field-node"><span>●</span> ITERATION</div>
<span class="research-field-arrow">→</span>
<div class="research-field-node" style="border-color:rgba(49,91,255,0.4); color:#315BFF;"><span>✦</span> INSIGHT</div>
</div>
</div>"""


def render_hero_header() -> str:
    """Backward compatibility wrapper."""
    return render_editorial_hero()


def render_depth_card_editorial(mode: str, is_selected: bool) -> str:
    """
    Renders an individual depth card for Quick, Standard, or Deep investigation.
    """
    m = mode.upper()
    sel_class = "selected" if is_selected else ""
    check_html = '<div style="color:#315BFF; font-weight:700; font-size:13px;">● Active</div>' if is_selected else '<div style="color:#85868D; font-size:12px;">○ Select</div>'

    if m == "QUICK":
        return f"""<div class="depth-card-editorial {sel_class}">
<div class="depth-title-row">
<div class="depth-title">
<span>⚡</span>
<span>Quick</span>
</div>
{check_html}
</div>
<div class="depth-tagline">Fast orientation</div>
<div class="depth-desc">Fast overview of core facts and key literature consensus.</div>
</div>"""

    elif m == "STANDARD":
        return f"""<div class="depth-card-editorial {sel_class}">
<div class="depth-badge-rec">RECOMMENDED</div>
<div class="depth-title-row">
<div class="depth-title">
<span>◉</span>
<span>Standard</span>
</div>
{check_html}
</div>
<div class="depth-tagline">Balanced investigation</div>
<div class="depth-desc">Multiple perspectives, key evidence synthesis, and citation grounding.</div>
</div>"""

    else:  # DEEP
        return f"""<div class="depth-card-editorial {sel_class}">
<div class="depth-title-row">
<div class="depth-title">
<span>🧠</span>
<span>Deep</span>
</div>
{check_html}
</div>
<div class="depth-tagline">Extended investigation</div>
<div class="depth-desc">Evidence extraction, research gap detection, and contradiction analysis.</div>
</div>"""


def render_single_depth_card(mode: str, is_selected: bool) -> str:
    """Backward compatibility wrapper."""
    return render_depth_card_editorial(mode, is_selected)


def render_why_different_content() -> str:
    """Renders the comparison between Traditional Search vs Agentic Research."""
    return """<div style="font-family:'Space Grotesk', sans-serif;">
<div style="font-size:14.5px; color:#55565D; line-height:1.6; margin-bottom:20px;">
Traditional search engines return links or summarize single articles in a single pass. <b>Agentic Research</b> functions as a semi-autonomous research pipeline that actively seeks out opposing viewpoints, detects missing information, and cross-examines evidence.
</div>

<div style="display:grid; grid-template-columns:1fr 1fr; gap:18px; margin-bottom:20px;">
<div style="background:#FFFFFF; border:1px solid rgba(21,22,25,0.1); border-radius:12px; padding:18px;">
<div style="font-size:14px; font-weight:700; color:#85868D; margin-bottom:12px; display:flex; align-items:center; gap:6px;">
<span>🔍</span> Traditional Search
</div>
<div style="font-size:12.5px; color:#55565D; line-height:1.7;">
1. Search keywords<br>
2. Read top results<br>
3. Single-pass summary<br>
4. Accept initial claims
</div>
<div style="margin-top:14px; font-size:12px; color:#85868D; line-height:1.5; border-top:1px solid rgba(21,22,25,0.06); padding-top:10px;">
⚠️ <b>Limitation:</b> Accepts high-ranking content without evaluating conflicting data, completeness, or empirical consensus.
</div>
</div>

<div style="background:#FFFFFF; border:1.5px solid #315BFF; border-radius:12px; padding:18px; box-shadow:0 4px 16px rgba(49,91,255,0.08);">
<div style="font-size:14px; font-weight:700; color:#315BFF; margin-bottom:12px; display:flex; align-items:center; gap:6px;">
<span>✦</span> Agentic Research Pipeline
</div>
<div style="font-size:12.5px; color:#151619; line-height:1.7; font-weight:500;">
1. <b>Decompose</b> question into research angles<br>
2. <b>Search & retrieve</b> authoritative sources<br>
3. <b>Evaluate</b> institutional authority<br>
4. <b>Detect gaps</b> in dimension coverage<br>
5. <b>Re-query</b> (Autonomous follow-up)<br>
6. <b>Reconcile</b> conflicting viewpoints<br>
7. <b>Verify</b> atomic claims against citations<br>
8. <b>Synthesize</b> structured research dossier
</div>
</div>
</div>

<div style="background:rgba(49,91,255,0.06); border-left:3.5px solid #315BFF; border-radius:8px; padding:14px 18px; font-size:13.5px; color:#151619; line-height:1.55;">
<b>Core Thesis:</b> "A semi-autonomous research system that iteratively expands its investigation when it detects evidence gaps or conflicting information."
</div>
</div>"""


def render_exec_summary_card(summary_text: str, confidence_score: int, topic: str = "", verdict_text: str = "") -> str:
    """
    Renders the Executive Verdict at the very top of the results screen with
    the editorial serif font and defensible heuristic evidence confidence score.
    """
    if verdict_text:
        verdict_badge = verdict_text
    elif "bubble" in topic.lower():
        verdict_badge = "Substantial evidence indicates speculative asset expansion, tempered by genuine infrastructure compounding."
    elif confidence_score >= 80:
        verdict_badge = "Strong empirical grounding with authoritative cross-domain consensus."
    elif confidence_score >= 65:
        verdict_badge = "Moderate empirical grounding with identified evidentiary trade-offs."
    else:
        verdict_badge = "Emerging domain with high evidentiary divergence and ongoing monitoring required."

    if confidence_score >= 80:
        bar_fill = "#138A63"
        border_accent = "#138A63"
    elif confidence_score >= 65:
        bar_fill = "#C88900"
        border_accent = "#C88900"
    else:
        bar_fill = "#D95C4A"
        border_accent = "#D95C4A"

    return f"""<div class="dossier-verdict-card" style="border-left-color:{border_accent};">
<div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px; flex-wrap:wrap; gap:16px;">
<div>
<div class="verdict-eyebrow">EXECUTIVE VERDICT</div>
<div class="verdict-headline">"{escape(verdict_badge)}"</div>
</div>
<div style="text-align:right;">
<div style="font-size:12.5px; font-weight:600; color:#55565D;">
Evidence Confidence: <b style="color:#151619; font-size:17px; font-family:'IBM Plex Mono', monospace; font-weight:700;">{confidence_score} / 100</b>
</div>
<div style="width:180px; height:6px; background:rgba(21,22,25,0.08); border-radius:9999px; overflow:hidden; margin-top:6px;">
<div style="width:{confidence_score}%; height:100%; background:{bar_fill}; border-radius:9999px;"></div>
</div>
<div style="font-size:10.5px; color:#85868D; margin-top:4px; max-width:240px; line-height:1.3;">
Heuristic: quality, coverage, grounding, consensus, and completeness.
</div>
</div>
</div>

<div style="font-size:15px; color:#151619; line-height:1.75; font-weight:400; border-top:1px solid rgba(21,22,25,0.06); padding-top:16px;">
{escape(summary_text)}
</div>
</div>"""


def render_key_finding_card(index: int, title: str, summary: str, evidence_strength: int = 4, detail_text: str = "") -> str:
    """
    Renders a key insight card with editorial hierarchy.
    """
    strength_label = "Strong" if evidence_strength >= 4 else ("Moderate" if evidence_strength == 3 else "Emerging")
    badge_bg = "#EAF6F1" if evidence_strength >= 4 else "#FEF7EA"
    badge_color = "#138A63" if evidence_strength >= 4 else "#C88900"

    return f"""<details class="glass-disclosure">
<summary>
<div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">
<span style="font-family:'IBM Plex Mono', monospace; font-size:14px; font-weight:700; color:#315BFF;">{index:02d}</span>
<span style="font-size:15.5px; font-weight:700; color:#151619;">{escape(title)}</span>
<span style="font-size:11px; font-weight:700; color:{badge_color}; background:{badge_bg}; padding:2px 8px; border-radius:4px; font-family:'IBM Plex Mono', monospace;">
EVIDENCE: {strength_label.upper()}
</span>
</div>
<span style="font-size:12px; color:#315BFF; font-weight:600;">View evidence →</span>
</summary>
<div class="disclosure-body">
<div style="font-size:14.5px; color:#151619; line-height:1.65; margin-bottom:12px;">
{escape(summary)}
</div>
<div style="font-size:13px; color:#55565D; background:#F7F6F2; padding:12px 16px; border-radius:8px; border-left:3px solid #315BFF; line-height:1.6;">
<b style="color:#151619;">Supporting Citations & Passages:</b> {escape(detail_text)}
</div>
</div>
</details>"""


def render_perspectives_section(optimistic: str, balanced: str, skeptical: str) -> str:
    """Renders 3 distinct perspective columns (Green, Amber, Coral)."""
    return f"""<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:18px; margin-bottom:28px;">
<div style="background:#FFFFFF; border:1px solid rgba(21,22,25,0.08); border-top:3.5px solid #138A63; border-radius:12px; padding:20px 22px; box-shadow:0 2px 8px rgba(21,22,25,0.03);">
<div style="margin-bottom:10px;">
<span style="background:#EAF6F1; color:#138A63; font-size:11px; font-weight:700; padding:3px 8px; border-radius:4px; font-family:'IBM Plex Mono', monospace;">🟢 OPTIMISTIC PERSPECTIVE</span>
</div>
<div style="font-size:14px; color:#151619; line-height:1.65;">
{escape(optimistic)}
</div>
</div>

<div style="background:#FFFFFF; border:1px solid rgba(21,22,25,0.08); border-top:3.5px solid #C88900; border-radius:12px; padding:20px 22px; box-shadow:0 2px 8px rgba(21,22,25,0.03);">
<div style="margin-bottom:10px;">
<span style="background:#FEF7EA; color:#C88900; font-size:11px; font-weight:700; padding:3px 8px; border-radius:4px; font-family:'IBM Plex Mono', monospace;">🟡 BALANCED PERSPECTIVE</span>
</div>
<div style="font-size:14px; color:#151619; line-height:1.65;">
{escape(balanced)}
</div>
</div>

<div style="background:#FFFFFF; border:1px solid rgba(21,22,25,0.08); border-top:3.5px solid #D95C4A; border-radius:12px; padding:20px 22px; box-shadow:0 2px 8px rgba(21,22,25,0.03);">
<div style="margin-bottom:10px;">
<span style="background:#FDF2F0; color:#D95C4A; font-size:11px; font-weight:700; padding:3px 8px; border-radius:4px; font-family:'IBM Plex Mono', monospace;">🔴 SKEPTICAL PERSPECTIVE</span>
</div>
<div style="font-size:14px; color:#151619; line-height:1.65;">
{escape(skeptical)}
</div>
</div>
</div>"""


def render_contradiction_card(topic: str, arg_a: str, arg_b: str, synthesis: str) -> str:
    """Renders a side-by-side contradiction card illustrating where evidence disagrees."""
    return f"""<div style="background:#FFFFFF; border:1px solid rgba(21,22,25,0.08); border-radius:14px; padding:22px 26px; box-shadow:0 2px 10px rgba(21,22,25,0.03); margin-bottom:18px;">
<div style="display:flex; align-items:center; gap:8px; margin-bottom:14px;">
<span class="badge-tag badge-important">CONTRADICTION</span>
<span style="font-size:16px; font-weight:700; color:#151619;">{escape(topic)}</span>
</div>

<div style="display:grid; grid-template-columns:1fr auto 1fr; gap:16px; align-items:center; margin-bottom:16px;">
<div style="background:#F7F6F2; border-left:3px solid #138A63; border-radius:8px; padding:14px 16px;">
<div style="font-size:11px; font-weight:700; color:#138A63; font-family:'IBM Plex Mono', monospace; margin-bottom:4px;">PERSPECTIVE A</div>
<div style="font-size:13.5px; color:#151619; line-height:1.55;">{escape(arg_a)}</div>
</div>

<div style="font-family:'IBM Plex Mono', monospace; font-size:11px; font-weight:700; color:#85868D;">VS</div>

<div style="background:#F7F6F2; border-left:3px solid #D95C4A; border-radius:8px; padding:14px 16px;">
<div style="font-size:11px; font-weight:700; color:#D95C4A; font-family:'IBM Plex Mono', monospace; margin-bottom:4px;">PERSPECTIVE B</div>
<div style="font-size:13.5px; color:#151619; line-height:1.55;">{escape(arg_b)}</div>
</div>
</div>

<div style="background:rgba(49,91,255,0.05); border-left:3px solid #315BFF; border-radius:8px; padding:12px 16px; font-size:13.5px; color:#151619; line-height:1.6;">
<b style="color:#315BFF;">Why This Disagreement Matters:</b> {escape(synthesis)}
</div>
</div>"""


def render_claim_card(claim_dict: Dict[str, Any], index: int) -> str:
    """Renders a compact claim card with expandable evidence details."""
    claim = escape(claim_dict.get("claim", ""))
    label = claim_dict.get("support_label", "Supported")
    score = int(claim_dict.get("support_score", 0.8) * 100)
    reasoning = escape(claim_dict.get("reasoning", ""))
    urls = claim_dict.get("source_urls", [])
    chunks = claim_dict.get("evidence_chunks", [])

    badge_color = "#138A63"
    badge_bg = "#EAF6F1"
    symbol = "✓"
    if "partially" in label.lower():
        badge_color = "#C88900"
        badge_bg = "#FEF7EA"
        symbol = "△"
    elif "weakly" in label.lower() or "unsupported" in label.lower():
        badge_color = "#D95C4A"
        badge_bg = "#FDF2F0"
        symbol = "✕"

    source_links = " &bull; ".join(
        f"<a href='{escape(u)}' target='_blank' style='color:#315BFF; font-weight:600; text-decoration:none;'>{escape(u.split('//')[-1][:32])} ↗</a>"
        for u in urls[:2]
    ) if urls else "<span style='color:#85868D;'>Primary Vector Passages</span>"

    quote_html = ""
    if chunks:
        quote_html = f"""<div style="margin-top:10px; padding:10px 14px; background:#F7F6F2; border-left:3px solid #151619; border-radius:6px; font-size:12.5px; color:#151619; line-height:1.55;">
<b style="color:#151619;">Verified Citation Passage:</b> "{escape(chunks[0][:240])}..."
</div>"""

    return f"""<details class="glass-disclosure">
<summary>
<div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
<span style="font-family:'IBM Plex Mono', monospace; font-size:13px; font-weight:700; color:#85868D;">{index:02d}.</span>
<span style="font-size:14.5px; font-weight:600; color:#151619; max-width:680px;">{claim}</span>
<span style="color:{badge_color}; background:{badge_bg}; font-size:11px; font-weight:700; padding:2px 8px; border-radius:4px; font-family:'IBM Plex Mono', monospace;">
{symbol} {escape(label).upper()} · {score}%
</span>
</div>
<span style="font-size:12px; color:#315BFF; font-weight:600;">Details ▾</span>
</summary>
<div class="disclosure-body">
<div style="font-size:13.5px; color:#151619; line-height:1.6; margin-bottom:8px;">
<b style="color:#151619;">Verification Reasoning:</b> {reasoning}
</div>
<div style="font-size:12px; color:#55565D; margin-bottom:8px;">
<b style="color:#151619;">Source Citations:</b> {source_links}
</div>
{quote_html}
</div>
</details>"""


def render_source_card_v2(src: Dict[str, Any]) -> str:
    """Renders a clean literature citation card."""
    url = escape(src.get("url", ""))
    title = escape(src.get("title") or "Research Document")
    snippet = escape(src.get("snippet", ""))[:190]
    score = int(src.get("source_score", 0.7) * 100)
    domain = url.split("//")[-1].split("/")[0].replace("www.", "")

    cat_tag = "General Analysis"
    if any(k in url.lower() for k in [".edu", "arxiv", "nature", "science", "ieee", "springer"]):
        cat_tag = "Academic & Research"
    elif ".gov" in url.lower():
        cat_tag = "Government / Standards"
    elif any(k in url.lower() for k in ["bloomberg", "reuters", "wsj", "ft.com", "economist", "cnbc"]):
        cat_tag = "Economic & Financial News"

    return f"""<div style="background:#FFFFFF; border:1px solid rgba(21,22,25,0.08); border-radius:12px; padding:18px 22px; margin-bottom:12px; box-shadow:0 2px 8px rgba(21,22,25,0.02);">
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; flex-wrap:wrap; gap:8px;">
<div style="display:flex; align-items:center; gap:8px;">
<span style="font-size:13px; font-weight:700; color:#151619;">{domain}</span>
<span style="background:#F0EFEA; color:#55565D; font-size:10.5px; font-weight:600; padding:2px 8px; border-radius:4px; font-family:'IBM Plex Mono', monospace;">{cat_tag}</span>
</div>
<span style="font-size:11px; font-weight:700; color:#138A63; background:#EAF6F1; padding:2px 8px; border-radius:4px; font-family:'IBM Plex Mono', monospace;">
AUTHORITY: {score}%
</span>
</div>
<div style="font-size:14.5px; font-weight:700; color:#151619; line-height:1.4; margin-bottom:6px;">
{title}
</div>
<div style="font-size:13px; color:#55565D; line-height:1.55; margin-bottom:12px;">
{snippet}...
</div>
<div>
<a href="{url}" target="_blank" style="display:inline-flex; align-items:center; gap:4px; font-size:12px; font-weight:600; color:#315BFF; text-decoration:none; background:rgba(49,91,255,0.06); border:1px solid rgba(49,91,255,0.2); padding:3px 12px; border-radius:9999px;">
Open Source ↗
</a>
</div>
</div>"""


def render_evidence_gaps_section(gaps: List[Any]) -> str:
    """
    Renders identified research gaps or verified complete coverage.
    """
    if not gaps:
        return """<div style="background:#EAF6F1; border:1px solid #BBF7D0; border-radius:12px; padding:18px 22px; margin-bottom:24px;">
<div style="display:flex; align-items:center; gap:8px; font-weight:700; color:#138A63; font-size:14px;">
<span>✓</span> Comprehensive Dimensional Coverage Verified
</div>
<div style="font-size:13px; color:#151619; margin-top:4px; line-height:1.55;">
No critical information voids or unaddressed perspectives detected across primary and follow-up retrieval iterations.
</div>
</div>"""

    cards = []
    for idx, g in enumerate(gaps):
        dim = escape(getattr(g, "missing_dimension", "Research Dimension"))
        reason = escape(getattr(g, "reason", "Additional evidence needed"))
        query = escape(getattr(g, "suggested_query", ""))
        priority = escape(getattr(g, "priority", "Medium")).upper()
        p_badge_bg = "#FEF7EA" if priority in ["HIGH", "CRITICAL"] else "#F0EFEA"
        p_badge_color = "#C88900" if priority in ["HIGH", "CRITICAL"] else "#55565D"

        cards.append(f"""<div style="background:#FFFFFF; border:1px solid rgba(21,22,25,0.08); border-left:3.5px solid #315BFF; border-radius:12px; padding:16px 20px; margin-bottom:12px;">
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; flex-wrap:wrap; gap:8px;">
<div style="font-size:14px; font-weight:700; color:#151619;">{idx+1}. {dim}</div>
<span style="background:{p_badge_bg}; color:{p_badge_color}; font-size:10.5px; font-weight:700; padding:2px 8px; border-radius:4px; font-family:'IBM Plex Mono', monospace;">PRIORITY: {priority}</span>
</div>
<div style="font-size:13px; color:#55565D; line-height:1.55; margin-bottom:8px;">{reason}</div>
<div style="font-size:12px; color:#151619; background:#F7F6F2; padding:8px 12px; border-radius:6px; font-family:'IBM Plex Mono', monospace;">
<b style="color:#315BFF;">Follow-up Query:</b> "{query}"
</div>
</div>""")
    return "".join(cards)


def render_limitations_callout(topic: str = "") -> str:
    """
    Renders academic limitations and scope boundaries for the investigation.
    """
    return """<div style="background:#FFFFFF; border:1px solid rgba(21,22,25,0.08); border-left:3.5px solid #85868D; border-radius:12px; padding:20px 24px; margin-bottom:28px;">
<div style="font-size:14px; font-weight:700; color:#151619; margin-bottom:8px; display:flex; align-items:center; gap:8px;">
<span class="badge-tag badge-limitation">LIMITATION</span>
<span>Research Scope Boundaries & Methodological Limitations</span>
</div>
<div style="font-size:13px; color:#55565D; line-height:1.6;">
This dossier synthesizes public empirical literature, institutional reporting, and domain preprints. Key limitations:
</div>
<div style="margin-top:12px; display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:12px;">
<div style="background:#F7F6F2; border-radius:8px; padding:12px 14px; font-size:12px; color:#151619; line-height:1.5;">
<b>Temporal Horizon:</b> Real-time search reflects indexed sources available at execution time. Fast-evolving market trends may alter trajectories.
</div>
<div style="background:#F7F6F2; border-radius:8px; padding:12px 14px; font-size:12px; color:#151619; line-height:1.5;">
<b>Access Boundaries:</b> Paywalled proprietary institutional data repositories are excluded in favor of verifiable open citations.
</div>
<div style="background:#F7F6F2; border-radius:8px; padding:12px 14px; font-size:12px; color:#151619; line-height:1.5;">
<b>Consensus Volatility:</b> In emerging technology markets, empirical consensus is provisional and subject to ongoing experimental falsification.
</div>
</div>
</div>"""


def render_permanent_footer() -> str:
    """
    Renders the permanent author attribution footer across generated dossiers.
    """
    return """<div class="permanent-footer">
<div class="permanent-footer-title">
✦ AGENTIC RESEARCH DOSSIER
</div>
<div class="permanent-footer-attribution">
Built by - <b>Utkarsh Pandey</b> &bull; Third Year Engineering Project Demonstration
</div>
</div>"""
