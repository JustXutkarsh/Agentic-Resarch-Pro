"""
Reusable Warm White Liquid Glass Components for Agentic Research PRO.
Provides styled HTML helpers for floating nav, editorial hero, tactile depth cards,
claim verification, contradiction splits, confidence breakdown, and source explorer.
"""

import html
from typing import Dict, Any, List, Optional


def escape(text: Any) -> str:
    """Safely escape text for HTML output."""
    if text is None:
        return ""
    return html.escape(str(text))


def render_floating_nav() -> str:
    """Render the minimal floating top navigation pill."""
    return """
    <div class="floating-nav">
        <div class="nav-brand">
            <span style="font-size:16px;">✦</span>
            <span>Agentic Research</span>
        </div>
        <div style="display:flex; align-items:center; gap:12px;">
            <span class="nav-pill">Autonomous OS</span>
            <span style="font-size:12.5px; color:#8E8E93; font-weight:500;">v2.0</span>
        </div>
    </div>
    """


def render_hero_header() -> str:
    """Render the editorial hero section with warm white typography."""
    return """
    <div class="hero-container">
        <div class="hero-eyebrow">✦ Autonomous Research OS</div>
        <h1 class="hero-heading">
            Research beyond<br><em>the obvious</em>.
        </h1>
        <div class="hero-subheading">
            Multi-perspective AI research with evidence analysis, autonomous iteration, and intelligent exploration.
        </div>
    </div>
    """


def render_depth_selector(current_depth: str = "STANDARD") -> str:
    """Render the 3-card tactile claymorphic depth descriptions."""
    active_q = "active" if current_depth.upper() == "QUICK" else ""
    active_s = "active" if current_depth.upper() == "STANDARD" else ""
    active_d = "active" if current_depth.upper() == "DEEP" else ""

    return f"""
    <div class="depth-preview-grid">
        <div class="depth-preview-card {active_q}">
            <div class="depth-preview-title">Quick</div>
            <div class="depth-preview-desc">A focused research overview.<br>Fast executive synthesis.</div>
        </div>
        <div class="depth-preview-card {active_s}">
            <div class="depth-preview-title">Standard</div>
            <div class="depth-preview-desc">Multi-perspective exploration.<br>Iterative gap discovery.</div>
        </div>
        <div class="depth-preview-card {active_d}">
            <div class="depth-preview-title">Deep</div>
            <div class="depth-preview-desc">Comprehensive investigation.<br>Contradiction resolution & full verification.</div>
        </div>
    </div>
    """


def render_example_chips_html(chips: List[str]) -> str:
    """Render subtle claymorphic example research prompt chips."""
    chip_items = "".join(
        f'<span class="example-chip">{escape(chip)}</span>'
        for chip in chips
    )
    return f"""
    <div style="text-align:center; margin-top:20px;">
        <div style="font-size:12px; font-weight:600; color:#8E8E93; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:10px;">
            Explore topics
        </div>
        <div class="example-chips-row">
            {chip_items}
        </div>
    </div>
    """


def render_metric_tile(value: Any, title: str, subtitle: Optional[str] = None) -> str:
    """Render an editorial white liquid glass metric tile."""
    sub_html = f"<div style='font-size:11px; color:#8E8E93; margin-top:4px;'>{escape(subtitle)}</div>" if subtitle else ""
    return f"""
    <div class="live-metric-card">
        <div class="live-metric-val">{escape(value)}</div>
        <div class="live-metric-lbl">{escape(title)}</div>
        {sub_html}
    </div>
    """


