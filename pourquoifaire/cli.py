import click
from rich.console import Console
from rich.table import Table
from rich import box
from .database import create_db
from . import api
from .errors import handle_db_errors

# Create the database tables
create_db()


@click.group()
def cli():
    """PourquoiFaire - a terminal-based ToDo list app."""
    pass


@cli.command()
@click.argument("description")
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


@cli.command(name="query")
@click.argument("keywords")
@click.option("--k", default=3, help="Number of results to return")
@handle_db_errors
def query(keywords, k):
    """Query tasks by description (case-insensitive)."""
    nodes = api.search_nodes(keywords)
    if not nodes:
        click.echo("No nodes found.")
        return

    console = Console()
    table = Table(show_header=True, header_style="bold magenta", box=box.MINIMAL)
    table.add_column("ID", style="cyan", width=4)
    table.add_column("Description", style="white")
    table.add_column("Context", style="green")
    table.add_column("Status", style="yellow", width=12)
    table.add_column("Type", style="bright_blue", width=10)

    for node in nodes[:k]:
        table.add_row(
            str(node.id),
            node.description,
            node.context or "-",
            node.status,
            node.type,
        )

    console.print(table)


@cli.command(name="search")
@click.argument("prompt")
@click.option("--k", default=3, help="Number of results to return")
@click.option(
    "--status",
    default=None,
    help="Optional status filter (pending, in_progress, stuck, done)",
)
@click.option(
    "--type", "node_type", default=None, help="Optional type filter (task, project)"
)
@click.option(
    "--max-distance", default=None, type=float, help="Optional max distance threshold"
)
@handle_db_errors
def search(prompt, k, status, node_type, max_distance):
    """Search tasks using semantic vector search (embedding-based)."""
    results = api.vector_search(
        query=prompt,
        k=k,
        status=status,
        type=node_type,
        max_distance=max_distance,
    )

    if not results:
        click.echo("No similar nodes found.")
        return

    console = Console()
    table = Table(show_header=True, header_style="bold magenta", box=box.MINIMAL)
    table.add_column("ID", style="cyan", width=4)
    table.add_column("Distance", style="bright_magenta", width=8)
    table.add_column("Description", style="white")
    table.add_column("Status", style="yellow", width=12)
    table.add_column("Type", style="bright_blue", width=10)

    for node, distance in results:
        table.add_row(
            str(node.id),
            f"{distance:.3f}",
            node.description,
            node.status,
            node.type,
        )

    console.print(table)


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
