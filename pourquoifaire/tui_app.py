"""Initial Textual TUI (Rich renderables) for browsing and editing nodes."""

from __future__ import annotations

from typing import ClassVar

from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Select,
    Static,
)

from . import api
from .database import create_db
from .display import render_node_detail, renderable_to_str, truncate_description

create_db()


def _node_id_from_row_key(row_key) -> int:
    """DataTable RowKey keeps the id in `.value`; ``str(row_key)`` is not the id string."""
    v = row_key.value
    if v is None:
        raise ValueError("Row key has no value")
    return int(v)


class MainScreen(Screen[None]):
    """Browse nodes; shortcuts for search, show, edit, link."""

    BINDINGS: ClassVar[list[Binding]] = [
        Binding("/", "search", "Search"),
        Binding("s", "show", "Show"),
        Binding("e", "edit", "Edit"),
        Binding("l", "link", "Link"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Label(
            "[bold]Nodes[/] — [cyan]/[/] search · [cyan]s[/] show · [cyan]e[/] edit · [cyan]l[/] link · [cyan]Enter[/] open · [cyan]q[/] quit",
            id="hint",
        )
        yield DataTable(
            id="main-table",
            zebra_stripes=True,
            cursor_type="row",
        )
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#main-table", DataTable)
        table.add_columns("ID", "Description", "Status", "Type")
        self.load_table()

    def on_screen_resume(self, event: events.ScreenResume) -> None:
        self.load_table()

    def load_table(self) -> None:
        table = self.query_one("#main-table", DataTable)
        table.clear()
        table.add_columns("ID", "Description", "Status", "Type")
        for n in api.list_nodes():
            table.add_row(
                str(n.id),
                truncate_description(n.description, 56),
                n.status,
                n.type,
                key=str(n.id),
            )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.data_table.id != "main-table":
            return
        self.app.push_screen(NodeDetailScreen(_node_id_from_row_key(event.row_key)))

    async def action_search(self) -> None:
        node_id = await self.app.push_screen_wait(SearchScreen())
        if node_id is not None:
            self._focus_node_id(node_id)

    def _focus_node_id(self, node_id: int) -> None:
        table = self.query_one("#main-table", DataTable)
        for i, row in enumerate(table.ordered_rows):
            if _node_id_from_row_key(row.key) == node_id:
                table.move_cursor(row=i, column=0)
                table.focus()
                break

    def action_show(self) -> None:
        nid = self._cursor_node_id()
        if nid is not None:
            self.app.push_screen(NodeDetailScreen(nid))

    def action_edit(self) -> None:
        nid = self._cursor_node_id()
        if nid is not None:
            self.app.push_screen(EditScreen(nid))

    def action_link(self) -> None:
        nid = self._cursor_node_id()
        if nid is not None:
            self.app.push_screen(LinkScreen(nid))

    def _cursor_node_id(self) -> int | None:
        table = self.query_one("#main-table", DataTable)
        if table.row_count == 0:
            return None
        coord = table.cursor_coordinate
        if coord is None:
            return None
        row_index, _ = coord
        rows = table.ordered_rows
        if row_index < 0 or row_index >= len(rows):
            return None
        return _node_id_from_row_key(rows[row_index].key)


class NodeDetailScreen(Screen[None]):
    """Full node view using shared Rich layout."""

    BINDINGS: ClassVar[list[Binding]] = [
        Binding("escape", "back", "Back"),
    ]

    def __init__(self, node_id: int) -> None:
        super().__init__()
        self.node_id = node_id

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield VerticalScroll(Static(id="node-body", expand=True))
        yield Footer()

    def on_mount(self) -> None:
        static = self.query_one("#node-body", Static)
        node = api.get_node(self.node_id)
        if not node:
            static.update(f"Node {self.node_id} not found.")
            return
        relations = api.get_links(self.node_id)
        renderable = render_node_detail(node, relations)
        try:
            static.update(renderable)
        except Exception:
            static.update(renderable_to_str(renderable))

    def action_back(self) -> None:
        self.app.pop_screen()


class SearchScreen(Screen[int | None]):
    """Keyword or semantic search; pick a row with Enter."""

    BINDINGS: ClassVar[list[Binding]] = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, exclude_id: int | None = None) -> None:
        super().__init__()
        self.exclude_id = exclude_id

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Label("Search nodes")
        yield Select(
            (("Keyword", "keyword"), ("Semantic", "semantic")),
            id="search-mode",
            value="keyword",
            allow_blank=False,
        )
        yield Input(placeholder="Query…", id="query-input")
        yield DataTable(
            id="search-results",
            zebra_stripes=True,
            cursor_type="row",
        )
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#search-results", DataTable)
        table.add_columns("ID", "Description", "Status", "Type")
        self.query_one("#query-input", Input).focus()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "query-input":
            return
        q = event.value.strip()
        if not q:
            return
        mode = self.query_one("#search-mode", Select).value
        table = self.query_one("#search-results", DataTable)
        table.clear()
        table.add_columns("ID", "Description", "Status", "Type")
        if str(mode) == "semantic":
            nodes = [n for n, _ in api.vector_search(q, k=50)]
        else:
            nodes = api.search_nodes(q)
        if self.exclude_id is not None:
            nodes = [n for n in nodes if n.id != self.exclude_id]
        for n in nodes:
            table.add_row(
                str(n.id),
                truncate_description(n.description, 48),
                n.status,
                n.type,
                key=str(n.id),
            )
        if table.row_count:
            table.focus()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.data_table.id != "search-results":
            return
        self.dismiss(_node_id_from_row_key(event.row_key))

    def action_cancel(self) -> None:
        self.dismiss(None)


class EditScreen(Screen[None]):
    BINDINGS: ClassVar[list[Binding]] = [
        Binding("escape", "back", "Back"),
    ]

    def __init__(self, node_id: int) -> None:
        super().__init__()
        self.node_id = node_id

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Label(f"[bold]Edit node {self.node_id}[/]")
        yield Label("Description")
        yield Input(id="f-desc")
        yield Label("Context")
        yield Input(id="f-ctx")
        yield Label("Status")
        yield Input(id="f-status")
        yield Label("Type")
        yield Input(id="f-type")
        yield Button("Save", variant="primary", id="btn-save")
        yield Footer()

    def on_mount(self) -> None:
        node = api.get_node(self.node_id)
        if not node:
            return
        self.query_one("#f-desc", Input).value = node.description
        self.query_one("#f-ctx", Input).value = node.context or ""
        self.query_one("#f-status", Input).value = node.status or ""
        self.query_one("#f-type", Input).value = node.type or ""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "btn-save":
            return
        api.modify_node(
            self.node_id,
            description=self.query_one("#f-desc", Input).value,
            context=self.query_one("#f-ctx", Input).value,
            status=self.query_one("#f-status", Input).value,
            type=self.query_one("#f-type", Input).value,
        )
        self.app.pop_screen()

    def action_back(self) -> None:
        self.app.pop_screen()


class NewNodeScreen(Screen[int | None]):
    """Create a node; dismiss with new id or None."""

    BINDINGS: ClassVar[list[Binding]] = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Label("[bold]New node[/]")
        yield Label("Description")
        yield Input(id="n-desc")
        yield Label("Context")
        yield Input(id="n-ctx")
        yield Label("Status")
        yield Input(id="n-status", value="pending")
        yield Label("Type")
        yield Input(id="n-type", value="task")
        yield Button("Create", variant="primary", id="btn-create")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "btn-create":
            return
        desc = self.query_one("#n-desc", Input).value.strip()
        if not desc:
            return
        nid = api.add_node(
            description=desc,
            context=self.query_one("#n-ctx", Input).value or "",
            status=self.query_one("#n-status", Input).value or "pending",
            type=self.query_one("#n-type", Input).value or "task",
        )
        self.dismiss(nid)

    def action_cancel(self) -> None:
        self.dismiss(None)


class LinkScreen(Screen[None]):
    """Link from a node: search existing or create new, then add_link."""

    BINDINGS: ClassVar[list[Binding]] = [
        Binding("escape", "back", "Back"),
    ]

    def __init__(self, from_id: int) -> None:
        super().__init__()
        self.from_id = from_id

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Label(f"[bold]Link from node {self.from_id}[/]")
        yield Label("Relation type")
        yield Select(
            (("why", "why"), ("how", "how"), ("but", "but")),
            id="link-type",
            value="why",
            allow_blank=False,
        )
        yield Button("Search existing node…", id="btn-search", variant="primary")
        yield Button("Create new node…", id="btn-new")
        yield Footer()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-search":
            target = await self.app.push_screen_wait(SearchScreen(exclude_id=self.from_id))
            if target is not None:
                lt = str(self.query_one("#link-type", Select).value)
                api.add_link(self.from_id, target, lt)
            self.app.pop_screen()
        elif event.button.id == "btn-new":
            new_id = await self.app.push_screen_wait(NewNodeScreen())
            if new_id is not None:
                lt = str(self.query_one("#link-type", Select).value)
                api.add_link(self.from_id, new_id, lt)
            self.app.pop_screen()

    def action_back(self) -> None:
        self.app.pop_screen()


class PourquoiApp(App[None]):
    """Root TUI."""

    TITLE = "PourquoiFaire"
    BINDINGS: ClassVar[list[Binding]] = [
        Binding("q", "quit", "Quit"),
    ]

    def on_mount(self) -> None:
        self.push_screen(MainScreen())

    def action_quit(self) -> None:
        self.exit()


def run() -> None:
    PourquoiApp().run()


if __name__ == "__main__":
    run()