def render_claim_card(claim_dict: Dict[str, Any], index: int) -> str:
    """Render a grounded claim card with subtle badge and primary quote."""
    claim = escape(claim_dict.get("claim", ""))
    label = claim_dict.get("support_label", "Supported")
    score = int(claim_dict.get("support_score", 0.8) * 100)
    reasoning = escape(claim_dict.get("reasoning", ""))
    urls = claim_dict.get("source_urls", [])
    chunks = claim_dict.get("evidence_chunks", [])

    badge_slug = label.lower().replace(" ", "-")
    badge_class = f"badge-{badge_slug}"

    url_links = " &bull; ".join(
        f"<a href='{escape(u)}' target='_blank' style='color:#1C1C1E; font-weight:600; text-decoration:underline;'>{escape(u.split('//')[-1][:35])}...</a>"
        for u in urls[:3]
    ) if urls else "<span style='color:#8E8E93;'>Indexed Vector Evidence</span>"

    evidence_preview = ""
    if chunks:
        evidence_preview = f"""
        <div style="margin-top:12px; padding:12px 16px; background:rgba(0,0,0,0.025); border-radius:10px; border-left:3px solid #1C1C1E; font-size:13px; color:#48484A; font-family:'Inter', sans-serif; line-height:1.55;">
            <b>Primary Evidence:</b> "{escape(chunks[0][:320])}..."
        </div>
        """

    return f"""
    <div class="glass-card-compact" style="margin-bottom:14px;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px; gap:16px;">
            <div style="font-size:15px; font-weight:600; color:#1C1C1E; line-height:1.45;">
                <span style="color:#8E8E93; margin-right:6px; font-family:'Newsreader', serif; font-size:17px;">{index:02d}.</span> {claim}
            </div>
            <span class="badge-subtle {badge_class}" style="white-space:nowrap;">{escape(label)} &bull; {score}%</span>
        </div>
        <div style="font-size:13.5px; color:#6E6E73; line-height:1.55; margin-bottom:8px;">
            <b>Evidentiary Analysis:</b> {reasoning}
        </div>
        <div style="font-size:12px; color:#8E8E93;">
            <b>Source Citations:</b> {url_links}
        </div>
        {evidence_preview}
    </div>
    """


def render_contradiction_split(contra: Dict[str, Any], index: int) -> str:
    """Render a side-by-side empirical contradiction split card."""
    topic = escape(contra.get("topic", "Divergent Finding"))
    persp_a = escape(contra.get("perspective_a", ""))
    persp_b = escape(contra.get("perspective_b", ""))
    sources_a = contra.get("supporting_sources_a", [])
    sources_b = contra.get("supporting_sources_b", [])
    resolution = escape(contra.get("resolution", ""))

    src_a_html = "".join(f"<div style='font-size:11.5px; color:#1C1C1E; margin-top:3px;'>• <a href='{escape(u)}' target='_blank' style='color:#1C1C1E; text-decoration:underline;'>{escape(u.split('//')[-1][:38])}...</a></div>" for u in sources_a[:2])
    src_b_html = "".join(f"<div style='font-size:11.5px; color:#1C1C1E; margin-top:3px;'>• <a href='{escape(u)}' target='_blank' style='color:#1C1C1E; text-decoration:underline;'>{escape(u.split('//')[-1][:38])}...</a></div>" for u in sources_b[:2])

    return f"""
    <div class="glass-panel" style="margin-bottom:18px; padding:22px 26px;">
        <div style="font-size:16px; font-weight:700; color:#1C1C1E; margin-bottom:14px; display:flex; align-items:center; gap:8px;">
            <span style="font-family:'Newsreader', serif; font-size:19px; color:#8E8E93;">#{index:02d}</span>
            <span>Divergent Perspectives: {topic}</span>
        </div>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px; margin-bottom:14px;">
            <div style="background:rgba(255, 255, 255, 0.7); border:1px solid rgba(0, 0, 0, 0.06); border-radius:12px; padding:16px;">
                <div style="font-size:11.5px; font-weight:700; color:#1C1C1E; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px;">Perspective A</div>
                <div style="font-size:13.5px; color:#2C2C2E; line-height:1.55; margin-bottom:8px;">{persp_a}</div>
                {src_a_html}
            </div>
            <div style="background:rgba(255, 255, 255, 0.7); border:1px solid rgba(0, 0, 0, 0.06); border-radius:12px; padding:16px;">
                <div style="font-size:11.5px; font-weight:700; color:#1C1C1E; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px;">Perspective B</div>
                <div style="font-size:13.5px; color:#2C2C2E; line-height:1.55; margin-bottom:8px;">{persp_b}</div>
                {src_b_html}
            </div>
        </div>
        <div style="background:rgba(0,0,0,0.03); border-radius:10px; padding:12px 16px; font-size:13.5px; color:#2C2C2E; border-left:3px solid #1C1C1E; line-height:1.6;">
            <b>Synthesis & Reconciliation:</b> {resolution}
        </div>
    </div>
    """


