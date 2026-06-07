from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import psutil
from textual.app import ComposeResult
from textual.binding import Binding
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, ProgressBar

from roftegar.plugin import SysmonPlugin


class SystemUsageView(Widget):
    """Live dashboard for basic system usage metrics."""

    BINDINGS = [
        Binding("r", "refresh", "Refresh"),
    ]

    DEFAULT_CSS = """
    SystemUsageView {
        height: 1fr;
        layout: vertical;
        padding: 1 2;
    }

    SystemUsageView > * {
        margin-bottom: 1;
    }

    SystemUsageView > .title {
        text-style: bold;
        color: $text;
    }

    SystemUsageView > .subtitle {
        color: $text-muted;
    }

    SystemUsageView > .metric-name {
        margin-top: 1;
        color: $text;
        text-style: bold;
    }

    SystemUsageView > ProgressBar {
        width: 1fr;
    }
    """

    boot_time: reactive[float] = reactive(0.0, init=False)

    def compose(self) -> ComposeResult:
        yield Label(" System Usage", classes="title")
        yield Label("", id="su-meta", classes="subtitle")
        yield Label("CPU", classes="metric-name")
        yield ProgressBar(id="su-cpu", show_eta=False)
        yield Label("Memory", classes="metric-name")
        yield ProgressBar(id="su-memory", show_eta=False)
        yield Label("Swap", classes="metric-name")
        yield ProgressBar(id="su-swap", show_eta=False)
        yield Label("Disk /", classes="metric-name")
        yield ProgressBar(id="su-disk", show_eta=False)
        yield Label("", id="su-footer", classes="subtitle")

    def on_mount(self) -> None:
        self.boot_time = psutil.boot_time()
        self.set_interval(1.0, self._refresh_stats)
        self._refresh_stats()

    def action_refresh(self) -> None:
        self._refresh_stats()

    def _refresh_stats(self) -> None:
        cpu = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        disk = psutil.disk_usage(Path.cwd().anchor or "/")

        self.query_one("#su-cpu", ProgressBar).update(total=100, progress=cpu)
        self.query_one("#su-memory", ProgressBar).update(
            total=100, progress=memory.percent
        )
        self.query_one("#su-swap", ProgressBar).update(total=100, progress=swap.percent)
        self.query_one("#su-disk", ProgressBar).update(total=100, progress=disk.percent)

        uptime = timedelta(seconds=int(datetime.now().timestamp() - self.boot_time))
        self.query_one("#su-meta", Label).update(
            f" Host uptime: {uptime}  |  CPU cores: {psutil.cpu_count(logical=True)}"
        )
        self.query_one("#su-footer", Label).update(
            f"Memory {self._fmt_bytes(memory.used)} / {self._fmt_bytes(memory.total)}"
            f"   Swap {self._fmt_bytes(swap.used)} / {self._fmt_bytes(swap.total)}"
            f"   Disk {self._fmt_bytes(disk.used)} / {self._fmt_bytes(disk.total)}"
        )

    @staticmethod
    def _fmt_bytes(num_bytes: float) -> str:
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        value = float(num_bytes)
        for unit in units:
            if value < 1024.0 or unit == units[-1]:
                return f"{value:.1f} {unit}"
            value /= 1024.0
        return f"{value:.1f} PB"


class SystemUsagePlugin(SysmonPlugin):
    id = "system_usage"
    name = "System Usage"
    description = "Live CPU, memory, swap, and disk usage dashboard"
    icon = "📈"

    def create_view(self) -> Widget:
        return SystemUsageView()
