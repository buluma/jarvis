import os

IS_WIN = os.name == 'nt'


if IS_WIN:
    if os.system('py --version') == 0:
        PY3 = "py -3"
        VIRTUALENV_CMD = "py -3 -m venv"
    else:
        PY3 = "python"
        VIRTUALENV_CMD = "python -m venv"
    VIRTUALENV_PYTHON = "env\\Scripts\\python.exe"
    VIRTUALENV_PIP = "env\\Scripts\\pip.exe"

else:
    PY3 = "python3"
    VIRTUALENV_CMD = "python3 -m venv"
    VIRTUALENV_PYTHON = "env/bin/python"
    VIRTUALENV_PIP = "env/bin/pip"
