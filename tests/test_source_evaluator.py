"""Unit tests for src/source_evaluator.py"""
import pytest
from src.source_evaluator import (
    evaluate_authority_and_reputation,
    evaluate_recency,
    evaluate_evidence_quality,
    evaluate_source,
    evaluate_and_filter_sources,
)


def test_domain_authority_ranking():
    gov_auth, gov_rep, _ = evaluate_authority_and_reputation("https://energy.gov/clean-energy")
    edu_auth, edu_rep, _ = evaluate_authority_and_reputation("https://web.mit.edu/research")
    news_auth, news_rep, _ = evaluate_authority_and_reputation("https://reuters.com/business")
    blog_auth, blog_rep, _ = evaluate_authority_and_reputation("https://myrandomtechblog.xyz/post")

    assert gov_auth >= 0.9
    assert edu_auth >= 0.9
    assert news_auth >= 0.8
    assert blog_auth < news_auth


def test_recency_with_and_without_date():
    score_recent, unk_recent = evaluate_recency("2026-01-15")
    assert score_recent >= 0.8
    assert unk_recent is False

    score_none, unk_none = evaluate_recency(None)
    assert score_none == 0.50
    assert unk_none is True


def test_evidence_quality():
    good_text = "The comprehensive study conducted by researchers found a 42.5% increase in battery efficiency across 150 laboratory tests."
    poor_text = "I think batteries are cool."

    score_good = evaluate_evidence_quality(good_text)
    score_poor = evaluate_evidence_quality(poor_text)

    assert score_good > score_poor


def test_evaluate_source():
    src = {
        "url": "https://nature.com/articles/solid-state-battery-advances",
        "title": "Solid State Battery Electrolytes",
        "snippet": "Researchers demonstrated a 35% increase in energy density according to laboratory reports.",
        "published_date": "2026-02-10",
    }
    evaluation = evaluate_source(src, topic="solid state batteries")

    assert 0.0 <= evaluation.overall_score <= 1.0
    assert evaluation.authority_score >= 0.9
    assert evaluation.recency_unknown is False


def test_evaluate_and_filter_sources_partition_and_safety():
    sources = [
        {
            "url": "https://nature.com/articles/quantum",
            "title": "Quantum Computing Breakthrough",
            "snippet": "According to new research, quantum processors achieved 99.9% gate fidelity.",
            "published_date": "2026-01-01",
        },
        {
            "url": "https://randomblog.com/post1",
            "title": "My Thoughts on Quantum",
            "snippet": "Quantum computers sound really fast and futuristic to me.",
            "published_date": None,
        },
    ]

    accepted, rejected = evaluate_and_filter_sources(
        sources,
        topic="quantum computing breakthroughs",
        quality_threshold=0.60,
        min_sources_to_retain=1,
    )

    assert len(accepted) >= 1
    assert accepted[0]["url"] == "https://nature.com/articles/quantum"
    assert "source_score" in accepted[0]
