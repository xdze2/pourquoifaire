from pathlib import Path
from sqlmodel import create_engine, SQLModel
from sqlalchemy import text
import sqlite_vec

DB_URL = "sqlite:///data/todo.db"
DB_PATH = Path("data/todo.db")

# Create engine first
engine = create_engine(DB_URL, echo=False)


def create_db():
    """Create database tables and ensure the data directory exists."""
    try:
        # Ensure the data directory exists
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Import models to register them with SQLModel.metadata
        from . import models  # noqa: F401

        # Create standard tables
        SQLModel.metadata.create_all(engine)

        # Initialize vector extension and table
        init_vector_db()

    except Exception as e:
        raise RuntimeError(f"Failed to initialize database: {e}")


def init_vector_db():
    """Initialize the vector database extension and create vector table."""
    with engine.connect() as conn:
        # We need to reach down to the raw driver to load the extension
        raw_con = conn.connection
        raw_con.enable_load_extension(True)
        sqlite_vec.load(raw_con)

        # Create the vector table if it doesn't exist
        # 'embedding float[768]' matches nomic-embed-text output size
        conn.execute(
            text(
                """
            CREATE VIRTUAL TABLE IF NOT EXISTS vec_nodes USING vec0(
                id INTEGER PRIMARY KEY,
                embedding float[768]
            );
        """
            )
        )
        conn.commit()


# Initialize database on module import
create_db()
