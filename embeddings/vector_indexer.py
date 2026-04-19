import os
import sys
import json
import uuid
from typing import List, Dict, Any

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from embeddings.embedder import TextEmbedder
from vectorstore.pinecone_client import get_pinecone_index


def index_vectors(
    json_chunks: List[Dict[str, Any]],
    project_id: str,
    index_name: str = "slack-bot-context"
):

    if not json_chunks:
        print("No chunks provided for indexing.")
        return

    embedder = TextEmbedder()
    embedding_dimension = 384

    pinecone_index = get_pinecone_index(
        index_name=index_name,
        dimension=embedding_dimension
    )

    valid_chunks = [
        chunk for chunk in json_chunks
        if chunk.get("chunk_id") and chunk.get("text")
    ]

    if not valid_chunks:
        print("No valid chunks found.")
        return

    texts = [chunk["text"] for chunk in valid_chunks]
    embeddings = embedder.model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        batch_size=32
    )

    formatted_vectors = []

    for chunk, vector in zip(valid_chunks, embeddings):

        if len(vector) != embedding_dimension:
            raise ValueError(
                f"Embedding dimension mismatch. "
                f"Expected {embedding_dimension}, got {len(vector)}"
            )

        metadata = {
            "layer": "base_layer",
            "document_id": chunk["document_id"],
            "document_type": chunk["document_type"],
            "section": chunk["section"],
            "chunk_index": chunk["chunk_index"],
            "section_chunk_count": chunk["section_chunk_count"],
            "text": chunk["text"],
            "token_count": chunk["token_count"]
        }

        vector_id = str(uuid.uuid4())

        formatted_vectors.append({
            "id": vector_id,
            "values": vector.tolist(),
            "metadata": metadata
        })

    batch_size = 100
    for i in range(0, len(formatted_vectors), batch_size):
        batch = formatted_vectors[i:i + batch_size]

        for vector_data in batch:
            print("--- Debug: Vector Payload ---")
            print(json.dumps(vector_data, indent=2))

        pinecone_index.upsert(
            vectors=batch,
            namespace=project_id
        )

        print(f"Upserted batch: {i} to {i + len(batch)}")

    print(f"Successfully processed and uploaded {len(formatted_vectors)} vectors.")