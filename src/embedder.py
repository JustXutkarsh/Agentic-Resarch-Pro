"""
Local Hugging Face Embedding Engine using sentence-transformers/all-MiniLM-L6-v2.
Completely replaces OpenAI embeddings with zero API cost, cached singleton model loading,
and SHA256 content-hash vector caching.
"""

import hashlib
from functools import lru_cache
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
from src.config import EMBEDDING_MODEL, EMBEDDING_DIMENSION

# In-memory vector cache keyed by SHA-256 hash of normalized text
_EMBEDDING_CACHE: Dict[str, List[float]] = {}


@lru_cache(maxsize=1)
def load_embedding_model() -> SentenceTransformer:
    """
    Loads and caches the SentenceTransformer model in memory.
    Singleton pattern ensures the model is loaded only once across the entire session.
    """
    return SentenceTransformer(EMBEDDING_MODEL)


def _compute_sha256(text: str) -> str:
    """Compute SHA-256 hash for text cache key."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def embed_text(text: str) -> List[float]:
    """
    Generate a 384-dimensional vector embedding for a single text string.
    Checks memory cache before generating embedding.
    """
    if not text or not text.strip():
        return [0.0] * EMBEDDING_DIMENSION

    cache_key = _compute_sha256(text)
    if cache_key in _EMBEDDING_CACHE:
        return list(_EMBEDDING_CACHE[cache_key])

    model = load_embedding_model()
    vec = model.encode(text, convert_to_numpy=True).tolist()
    _EMBEDDING_CACHE[cache_key] = vec
    return vec


def embed_documents(documents: List[str], batch_size: int = 32) -> List[List[float]]:
    """
    Generate vector embeddings for a list of document strings with batching and caching.
    Returns a list of 384-dimensional vectors.
    """
    if not documents:
        return []

    results: List[Optional[List[float]]] = [None] * len(documents)
    uncached_indices: List[int] = []
    uncached_texts: List[str] = []

    # Check cache for each document
    for idx, doc in enumerate(documents):
        if not doc or not doc.strip():
            results[idx] = [0.0] * EMBEDDING_DIMENSION
            continue

        cache_key = _compute_sha256(doc)
        if cache_key in _EMBEDDING_CACHE:
            results[idx] = list(_EMBEDDING_CACHE[cache_key])
        else:
            uncached_indices.append(idx)
            uncached_texts.append(doc)

    # Compute embeddings for uncached texts in batches
    if uncached_texts:
        model = load_embedding_model()
        computed_vectors = model.encode(
            uncached_texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=False
        ).tolist()

        for idx, doc, vec in zip(uncached_indices, uncached_texts, computed_vectors):
            cache_key = _compute_sha256(doc)
            _EMBEDDING_CACHE[cache_key] = vec
            results[idx] = vec

    return [v for v in results if v is not None]


def clear_embedding_cache() -> None:
    """Clear in-memory embedding cache."""
    _EMBEDDING_CACHE.clear()


class HuggingFaceEmbedder:
    """
    Object wrapper around the singleton embedding model.
    Provides standard .embed() interface for pipeline components.
    """
    def __init__(self):
        self.model_name = EMBEDDING_MODEL
        self.dimension = EMBEDDING_DIMENSION

    def embed(self, text_list: List[str]) -> List[List[float]]:
        return embed_documents(text_list)

    def embed_query(self, query: str) -> List[float]:
        return embed_text(query)


# Alias for backward-compatibility if old components import Embedder
OpenAIEmbedder = HuggingFaceEmbedder
