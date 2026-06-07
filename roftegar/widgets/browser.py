from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import DataTable

from roftegar.scanner import DirEntry, format_size, make_bar

BAR_WIDTH = 20


class FileBrowser(Widget):
    """A DataTable-based widget that displays directory entries."""

    # ── Messages ──────────────────────────────────────────────────────────────

    @dataclass
    class EntrySelected(Message):
        """Posted when the user presses Enter on a row."""
        entry: DirEntry

    @dataclass
    class EntryHighlighted(Message):
        """Posted when the cursor moves to a new row."""
        entry: Optional[DirEntry]

    # ── Internals ─────────────────────────────────────────────────────────────

    DEFAULT_CSS = """
    FileBrowser {
        height: 1fr;
    }
    FileBrowser DataTable {
        height: 1fr;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._entries: list[DirEntry] = []

    def compose(self) -> ComposeResult:
        table: DataTable = DataTable(
            cursor_type="row",
            zebra_stripes=True,
            id="file-table",
        )
        yield table

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        (
            self._col_icon,
            self._col_name,
            self._col_size,
            self._col_bar,
        ) = table.add_columns("", "Name", "Size", "Usage")

    # ── Public API ────────────────────────────────────────────────────────────

    def load_entries(self, entries: list[DirEntry]) -> None:
        """Replace the table contents with *entries*."""
        self._entries = entries
        table = self.query_one(DataTable)
        table.clear()

        max_size = entries[0].size if entries else 0

        for entry in entries:
            icon = "📁" if entry.is_dir else "📄"
            size_str = format_size(entry.size)
            bar = make_bar(entry.size, max_size, BAR_WIDTH)
            table.add_row(icon, entry.name, size_str, bar, key=entry.path)

    def update_entry_size(self, path: str, size: int) -> None:
        """Update the Size cell for one entry in-place (live progress update)."""
        entry = next((e for e in self._entries if e.path == path), None)
        if entry is None:
            return
        entry.size = size
        table = self.query_one(DataTable)
        table.update_cell(path, self._col_size, format_size(size))

    def move_cursor_up(self) -> None:
        self.query_one(DataTable).action_cursor_up()

    def move_cursor_down(self) -> None:
        self.query_one(DataTable).action_cursor_down()

    def open_selected(self) -> None:
        self.query_one(DataTable).action_select_cursor()

    def get_selected_entry(self) -> DirEntry | None:
        """Return the DirEntry for the currently highlighted row, or None."""
        table = self.query_one(DataTable)
        if not self._entries or table.row_count == 0:
            return None
        try:
            row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
            path = row_key.value
            return next((e for e in self._entries if e.path == path), None)
        except Exception:
            return None

    # ── Event handlers ────────────────────────────────────────────────────────

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        path = event.row_key.value
        entry = next((e for e in self._entries if e.path == path), None)
        if entry is not None:
            self.post_message(self.EntrySelected(entry=entry))

    def on_data_table_row_highlighted(
        self, event: DataTable.RowHighlighted
    ) -> None:
        if event.row_key is None:
            self.post_message(self.EntryHighlighted(entry=None))
            return
        path = event.row_key.value
        entry = next((e for e in self._entries if e.path == path), None)
        self.post_message(self.EntryHighlighted(entry=entry))
