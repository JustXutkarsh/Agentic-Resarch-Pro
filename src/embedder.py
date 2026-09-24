import os
import gc
import hashlib
from functools import lru_cache
from typing import List, Dict, Optional, Any
from src.config import EMBEDDING_MODEL, EMBEDDING_DIMENSION
from src.memory_guard import configure_low_memory_environment, log_memory_stage, trigger_garbage_collection

# Ensure environment variables for single-threaded CPU operations are set
configure_low_memory_environment()

# In-memory vector cache keyed by SHA-256 hash of normalized text
_EMBEDDING_CACHE: Dict[str, List[float]] = {}
MAX_CACHE_ENTRIES = 512


@lru_cache(maxsize=1)
def load_embedding_model() -> Any:
    """
    Loads and caches the SentenceTransformer model in memory.
    Singleton pattern ensures the model is loaded only once across the entire process.
    Configured strictly for CPU inference with gradient tracking disabled and bounded threads.
    """
    import torch
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    torch.set_grad_enabled(False)

    from sentence_transformers import SentenceTransformer
    log_memory_stage("pre_embedding_model_load")
    model = SentenceTransformer(EMBEDDING_MODEL, device="cpu")
    model.eval()
    for param in model.parameters():
        param.requires_grad = False
    log_memory_stage("post_embedding_model_load")
    return model


def is_embedding_model_loaded() -> bool:
    """Return True if the embedding model is already loaded in memory."""
    try:
        return load_embedding_model.cache_info().currsize > 0
    except Exception:
        return False


def _compute_sha256(text: str) -> str:
    """Compute SHA-256 hash for text cache key."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _set_cache(key: str, vec: List[float]) -> None:
    """Store vector in cache with bounded size to prevent memory leaks in constrained environments."""
    if len(_EMBEDDING_CACHE) >= MAX_CACHE_ENTRIES:
        # Evict oldest 25% of entries
        for k in list(_EMBEDDING_CACHE.keys())[:MAX_CACHE_ENTRIES // 4]:
            _EMBEDDING_CACHE.pop(k, None)
    _EMBEDDING_CACHE[key] = vec


def embed_text(text: str) -> List[float]:
    """
    Generate a 384-dimensional vector embedding for a single text string.
    Checks memory cache before generating embedding using inference_mode.
    """
    if not text or not text.strip():
        return [0.0] * EMBEDDING_DIMENSION

    cache_key = _compute_sha256(text)
    if cache_key in _EMBEDDING_CACHE:
        return list(_EMBEDDING_CACHE[cache_key])

    import torch
    model = load_embedding_model()
    with torch.inference_mode():
        vec = model.encode(text, convert_to_numpy=True, show_progress_bar=False).tolist()
    _set_cache(cache_key, vec)
    return vec


def embed_documents(documents: List[str], batch_size: int = 16) -> List[List[float]]:
    """
    Generate vector embeddings for a list of document strings with batching and caching.
    Uses bounded batch size (default 16) and releases intermediate representations.
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

    # Compute embeddings for uncached texts in bounded batches
    if uncached_texts:
        import torch
        model = load_embedding_model()
        computed_vectors: List[List[float]] = []

        with torch.inference_mode():
            for b_start in range(0, len(uncached_texts), batch_size):
                b_slice = uncached_texts[b_start : b_start + batch_size]
                b_vecs = model.encode(
                    b_slice,
                    batch_size=len(b_slice),
                    convert_to_numpy=True,
                    show_progress_bar=False,
                )
                computed_vectors.extend(b_vecs.tolist())
                del b_slice
                del b_vecs

        for idx, doc, vec in zip(uncached_indices, uncached_texts, computed_vectors):
            cache_key = _compute_sha256(doc)
            _set_cache(cache_key, vec)
            results[idx] = vec

        del uncached_texts
        del computed_vectors
        if len(uncached_indices) > 32:
            trigger_garbage_collection("embed_documents_batch")

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
