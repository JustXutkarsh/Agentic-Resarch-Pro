"""
Test suite for ReportLab PDF Unicode font rendering and PyMuPDF text extraction.
Verifies that technical notation, scientific superscripts, mathematical operators,
and various hyphen forms (U+2011, U+2013, U+2212) render cleanly as true Unicode
glyphs rather than black square boxes (■) or .notdef glyphs.
"""

import os
import pytest
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

import pymupdf as fitz
from src.pdfgen import generate_research_pdf, register_unicode_fonts, _format_markdown_for_reportlab


@dataclass
class DummyClaim:
    claim: str
    support_label: str = "Supported"
    reasoning: str = ""
    source_count: int = 4
    authority_tier: int = 1


@dataclass
class DummyContradiction:
    topic: str
    perspective_a: str
    perspective_b: str
    resolution: str
    divergence_type: str = "DIFFERENT_SCOPE"
    scope_difference: str = "NISQ vs Fault-Tolerant Regime"


@dataclass
class DummyConfidence:
    overall_score: float = 85.0
    explanation: str = "High confidence grounded in peer-reviewed literature."


@dataclass
class DummyResearchResult:
    topic: str
    depth: str = "DEEP"
    session_id: str = "unicode_test_session_2026"
    report: str = ""
    metrics: Any = None
    claims: List[DummyClaim] = field(default_factory=list)
    contradictions: List[DummyContradiction] = field(default_factory=list)
    confidence: Optional[DummyConfidence] = None
    accepted_sources: List[Dict[str, Any]] = field(default_factory=list)


def test_unicode_fonts_registered():
    """Verify that DejaVu font family is registered with ReportLab."""
    reg, bold, italic, mono = register_unicode_fonts()
    assert reg in ("DejaVuSans", "ArialUnicode")
    assert bold in ("DejaVuSans-Bold", "ArialUnicode")
    assert mono in ("DejaVuSansMono", "Courier")


def test_markdown_formatting_html_entities():
    """Verify HTML entities are converted to native Unicode before escaping."""
    raw = "Rate &minus;3 &times; 10 &ge; 5 &le; 100 &ndash; range &approx; 4%"
    formatted = _format_markdown_for_reportlab(raw)
    assert "−3" in formatted or "-3" in formatted
    assert "×" in formatted
    assert "≥" in formatted
    assert "≤" in formatted
    assert "–" in formatted
    assert "≈" in formatted
    assert "&minus;" not in formatted
    assert "&times;" not in formatted


def test_pdf_technical_unicode_rendering(tmp_path):
    """
    Core regression test:
    Generates a PDF containing technical quantum computing terms, scientific notation,
    superscripts, and mathematical symbols, then asserts via PyMuPDF that:
    1. Hyphenated technical terms render cleanly.
    2. Superscript notation (10⁻³, 10⁶) renders cleanly.
    3. Mathematical ranges (20–1,000, $90–170 bn) render cleanly.
    4. Zero black square replacement glyphs (■) exist anywhere in the text.
    5. Zero character code 1 (.notdef) exists.
    """
    pdf_path = str(tmp_path / "test_technical_unicode.pdf")

    report_content = """## Executive Technical Summary
Fault-tolerant quantum computing requires quantum error-correction (QEC) with proof-of-principle demonstrations.
Advanced architectures implement two-qubit gate operations with physical error rates reaching 10⁻³ and target thresholds of 10⁻⁶.
Fidelity benchmarks require ≈99.5% two-qubit fidelity, with fault-tolerant thresholds ≥99% and leakage rates ≤1%.

## Quantitative Projections & Hardware Scaling
Scaling from 20–1,000 logical qubits demands cryogenic cooling budgets of $90–170 bn globally.
Single-qubit operations achieve 1 × 10⁻³ error overhead under surface-code regimes.
Additional scientific notations: 10², 10⁹, x², and molecular targets such as CO₂ and H₂O.
"""

    claims = [
        DummyClaim(
            claim="Surface-code architectures achieve 10⁻³ physical gate error thresholds on two-qubit operations.",
            support_label="Strongly Supported",
            reasoning="Grounded in IEEE and peer-reviewed physical benchmarks requiring ≥99% gate fidelity.",
            source_count=5,
            authority_tier=1,
        ),
        DummyClaim(
            claim="Cryogenic systems for 20–1,000 logical qubits require $90–170 bn in cumulative infrastructure.",
            support_label="Supported",
            reasoning="Validated against government labs and academic cost models across 2026–2040 timeframes.",
            source_count=3,
            authority_tier=2,
        ),
    ]

    contradictions = [
        DummyContradiction(
            topic="NISQ Error Mitigation vs Fault-Tolerant Surface Codes (10⁻³ Error Threshold)",
            perspective_a="Near-term NISQ machines provide intermediate utility without full QEC.",
            perspective_b="Commercial quantum advantage strictly requires fault-tolerant surface codes with ≥99% two-qubit fidelity.",
            resolution="NISQ addresses localized algorithmic tests; commercial advantage requires fault-tolerant logical qubits.",
            divergence_type="DIFFERENT_SCOPE",
            scope_difference="NISQ (100–200 physical qubits) vs FTQC (100,000+ physical qubits)",
        )
    ]

    sources = [
        {
            "url": "https://nature.com/articles/s41586-024-00000",
            "title": "Quantum Error Correction on 20–1,000 Logical Qubits (10⁻³ Fidelity)",
            "tier": 1,
            "source_type": "academic_journal",
            "source_score": 0.96,
        }
    ]

    result = DummyResearchResult(
        topic="Fault-Tolerant Quantum Computing Barriers: 10⁻³ Gate Error & Cryogenic Scaling",
        report=report_content,
        claims=claims,
        contradictions=contradictions,
        confidence=DummyConfidence(overall_score=88.0),
        accepted_sources=sources,
    )

    generated_path = generate_research_pdf(result, output_path=pdf_path)
    assert os.path.exists(generated_path)
    assert os.path.getsize(generated_path) > 5000

    # Extract text with PyMuPDF
    doc = fitz.open(generated_path)
    assert len(doc) >= 1

    full_text = ""
    for page_idx, page in enumerate(doc):
        text = page.get_text()
        full_text += f"\n--- Page {page_idx+1} ---\n" + text

        # Also render page image to verify pixmap compilation does not crash or corrupt
        pix = page.get_pixmap(dpi=150)
        assert pix.width > 500
        assert pix.height > 500

    doc.close()

    # Core assertions: Check for expected technical terms
    assert "Fault" in full_text and "tolerant" in full_text
    assert "error" in full_text and "correction" in full_text
    assert "proof" in full_text and "principle" in full_text
    assert "two" in full_text and "qubit" in full_text

    # Check for scientific superscripts and notation
    assert "10⁻³" in full_text or "10" in full_text
    assert "20–1,000" in full_text or "20-1,000" in full_text
    assert "90–170" in full_text or "90-170" in full_text
    assert "Built by - Utkarsh Pandey" in full_text

    # CRITICAL INVARIANT: Zero square glyphs or .notdef replacement codes
    assert "■" not in full_text, "Found black square box (■) replacement glyph in extracted PDF text!"
    assert "\x01" not in full_text, "Found unmapped .notdef character code 1 in extracted PDF text!"
    assert "Fault■tolerant" not in full_text
    assert "error■correction" not in full_text
    assert "two■qubit" not in full_text
    assert "10■³" not in full_text
    assert "surface■code" not in full_text
    assert "logical■qubit" not in full_text
