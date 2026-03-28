"""API layer for Node operations. Can be used by CLI, web server, TUI, etc."""

import json
from pathlib import Path
from sqlmodel import Session, select
from .database import engine
from .models import Node
from .vector_index import get_embedding, store_embedding


def add_node(
    description: str, context: str = "", status: str = "pending", type: str = "task"
) -> int:
    """Add a new node. Returns the node ID."""
    node = Node(description=description, context=context, status=status, type=type)
    with Session(engine) as session:
        session.add(node)
        session.commit()

        # Compute and store embedding using description, context, and type
        embedding = get_embedding(description, context, type)
        store_embedding(node.id, embedding)

        return node.id


def search_nodes(query: str) -> list[Node]:
    """Search nodes by description (case-insensitive)."""
    with Session(engine) as session:
        statement = select(Node).where(Node.description.ilike(f"%{query}%"))
        nodes = session.exec(statement).all()
        # Detach from session to avoid lazy loading issues
        return [Node.model_validate(node.model_dump()) for node in nodes]


def get_node(node_id: int) -> Node | None:
    """Get a single node by ID."""
    with Session(engine) as session:
        node = session.get(Node, node_id)
        return Node.model_validate(node.model_dump()) if node else None


def add_link(src_id: int, tgt_id: int, link_type: str = "why") -> int:
    """Create a directional link between nodes."""
    # Validate source/target exist
    if not get_node(src_id) or not get_node(tgt_id):
        raise ValueError("Source or target node not found")

    from .models import Link

    link = Link(src=src_id, tgt=tgt_id, link_type=link_type)
    with Session(engine) as session:
        session.add(link)
        session.commit()
        session.refresh(link)
        return link.id


def get_links(node_id: int) -> list[tuple[str, Node, Node]]:
    """Get all links where node is source or target."""
    from .models import Link

    with Session(engine) as session:
        statement = select(Link).where((Link.src == node_id) | (Link.tgt == node_id))
        links = session.exec(statement).all()

        results = []
        for link in links:
            src_node = session.get(Node, link.src)
            tgt_node = session.get(Node, link.tgt)
            if src_node and tgt_node:
                results.append((link.link_type, src_node, tgt_node))

    return results


def vector_search(
    query: str,
    k: int = 3,
    status: str | None = None,
    type: str | None = None,
    max_distance: float | None = None,
    exclude_ids: list[int] | None = None,
) -> list[tuple[Node, float]]:
    """Perform vector search with optional status/type filtering and max distance."""
    query_embedding = get_embedding(query)
    from .vector_index import fuzzy_search

    candidates = fuzzy_search(
        query_embedding,
        k=100,
        max_distance=max_distance,
        exclude_ids=exclude_ids,
    )

    results = []
    with Session(engine) as session:
        for node_id, distance in candidates:
            node = session.get(Node, node_id)
            if not node:
                continue
            if status is not None and node.status != status:
                continue
            if type is not None and node.type != type:
                continue
            results.append((Node.model_validate(node.model_dump()), distance))
            if len(results) >= k:
                break

    return results


def modify_node(
    node_id: int,
    description: str | None = None,
    context: str | None = None,
    status: str | None = None,
    type: str | None = None,
) -> bool:
    """Modify a node. Returns True if successful, False if not found."""
    with Session(engine) as session:
        node = session.get(Node, node_id)
        if not node:
            return False

        embedding_changed = False
        if description is not None:
            node.description = description
            embedding_changed = True
        if context is not None:
            node.context = context
            embedding_changed = True
        if status is not None:
            node.status = status
        if type is not None:
            node.type = type
            embedding_changed = True

        # Recompute embedding if any of the embedding-relevant fields changed
        if embedding_changed:
            embedding = get_embedding(node.description, node.context, node.type)
            store_embedding(node.id, embedding)

        session.commit()
        return True


def export_nodes(filepath: str) -> int:
    """Export all nodes to a JSON file. Returns the count of exported nodes."""
    with Session(engine) as session:
        statement = select(Node)
        nodes = session.exec(statement).all()

        data = [node.model_dump() for node in nodes]

        Path(filepath).write_text(json.dumps(data, indent=2))
        return len(nodes)


def import_nodes(filepath: str, clear: bool = False) -> int:
    """Import nodes from a JSON file. Returns the count of imported nodes."""
    data = json.loads(Path(filepath).read_text())

    with Session(engine) as session:
        if clear:
            # Clear existing nodes
            statement = select(Node)
            nodes = session.exec(statement).all()
            for node in nodes:
                session.delete(node)

        count = 0
        for item in data:
            # Validate using Node's Pydantic model
            node_data = Node.model_validate(item)

            if item.get("id") and not clear:
                # Try to update existing node
                node = session.get(Node, item["id"])
                if node:
                    for field, value in node_data.model_dump(
                        exclude_unset=True
                    ).items():
                        setattr(node, field, value)
                else:
                    session.add(node_data)
            else:
                # Create new node (auto-increment id)
                node_data.id = None  # Reset id for auto-increment
                session.add(node_data)

            count += 1

        session.commit()
        return count
