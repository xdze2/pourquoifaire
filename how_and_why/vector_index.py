"""Vector embedding operations using Ollama and sqlite-vec."""

import ollama
from typing import List
from sqlalchemy import text
import sqlite_vec

from sqlite_vec import serialize_float32

from .database import engine


def get_embedding(prompt_text: str, model: str = "mxbai-embed-large") -> List[float]:
    """Get embedding for text using Ollama API."""
    response = ollama.embeddings(model=model, prompt=prompt_text)
    return response["embedding"]


def store_embedding(node_id: int, embedding: List[float]) -> None:
    """Store embedding in sqlite-vec table."""
    with engine.connect() as conn:
        # Load extension for this connection
        raw_con = conn.connection
        raw_con.enable_load_extension(True)

        sqlite_vec.load(raw_con)

        # Insert or replace the embedding

        conn.execute(
            text(
                """
            INSERT OR REPLACE INTO vec_nodes (id, embedding)
            VALUES (:id, :embedding)
        """
            ),
            {"id": node_id, "embedding": serialize_float32(embedding)},
        )
        conn.commit()


def get_embedding_for_node(node_id: int) -> List[float] | None:
    """Retrieve embedding for a node from sqlite-vec table."""
    with engine.connect() as conn:
        # Load extension for this connection
        raw_con = conn.connection
        raw_con.enable_load_extension(True)

        sqlite_vec.load(raw_con)

        result = conn.execute(
            text(
                """
            SELECT embedding FROM vec_nodes WHERE id = :id
        """
            ),
            {"id": node_id},
        ).fetchone()

        if result:
            # sqlite-vec returns the vector as a list of floats when queried
            return result[0]
        return None


def fuzzy_search(query_vector: List[float], k: int = 3) -> List[tuple[int, float]]:
    """Find k nearest neighbors using sqlite-vec."""
    with engine.connect() as conn:
        # Load extension for this connection
        raw_con = conn.connection
        raw_con.enable_load_extension(True)

        sqlite_vec.load(raw_con)

        # KNN Search: Find the closest Node IDs

        results = conn.execute(
            text(
                """
            SELECT id, distance
            FROM vec_nodes
            WHERE embedding MATCH :query_vec AND k = :k
            ORDER BY distance
        """
            ),
            {"query_vec": serialize_float32(query_vector), "k": k},
        ).fetchall()

        return [(int(row[0]), float(row[1])) for row in results]
