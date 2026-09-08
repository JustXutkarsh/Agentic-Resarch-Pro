"""Unit tests for src/chroma_store.py"""
import pytest
from src.chroma_store import (
    get_vector_store,
    save_vectors,
    query_vectors,
    retrieve_relevant_chunks,
    reset_chroma_client,
)
from src.embedder import embed_documents, embed_text


@pytest.fixture(autouse=True)
def setup_teardown():
    reset_chroma_client()
    yield
    reset_chroma_client()


def test_get_vector_store_isolation():
    store_a = get_vector_store("session_aaa")
    store_b = get_vector_store("session_bbb")
    assert store_a.name != store_b.name
    assert "session_aaa" in store_a.name
    assert "session_bbb" in store_b.name


def test_save_and_query_vectors_with_metadata():
    store = get_vector_store("test_session_1")

    docs = [
        "Solar photovoltaic panels convert sunlight into electrical power cleanly.",
        "William Shakespeare wrote Romeo and Juliet in London in the late 16th century.",
        "Wind turbines generate kinetic green energy across offshore wind farms.",
    ]
    metadatas = [
        {
            "source_url": "https://energy.gov/solar",
            "source_title": "Solar Energy",
            "search_query": "renewable energy",
            "source_score": 0.92,
            "research_iteration": 1,
        },
        {
            "source_url": "https://literature.org/william",
            "source_title": "Shakespeare Plays",
            "search_query": "english playwrights",
            "source_score": 0.85,
            "research_iteration": 1,
        },
        {
            "source_url": "https://energy.gov/wind",
            "source_title": "Wind Energy",
            "search_query": "renewable energy",
            "source_score": 0.90,
            "research_iteration": 1,
        },
    ]
    embeddings = embed_documents(docs)
    ids = save_vectors(store, embeddings, docs, metadatas=metadatas)

    assert len(ids) == 3
    assert store.count() == 3

    # Query with solar / green energy topic
    results = query_vectors(store, "green solar electricity and clean power", top_k=2)
    top_docs = results["documents"][0]
    top_metas = results["metadatas"][0]

    assert len(top_docs) == 2
    # The top result must be the solar document
    assert "Solar photovoltaic" in top_docs[0]
    assert top_metas[0]["source_url"] == "https://energy.gov/solar"
    assert top_metas[0]["source_score"] == 0.92


def test_retrieve_relevant_chunks_structure():
    store = get_vector_store("test_session_2")
    docs = ["Electric vehicles reduce carbon dioxide emissions from urban transportation."]
    embeddings = embed_documents(docs)
    save_vectors(store, embeddings, docs)

    chunks = retrieve_relevant_chunks(store, "EV cars climate impact", top_k=5)
    assert len(chunks) == 1
    assert "Electric vehicles" in chunks[0]["text"]
    assert "similarity" in chunks[0]
    assert 0.0 <= chunks[0]["similarity"] <= 1.0


def test_empty_collection_query():
    store = get_vector_store("empty_session")
    results = query_vectors(store, "any query", top_k=5)
    assert results["documents"] == [[]]
    chunks = retrieve_relevant_chunks(store, "any query", top_k=5)
    assert chunks == []
