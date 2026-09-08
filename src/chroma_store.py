"""
ChromaDB Vector Store Module for Agentic Research PRO.
Uses in-memory EphemeralClient with session-based isolation, cosine distance index,
rich source metadata, and unified Hugging Face embeddings for indexing and retrieval.
"""

import uuid
from typing import List, Dict, Any, Optional
from chromadb import EphemeralClient
from chromadb.api.models.Collection import Collection
from src.embedder import embed_text

# Global client instance to manage collections per session
_CHROMA_CLIENT: Optional[EphemeralClient] = None


def get_chroma_client() -> EphemeralClient:
    """Singleton getter for the Chroma EphemeralClient."""
    global _CHROMA_CLIENT
    if _CHROMA_CLIENT is None:
        _CHROMA_CLIENT = EphemeralClient()
    return _CHROMA_CLIENT


def reset_chroma_client() -> None:
    """Reset the global Chroma client (useful for testing and fresh sessions)."""
    global _CHROMA_CLIENT
    _CHROMA_CLIENT = None


def get_vector_store(session_id: Optional[str] = None) -> Collection:
    """
    Create or get a ChromaDB collection isolated by session_id.
    Uses cosine space for distance calculation.
    """
    client = get_chroma_client()
    collection_name = f"research_{session_id}" if session_id else "research_default"
    
    # Sanitize collection name (Chroma requires 3-63 chars, alphanumeric, dashes, underscores)
    safe_name = "".join(c if (c.isalnum() or c in "-_") else "_" for c in collection_name)[:63]
    if len(safe_name) < 3:
        safe_name = "research_store"

    existing_names = [c.name for c in client.list_collections()]
    if safe_name in existing_names:
        return client.get_collection(safe_name)
    
    return client.create_collection(
        name=safe_name,
        metadata={"hnsw:space": "cosine"}
    )


def save_vectors(
    collection: Collection,
    embeddings: List[List[float]],
    documents: List[str],
    metadatas: Optional[List[Dict[str, Any]]] = None,
    ids: Optional[List[str]] = None,
) -> List[str]:
    """
    Store documents, embeddings, and metadata into the Chroma collection.
    Automatically assigns unique deterministic/UUID ids if not provided.
    """
    if not documents or not embeddings:
        return []

    count = len(documents)
    if ids is None:
        ids = [f"{collection.name}_{uuid.uuid4().hex[:12]}_{i}" for i in range(count)]

    if metadatas is None:
        metadatas = [
            {
                "source_url": "",
                "source_title": "",
                "search_query": "",
                "source_score": 0.0,
                "research_iteration": 1,
            }
            for _ in range(count)
        ]
    else:
        # Ensure all metadata values are primitive types supported by Chroma (str, int, float, bool)
        clean_metadatas = []
        for m in metadatas:
            clean_m = {}
            for k, v in m.items():
                if isinstance(v, (str, int, float, bool)):
                    clean_m[k] = v
                elif v is None:
                    clean_m[k] = ""
                else:
                    clean_m[k] = str(v)
            clean_metadatas.append(clean_m)
        metadatas = clean_metadatas

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )
    return ids


def query_vectors(
    collection: Collection,
    query_text: str,
    top_k: int = 5,
    query_embedding: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """
    Query the collection using a unified Hugging Face embedding vector.
    If query_embedding is not pre-computed, it is computed via embed_text().
    """
    if collection.count() == 0:
        return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

    # Ensure query vector uses the exact same embedding model
    if query_embedding is None:
        query_embedding = embed_text(query_text)

    # top_k cannot exceed collection document count
    actual_k = min(top_k, collection.count())
    if actual_k <= 0:
        return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=actual_k,
        include=["documents", "metadatas", "distances"]
    )
    return results


def retrieve_relevant_chunks(
    collection: Collection,
    query: str,
    top_k: int = 10,
    query_embedding: Optional[List[float]] = None,
) -> List[Dict[str, Any]]:
    """
    Convenience function returning a flat list of structured evidence chunks:
    [{"text": ..., "metadata": ..., "similarity": ...}]
    """
    raw = query_vectors(collection, query, top_k=top_k, query_embedding=query_embedding)
    out = []
    if not raw or "documents" not in raw or not raw["documents"] or not raw["documents"][0]:
        return out

    docs = raw["documents"][0]
    metas = raw.get("metadatas", [[]])[0]
    dists = raw.get("distances", [[]])[0]

    for i in range(len(docs)):
        meta = metas[i] if i < len(metas) else {}
        dist = dists[i] if i < len(dists) else 0.0
        # In cosine distance: similarity = 1 - distance
        similarity = max(0.0, min(1.0, 1.0 - dist))
        out.append({
            "text": docs[i],
            "metadata": meta,
            "similarity": similarity,
            "distance": dist,
        })
    return out
