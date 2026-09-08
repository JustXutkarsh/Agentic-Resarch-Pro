"""Unit tests for src/claim_verifier.py"""
from unittest.mock import MagicMock
import json
import pytest
from src.config import get_research_config
from src.chroma_store import get_vector_store, save_vectors, reset_chroma_client
from src.embedder import embed_documents
from src.claim_verifier import (
    ClaimVerifier,
    ClaimVerification,
    _prioritize_claims,
    SUPPORT_SCORES,
)


@pytest.fixture(autouse=True)
def setup_teardown():
    reset_chroma_client()
    yield
    reset_chroma_client()


def test_prioritize_claims():
    claims = [
        "In this report we discuss energy.",
        "Solar cell conversion efficiency reached 24.8% in recent laboratory trials.",
        "This is an interesting topic.",
        "Wind turbine manufacturing costs decreased by 15% year-over-year.",
    ]
    prioritized = _prioritize_claims(claims, max_claims=2)
    assert len(prioritized) == 2
    # The two statistical / quantitative claims should be chosen
    assert any("24.8%" in c for c in prioritized)
    assert any("15%" in c for c in prioritized)


def test_extract_claims_with_mock():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content=json.dumps({
                    "claims": [
                        "Global EV sales surpassed 14 million units in 2023.",
                        "Battery pack costs fell below $140 per kWh.",
                    ]
                })
            )
        )
    ]
    mock_client.chat.completions.create.return_value = mock_response

    verifier = ClaimVerifier(client=mock_client)
    claims = verifier.extract_claims("Sample report body text", max_claims=5)

    assert len(claims) == 2
    assert "14 million units" in claims[0]


def test_verify_claims_with_chroma_and_mock_llm():
    # 1. Setup Chroma store with evidence
    store = get_vector_store("claim_verify_session")
    docs = [
        "Independent tests confirm battery pack costs fell below $140 per kilowatt-hour in 2023.",
    ]
    metas = [{"source_url": "https://bloomberg.com/bnef-battery", "source_score": 0.90}]
    embeddings = embed_documents(docs)
    save_vectors(store, embeddings, docs, metadatas=metas)

    # 2. Mock GPT-4o evaluation
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content=json.dumps({
                    "evaluations": [
                        {
                            "id": 0,
                            "support_label": "Strongly Supported",
                            "reasoning": "The evidence directly cites the exact $140/kWh battery threshold.",
                        }
                    ]
                })
            )
        )
    ]
    mock_client.chat.completions.create.return_value = mock_response

    verifier = ClaimVerifier(client=mock_client)
    config = get_research_config("STANDARD")

    results = verifier.verify_claims_against_evidence(
        ["Battery pack costs fell below $140 per kWh."],
        store,
        config=config,
    )

    assert len(results) == 1
    res = results[0]
    assert isinstance(res, ClaimVerification)
    assert res.support_label == "Strongly Supported"
    assert res.support_score == 1.0
    assert len(res.evidence_chunks) >= 1
    assert "https://bloomberg.com/bnef-battery" in res.source_urls
