"""
Research Results Workspace for Agentic Research PRO.
Editorial Warm White Liquid Glass Workspace for exploring the executive dossier,
grounded claims, empirical perspectives, methodology, sources, and publication PDF.
"""

import os
import re
import html
import streamlit as st
from typing import Dict, Any, List, Optional
from src.research_orchestrator import ResearchResult
from src.ui.components import (
    render_metric_tile,
    render_claim_card,
    render_contradiction_split,
    render_source_card,
    render_confidence_breakdown,
    render_research_gap_visualization,
    render_methodology_pipeline,
    render_technical_architecture_card,
    escape,
)


def _format_key_insights_html(report_text: str) -> str:
    """
    Extracts bullet points under Key Findings / Strategic Insights
    and formats them as clean editorial numbered cards (01, 02, 03).
    """
    insights_html = []
    matches = re.findall(r"(?:-|\*|•)\s+\*\*([^*]+)\*\*:\s*(.+)", report_text)
    if not matches:
        plain_matches = re.findall(r"(?:-|\*|•)\s+(.+)", report_text)
        matches = [(f"Key Insight {idx+1}", m) for idx, m in enumerate(plain_matches[:4])]

    for idx, (title, content) in enumerate(matches[:5]):
        num_str = f"0{idx+1}"
        insights_html.append(
            f"""
            <div class="insight-card">
                <div class="insight-number">{num_str}</div>
                <div class="insight-text">
                    <b style="color:#1C1C1E; font-size:15.5px;">{escape(title)}</b><br>
                    <span style="color:#6E6E73; margin-top:4px; display:inline-block;">{escape(content)}</span>
                </div>
            </div>
            """
        )

    return "".join(insights_html) if insights_html else "<p style='color:#8E8E93;'>Insights summarized in executive report.</p>"


