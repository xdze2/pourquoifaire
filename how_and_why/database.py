from pathlib import Path
from sqlmodel import create_engine, SQLModel

DB_URL = "sqlite:///data/todo.db"
DB_PATH = Path("data/todo.db")


def create_db():
    """Create database tables and ensure the data directory exists."""
    try:
        # Ensure the data directory exists
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        SQLModel.metadata.create_all(engine)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize database: {e}")


engine = create_engine(DB_URL, echo=False)
create_db()
