"""
Unit and integration tests for NVIDIA Remote Embedding Provider and Provider Abstraction.
Tests:
- Provider selection (local vs nvidia)
- Lazy imports: verify torch is NOT loaded when EMBEDDING_PROVIDER=nvidia
- Query vs passage mode distinction
- Bounded batching and index order preservation
- Dimension validation and mismatch rejection
- Retry policy on transient errors (429, 500)
- Non-retryable authentication errors (401)
- Chroma collection model namespace isolation
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

from src.embedder import (
    EmbeddingProvider,
    LocalSentenceTransformerProvider,
    NVIDIAEmbeddingProvider,
    get_embedding_provider,
    reset_embedding_provider,
    embed_text,
    embed_query,
    embed_documents,
    clear_embedding_cache,
    HuggingFaceEmbedder,
)
from src.chroma_store import get_vector_store, save_vectors, query_vectors, reset_chroma_client


@pytest.fixture(autouse=True)
def clean_state():
    clear_embedding_cache()
    reset_embedding_provider()
    reset_chroma_client()
    orig_provider = os.environ.get("EMBEDDING_PROVIDER")
    yield
    clear_embedding_cache()
    reset_embedding_provider()
    reset_chroma_client()
    if orig_provider is not None:
        os.environ["EMBEDDING_PROVIDER"] = orig_provider
    elif "EMBEDDING_PROVIDER" in os.environ:
        del os.environ["EMBEDDING_PROVIDER"]


def test_provider_factory_selection():
    """Verify factory returns appropriate provider based on EMBEDDING_PROVIDER env var."""
    os.environ["EMBEDDING_PROVIDER"] = "local"
    reset_embedding_provider()
    p_loc = get_embedding_provider()
    assert isinstance(p_loc, LocalSentenceTransformerProvider)
    assert p_loc.provider_name == "local"
    assert p_loc.dimension == 384

    with patch.dict(os.environ, {"EMBEDDING_PROVIDER": "nvidia", "NVIDIA_API_KEY": "mock_test_key"}):
        reset_embedding_provider()
        p_nv = get_embedding_provider()
        assert isinstance(p_nv, NVIDIAEmbeddingProvider)
        assert p_nv.provider_name == "nvidia"
        assert p_nv.dimension == 2048


def test_nvidia_provider_requires_api_key():
    """Verify NVIDIAEmbeddingProvider raises ValueError if NVIDIA_API_KEY is empty."""
    with patch.dict(os.environ, {"NVIDIA_API_KEY": ""}):
        with pytest.raises(ValueError, match="NVIDIA_API_KEY environment variable is required"):
            NVIDIAEmbeddingProvider(api_key="")


def test_nvidia_provider_query_mode_payload():
    """Verify input_type='query' is sent for search queries."""
    provider = NVIDIAEmbeddingProvider(api_key="test_key_mock")
    
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "data": [{"index": 0, "embedding": [0.1] * 2048}]
    }

    with patch("httpx.Client.post", return_value=mock_resp) as mock_post:
        vec = provider.embed_query("search for clean energy")
        assert len(vec) == 2048
        
        args, kwargs = mock_post.call_args
        payload = kwargs.get("json", {})
        assert payload.get("input_type") == "query"
        assert payload.get("input") == ["search for clean energy"]
        assert payload.get("model") == "nvidia/nemotron-3-embed-1b"


def test_nvidia_provider_passage_mode_payload():
    """Verify input_type='passage' is sent for document chunks."""
    provider = NVIDIAEmbeddingProvider(api_key="test_key_mock")
    
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "data": [{"index": 0, "embedding": [0.2] * 2048}]
    }

    with patch("httpx.Client.post", return_value=mock_resp) as mock_post:
        vec = provider.embed_text("Solar panels convert sunlight to power.", is_query=False)
        assert len(vec) == 2048
        
        args, kwargs = mock_post.call_args
        payload = kwargs.get("json", {})
        assert payload.get("input_type") == "passage"
        assert payload.get("input") == ["Solar panels convert sunlight to power."]


def test_nvidia_provider_batching_and_ordering():
    """Verify document batches preserve strict input order even if API returns out-of-order."""
    provider = NVIDIAEmbeddingProvider(api_key="test_key_mock", batch_size=2)
    
    # Simulate API returning items out of order
    mock_resp_1 = MagicMock()
    mock_resp_1.status_code = 200
    mock_resp_1.json.return_value = {
        "data": [
            {"index": 1, "embedding": [1.0] * 2048},
            {"index": 0, "embedding": [0.0] * 2048},
        ]
    }

    with patch("httpx.Client.post", return_value=mock_resp_1):
        docs = ["Doc A (idx 0)", "Doc B (idx 1)"]
        vectors = provider.embed_documents(docs, batch_size=2)
        assert len(vectors) == 2
        assert vectors[0][0] == 0.0  # Doc A received vector 0
        assert vectors[1][0] == 1.0  # Doc B received vector 1


def test_dimension_validation_rejection():
    """Verify ValueError is raised if provider returns wrong dimension."""
    provider = NVIDIAEmbeddingProvider(api_key="test_key_mock")
    
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    # Returns 384 dimensions instead of 2048
    mock_resp.json.return_value = {
        "data": [{"index": 0, "embedding": [0.1] * 384}]
    }

    with patch("httpx.Client.post", return_value=mock_resp):
        with pytest.raises(ValueError, match="NVIDIA embedding vector dimension mismatch"):
            provider.embed_text("Test query", is_query=True)


def test_nvidia_retry_on_429():
    """Verify exponential backoff retry on HTTP 429 rate limit."""
    provider = NVIDIAEmbeddingProvider(api_key="test_key_mock", max_retries=2)
    
    resp_429 = MagicMock()
    resp_429.status_code = 429
    
    resp_200 = MagicMock()
    resp_200.status_code = 200
    resp_200.json.return_value = {
        "data": [{"index": 0, "embedding": [0.5] * 2048}]
    }

    with patch("httpx.Client.post", side_effect=[resp_429, resp_200]) as mock_post:
        with patch("time.sleep") as mock_sleep:
            vec = provider.embed_text("Retry query", is_query=True)
            assert len(vec) == 2048
            assert mock_post.call_count == 2
            mock_sleep.assert_called_once_with(1.0)


def test_nvidia_no_retry_on_auth_failure_401():
    """Verify immediate PermissionError without retry on HTTP 401."""
    provider = NVIDIAEmbeddingProvider(api_key="test_key_mock", max_retries=3)
    
    resp_401 = MagicMock()
    resp_401.status_code = 401
    resp_401.text = "Unauthorized: Invalid key"

    with patch("httpx.Client.post", return_value=resp_401) as mock_post:
        with pytest.raises(PermissionError, match="NVIDIA API authentication failure"):
            provider.embed_text("Test query")
        assert mock_post.call_count == 1  # No retries


def test_chroma_model_isolation():
    """Verify local and nvidia providers use separate isolated collections."""
    os.environ["EMBEDDING_PROVIDER"] = "local"
    reset_embedding_provider()
    col_local = get_vector_store("test_iso_session")
    assert col_local.name == "research_test_iso_session"

    with patch.dict(os.environ, {"EMBEDDING_PROVIDER": "nvidia", "NVIDIA_API_KEY": "mock_test_key"}):
        reset_embedding_provider()
        col_nvidia = get_vector_store("test_iso_session")
        assert col_nvidia.name == "research_nv_test_iso_session"
        assert col_local.name != col_nvidia.name


def test_chroma_dimension_mismatch_fails_safely():
    """Verify Chroma fails clearly if querying a local collection with nvidia vector or vice versa."""
    os.environ["EMBEDDING_PROVIDER"] = "local"
    reset_embedding_provider()
    store = get_vector_store("test_dim_mismatch_session")
    
    # Attempt to save 2048-dimensional vector into local 384-dim store
    bad_vectors = [[0.1] * 2048]
    with pytest.raises(ValueError, match="Document embedding at index 0 has invalid dimension 2048, expected 384"):
        save_vectors(store, bad_vectors, ["Sample text"], session_id="test_dim_mismatch_session")


def test_zero_torch_imports_with_nvidia_provider():
    """Verify that when EMBEDDING_PROVIDER=nvidia, torch and sentence_transformers are not imported."""
    # Run in a clean subprocess to ensure no pollution from other tests that may have used local provider
    import subprocess
    cmd = [
        sys.executable,
        "-c",
        (
            "import os, sys; "
            "os.environ['EMBEDDING_PROVIDER'] = 'nvidia'; "
            "os.environ['NVIDIA_API_KEY'] = 'mock_key'; "
            "import server; "
            "forbidden = ['torch', 'sentence_transformers', 'transformers', 'scipy', 'sklearn']; "
            "loaded = [m for m in forbidden if m in sys.modules]; "
            "assert len(loaded) == 0, f'Forbidden modules loaded: {loaded}'; "
            "print('OK')"
        )
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"Subprocess failed: {res.stderr}"
    assert "OK" in res.stdout

