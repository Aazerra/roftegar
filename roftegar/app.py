from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Footer, Header, Label, ListItem, ListView

import roftegar.plugins  # noqa: F401 — side-effect: registers built-in plugins
from roftegar.plugin import SysmonPlugin
from roftegar.registry import registry


# ── Infrastructure widgets ────────────────────────────────────────────────────


class StartupMenu(Widget):
    """Startup menu that lets the user choose which plugin to open."""

    BINDINGS = [
        Binding("j", "cursor_down", "Down"),
        Binding("k", "cursor_up", "Up"),
        Binding("l,enter", "select_cursor", "Open"),
    ]

    DEFAULT_CSS = """
    StartupMenu {
        width: 1fr;
        height: 1fr;
        align: center middle;
        background: $surface;
    }

    StartupMenu > Vertical {
        width: 54;
        height: auto;
        padding: 1 2;
        border: thick $primary;
        background: $surface-darken-1;
    }

    StartupMenu .panel-title {
        background: $primary;
        color: $text;
        text-align: center;
        text-style: bold;
        height: 1;
        padding: 0 1;
        width: 1fr;
    }

    StartupMenu .panel-subtitle {
        color: $text-muted;
        text-align: center;
        margin: 1 0;
    }

    StartupMenu ListView {
        height: 1fr;
        background: $surface-darken-1;
        border: none;
    }
    """

    class PluginActivated(Message):
        """Posted when the user selects a plugin from the startup menu."""

        def __init__(self, plugin_id: str) -> None:
            super().__init__()
            self.plugin_id = plugin_id

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(" roftegar", classes="panel-title")
            yield Label("Choose a plugin to open", classes="panel-subtitle")
            yield ListView(id="plugin-list")

    def populate(self, plugins: list[SysmonPlugin]) -> None:
        lv = self.query_one(ListView)
        for plugin in plugins:
            lv.append(
                ListItem(
                    Label(f" {plugin.icon}  {plugin.name}"),
                    id=f"plugin-{plugin.id}",
                )
            )

    def highlight(self, plugin_id: str) -> None:
        """Move the ListView cursor to the item for *plugin_id*."""
        lv = self.query_one(ListView)
        for i, p in enumerate(registry.all()):
            if p.id == plugin_id:
                lv.index = i
                return

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item.id is None:
            return
        plugin_id = event.item.id.removeprefix("plugin-")
        self.post_message(self.PluginActivated(plugin_id=plugin_id))

    def action_cursor_down(self) -> None:
        self.query_one(ListView).action_cursor_down()

    def action_cursor_up(self) -> None:
        self.query_one(ListView).action_cursor_up()

    def action_select_cursor(self) -> None:
        self.query_one(ListView).action_select_cursor()


class StartupHost(Widget):
    """Container that swaps the startup menu for the active plugin view."""

    DEFAULT_CSS = """
    StartupHost {
        height: 1fr;
        width: 1fr;
    }
    StartupHost > StartupMenu {
        height: 1fr;
        width: 1fr;
    }
    """

    def show_menu(self, plugins: list[SysmonPlugin]) -> None:
        for child in list(self.children):
            child.remove()
        menu = StartupMenu(id="startup-menu")
        self.mount(menu)
        menu.populate(plugins)
        if plugins:
            menu.highlight(plugins[0].id)
        self.app.call_after_refresh(lambda: self._focus_view(menu))

    def show_plugin(self, plugin: SysmonPlugin) -> None:
        for child in list(self.children):
            child.remove()
        view = plugin.create_view()
        self.mount(view)
        self.app.call_after_refresh(lambda: self._focus_view(view))

    @staticmethod
    def _focus_view(view: Widget) -> None:
        for widget in view.query("*"):
            if widget.can_focus:
                widget.focus()
                return


# ── Main application ──────────────────────────────────────────────────────────


class SysmonApp(App):
    """Plugin-based system-monitor TUI shell.

    The app itself contains no feature logic — all functionality lives in
    plugins registered with :data:`roftegar.registry.registry`.
    """

    TITLE = "roftegar"
    CSS_PATH = "roftegar.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("m", "show_menu", "Menu"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield StartupHost(id="startup-host")
        yield Footer()

    def on_mount(self) -> None:
        plugins = registry.all()
        self._show_menu()

    # ── Plugin activation ─────────────────────────────────────────────────────

    def _activate(self, plugin_id: str) -> None:
        plugin = registry.get(plugin_id)
        if plugin is None:
            return
        self.query_one(StartupHost).show_plugin(plugin)
        self.sub_title = f"{plugin.icon} {plugin.name}"

    def _show_menu(self) -> None:
        plugins = registry.all()
        self.query_one(StartupHost).show_menu(plugins)
        self.sub_title = "Choose a plugin"

    # ── Message handler from startup menu ─────────────────────────────────────

    def on_startup_menu_plugin_activated(
        self, message: StartupMenu.PluginActivated
    ) -> None:
        self._activate(message.plugin_id)

    # ── Actions ───────────────────────────────────────────────────────────────

    def action_show_menu(self) -> None:
        self._show_menu()
