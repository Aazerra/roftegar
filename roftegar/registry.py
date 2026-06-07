from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from roftegar.plugin import SysmonPlugin


class PluginRegistry:
    """Ordered registry of :class:`~roftegar.plugin.SysmonPlugin` instances.

    Use the module-level :data:`registry` singleton rather than creating
    new instances.
    """

    def __init__(self) -> None:
        self._plugins: list[SysmonPlugin] = []

    def register(self, plugin: SysmonPlugin) -> None:
        """Add *plugin* to the registry (silently skips duplicates by id)."""
        if any(p.id == plugin.id for p in self._plugins):
            return
        self._plugins.append(plugin)

    def all(self) -> list[SysmonPlugin]:
        """Return all registered plugins in registration order."""
        return list(self._plugins)

    def get(self, plugin_id: str) -> SysmonPlugin | None:
        """Return the plugin with the given *plugin_id*, or ``None``."""
        return next((p for p in self._plugins if p.id == plugin_id), None)


#: Global plugin registry — import and call :meth:`PluginRegistry.register`
#: from any ``roftegar/plugins/*.py`` module to add a plugin.
registry = PluginRegistry()
