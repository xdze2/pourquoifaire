"""Shared Rich renderables for CLI and TUI."""

from __future__ import annotations

from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from .models import Node


def link_type_border_style(link_type: str) -> str:
    lt = (link_type or "").lower()
    if lt == "why":
        return "cyan"
    if lt == "how":
        return "magenta"
    if lt == "but":
        return "yellow"
    return "bright_black"


def truncate_description(text: str, max_len: int = 72) -> str:
    if not text:
        return "—"
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def render_node_detail(
    node: Node, relations: list[tuple[str, Node, Node]]
) -> RenderableType:
    """Two-column layout: full node card + related link cards (no outer Related border)."""
    main_body = Group(
        Text(node.description or "—", style="bold magenta"),
        Text(""),
        Text.from_markup(
            f"[yellow]status[/] {node.status or '—'}   "
            f"[blue]type[/] {node.type or '—'}   "
            f"[cyan]id[/] {node.id}"
        ),
        Text(""),
        Text("Context", style="bold green"),
        Text(node.context if node.context else "—", style="white"),
    )

    main_card = Panel(
        main_body,
        title=f"[bold white]●[/] [bold]Node {node.id}[/]",
        title_align="left",
        border_style="magenta",
        box=box.ROUNDED,
        padding=(1, 2),
        expand=True,
    )

    link_panels: list[Panel] = []
    for link_type, src_node, tgt_node in relations:
        is_out = src_node.id == node.id
        other = tgt_node if is_out else src_node
        role = "out" if is_out else "in"
        bstyle = link_type_border_style(link_type)
        title = f"[dim]{role}[/] [dim]·[/] [bold {bstyle}]{link_type}[/]"
        mini = Group(
            Text(truncate_description(other.description), style="white"),
            Text(
                f"id {other.id} · {other.status or '—'} · {other.type or '—'}",
                style="dim",
            ),
        )
        link_panels.append(
            Panel(
                mini,
                title=title,
                title_align="left",
                border_style=bstyle,
                box=box.ROUNDED,
                padding=(0, 1),
            )
        )

    if link_panels:
        related_body = Group(*link_panels)
    else:
        related_body = Group(Text("No linked nodes.", style="dim italic"))

    related_column = Group(
        Text("Related", style="bold"),
        Text(""),
        related_body,
    )

    layout = Table.grid(expand=True, padding=0)
    layout.add_column(ratio=3, min_width=28)
    layout.add_column(ratio=2, min_width=24)
    layout.add_row(main_card, related_column)
    return layout


def render_nodes_table(nodes: list[Node], *, max_rows: int | None = None) -> Table:
    table = Table(show_header=True, header_style="bold magenta", box=box.MINIMAL)
    table.add_column("ID", style="cyan", width=4)
    table.add_column("Description", style="white")
    table.add_column("Context", style="green")
    table.add_column("Status", style="yellow", width=12)
    table.add_column("Type", style="bright_blue", width=10)
    rows = nodes if max_rows is None else nodes[:max_rows]
    for n in rows:
        table.add_row(
            str(n.id),
            n.description,
            n.context or "-",
            n.status,
            n.type,
        )
    return table


def render_vector_search_table(
    results: list[tuple[Node, float]], *, max_rows: int | None = None
) -> Table:
    table = Table(show_header=True, header_style="bold magenta", box=box.MINIMAL)
    table.add_column("ID", style="cyan", width=4)
    table.add_column("Distance", style="bright_magenta", width=8)
    table.add_column("Description", style="white")
    table.add_column("Status", style="yellow", width=12)
    table.add_column("Type", style="bright_blue", width=10)
    rows = results if max_rows is None else results[:max_rows]
    for node, distance in rows:
        table.add_row(
            str(node.id),
            f"{distance:.3f}",
            node.description,
            node.status,
            node.type,
        )
    return table


def render_links_table(relations: list[tuple[str, Node, Node]]) -> Table:
    table = Table(show_header=True, header_style="bold magenta", box=box.MINIMAL)
    table.add_column("Type", style="cyan", width=8)
    table.add_column("Src", style="green", width=5)
    table.add_column("Src Desc", style="white")
    table.add_column("Tgt", style="yellow", width=5)
    table.add_column("Tgt Desc", style="white")
    for link_type, src_node, tgt_node in relations:
        table.add_row(
            link_type,
            str(src_node.id),
            src_node.description,
            str(tgt_node.id),
            tgt_node.description,
        )
    return table


def renderable_to_str(renderable: RenderableType, width: int | None = None) -> str:
    """Render a Rich object to a plain string (e.g. for Textual Static fallback)."""
    console = Console(width=width, force_terminal=True, color_system="standard")
    with console.capture() as capture:
        console.print(renderable)
    return capture.get()
