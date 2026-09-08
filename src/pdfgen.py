"""
PDF Dossier Generator for Agentic Research PRO.
Built using ReportLab with clean typographic hierarchy, custom styling,
and automated sections:
1. Cover / Executive Header (Topic, Date, Depth, Session ID)
2. Research Methodology & Computational Metrics
3. Research Findings (Executive Summary, Key Insights, Pros & Cons)
4. Evidence Grounding & Claim Verification Matrix
5. Contradictions & Divergent Perspectives (if detected)
6. Explainable Research Confidence & Academic Disclaimer
7. Authoritative Citations & Source Links
"""

import html
import logging
import os
from datetime import datetime
from typing import Optional, Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.units import inch

logger = logging.getLogger(__name__)


def _escape(text: Any) -> str:
    """Safely escape text for ReportLab Paragraph markup."""
    if text is None:
        return ""
    clean = str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return clean


def generate_research_pdf(result: Any, output_path: str = "research_report.pdf") -> str:
    """
    Generate a comprehensive research dossier PDF from a ResearchResult object.
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=6,
    )

    h1_style = ParagraphStyle(
        "SectionH1",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=14,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=5,
    )

    bullet_style = ParagraphStyle(
        "Bullet",
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=4,
    )

    meta_style = ParagraphStyle(
        "Meta",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#64748b"),
    )

    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#64748b"),
        spaceBefore=6,
    )

    story = []

    # 1. Header & Metadata
    story.append(Paragraph(f"<b>Research Dossier: {_escape(result.topic)}</b>", title_style))
    meta_text = (
        f"<b>Depth:</b> {_escape(result.depth)} &nbsp;|&nbsp; "
        f"<b>Session ID:</b> {_escape(result.session_id)} &nbsp;|&nbsp; "
        f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')} &nbsp;|&nbsp; "
        f"<b>Agentic Research PRO v2.0</b>"
    )
    story.append(Paragraph(meta_text, meta_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3b82f6"), spaceAfter=12))

    # 2. Research Methodology & Execution Metrics
    story.append(Paragraph("1. Research Methodology & Pipeline Metrics", h1_style))
    if result.metrics:
        m = result.metrics
        metrics_data = [
            [
                Paragraph("<b>Execution Depth:</b>", body_style),
                Paragraph(_escape(result.depth), body_style),
                Paragraph("<b>Research Iterations:</b>", body_style),
                Paragraph(str(m.research_iterations), body_style),
            ],
            [
                Paragraph("<b>Search Queries:</b>", body_style),
                Paragraph(str(m.generated_queries), body_style),
                Paragraph("<b>Total Sources Evaluated:</b>", body_style),
                Paragraph(f"{m.total_sources_found} ({m.sources_accepted} accepted)", body_style),
            ],
            [
                Paragraph("<b>Evidence Chunks:</b>", body_style),
                Paragraph(f"{m.total_chunks} indexed ({m.retrieved_evidence_chunks} retrieved)", body_style),
                Paragraph("<b>Execution Time:</b>", body_style),
                Paragraph(f"{m.execution_time_seconds}s", body_style),
            ],
        ]
        t = Table(metrics_data, colWidths=[125, 130, 135, 130])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(t)
        story.append(Spacer(1, 10))

    # 3. Research Report Findings
    story.append(Paragraph("2. Executive Findings & Analysis", h1_style))
    # Parse markdown lines into clean paragraphs
    report_text = result.report or "No report content generated."
    for line in report_text.split("\n"):
        line_s = line.strip()
        if not line_s:
            story.append(Spacer(1, 3))
            continue
        if line_s.startswith("# "):
            continue  # Already displayed in main title
        elif line_s.startswith("## "):
            story.append(Spacer(1, 4))
            story.append(Paragraph(f"<b>{_escape(line_s[3:])}</b>", h1_style))
        elif line_s.startswith("### "):
            story.append(Paragraph(f"<b>{_escape(line_s[4:])}</b>", body_style))
        elif line_s.startswith("- ") or line_s.startswith("• "):
            story.append(Paragraph(f"• {_escape(line_s[2:])}", bullet_style))
        else:
            story.append(Paragraph(_escape(line_s), body_style))

    story.append(Spacer(1, 10))

    # 4. Evidence Grounding & Claim Verification Matrix
    if result.claims:
        story.append(Paragraph("3. Factual Claim Verification & Evidence Grounding", h1_style))
        claim_rows = [
            [
                Paragraph("<b>Claim</b>", body_style),
                Paragraph("<b>Support Label</b>", body_style),
                Paragraph("<b>Reasoning & Sources</b>", body_style),
            ]
        ]
        for c in result.claims[:10]:
            label_color = "#16a34a" if c.support_label in ["Strongly Supported", "Supported"] else "#ca8a04" if c.support_label == "Partially Supported" else "#dc2626"
            sources_summary = f"{c.source_count} sources" if c.source_count else "ChromaDB"
            claim_rows.append([
                Paragraph(_escape(c.claim), body_style),
                Paragraph(f"<font color='{label_color}'><b>{_escape(c.support_label)}</b></font>", body_style),
                Paragraph(f"{_escape(c.reasoning)} <i>({sources_summary})</i>", body_style),
            ])
        ct = Table(claim_rows, colWidths=[180, 110, 230])
        ct.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(ct)
        story.append(Spacer(1, 10))

    # 5. Contradictions & Divergent Perspectives (if present)
    if result.contradictions:
        story.append(Paragraph("4. Empirical Contradictions & Competing Views", h1_style))
        for idx, contra in enumerate(result.contradictions):
            story.append(Paragraph(f"<b>Issue {idx+1}: {_escape(contra.topic)}</b>", body_style))
            story.append(Paragraph(f"• <b>Perspective A:</b> {_escape(contra.perspective_a)}", bullet_style))
            story.append(Paragraph(f"• <b>Perspective B:</b> {_escape(contra.perspective_b)}", bullet_style))
            story.append(Paragraph(f"• <i>Synthesis / Reconciliation:</i> {_escape(contra.resolution)}", bullet_style))
            story.append(Spacer(1, 4))
        story.append(Spacer(1, 6))

    # 6. Research Confidence Engine Heuristic
    if result.confidence:
        conf = result.confidence
        story.append(Paragraph(f"5. Research Confidence Evaluation: {int(conf.overall_score)}/100", h1_style))
        conf_data = [
            [
                Paragraph("<b>Source Quality:</b>", body_style),
                Paragraph(f"{int(conf.source_quality)}/100", body_style),
                Paragraph("<b>Evidence Coverage:</b>", body_style),
                Paragraph(f"{int(conf.evidence_coverage)}/100", body_style),
            ],
            [
                Paragraph("<b>Claim Support:</b>", body_style),
                Paragraph(f"{int(conf.claim_support)}/100", body_style),
                Paragraph("<b>Source Agreement:</b>", body_style),
                Paragraph(f"{int(conf.source_agreement)}/100", body_style),
            ],
            [
                Paragraph("<b>Completeness:</b>", body_style),
                Paragraph(f"{int(conf.research_completeness)}/100", body_style),
                Paragraph("<b>Overall Score:</b>", body_style),
                Paragraph(f"<b>{int(conf.overall_score)}/100</b>", body_style),
            ],
        ]
        c_table = Table(conf_data, colWidths=[125, 130, 135, 130])
        c_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(c_table)
        story.append(Spacer(1, 5))
        story.append(Paragraph(f"<b>Analysis:</b> {_escape(conf.explanation)}", body_style))
        story.append(Paragraph(f"<b>Academic Disclaimer:</b> {_escape(conf.limitations)}", disclaimer_style))
        story.append(Spacer(1, 10))

    # 7. Authoritative Citations & Source Links
    if result.accepted_sources:
        story.append(Paragraph("6. Source References & Citations", h1_style))
        for src in result.accepted_sources[:15]:
            url = src.get("url", "")
            title = src.get("title") or url
            score = src.get("source_score", 0.5)
            story.append(Paragraph(
                f"• <a href='{_escape(url)}' color='#2563eb'><u>{_escape(title)}</u></a> "
                f"(Priority Score: {int(score*100)}%)",
                bullet_style
            ))

    doc.build(story)
    return output_path


def generate_pdf(summary, insights, pros_cons, citations, output_path="research_report.pdf"):
    """
    Backward-compatible legacy wrapper.
    """
    from dataclasses import make_dataclass
    # Create an ad-hoc pseudo result for backward compatibility
    PseudoResult = make_dataclass(
        "PseudoResult",
        [
            ("topic", str),
            ("depth", str),
            ("session_id", str),
            ("report", str),
            ("metrics", Any),
            ("claims", list),
            ("contradictions", list),
            ("confidence", Any),
            ("accepted_sources", list),
        ]
    )

    report_lines = [f"## Summary\n{summary}\n", "## Key Findings & Strategic Insights"]
    for i in (insights or []):
        report_lines.append(f"- {i}")
    report_lines.append("\n## Trade-offs & Comparative Analysis\n### Strengths & Opportunities (Pros)")
    for p in pros_cons.get("pros", []):
        report_lines.append(f"- {p}")
    report_lines.append("\n### Limitations & Risks (Cons)")
    for c in pros_cons.get("cons", []):
        report_lines.append(f"- {c}")

    pseudo_result = PseudoResult(
        topic="Research Report",
        depth="STANDARD",
        session_id="legacy_export",
        report="\n".join(report_lines),
        metrics=None,
        claims=[],
        contradictions=[],
        confidence=None,
        accepted_sources=[{"url": u, "title": u, "source_score": 0.8} for u in (citations or [])],
    )
    return generate_research_pdf(pseudo_result, output_path)
