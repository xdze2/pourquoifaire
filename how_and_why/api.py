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

        # Compute and store embedding for the description
        embedding = get_embedding(description)
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

        if description is not None:
            node.description = description
            # Recompute embedding when description changes
            embedding = get_embedding(description)
            store_embedding(node.id, embedding)
        if context is not None:
            node.context = context
        if status is not None:
            node.status = status
        if type is not None:
            node.type = type

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
