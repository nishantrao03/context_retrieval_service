from typing import List
from sentence_transformers import SentenceTransformer
import json


class TextEmbedder:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize embedding model.
        """
        self.model = SentenceTransformer(model_name)

    def embed_text(self, text: str) -> List[float]:
        """
        Converts a single piece of text into an embedding vector.
        """
        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embedding.tolist()

    def embed_text_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Converts multiple pieces of text into embedding vectors using batch encoding.
        """
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embeddings.tolist()


# -----------------------------
# Test Main
# -----------------------------

def main():
    sample_text = (
        "Global warming is causing significant changes in natural environments. "
        "One of the most visible effects is the melting of glaciers."
    )

    embedder = TextEmbedder()
    vector = embedder.embed_text(sample_text)

    # Write entire vector to file
    with open("embedded_text.txt", "w", encoding="utf-8") as f:
        json.dump(vector, f, indent=4)

    print("Embedding vector length:", len(vector))
    print("Embedding written to embedded_text.txt")


if __name__ == "__main__":
    main()