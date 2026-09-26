"""
Unified Embedding Subsystem for Agentic Research PRO.

Provides a clean provider abstraction supporting:
1. Local SentenceTransformer (all-MiniLM-L6-v2, 384-dim) for offline local development.
   Uses lazy imports so torch/transformers are NEVER loaded when using remote providers.
2. NVIDIA Remote NIM Embeddings (nvidia/nemotron-3-embed-1b, 2048-dim) for memory-constrained
   production deployments (e.g. Render 512 MB Free tier).

Configured via EMBEDDING_PROVIDER ('local' or 'nvidia').
"""

import os
import gc
import time
import hashlib
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from functools import lru_cache

from src.config import (
    EMBEDDING_PROVIDER,
    NVIDIA_BASE_URL,
    NVIDIA_EMBEDDING_MODEL,
    EMBEDDING_BATCH_SIZE,
    get_embedding_dimension,
    get_embedding_model,
    get_embedding_provider_name,
)
from src.memory_guard import configure_low_memory_environment, log_memory_stage, trigger_garbage_collection

logger = logging.getLogger("Embedder")

# Ensure environment variables for single-threaded CPU operations are set
configure_low_memory_environment()

# In-memory vector cache keyed by SHA-256 hash of f"{mode}:{text}"
_EMBEDDING_CACHE: Dict[str, List[float]] = {}
MAX_CACHE_ENTRIES = 1024


