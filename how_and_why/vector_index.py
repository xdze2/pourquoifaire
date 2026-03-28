"""Vector embedding operations using Ollama and sqlite-vec."""

import ollama
from typing import List
from sqlalchemy import text
import sqlite_vec

from sqlite_vec import serialize_float32

from .database import engine


def prepare_embedding_text(
    description: str, context: str = "", type: str = "task"
) -> str:
    """Prepare text for embedding by combining description, context, and type."""
    parts = [description]
    if context:
        parts.append(f"Context: {context}")
    parts.append(f"Type: {type}")
    return " ".join(parts)


def get_embedding(
    description: str,
    context: str = "",
    type: str = "task",
    model: str = "nomic-embed-text",
) -> List[float]:
    """Get embedding for node using Ollama API.

    Uses nomic-embed-text (384 dimensions) which is optimized for shorter texts.
    Combines description, context, and type for richer embeddings.
    """
    prompt_text = prepare_embedding_text(description, context, type)
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


def fuzzy_search(
    query_vector: List[float],
    k: int = 3,
    max_distance: float | None = None,
    exclude_ids: list[int] | None = None,
) -> List[tuple[int, float]]:
    """Find k nearest neighbors using sqlite-vec."""
    with engine.connect() as conn:
        # Load extension for this connection
        raw_con = conn.connection
        raw_con.enable_load_extension(True)

        sqlite_vec.load(raw_con)

        results = conn.execute(
            text(
                """
            SELECT id, distance
            FROM vec_nodes
            WHERE embedding MATCH :query_vec AND k = :k
            ORDER BY distance
        """
            ),
            {"query_vec": serialize_float32(query_vector), "k": max(k * 5, 10)},
        ).fetchall()

        processed = []
        for row in results:
            node_id = int(row[0])
            distance = float(row[1])
            if exclude_ids and node_id in exclude_ids:
                continue
            if max_distance is not None and distance > max_distance:
                continue
            processed.append((node_id, distance))
            if len(processed) >= k:
                break

        return processed
