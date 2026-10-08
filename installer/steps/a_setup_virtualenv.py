import os
import shutil

from helper import section, fail, shell, printlog, log
import sys
import unix_windows


section("Preparing Python venv")

# Make sure that not running in virtualenv
if sys.prefix != getattr(sys, 'base_prefix', sys.prefix):
    fail("""Please exit virtualenv!""")

# check that virtualenv on python3 installed
py3_installed = shell("{} --version".format(unix_windows.PY3))
if not py3_installed.success() or not py3_installed.cli_output.startswith('Python 3'):
    fail("Please install Python3!\n")
if sys.version_info < (3, 10):
    fail("Python 3.10 or newer is required.\n")

# Reuse an existing environment when it already contains Python 3.
venv_exists = os.path.isdir("env")

# Check that virtualenv works + is Python 3
if venv_exists:
    venv_version = shell("{} --version".format(unix_windows.VIRTUALENV_PYTHON))
    if not venv_version.cli_output.startswith('Python 3'):
        log("WARNING: python --version returns {}".format(venv_version.cli_output))

        printlog("Recreating virtualenv...")
        shutil.rmtree("env")
        venv_exists = False

# Create virtualenv if necessary
if not venv_exists:
    shell("{} env".format(unix_windows.VIRTUALENV_CMD)).should_not_fail()
