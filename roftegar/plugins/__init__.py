"""Built-in plugin registrations.

Importing this package has the side-effect of registering all built-in
plugins with the global registry.  External plugins can do the same by
importing ``roftegar.registry.registry`` and calling ``.register()``.
"""

from roftegar.plugins.disk_analyzer import DiskAnalyzerPlugin
from roftegar.plugins.system_usage import SystemUsagePlugin
from roftegar.registry import registry

registry.register(DiskAnalyzerPlugin())
registry.register(SystemUsagePlugin())
