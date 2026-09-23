"""
ChromaDB Vector Store Module for Agentic Research PRO.
Uses in-memory EphemeralClient with session-based isolation, cosine distance index,
rich source metadata, and unified Hugging Face embeddings for indexing and retrieval.
"""

import os
import uuid
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import chromadb
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection
from src.embedder import embed_text

logger = logging.getLogger("ChromaStore")

# Global client instance to manage collections per session
_CHROMA_CLIENT: Optional[ClientAPI] = None


def get_chroma_client() -> ClientAPI:
    """
    Singleton getter for the Chroma client.
    Defaults to in-memory EphemeralClient for containerized research isolation.
    If CHROMA_PERSIST_DIR is set (e.g. Railway mounted persistent volume),
    uses PersistentClient at that directory.
    """
    global _CHROMA_CLIENT
    if _CHROMA_CLIENT is None:
        persist_dir = os.environ.get("CHROMA_PERSIST_DIR", "").strip()
        if persist_dir:
            os.makedirs(persist_dir, exist_ok=True)
            _CHROMA_CLIENT = chromadb.PersistentClient(path=persist_dir)
            logger.info(f"Initialized Chroma PersistentClient at {persist_dir}")
        else:
            _CHROMA_CLIENT = chromadb.EphemeralClient()
            logger.info("Initialized Chroma EphemeralClient (in-memory)")
    return _CHROMA_CLIENT



def reset_chroma_client() -> None:
    """Reset the global Chroma client (useful for testing and fresh sessions)."""
    global _CHROMA_CLIENT
    _CHROMA_CLIENT = None


def _extract_session_id(collection: Collection, explicit_session_id: Optional[str] = None) -> str:
    """Extract or validate the research session ID associated with a collection."""
    if explicit_session_id and explicit_session_id.strip():
        return explicit_session_id.strip()
    
    col_name = collection.name
    if col_name.startswith("research_") and len(col_name) > len("research_"):
        return col_name[len("research_"):]
    return col_name


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
    session_id: Optional[str] = None,
) -> List[str]:
    """
    Store documents, embeddings, and metadata into the Chroma collection.
    Guarantees that every item is stamped with research_session_id, document_id, and chunk_id.
    """
    if not documents or not embeddings:
        return []

    count = len(documents)
    current_session = _extract_session_id(collection, session_id)

    if ids is None:
        ids = [f"chk_{current_session[:16]}_{uuid.uuid4().hex[:12]}_{i}" for i in range(count)]

    clean_metadatas = []
    for i in range(count):
        raw_meta = metadatas[i] if metadatas and i < len(metadatas) else {}
        
        # Ensure mandatory provenance and isolation keys
        src_url = str(raw_meta.get("source_url") or "")
        src_domain = raw_meta.get("source_domain")
        if not src_domain and src_url:
            try:
                src_domain = urlparse(src_url).netloc.lower()
            except Exception:
                src_domain = ""
        
        doc_id = str(raw_meta.get("document_id") or f"doc_{uuid.uuid4().hex[:8]}")
        chunk_id = str(raw_meta.get("chunk_id") or ids[i])
        item_session = str(raw_meta.get("research_session_id") or current_session)

        # Build clean metadata with primitive types
        clean_m: Dict[str, Any] = {
            "research_session_id": item_session,
            "document_id": doc_id,
            "chunk_id": chunk_id,
            "source_url": src_url,
            "source_domain": str(src_domain or ""),
            "source_title": str(raw_meta.get("source_title") or ""),
            "search_query": str(raw_meta.get("search_query") or ""),
            "source_score": float(raw_meta.get("source_score", 0.5)),
            "research_iteration": int(raw_meta.get("research_iteration", 1)),
            "acquisition_method": str(raw_meta.get("acquisition_method", "http")),
            "authority_tier": int(raw_meta.get("authority_tier", 3)),
            "source_type": str(raw_meta.get("source_type", "general")),
            "section_heading": str(raw_meta.get("section_heading") or ""),
        }

        # Copy any additional primitive fields
        for k, v in raw_meta.items():
            if k not in clean_m:
                if isinstance(v, (str, int, float, bool)):
                    clean_m[k] = v
                elif v is None:
                    clean_m[k] = ""
                else:
                    clean_m[k] = str(v)

        clean_metadatas.append(clean_m)

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=clean_metadatas,
    )
    return ids


def query_vectors(
    collection: Collection,
    query_text: str,
    top_k: int = 5,
    query_embedding: Optional[List[float]] = None,
    session_id: Optional[str] = None,
    where: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Query the collection using a unified Hugging Face embedding vector.
    Strictly scoped to research_session_id BEFORE semantic similarity ranking.
    """
    if collection.count() == 0:
        return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

    current_session = _extract_session_id(collection, session_id)

    # Build strict session-isolated where clause
    query_where: Dict[str, Any] = {"research_session_id": current_session}
    if where:
        query_where.update(where)

    # Ensure query vector uses the exact same embedding model
    if query_embedding is None:
        query_embedding = embed_text(query_text)

    # top_k cannot exceed collection document count
    actual_k = min(top_k, collection.count())
    if actual_k <= 0:
        return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=actual_k,
            where=query_where,
            include=["documents", "metadatas", "distances"]
        )
    except Exception as e:
        logger.warning(f"Chroma query with where filter failed ({e}), falling back to collection-scoped query.")
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
    session_id: Optional[str] = None,
    where: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Convenience function returning a flat list of structured evidence chunks:
    [{"text": ..., "metadata": ..., "similarity": ...}]
    Enforces dual-layer session isolation:
    1. Pre-retrieval ChromaDB where clause.
    2. Post-retrieval verification dropping any mismatched chunk with SESSION_ISOLATION_VIOLATION warning.
    """
    current_session = _extract_session_id(collection, session_id)
    raw = query_vectors(
        collection,
        query,
        top_k=top_k,
        query_embedding=query_embedding,
        session_id=current_session,
        where=where,
    )
    out = []
    if not raw or "documents" not in raw or not raw["documents"] or not raw["documents"][0]:
        return out

    docs = raw["documents"][0]
    metas = raw.get("metadatas", [[]])[0]
    dists = raw.get("distances", [[]])[0]

    for i in range(len(docs)):
        meta = metas[i] if i < len(metas) else {}
        dist = dists[i] if i < len(dists) else 0.0

        # Post-retrieval isolation guard
        chunk_session = meta.get("research_session_id")
        if chunk_session and current_session and chunk_session != current_session:
            logger.warning(
                f"SESSION_ISOLATION_VIOLATION: Chunk {meta.get('chunk_id')} belongs to session "
                f"'{chunk_session}', but current session is '{current_session}'. Rejecting evidence."
            )
            continue

        # In cosine distance: similarity = 1 - distance
        similarity = max(0.0, min(1.0, 1.0 - dist))
        out.append({
            "text": docs[i],
            "metadata": meta,
            "similarity": similarity,
            "distance": dist,
            "chunk_id": meta.get("chunk_id", ""),
            "document_id": meta.get("document_id", ""),
            "source_url": meta.get("source_url", ""),
            "source_domain": meta.get("source_domain", ""),
        })
    return out
