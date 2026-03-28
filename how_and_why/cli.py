import click
from sqlalchemy.exc import OperationalError
from sqlmodel import Session, select
from .database import engine, create_db
from .models import Node
from .export import export_nodes, import_nodes

# Create the database tables
create_db()


def _handle_db_error(e: Exception) -> None:
    """Show user-friendly error messages for database issues."""
    if isinstance(e, RuntimeError) and "Failed to initialize database" in str(e):
        raise click.ClickException(str(e))
    raise e


@click.group()
def cli():
    """A terminal-based todo list app using SQLModel."""
    pass


@cli.command()
@click.option("--description", prompt="Description", help="Task description")
@click.option("--context", default="", help="Task context")
@click.option("--status", default="pending", help="Task status")
@click.option("--type", default="task", help="Task type")
def add(description, context, status, type):
    """Add a new task (node)."""
    try:
        node = Node(description=description, context=context, status=status, type=type)
        with Session(engine) as session:
            session.add(node)
            session.commit()
            click.echo(f"Added node {node.id}")
    except Exception as e:
        _handle_db_error(e)
        raise click.ClickException(f"Failed to add node: {e}")


@cli.command()
@click.option(
    "--query", prompt="Search query", help="Search in description (case-insensitive)"
)
def search(query):
    """Search tasks by description."""
    try:
        with Session(engine) as session:
            statement = select(Node).where(Node.description.ilike(f"%{query}%"))
            nodes = session.exec(statement).all()
            if not nodes:
                click.echo("No nodes found.")
            else:
                for node in nodes:
                    click.echo(
                        f"ID: {node.id}, Description: {node.description}, Context: {node.context}, Status: {node.status}, Type: {node.type}"
                    )
    except Exception as e:
        _handle_db_error(e)
        raise click.ClickException(f"Search failed: {e}")


@cli.command()
@click.option("--id", prompt="Node ID", type=int, help="ID of the node to modify")
@click.option("--description", default=None, help="New description")
@click.option("--context", default=None, help="New context")
@click.option("--status", default=None, help="New status")
@click.option("--type", default=None, help="New type")
def modify(id, description, context, status, type):
    """Modify an existing task (node)."""
    try:
        with Session(engine) as session:
            node = session.get(Node, id)
            if not node:
                click.echo(f"Node with ID {id} not found.")
                return
            if description is not None:
                node.description = description
            if context is not None:
                node.context = context
            if status is not None:
                node.status = status
            if type is not None:
                node.type = type
            session.commit()
            click.echo(f"Modified node {id}")
    except Exception as e:
        _handle_db_error(e)
        raise click.ClickException(f"Failed to modify node: {e}")


@cli.command()
@click.option(
    "--output",
    prompt="Output filename",
    default="nodes.json",
    help="JSON file to export to",
)
def export(output):
    """Export all nodes to a JSON file."""
    try:
        count = export_nodes(output)
        click.echo(f"Exported {count} nodes to {output}")
    except Exception as e:
        _handle_db_error(e)
        raise click.ClickException(f"Export failed: {e}")


@cli.command("import")
@click.option(
    "--input", "input_file", prompt="Input filename", help="JSON file to import from"
)
@click.option("--clear", is_flag=True, help="Clear existing nodes before importing")
def import_db(input_file, clear):
    """Import nodes from a JSON file."""
    try:
        count = import_nodes(input_file, clear=clear)
        click.echo(f"Imported {count} nodes from {input_file}")
    except Exception as e:
        _handle_db_error(e)
        raise click.ClickException(f"Import failed: {e}")
