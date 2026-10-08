"""Import-path support for running Jarvis as a script or a package."""

import os
import sys


def prepare_import_paths(entrypoint):
    """Expose the legacy top-level modules and the repository package root."""
    package_directory = os.path.dirname(os.path.abspath(entrypoint))
    project_directory = os.path.dirname(package_directory)
    for directory in (package_directory, project_directory):
        if directory not in sys.path:
            sys.path.insert(0, directory)