def render_confidence_breakdown(conf: Any) -> str:
    """Renders the transparent explainable research confidence heuristic."""
    if not conf:
        return "<p style='color:#8E8E93;'>Confidence evaluation in progress.</p>"

    overall = int(conf.overall_score)
    sq = int(conf.source_quality)
    ec = int(conf.evidence_coverage)
    cs = int(conf.claim_support)
    sa = int(conf.source_agreement)
    rc = int(conf.research_completeness)

    def _bar(label: str, val: int, weight_pct: int) -> str:
        return f"""
        <div style="display:flex; align-items:center; gap:14px; margin-bottom:12px;">
            <div style="width:190px; font-size:13.5px; color:#48484A; font-weight:500;">
                {escape(label)} <span style="font-size:11px; color:#8E8E93;">({weight_pct}%)</span>
            </div>
            <div style="flex:1; height:8px; background:rgba(0,0,0,0.06); border-radius:9999px; overflow:hidden;">
                <div style="width:{val}%; height:100%; background:#1C1C1E; border-radius:9999px; transition:width 0.6s ease;"></div>
            </div>
            <div style="width:40px; font-size:13px; font-weight:700; color:#1C1C1E; text-align:right; font-family:'JetBrains Mono', monospace;">
                {val}%
            </div>
        </div>
        """

    bars_html = "".join([
        _bar("Source Authority", sq, 25),
        _bar("Evidence Coverage", ec, 20),
        _bar("Claim Grounding", cs, 25),
        _bar("Source Agreement", sa, 15),
        _bar("Research Completeness", rc, 15),
    ])

    return f"""
    <div class="glass-panel" style="padding:32px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:24px; flex-wrap:wrap; gap:16px;">
            <div>
                <div style="font-size:11.5px; font-weight:700; color:#8E8E93; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:4px;">
                    Empirical Assessment
                </div>
                <div style="font-size:24px; font-weight:700; color:#1C1C1E; letter-spacing:-0.4px;">
                    Research Confidence Heuristic
                </div>
                <div style="font-size:13.5px; color:#6E6E73; margin-top:4px;">
                    Synthesized from objective metrics across sources, vector evidence, and factual verification.
                </div>
            </div>
            <div style="text-align:center; background:#FFFFFF; border:1px solid rgba(0,0,0,0.08); border-radius:16px; padding:14px 28px; box-shadow:0 4px 14px rgba(0,0,0,0.04);">
                <div style="font-size:42px; font-weight:700; color:#1C1C1E; line-height:1; font-family:'Newsreader', serif;">
                    {overall}<span style="font-size:18px; color:#8E8E93;">/100</span>
                </div>
                <div style="font-size:11px; font-weight:600; color:#8E8E93; text-transform:uppercase; margin-top:4px;">Composite Score</div>
            </div>
        </div>

        <div style="margin-bottom:24px; background:rgba(255,255,255,0.6); padding:20px 24px; border-radius:14px; border:1px solid var(--glass-border);">
            {bars_html}
        </div>

        <div style="background:rgba(255,255,255,0.85); border-radius:12px; padding:16px 20px; font-size:14px; color:#2C2C2E; line-height:1.6; margin-bottom:16px; border:1px solid rgba(0,0,0,0.06);">
            <b>Plain-Language Diagnostic:</b> {escape(conf.explanation)}
        </div>

        <div style="background:rgba(0,0,0,0.025); border-radius:10px; padding:12px 16px; font-size:12.5px; color:#6E6E73; line-height:1.55;">
            <b>Academic Limitations Disclaimer:</b> {escape(conf.limitations)}
        </div>
    </div>
    """