def render_results_workspace(result: ResearchResult, pdf_path: Optional[str] = None):
    """
    Render the complete editorial research workspace in warm white liquid glass.
    """
    state = result.state
    m = result.metrics
    conf = result.confidence

    # 1. Editorial Header Card
    conf_score = int(conf.overall_score) if conf else 0
    st.markdown(
        f"""
        <div class="glass-panel" style="margin-top:20px; border-left: 4px solid #1C1C1E;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:16px;">
                <div style="max-width:680px;">
                    <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
                        <span class="badge-subtle" style="background:#1C1C1E; color:#FFFFFF; border:none; padding:3px 12px;">RESEARCH COMPLETE</span>
                        <span style="font-size:12px; color:#8E8E93; font-family:'JetBrains Mono', monospace;">ID: {escape(result.session_id)}</span>
                    </div>
                    <h1 class="editorial-title">
                        {escape(result.topic)}
                    </h1>
                    <div style="font-size:14px; color:#6E6E73;">
                        Mode: <b style="color:#1C1C1E;">{escape(result.depth.title())}</b> &bull; Duration: <b style="color:#1C1C1E;">{m.execution_time_seconds if m else 0}s</b> &bull; Agentic Research PRO
                    </div>
                </div>
                <div style="text-align:center; background:#FFFFFF; border:1px solid rgba(0,0,0,0.06); border-radius:18px; padding:14px 28px; box-shadow:0 4px 16px rgba(0,0,0,0.03);">
                    <div style="font-size:11px; font-weight:700; color:#8E8E93; text-transform:uppercase; letter-spacing:0.8px;">Confidence Score</div>
                    <div style="font-size:40px; font-weight:700; color:#1C1C1E; font-family:'Newsreader', serif; line-height:1.1;">
                        {conf_score}<span style="font-size:16px; color:#8E8E93;">/100</span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2. Simple Research Summary Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(render_metric_tile(len(result.accepted_sources), "Sources Reviewed", f"{m.sources_rejected if m else 0} low-priority filtered"), unsafe_allow_html=True)
    with col2:
        st.markdown(render_metric_tile(len(result.plan.research_dimensions) if result.plan else 3, "Perspectives Mapped", "Core topical dimensions"), unsafe_allow_html=True)
    with col3:
        st.markdown(render_metric_tile(len(result.claims), "Claims Verified", f"{m.supported_claims if m else 0} empirically supported"), unsafe_allow_html=True)
    with col4:
        st.markdown(render_metric_tile(m.research_iterations if m else 1, "Research Loops", f"{len(result.gaps)} voids expanded"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Clean Editorial Workspace Tabs
    tab_dossier, tab_claims, tab_perspectives, tab_methodology, tab_confidence, tab_sources, tab_export = st.tabs([
        "📄 Research Dossier",
        "🛡️ Claim Verification",
        "⚖️ Perspectives & Trade-offs",
        "🗺️ Research Process",
        "📈 Confidence Heuristic",
        "🌐 Source Explorer",
        "📥 Download PDF",
    ])

    # Tab 1: Executive Dossier
    with tab_dossier:
        st.markdown("### 🌟 Strategic Findings & Key Insights")
        insights_html = _format_key_insights_html(result.report)
        st.markdown(insights_html, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📑 Full Research Report")
        st.markdown(f"<div class='editorial-paper'>{result.report}</div>", unsafe_allow_html=True)

    # Tab 2: Claim Verification
    with tab_claims:
        st.markdown("### 🛡️ Factual Claim Grounding & Verification Matrix")
        st.markdown(
            "Every core empirical assertion in the synthesized report is extracted and rigorously verified "
            "against retrieved source evidence passages."
        )

        if result.claims:
            for idx, c in enumerate(result.claims):
                st.markdown(render_claim_card(c.to_dict(), index=idx+1), unsafe_allow_html=True)
        else:
            st.info("No atomic claims extracted for this research session.")

    # Tab 3: Perspectives & Trade-offs
    with tab_perspectives:
        st.markdown("### ⚖️ Empirical Divergences & Competing Perspectives")
        st.markdown("Identifies genuine differences of opinion, varying methodologies, or trade-offs across literature.")

        if result.contradictions:
            for idx, c in enumerate(result.contradictions):
                st.markdown(render_contradiction_split(c.to_dict(), index=idx+1), unsafe_allow_html=True)
        else:
            if result.depth.upper() == "DEEP":
                st.info("No significant empirical contradictions detected across the evaluated literature.")
            else:
                st.info("Contradiction detection is active in Deep research mode. Standard mode focuses on core consensus dimensions.")

    # Tab 4: Research Process & Methodology
    with tab_methodology:
        # User-friendly scientific process pipeline
        st.markdown(render_methodology_pipeline(result), unsafe_allow_html=True)

        # Dimension coverage & gap detection
        dims = result.plan.research_dimensions if result.plan else ["Core Inquiry", "Market Scale", "Technological Challenges"]
        st.markdown(render_research_gap_visualization(dims, result.gaps), unsafe_allow_html=True)

        # Expandable Technical Architecture Section (for engineering presentations)
        with st.expander("🛠️ View Underlying Technical Architecture (Engineering Specs)", expanded=False):
            st.markdown(render_technical_architecture_card(), unsafe_allow_html=True)

    # Tab 5: Confidence Heuristic
    with tab_confidence:
        st.markdown(render_confidence_breakdown(conf), unsafe_allow_html=True)

    # Tab 6: Source Explorer
    with tab_sources:
        st.markdown(f"### 🌐 Evaluated Literature Sources ({len(result.accepted_sources)} Accepted)")

        filter_choice = st.selectbox(
            "Filter Literature by Priority Level",
            options=["All Accepted Sources", "High Priority (≥ 80%)", "Academic & Research", "Government & Standards"],
            index=0,
        )

        filtered = result.accepted_sources
        if filter_choice == "High Priority (≥ 80%)":
            filtered = [s for s in filtered if s.get("source_score", 0.0) >= 0.80]
        elif filter_choice == "Academic & Research":
            filtered = [s for s in filtered if any(term in s.get("url", "").lower() for term in [".edu", "arxiv", "nature", "science", "ieee"])]
        elif filter_choice == "Government & Standards":
            filtered = [s for s in filtered if ".gov" in s.get("url", "").lower()]

        for src in filtered:
            st.markdown(render_source_card(src), unsafe_allow_html=True)

        if not filtered:
            st.info("No sources matched the selected filter.")

        if result.rejected_sources:
            with st.expander(f"View {len(result.rejected_sources)} Low-Priority Filtered Sources"):
                for rej in result.rejected_sources:
                    score = int(rej.get("source_score", 0.0) * 100)
                    st.caption(f"❌ [{escape(rej.get('title') or rej.get('url'))}]({rej.get('url')}) &bull; Score: {score}% (Below relevance threshold)")

    # Tab 7: Download PDF
    with tab_export:
        st.markdown("### 📥 Publication-Ready PDF Dossier")
        st.markdown(
            "Download the complete research report compiled with executive findings, verified claims, "
            "methodology provenance, and clickable literature citations."
        )

        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
                st.download_button(
                    label="Download Research PDF Dossier ↑",
                    data=pdf_bytes,
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf",
                    use_container_width=True,
                )
        else:
            st.warning("PDF dossier is compiling or not found.")
