import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

JARVISCLI_DIR = Path(__file__).resolve().parents[1]


class LazyNltkTest(unittest.TestCase):
    # Run in a subprocess so nltk imported by other tests can't mask a regression.
    # first_reaction=False skips the spoken greeting, which blocks when voice is enabled.
    def test_starting_jarvis_does_not_import_nltk(self):
        script = (
            "import sys\n"
            "import Jarvis\n"
            "Jarvis.Jarvis(first_reaction=False)\n"
            "print('nltk' in sys.modules)\n"
        )
        env = os.environ.copy()
        python_path = [str(JARVISCLI_DIR)]
        if env.get("PYTHONPATH"):
            python_path.append(env["PYTHONPATH"])
        env["PYTHONPATH"] = os.pathsep.join(python_path)

        with tempfile.TemporaryDirectory(prefix="jarvis-lazy-nltk-") as working_dir:
            result = subprocess.run(
                [sys.executable, "-c", script],
                cwd=working_dir,
                env=env,
                capture_output=True,
                text=True,
                check=True,
            )
        self.assertEqual(result.stdout.strip().splitlines()[-1], "False")


if __name__ == "__main__":
    unittest.main()
