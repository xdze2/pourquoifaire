import json
from pathlib import Path
from sqlalchemy.exc import OperationalError
from sqlmodel import Session, select
from .database import engine, DB_PATH
from .models import Node


def _handle_db_error(e: OperationalError) -> None:
    """Provide helpful error messages for database errors."""
    if "unable to open database file" in str(e):
        raise RuntimeError(
            f"❌ Database file cannot be accessed. "
            f"Ensure the directory exists: {DB_PATH.parent}"
        )
    raise e


def export_nodes(filepath: str) -> int:
    """Export all nodes to a JSON file. Returns the count of exported nodes."""
    try:
        with Session(engine) as session:
            statement = select(Node)
            nodes = session.exec(statement).all()

            data = [node.model_dump() for node in nodes]

            Path(filepath).write_text(json.dumps(data, indent=2))
            return len(nodes)
    except OperationalError as e:
        _handle_db_error(e)


def import_nodes(filepath: str, clear: bool = False) -> int:
    """Import nodes from a JSON file. Returns the count of imported nodes."""
    try:
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
    except OperationalError as e:
        _handle_db_error(e)
