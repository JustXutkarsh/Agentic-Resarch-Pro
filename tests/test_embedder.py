"""Unit tests for src/embedder.py"""
import pytest
from src.embedder import (
    load_embedding_model,
    embed_text,
    embed_documents,
    clear_embedding_cache,
    HuggingFaceEmbedder,
    _EMBEDDING_CACHE,
)
from src.config import EMBEDDING_DIMENSION


@pytest.fixture(autouse=True)
def setup_teardown():
    clear_embedding_cache()
    yield
    clear_embedding_cache()


def test_load_embedding_model_singleton():
    model1 = load_embedding_model()
    model2 = load_embedding_model()
    assert model1 is model2


def test_embed_single_text():
    text = "Artificial intelligence and quantum computing advancements."
    vec = embed_text(text)
    assert isinstance(vec, list)
    assert len(vec) == EMBEDDING_DIMENSION
    assert all(isinstance(v, float) for v in vec)


def test_embed_empty_and_blank():
    vec_empty = embed_text("")
    assert len(vec_empty) == EMBEDDING_DIMENSION
    assert all(v == 0.0 for v in vec_empty)

    vec_spaces = embed_text("   ")
    assert len(vec_spaces) == EMBEDDING_DIMENSION
    assert all(v == 0.0 for v in vec_spaces)

    docs = embed_documents([])
    assert docs == []


def test_embed_multiple_documents():
    texts = [
        "First document on renewable energy.",
        "Second document regarding wind turbines.",
        "Third document analyzing solar panel efficiency.",
    ]
    vectors = embed_documents(texts)
    assert len(vectors) == 3
    for v in vectors:
        assert len(v) == EMBEDDING_DIMENSION


def test_embedding_cache():
    text = "Repeated query for cache verification."
    assert len(_EMBEDDING_CACHE) == 0

    vec1 = embed_text(text)
    assert len(_EMBEDDING_CACHE) == 1

    vec2 = embed_text(text)
    assert vec1 == vec2
    assert len(_EMBEDDING_CACHE) == 1


def test_huggingface_embedder_class():
    embedder = HuggingFaceEmbedder()
    vec = embedder.embed_query("Sample query")
    assert len(vec) == EMBEDDING_DIMENSION

    batch = embedder.embed(["Doc 1", "Doc 2"])
    assert len(batch) == 2
    assert len(batch[0]) == EMBEDDING_DIMENSION
