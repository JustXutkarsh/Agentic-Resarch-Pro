import numpy as np

def cosine_similarity(a, b):
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def verify_insight_semantically(insight, chunks, embedder, threshold=0.70):
    """
    Semantic validation using embeddings.
    """
    # Embed the insight
    insight_vec = embedder.embed([insight])[0]

    supporting = []
    for i, chunk in enumerate(chunks):
        chunk_vec = embedder.embed([chunk])[0]
        sim = cosine_similarity(insight_vec, chunk_vec)
        if sim >= threshold:
            supporting.append((i, sim))

    # Sort by best match first
    supporting.sort(key=lambda x: x[1], reverse=True)
    return supporting