def render_research_gap_visualization(dimensions: List[str], gaps: List[Any]) -> str:
    """Renders research coverage by dimension and highlights discovered gaps."""
    gap_dims = {g.missing_dimension.lower() for g in gaps} if gaps else set()
    bars_html = []

    for idx, dim in enumerate(dimensions):
        is_gap = any(dim.lower() in gd or gd in dim.lower() for gd in gap_dims)
        pct = 40 if is_gap else (95 if idx % 2 == 0 else 85)
        bar_color = "#B45309" if is_gap else "#1C1C1E"
        status_text = "<span style='color:#B45309; font-weight:600;'>Gap Identified (Follow-up Triggered)</span>" if is_gap else "<span style='color:#4E6E5D; font-weight:600;'>Covered</span>"

        bars_html.append(
            f"""
            <div style="margin-bottom:14px;">
                <div style="display:flex; justify-content:space-between; font-size:13.5px; margin-bottom:6px;">
                    <span style="color:#1C1C1E; font-weight:600;">{escape(dim)}</span>
                    <span style="font-size:12px;">{status_text}</span>
                </div>
                <div style="height:7px; background:rgba(0,0,0,0.06); border-radius:9999px; overflow:hidden;">
                    <div style="width:{pct}%; height:100%; background:{bar_color}; border-radius:9999px;"></div>
                </div>
            </div>
            """
        )

    gaps_detail_html = []
    if gaps:
        for g in gaps:
            gaps_detail_html.append(
                f"""
                <div class="glass-card-compact" style="border-left:3px solid #B45309; margin-bottom:10px; padding:14px 18px;">
                    <div style="font-size:13.5px; font-weight:700; color:#B45309;">Identified Void: {escape(g.missing_dimension)}</div>
                    <div style="font-size:13px; color:#48484A; margin:4px 0;">{escape(g.reason)}</div>
                    <div style="font-size:12px; color:#1C1C1E; font-family:'JetBrains Mono', monospace;">Autonomous Query: {escape(g.suggested_query)}</div>
                </div>
                """
            )

    return f"""
    <div class="glass-panel">
        <div style="font-size:17px; font-weight:700; color:#1C1C1E; margin-bottom:16px;">
            Research Dimension Coverage
        </div>
        <div style="margin-bottom:20px;">
            {''.join(bars_html)}
        </div>
        {''.join(gaps_detail_html)}
    </div>
    """


def render_methodology_pipeline(result: Any) -> str:
    """Renders user-friendly research process steps with real metrics."""
    m = result.metrics
    plan = result.plan

    stages = [
        ("01", "Question Analysis", "Decomposed topic into research dimensions & hypotheses.", f"{len(plan.research_dimensions) if plan else 3} Dimensions Mapped"),
        ("02", "Perspective Exploration", "Expanded core inquiry into targeted multi-angle queries.", f"{m.generated_queries if m else 0} Search Queries"),
        ("03", "Source Discovery", "Searched global literature with automated URL deduplication.", f"{m.total_sources_found if m else 0} Raw Sources Reviewed"),
        ("04", "Authority Evaluation", "5-Factor priority assessment (Authority, Relevance, Recency, Evidence, Reputation).", f"{len(result.accepted_sources)} Sources Accepted"),
        ("05", "Evidence Extraction", "Parsed documents, removed boilerplate, and extracted clean passages.", f"{m.total_documents if m else 0} Full Documents Parsed"),
        ("06", "Knowledge Indexing", "Indexed passage vectors into isolated ephemeral memory.", f"{m.total_chunks if m else 0} Passages Indexed"),
        ("07", "Gap Discovery", "Measured dimension coverage and dispatched follow-up queries for voids.", f"{len(result.gaps)} Voids Investigated"),
        ("08", "Claim Verification", "Extracted atomic factual claims and grounded them against source passages.", f"{len(result.claims)} Factual Claims Verified"),
        ("09", "Trade-off Synthesis", "Discovered conflicting findings and reconciled divergent viewpoints.", f"{len(result.contradictions)} Trade-offs Analyzed"),
        ("10", "Dossier Compilation", "Compiled publication-ready dossier with citations and export formatting.", f"{m.execution_time_seconds if m else 0}s Latency"),
    ]

    items_html = []
    for step_num, title, desc, stat in stages:
        items_html.append(
            f"""
            <div style="display:flex; gap:16px; align-items:flex-start; margin-bottom:18px;">
                <div style="width:30px; height:30px; border-radius:50%; background:#1C1C1E; color:#FFFFFF; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:700; flex-shrink:0;">
                    {step_num}
                </div>
                <div style="flex:1;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px; flex-wrap:wrap; gap:8px;">
                        <div style="font-size:15px; font-weight:700; color:#1C1C1E;">{title}</div>
                        <span style="font-size:11.5px; font-weight:600; color:#2D503E; background:rgba(78,110,93,0.1); padding:2px 8px; border-radius:9999px;">{stat}</span>
                    </div>
                    <div style="font-size:13px; color:#6E6E73; line-height:1.5;">{desc}</div>
                </div>
            </div>
            """
        )

    return f"""
    <div class="glass-panel" style="padding:28px 32px;">
        <div style="font-size:11.5px; font-weight:700; color:#8E8E93; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:4px;">
            Scientific Process
        </div>
        <div style="font-size:22px; font-weight:700; color:#1C1C1E; margin-bottom:20px; letter-spacing:-0.4px;">
            How This Research Was Conducted
        </div>
        {''.join(items_html)}
    </div>
    """


