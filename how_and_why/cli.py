import click
from sqlmodel import Session, select
from .database import engine, create_db
from .models import Node

# Create the database tables
create_db()


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
    node = Node(description=description, context=context, status=status, type=type)
    with Session(engine) as session:
        session.add(node)
        session.commit()
        click.echo(f"Added node {node.id}")


@cli.command()
@click.option(
    "--query", prompt="Search query", help="Search in description (case-insensitive)"
)
def search(query):
    """Search tasks by description."""
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


@cli.command()
@click.option("--id", prompt="Node ID", type=int, help="ID of the node to modify")
@click.option("--description", default=None, help="New description")
@click.option("--context", default=None, help="New context")
@click.option("--status", default=None, help="New status")
@click.option("--type", default=None, help="New type")
def modify(id, description, context, status, type):
    """Modify an existing task (node)."""
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
