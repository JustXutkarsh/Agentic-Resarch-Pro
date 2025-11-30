from chromadb import EphemeralClient

# Create new Chroma client (no deprecated settings)
def get_vector_store():
    client = EphemeralClient()

    # Create or reuse collection
    if "research" not in [c.name for c in client.list_collections()]:
        collection = client.create_collection(
            name="research",
            metadata={"hnsw:space": "cosine"}
        )
    else:
        collection = client.get_collection("research")

    return collection


def save_vectors(collection, embeddings, documents):
    ids = [f"doc_{i}" for i in range(len(documents))]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents
    )


def query_vectors(collection, query_text, top_k=5):
    return collection.query(
        query_texts=[query_text],
        n_results=top_k
    )


