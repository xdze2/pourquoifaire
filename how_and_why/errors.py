import functools
import click
from sqlalchemy.exc import OperationalError
from .database import DB_PATH


def handle_db_errors(func):
    """Decorator to handle database errors with user-friendly messages."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RuntimeError as e:
            if "Failed to initialize database" in str(e):
                raise click.ClickException(str(e))
            raise click.ClickException(f"{func.__name__} error: {e}")
        except OperationalError as e:
            if "unable to open database file" in str(e):
                raise click.ClickException(
                    f"❌ Cannot access database. Ensure the directory exists: {DB_PATH.parent}"
                )
            raise click.ClickException(f"Database error: {e}")
        except Exception as e:
            raise click.ClickException(f"{func.__name__} failed: {e}")

    return wrapper
