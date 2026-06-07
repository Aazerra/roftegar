from __future__ import annotations

import os
import shutil
from pathlib import Path

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, ProgressBar
from textual.worker import get_current_worker

from roftegar.plugin import SysmonPlugin
from roftegar.scanner import DirEntry, format_size, get_size, list_entries_fast
from roftegar.widgets.browser import FileBrowser
from roftegar.widgets.confirm import ConfirmModal


class DiskAnalyzerView(Widget):
    """Self-contained disk-analyzer UI widget.

    Owns all reactive state, the background scanner worker, and every
    keybinding needed by the disk-analyzer feature.  The host app shell
    does not need to know about any disk-specific logic.
    """

    BINDINGS = [
        Binding("r", "refresh", "Refresh"),
        Binding("j", "cursor_down", "Down"),
        Binding("k", "cursor_up", "Up"),
        Binding("h", "go_up", "Go up"),
        Binding("l,enter", "open_selected", "Open"),
        Binding("ctrl+h", "toggle_hidden", "Hidden"),
        Binding("s", "toggle_sort", "Sort"),
        Binding("d,delete", "delete", "Delete"),
        Binding("backspace,left", "go_up", "Go up"),
    ]

    DEFAULT_CSS = """
    DiskAnalyzerView {
        height: 1fr;
        layout: vertical;
    }
    DiskAnalyzerView > #da-path {
        background: $primary-darken-2;
        color: $text;
        width: 1fr;
        padding: 0 1;
        text-style: bold;
        height: 1;
    }
    DiskAnalyzerView > #da-progress {
        height: 1;
        width: 1fr;
        display: none;
    }
    DiskAnalyzerView > #da-status {
        background: $primary-darken-3;
        color: $text-muted;
        width: 1fr;
        padding: 0 1;
        height: 1;
    }
    """

    current_path: reactive[str] = reactive(str(Path.cwd()), init=False)
    show_hidden: reactive[bool] = reactive(False, init=False)
    sort_by: reactive[str] = reactive("size", init=False)

    def compose(self) -> ComposeResult:
        yield Label("", id="da-path")
        yield FileBrowser(id="da-browser")
        yield ProgressBar(id="da-progress", show_eta=False)
        yield Label("", id="da-status")

    def on_mount(self) -> None:
        self._load_directory(str(Path.cwd()))

    # ── Watchers ──────────────────────────────────────────────────────────────

    def watch_current_path(self, new_path: str) -> None:
        self._load_directory(new_path)

    def watch_show_hidden(self) -> None:
        self._load_directory(self.current_path)

    def watch_sort_by(self) -> None:
        self._load_directory(self.current_path)

    # ── Background worker ─────────────────────────────────────────────────────

    @work(exclusive=True, thread=True)
    def _load_directory(self, path: str) -> None:
        worker = get_current_worker()

        # Phase 1 — instant listing (dirs show 0 until computed)
        entries = list_entries_fast(path, self.show_hidden)
        entries.sort(key=lambda e: (not e.is_dir, e.name.lower()))
        if worker.is_cancelled:
            return

        dir_entries = [e for e in entries if e.is_dir]
        n_dirs = len(dir_entries)

        self.app.call_from_thread(self._begin_scan, path, list(entries), n_dirs)

        # Phase 2 — compute directory sizes one by one, update rows live
        for done, entry in enumerate(dir_entries, start=1):
            if worker.is_cancelled:
                return
            entry.size = get_size(entry.path)
            self.app.call_from_thread(
                self._update_one, entry.path, entry.size, done, n_dirs
            )

        if worker.is_cancelled:
            return

        # Phase 3 — sort with real sizes and do a final full redraw
        if self.sort_by == "size":
            entries.sort(key=lambda e: e.size, reverse=True)
        else:
            entries.sort(key=lambda e: (not e.is_dir, e.name.lower()))
        self.app.call_from_thread(self._finish_scan, path, list(entries))

    def _begin_scan(
        self, path: str, entries: list[DirEntry], n_dirs: int
    ) -> None:
        self.query_one("#da-path", Label).update(f" 📂 {path}")
        self.query_one(FileBrowser).load_entries(entries)
        progress = self.query_one("#da-progress", ProgressBar)
        if n_dirs:
            progress.update(total=n_dirs, progress=0)
            progress.display = True
            self.query_one("#da-status", Label).update(
                f" {len(entries)} items  │  computing 0 / {n_dirs} dir sizes…"
            )
        else:
            progress.display = False
            self._set_status(len(entries))

    def _update_one(
        self, path: str, size: int, done: int, total: int
    ) -> None:
        self.query_one(FileBrowser).update_entry_size(path, size)
        self.query_one("#da-progress", ProgressBar).advance(1)
        self.query_one("#da-status", Label).update(
            f" computing {done} / {total} dir sizes…"
        )

    def _finish_scan(self, path: str, entries: list[DirEntry]) -> None:
        self.query_one("#da-progress", ProgressBar).display = False
        self.query_one(FileBrowser).load_entries(entries)
        self._set_status(len(entries))

    def _set_status(self, count: int) -> None:
        self.query_one("#da-status", Label).update(
            f" {count} items"
            + ("  [hidden shown]" if self.show_hidden else "")
            + f"  sort: {self.sort_by}"
        )

    def _populate(
        self, path: str, entries: list[DirEntry], status_suffix: str = ""
    ) -> None:
        self.query_one("#da-path", Label).update(f" 📂 {path}")
        self.query_one(FileBrowser).load_entries(entries)
        self.query_one("#da-status", Label).update(
            f" {len(entries)} items"
            + ("  [hidden shown]" if self.show_hidden else "")
            + f"  sort: {self.sort_by}"
            + status_suffix
        )

    # ── Message handlers ──────────────────────────────────────────────────────

    def on_file_browser_entry_selected(
        self, message: FileBrowser.EntrySelected
    ) -> None:
        if message.entry.is_dir:
            self.current_path = message.entry.path

    def on_file_browser_entry_highlighted(
        self, message: FileBrowser.EntryHighlighted
    ) -> None:
        entry = message.entry
        if entry is None:
            return
        kind = "dir" if entry.is_dir else "file"
        self.query_one("#da-status", Label).update(
            f" {entry.name}  [{kind}]  {format_size(entry.size)}"
        )

    # ── Actions ───────────────────────────────────────────────────────────────

    def action_refresh(self) -> None:
        self._load_directory(self.current_path)

    def action_cursor_down(self) -> None:
        self.query_one(FileBrowser).move_cursor_down()

    def action_cursor_up(self) -> None:
        self.query_one(FileBrowser).move_cursor_up()

    def action_open_selected(self) -> None:
        browser = self.query_one(FileBrowser)
        entry = browser.get_selected_entry()
        if entry is None:
            return
        if entry.is_dir:
            self.current_path = entry.path

    def action_toggle_hidden(self) -> None:
        self.show_hidden = not self.show_hidden

    def action_toggle_sort(self) -> None:
        self.sort_by = "name" if self.sort_by == "size" else "size"

    def action_go_up(self) -> None:
        parent = str(Path(self.current_path).parent)
        if parent != self.current_path:
            self.current_path = parent

    def action_delete(self) -> None:
        entry = self.query_one(FileBrowser).get_selected_entry()
        if entry is None:
            return
        self.app.push_screen(
            ConfirmModal(entry.name),
            lambda confirmed: self._do_delete(entry, confirmed),
        )

    def _do_delete(self, entry: DirEntry, confirmed: bool | None) -> None:
        if not confirmed:
            return
        try:
            if entry.is_dir:
                shutil.rmtree(entry.path)
            else:
                os.remove(entry.path)
        except OSError as exc:
            self.query_one("#da-status", Label).update(
                f" [red]Error:[/red] {exc}"
            )
        else:
            self._load_directory(self.current_path)


# ── Plugin descriptor ─────────────────────────────────────────────────────────


class DiskAnalyzerPlugin(SysmonPlugin):
    id = "disk_analyzer"
    name = "Disk Analyzer"
    description = "Browse directories and analyse disk usage"
    icon = "💾"

    def create_view(self) -> Widget:
        return DiskAnalyzerView()
