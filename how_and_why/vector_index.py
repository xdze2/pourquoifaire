"""Vector embedding operations using Ollama."""

import ollama
from typing import List


def get_embedding(text: str, model: str = "mxbai-embed-large") -> List[float]:
    """Get embedding for text using Ollama API."""
    response = ollama.embeddings(model=model, prompt=text)
    return response["embedding"]


# Mock storage - in-memory dict for now
_mock_embeddings = {}


def store_embedding(node_id: int, embedding: List[float]) -> None:
    """Mock storage of embedding - just print for now."""
    _mock_embeddings[node_id] = embedding
    print(f"Mock stored embedding for node {node_id}: {len(embedding)} dimensions")


def get_embedding_for_node(node_id: int) -> List[float] | None:
    """Mock retrieval of embedding."""
    return _mock_embeddings.get(node_id)