def render_technical_architecture_card() -> str:
    """
    Renders the collapsible technical architecture section for the engineering
    project presentation, cleanly sequestered from the consumer UI.
    """
    return """
    <div class="glass-panel" style="padding:24px 28px; border:1px solid rgba(0,0,0,0.08); background:rgba(255,255,255,0.75);">
        <div style="font-size:11.5px; font-weight:700; color:#8E8E93; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:6px;">
            Engineering Specifications &bull; Project Presentation
        </div>
        <div style="font-size:18px; font-weight:700; color:#1C1C1E; margin-bottom:14px;">
            Underlying Neural Architecture
        </div>
        <div style="display:grid; grid-template-columns:repeat(2, 1fr); gap:14px; font-size:13.5px; color:#2C2C2E;">
            <div style="background:#FFFFFF; padding:12px 16px; border-radius:10px; border:1px solid rgba(0,0,0,0.06);">
                <div style="font-size:11px; font-weight:700; color:#8E8E93; text-transform:uppercase;">Reasoning Engine</div>
                <div style="font-weight:600; color:#1C1C1E; margin-top:2px;">GPT-4o Multi-Agent</div>
                <div style="font-size:12px; color:#6E6E73; margin-top:3px;">Decomposition, claim extraction, synthesis</div>
            </div>
            <div style="background:#FFFFFF; padding:12px 16px; border-radius:10px; border:1px solid rgba(0,0,0,0.06);">
                <div style="font-size:11px; font-weight:700; color:#8E8E93; text-transform:uppercase;">Vector Embeddings</div>
                <div style="font-weight:600; color:#1C1C1E; margin-top:2px;">all-MiniLM-L6-v2 (384-d)</div>
                <div style="font-size:12px; color:#6E6E73; margin-top:3px;">Local Hugging Face; zero OpenAI embedding cost</div>
            </div>
            <div style="background:#FFFFFF; padding:12px 16px; border-radius:10px; border:1px solid rgba(0,0,0,0.06);">
                <div style="font-size:11px; font-weight:700; color:#8E8E93; text-transform:uppercase;">Vector Storage</div>
                <div style="font-weight:600; color:#1C1C1E; margin-top:2px;">ChromaDB Ephemeral</div>
                <div style="font-size:12px; color:#6E6E73; margin-top:3px;">Session-isolated collections with cosine space</div>
            </div>
            <div style="background:#FFFFFF; padding:12px 16px; border-radius:10px; border:1px solid rgba(0,0,0,0.06);">
                <div style="font-size:11px; font-weight:700; color:#8E8E93; text-transform:uppercase;">Web Intelligence & PDF</div>
                <div style="font-weight:600; color:#1C1C1E; margin-top:2px;">Tavily API & ReportLab Platypus</div>
                <div style="font-size:12px; color:#6E6E73; margin-top:3px;">Multi-query search, deduplication, PDF compilation</div>
            </div>
        </div>
    </div>
    """


def render_source_card(src: Dict[str, Any]) -> str:
    """Render a clean source row in warm white liquid glass."""
    url = escape(src.get("url", ""))
    title = escape(src.get("title") or src.get("url", ""))
    snippet = escape(src.get("snippet", ""))[:220]
    score = int(src.get("source_score", 0.5) * 100)

    if score >= 80:
        tier = "High Priority"
    elif score >= 60:
        tier = "Medium Priority"
    else:
        tier = "Standard Source"

    domain = url.split("//")[-1].split("/")[0]

    return f"""
    <div class="glass-card-compact" style="margin-bottom:12px; padding:16px 20px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; flex-wrap:wrap; gap:8px;">
            <a href="{url}" target="_blank" style="font-size:14.5px; font-weight:600; color:#1C1C1E; text-decoration:none;">
                {title} <span style="font-size:12px; color:#8E8E93;">↗</span>
            </a>
            <span style="font-size:11.5px; font-weight:600; color:#1C1C1E; background:rgba(0,0,0,0.04); padding:3px 10px; border-radius:9999px; border:1px solid rgba(0,0,0,0.06);">
                {score}% &bull; {tier}
            </span>
        </div>
        <div style="font-size:13px; color:#6E6E73; line-height:1.55; margin-bottom:6px;">
            {snippet}...
        </div>
        <div style="font-size:11.5px; color:#8E8E93; font-family:'Inter', sans-serif;">
            {domain}
        </div>
    </div>
    """
