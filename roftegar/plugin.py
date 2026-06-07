from __future__ import annotations

from abc import ABC, abstractmethod

from textual.widget import Widget


class SysmonPlugin(ABC):
    """Base class every sysmon plugin must implement.

    Subclass this, fill in the class-level attributes, and implement
    :meth:`create_view`.  Then register an instance with the global
    :data:`roftegar.registry.registry`.
    """

    #: Unique machine-readable identifier (e.g. ``"disk_analyzer"``).
    id: str
    #: Human-readable display name shown in the plugin panel.
    name: str
    #: One-line description (shown as a tooltip / sub-title).
    description: str
    #: Emoji icon displayed next to the name in the sidebar.
    icon: str = "🔌"

    @abstractmethod
    def create_view(self) -> Widget:
        """Return a fresh widget that fills the content area.

        Called each time the user activates this plugin.  The returned
        widget is mounted into :class:`~roftegar.app.ContentArea`; any
        previous plugin view is removed first.
        """
        ...
