from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label
from textual.containers import Grid


class ConfirmModal(ModalScreen[bool]):
    """A modal confirmation dialog that returns True if the user confirms."""

    DEFAULT_CSS = """
    ConfirmModal {
        align: center middle;
    }

    ConfirmModal > Grid {
        grid-size: 2;
        grid-gutter: 1 2;
        grid-rows: auto auto;
        padding: 1 2;
        width: 50;
        height: auto;
        border: thick $error;
        background: $surface;
    }

    ConfirmModal Label {
        column-span: 2;
        width: 1fr;
        text-align: center;
        color: $text;
    }

    ConfirmModal Button {
        width: 1fr;
    }
    """

    def __init__(self, target_name: str) -> None:
        super().__init__()
        self._target_name = target_name

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(f"Delete [bold]{self._target_name}[/bold]?"),
            Button("Yes, delete", id="yes", variant="error"),
            Button("No, cancel", id="no", variant="primary"),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "yes")

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(False)
