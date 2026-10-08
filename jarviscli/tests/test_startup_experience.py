import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CLI_DIR = Path(__file__).resolve().parents[1]


class StartupExperienceTest(unittest.TestCase):
    def test_prime_factor_command_is_distinct_and_handles_input(self):
        from plugins.factor import prime_factors

        self.assertEqual(prime_factors(84), [2, 2, 3, 7])
        self.assertEqual(prime_factors(1), [])
        with self.assertRaises(ValueError):
            prime_factors(0)

    def test_movie_database_path_can_be_configured(self):
        from unittest.mock import patch
        from plugins.movie import movie_database_path

        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "imdb.db"
            with patch.dict(os.environ, {"JARVIS_IMDB_DATABASE": str(path)}):
                self.assertEqual(movie_database_path(), path)
            self.assertFalse(path.exists())

    def test_movie_database_defaults_to_user_data_directory(self):
        from unittest.mock import patch
        from plugins.movie import movie_database_path

        with tempfile.TemporaryDirectory() as temporary_directory:
            with patch.dict(os.environ, {
                "JARVIS_DATA_DIR": temporary_directory,
                "JARVIS_IMDB_DATABASE": "",
            }):
                self.assertEqual(
                    movie_database_path(),
                    Path(temporary_directory) / "cinemagoer.db",
                )

    def test_voice_input_requires_explicit_consent(self):
        from plugins.voice_control import confirm_voice_input

        class FakeJarvis:
            def __init__(self, response):
                self.response = response
                self.messages = []

            def say(self, message):
                self.messages.append(message)

            def input(self, prompt):
                self.messages.append(prompt)
                return self.response

        denied = FakeJarvis("no")
        self.assertFalse(confirm_voice_input(denied))
        self.assertTrue(any("Google's speech-recognition service" in message
                            for message in denied.messages))

        accepted = FakeJarvis("yes")
        self.assertTrue(confirm_voice_input(accepted))

    def test_entry_point_compatibility_uses_importlib_metadata(self):
        from unittest.mock import patch
        from pluginmanager_compat import EntryPointManager

        class EntryPoint:
            name = "sample"

            def load(self):
                return "loaded plugin"

        class EntryPoints:
            def select(self, group):
                self.selected_group = group
                return [EntryPoint()]

        discovered = EntryPoints()
        manager = EntryPointManager("jarvis.test")
        with patch("pluginmanager_compat.discover_entry_points", return_value=discovered):
            plugins, names = manager.collect_plugins()

        self.assertEqual(discovered.selected_group, "jarvis.test")
        self.assertEqual(plugins, ["loaded plugin"])
        self.assertEqual(names, ["sample"])

    def test_startup_is_quiet_and_guides_greetings_and_mistyped_commands(self):
        script = r'''
import contextlib
import io
import os
import sys
import warnings

import Jarvis

startup_output = io.StringIO()
with contextlib.redirect_stdout(startup_output):
    jarvis = Jarvis.Jarvis(first_reaction=False)
jarvis.speak = lambda text: None

command_output = io.StringIO()
with warnings.catch_warnings(record=True) as recorded:
    warnings.simplefilter("always")
    with contextlib.redirect_stdout(command_output):
        jarvis.onecmd(jarvis.precmd("hi"))
        jarvis.onecmd(jarvis.precmd("hellp"))
        jarvis.onecmd(jarvis.precmd("prime factors 84"))
        jarvis.onecmd(jarvis.precmd("factor x**2-y**2"))
        jarvis.onecmd(jarvis.precmd("movie search avatar"))
        jarvis.do_status("short")

assert "pkg_resources" not in sys.modules
assert not os.path.exists("cinemagoer.db")
assert not os.path.exists(os.environ["JARVIS_IMDB_DATABASE"])
assert "No module named" not in startup_output.getvalue()
assert "Duplicate command 'factor'" not in startup_output.getvalue()
assert "factor" in jarvis._command_names()
assert "prime factors" in jarvis._command_names()
assert "Hi! Try 'help'" in command_output.getvalue()
assert "Did you mean" in command_output.getvalue()
assert "2 x 2 x 3 x 7" in command_output.getvalue()
assert "(x - y)*(x + y)" in command_output.getvalue()
assert "Cinemagoer database" in command_output.getvalue(), command_output.getvalue()
assert "plugin modules unavailable" in command_output.getvalue()
assert not any(isinstance(item.message, FutureWarning) for item in recorded)
print("startup checks passed")
'''
        env = os.environ.copy()
        python_path = [str(CLI_DIR)]
        if env.get("PYTHONPATH"):
            python_path.append(env["PYTHONPATH"])
        env["PYTHONPATH"] = os.pathsep.join(python_path)

        with tempfile.TemporaryDirectory(prefix="jarvis-startup-") as working_dir:
            env["JARVIS_IMDB_DATABASE"] = str(Path(working_dir) / "movie.db")
            result = subprocess.run(
                [sys.executable, "-c", script],
                cwd=working_dir,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("startup checks passed", result.stdout)
        self.assertNotIn("pkg_resources is deprecated", result.stderr)


if __name__ == "__main__":
    unittest.main()
