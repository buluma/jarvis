"""Bridge pluginmanager 0.4.x entry points to the Python standard library.

pluginmanager 0.4.1 imports setuptools' deprecated pkg_resources module even
though Jarvis only needs the entry-point manager's public interface. Install a
small compatible implementation before importing pluginmanager so Python 3.13+
does not need that removed setuptools API.
"""

import sys
from importlib.metadata import entry_points as discover_entry_points
from types import ModuleType


def _as_set(values):
    if values is None:
        return set()
    if isinstance(values, str):
        return {values}
    return set(values)


class EntryPointManager:
    """Subset of pluginmanager's EntryPointManager API using importlib."""

    def __init__(self, entry_point_names=None):
        self.entry_point_names = _as_set(entry_point_names)

    def add_entry_points(self, names):
        self.entry_point_names.update(_as_set(names))

    def set_entry_points(self, names):
        self.entry_point_names = _as_set(names)

    def remove_entry_points(self, names):
        self.entry_point_names.difference_update(_as_set(names))

    def get_entry_points(self):
        return self.entry_point_names

    def collect_plugins(
        self, entry_points=None, verify_requirements=False, return_dict=False
    ):
        groups = self.entry_point_names if entry_points is None else _as_set(entry_points)
        plugins = []
        names = []
        discovered = discover_entry_points()
        for group in groups:
            for entry_point in discovered.select(group=group):
                plugins.append(entry_point.load())
                names.append(entry_point.name)

        if return_dict:
            return dict(zip(names, plugins))
        return plugins, names


def install_entry_point_compatibility():
    """Provide pluginmanager's entry-point module without importing pkg_resources."""
    module_name = "pluginmanager.entry_point_manager"
    if module_name in sys.modules:
        return

    compatibility_module = ModuleType(module_name)
    compatibility_module.EntryPointManager = EntryPointManager
    compatibility_module.__package__ = "pluginmanager"
    sys.modules[module_name] = compatibility_module
