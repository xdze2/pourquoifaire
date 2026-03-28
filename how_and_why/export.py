import json
from pathlib import Path
from sqlmodel import Session, select
from .database import engine
from .models import Node


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
