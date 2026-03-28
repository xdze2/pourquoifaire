import click
from .database import create_db
from . import api
from .errors import handle_db_errors

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
@handle_db_errors
def add(description, context, status, type):
    """Add a new task (node)."""
    node_id = api.add_node(
        description=description, context=context, status=status, type=type
    )
    click.echo(f"Added node {node_id}")


@cli.command()
@click.option("--query", prompt="Search query", help="Semantic search query")
@click.option("--k", default=3, help="Number of results to return")
@handle_db_errors
def search(query, k):
    """Search tasks by description."""
    nodes = api.search_nodes(query)
    if not nodes:
        click.echo("No nodes found.")
    else:
        for node in nodes:
            click.echo(
                f"ID: {node.id}, Description: {node.description}, Context: {node.context}, Status: {node.status}, Type: {node.type}"
            )


@cli.command()
@click.option(
    "--query", prompt="Vector search query", help="Semantic search using embeddings"
)
@click.option("--k", default=3, help="Number of results to return")
@handle_db_errors
def find(query, k):
    """Find tasks using semantic vector search."""
    from . import vector_index

    query_embedding = vector_index.get_embedding(query)
    results = vector_index.fuzzy_search(query_embedding, k=k)

    if not results:
        click.echo("No similar nodes found.")
    else:
        for node_id, distance in results:
            node = api.get_node(node_id)
            if node:
                click.echo(
                    f"ID: {node.id}, Distance: {distance:.3f}, Description: {node.description}"
                )


@cli.command()
@click.option("--id", prompt="Node ID", type=int, help="ID of the node to modify")
@click.option("--description", default=None, help="New description")
@click.option("--context", default=None, help="New context")
@click.option("--status", default=None, help="New status")
@click.option("--type", default=None, help="New type")
@handle_db_errors
def modify(id, description, context, status, type):
    """Modify an existing task (node)."""
    found = api.modify_node(
        node_id=id,
        description=description,
        context=context,
        status=status,
        type=type,
    )
    if not found:
        click.echo(f"Node with ID {id} not found.")
    else:
        click.echo(f"Modified node {id}")


@cli.command()
@click.option(
    "--output",
    prompt="Output filename",
    default="nodes.json",
    help="JSON file to export to",
)
@handle_db_errors
def export(output):
    """Export all nodes to a JSON file."""
    count = api.export_nodes(output)
    click.echo(f"Exported {count} nodes to {output}")


@cli.command("import")
@click.option(
    "--input", "input_file", prompt="Input filename", help="JSON file to import from"
)
@click.option("--clear", is_flag=True, help="Clear existing nodes before importing")
@handle_db_errors
def import_db(input_file, clear):
    """Import nodes from a JSON file."""
    count = api.import_nodes(input_file, clear=clear)
    click.echo(f"Imported {count} nodes from {input_file}")