def _compute_cache_key(provider: str, mode: str, text: str) -> str:
    """Compute SHA-256 cache key including provider ('local' or 'nvidia') and mode ('query' or 'passage')."""
    payload = f"{provider}:{mode}:{text}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _set_cache(key: str, vec: List[float]) -> None:
    """Store vector in cache with bounded size to prevent memory leaks."""
    if len(_EMBEDDING_CACHE) >= MAX_CACHE_ENTRIES:
        # Evict oldest 25% of entries
        keys = list(_EMBEDDING_CACHE.keys())[: MAX_CACHE_ENTRIES // 4]
        for k in keys:
            _EMBEDDING_CACHE.pop(k, None)
    _EMBEDDING_CACHE[key] = vec


def clear_embedding_cache() -> None:
    """Clear the in-memory embedding cache."""
    _EMBEDDING_CACHE.clear()


# ==============================================================================
# Abstract Embedding Provider Base Class
# ==============================================================================

class EmbeddingProvider(ABC):
    """Abstract interface for text embedding providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of provider ('local' or 'nvidia')."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Active model identifier."""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Vector embedding dimension."""
        pass

    @abstractmethod
    def embed_text(self, text: str, is_query: bool = False) -> List[float]:
        """Generate vector embedding for a single string."""
        pass

    @abstractmethod
    def embed_documents(self, documents: List[str], batch_size: int = 16) -> List[List[float]]:
        """Generate vector embeddings for a list of document strings."""
        pass

    def embed_query(self, query: str) -> List[float]:
        """Convenience method to generate a query embedding."""
        return self.embed_text(query, is_query=True)


# ==============================================================================
# Local SentenceTransformer Provider (Lazy Imports)
# ==============================================================================

class LocalSentenceTransformerProvider(EmbeddingProvider):
    """
    Local in-process SentenceTransformer provider using CPU inference.
    CRITICAL: torch and sentence_transformers are imported ONLY when this provider is used,
    preventing any memory allocation on remote/production environments.
    """

    def __init__(self, model_name: Optional[str] = None):
        self._model_name = model_name or "sentence-transformers/all-MiniLM-L6-v2"
        self._dimension = 384
        self._model: Optional[Any] = None

    @property
    def provider_name(self) -> str:
        return "local"

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimension(self) -> int:
        return self._dimension

    def _ensure_model(self) -> Any:
        """Lazy-load the SentenceTransformer model on first invocation."""
        if self._model is None:
            # Lazy import to keep production memory footprint small
            import torch

            torch.set_num_threads(1)
            try:
                torch.set_num_interop_threads(1)
            except RuntimeError:
                pass
            torch.set_grad_enabled(False)

            from sentence_transformers import SentenceTransformer

            log_memory_stage("pre_embedding_model_load")
            model = SentenceTransformer(self._model_name, device="cpu")
            model.eval()
            for param in model.parameters():
                param.requires_grad = False
            self._model = model
            log_memory_stage("post_embedding_model_load")
        return self._model

    def is_loaded(self) -> bool:
        return self._model is not None

    def embed_text(self, text: str, is_query: bool = False) -> List[float]:
        if not text or not text.strip():
            return [0.0] * self._dimension

        mode = "query" if is_query else "passage"
        cache_key = _compute_cache_key(self.provider_name, mode, text)
        if cache_key in _EMBEDDING_CACHE:
            return list(_EMBEDDING_CACHE[cache_key])

        import torch
        model = self._ensure_model()
        with torch.inference_mode():
            vec = model.encode(text, convert_to_numpy=True, show_progress_bar=False).tolist()

        if len(vec) != self._dimension:
            raise ValueError(f"Local embedder returned vector of dimension {len(vec)}, expected {self._dimension}.")

        _set_cache(cache_key, vec)
        return vec

    def embed_documents(self, documents: List[str], batch_size: int = 16) -> List[List[float]]:
        if not documents:
            return []

        results: List[Optional[List[float]]] = [None] * len(documents)
        uncached_indices: List[int] = []
        uncached_texts: List[str] = []

        for idx, doc in enumerate(documents):
            if not doc or not doc.strip():
                results[idx] = [0.0] * self._dimension
                continue

            cache_key = _compute_cache_key(self.provider_name, "passage", doc)
            if cache_key in _EMBEDDING_CACHE:
                results[idx] = list(_EMBEDDING_CACHE[cache_key])
            else:
                uncached_indices.append(idx)
                uncached_texts.append(doc)

        if uncached_texts:
            import torch
            model = self._ensure_model()
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
                if len(vec) != self._dimension:
                    raise ValueError(f"Vector at index {idx} has invalid dimension {len(vec)}, expected {self._dimension}.")
                cache_key = _compute_cache_key(self.provider_name, "passage", doc)
                _set_cache(cache_key, vec)
                results[idx] = vec

            del uncached_texts
            del computed_vectors
            if len(uncached_indices) > 32:
                trigger_garbage_collection("local_embed_batch")

        return [v for v in results if v is not None]


# ==============================================================================
# NVIDIA Remote NIM Embedding Provider
# ==============================================================================

class NVIDIAEmbeddingProvider(EmbeddingProvider):
    """
    Remote embedding provider invoking NVIDIA NIM embeddings API (nemotron-3-embed-1b).
    - Requires zero local PyTorch or SentenceTransformers imports.
    - Uses 2048-dimensional dense embeddings.
    - Distinguishes input_type='passage' for documents from input_type='query' for search queries.
    - Handles bounded batching and exponential backoff on transient errors.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        batch_size: Optional[int] = None,
        max_retries: int = 3,
        timeout: float = 30.0,
    ):
        self._api_key = (api_key or os.getenv("NVIDIA_API_KEY", "")).strip()
        if not self._api_key:
            raise ValueError(
                "NVIDIA_API_KEY environment variable is required to use NVIDIAEmbeddingProvider. "
                "Ensure NVIDIA_API_KEY is configured or set EMBEDDING_PROVIDER=local."
            )

        self._base_url = (base_url or os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")).rstrip("/")
        self._model_name = (model_name or os.getenv("NVIDIA_EMBEDDING_MODEL", "nvidia/nemotron-3-embed-1b")).strip()
        self._batch_size = batch_size or int(os.getenv("EMBEDDING_BATCH_SIZE", str(EMBEDDING_BATCH_SIZE)))
        self._dimension = 2048
        self._max_retries = max_retries
        self._timeout = timeout

    @property
    def provider_name(self) -> str:
        return "nvidia"

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimension(self) -> int:
        return self._dimension

    def _post_with_retry(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute POST request to NVIDIA embeddings endpoint with exponential backoff on transient errors.
        Does NOT retry on 401, 403, 400, 404, or 422.
        """
        import httpx

        url = f"{self._base_url}/embeddings"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        last_exception = None
        for attempt in range(self._max_retries + 1):
            try:
                with httpx.Client(timeout=self._timeout) as client:
                    resp = client.post(url, headers=headers, json=payload)

                if resp.status_code == 200:
                    return resp.json()

                # Non-retryable status codes
                if resp.status_code in (401, 403):
                    raise PermissionError(
                        f"NVIDIA API authentication failure ({resp.status_code}). Check NVIDIA_API_KEY: {resp.text}"
                    )
                if resp.status_code in (400, 404, 422):
                    raise ValueError(
                        f"NVIDIA API request rejected ({resp.status_code}) for model '{self._model_name}': {resp.text}"
                    )

                # Transient server / rate limit errors: 429, 500, 502, 503, 504
                if resp.status_code in (429, 500, 502, 503, 504):
                    if attempt < self._max_retries:
                        backoff = 1.0 * (2 ** attempt)
                        logger.warning(
                            f"NVIDIA embeddings API returned {resp.status_code}; retrying in {backoff:.1f}s (attempt {attempt+1}/{self._max_retries})"
                        )
                        time.sleep(backoff)
                        continue
                    resp.raise_for_status()

                # Any other unexpected status code
                resp.raise_for_status()

            except (httpx.TimeoutException, httpx.NetworkError) as e:
                last_exception = e
                if attempt < self._max_retries:
                    backoff = 1.0 * (2 ** attempt)
                    logger.warning(
                        f"NVIDIA embeddings network error ({type(e).__name__}); retrying in {backoff:.1f}s (attempt {attempt+1}/{self._max_retries})"
                    )
                    time.sleep(backoff)
                    continue
                raise

        if last_exception:
            raise last_exception
        raise RuntimeError("NVIDIA embeddings request failed after retries.")

    def embed_text(self, text: str, is_query: bool = False) -> List[float]:
        if not text or not text.strip():
            return [0.0] * self._dimension

        input_type = "query" if is_query else "passage"
        cache_key = _compute_cache_key(self.provider_name, input_type, text)
        if cache_key in _EMBEDDING_CACHE:
            return list(_EMBEDDING_CACHE[cache_key])

        payload = {
            "model": self._model_name,
            "input": [text],
            "input_type": input_type,
        }

        data = self._post_with_retry(payload)
        items = data.get("data", [])
        if not items or "embedding" not in items[0]:
            raise ValueError(f"NVIDIA embeddings API returned malformed response: {data}")

        vec = items[0]["embedding"]
        if len(vec) != self._dimension:
            raise ValueError(
                f"NVIDIA embedding vector dimension mismatch: got {len(vec)}, expected {self._dimension}."
            )

        _set_cache(cache_key, vec)
        return vec

    def embed_documents(self, documents: List[str], batch_size: Optional[int] = None) -> List[List[float]]:
        if not documents:
            return []

        effective_batch_size = batch_size or self._batch_size
        results: List[Optional[List[float]]] = [None] * len(documents)
        uncached_indices: List[int] = []
        uncached_texts: List[str] = []

        # Check in-memory cache first
        for idx, doc in enumerate(documents):
            if not doc or not doc.strip():
                results[idx] = [0.0] * self._dimension
                continue

            cache_key = _compute_cache_key(self.provider_name, "passage", doc)
            if cache_key in _EMBEDDING_CACHE:
                results[idx] = list(_EMBEDDING_CACHE[cache_key])
            else:
                uncached_indices.append(idx)
                uncached_texts.append(doc)

        # Batch uncached texts
        if uncached_texts:
            for b_start in range(0, len(uncached_texts), effective_batch_size):
                b_slice = uncached_texts[b_start : b_start + effective_batch_size]
                b_indices = uncached_indices[b_start : b_start + effective_batch_size]

                payload = {
                    "model": self._model_name,
                    "input": b_slice,
                    "input_type": "passage",
                }

                data = self._post_with_retry(payload)
                raw_items = data.get("data", [])
                if len(raw_items) != len(b_slice):
                    raise ValueError(
                        f"NVIDIA embeddings returned {len(raw_items)} vectors for batch of {len(b_slice)} texts."
                    )

                # Sort by index to guarantee strict input ordering
                sorted_items = sorted(raw_items, key=lambda item: item.get("index", 0))

                for orig_idx, doc, item in zip(b_indices, b_slice, sorted_items):
                    vec = item.get("embedding", [])
                    if len(vec) != self._dimension:
                        raise ValueError(
                            f"NVIDIA embedding vector at index {orig_idx} has dimension {len(vec)}, expected {self._dimension}."
                        )
                    cache_key = _compute_cache_key(self.provider_name, "passage", doc)
                    _set_cache(cache_key, vec)
                    results[orig_idx] = vec

        return [v for v in results if v is not None]


# ==============================================================================
# Factory & Singleton Management
# ==============================================================================

_ACTIVE_PROVIDER: Optional[EmbeddingProvider] = None


def get_embedding_provider() -> EmbeddingProvider:
    """
    Get the configured embedding provider singleton ('local' or 'nvidia').
    Dynamically respects EMBEDDING_PROVIDER environment variable.
    """
    global _ACTIVE_PROVIDER
    configured_provider = os.getenv("EMBEDDING_PROVIDER", "local").strip().lower()

    if _ACTIVE_PROVIDER is not None:
        if _ACTIVE_PROVIDER.provider_name == configured_provider:
            return _ACTIVE_PROVIDER

    if configured_provider == "nvidia":
        logger.info(f"Initializing NVIDIAEmbeddingProvider (model={NVIDIA_EMBEDDING_MODEL}, dim=2048)")
        _ACTIVE_PROVIDER = NVIDIAEmbeddingProvider()
    else:
        logger.info("Initializing LocalSentenceTransformerProvider (all-MiniLM-L6-v2, dim=384)")
        _ACTIVE_PROVIDER = LocalSentenceTransformerProvider()

    return _ACTIVE_PROVIDER


def reset_embedding_provider() -> None:
    """Reset the singleton embedding provider (useful for tests and dynamic configuration)."""
    global _ACTIVE_PROVIDER
    _ACTIVE_PROVIDER = None


# ==============================================================================
# Public API Functions (Provider-Agnostic)
# ==============================================================================

def embed_text(text: str, is_query: bool = False) -> List[float]:
    """Generate embedding vector for a single text string."""
    return get_embedding_provider().embed_text(text, is_query=is_query)


def embed_query(query: str) -> List[float]:
    """Generate embedding vector optimized for retrieval queries."""
    return get_embedding_provider().embed_query(query)


def embed_documents(documents: List[str], batch_size: Optional[int] = None) -> List[List[float]]:
    """Generate embeddings for a list of document chunks using bounded batches."""
    bs = batch_size or EMBEDDING_BATCH_SIZE
    return get_embedding_provider().embed_documents(documents, batch_size=bs)


def load_embedding_model() -> Any:
    """
    Backward-compatible model loader.
    For local provider, loads and returns the SentenceTransformer instance.
    For remote NVIDIA provider, returns the provider instance.
    """
    provider = get_embedding_provider()
    if isinstance(provider, LocalSentenceTransformerProvider):
        return provider._ensure_model()
    return provider


def is_embedding_model_loaded() -> bool:
    """Return True if local embedding model is currently resident in memory."""
    provider = get_embedding_provider()
    if isinstance(provider, LocalSentenceTransformerProvider):
        return provider.is_loaded()
    # Remote provider requires no local model in memory
    return True


class HuggingFaceEmbedder:
    """
    Object wrapper around the active embedding provider.
    Provides standard .embed() and .embed_query() interface for legacy components.
    """
    def __init__(self):
        self._provider = get_embedding_provider()
        self.model_name = self._provider.model_name
        self.dimension = self._provider.dimension

    def embed(self, text_list: List[str]) -> List[List[float]]:
        return self._provider.embed_documents(text_list)

    def embed_query(self, query: str) -> List[float]:
        return self._provider.embed_query(query)


# Alias for backward-compatibility
OpenAIEmbedder = HuggingFaceEmbedder
