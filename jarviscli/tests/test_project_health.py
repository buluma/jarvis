import importlib
import sys
import tempfile
import unittest
from pathlib import Path

from bootstrap import prepare_import_paths


class ProjectHealthTest(unittest.TestCase):
    def test_executable_lookup_works_without_distutils(self):
        from utilities.GeneralUtilities import executable_exists

        self.assertTrue(executable_exists("python"))
        self.assertFalse(executable_exists("jarvis-command-that-does-not-exist"))

    def test_plugin_modules_import(self):
        for module_name in (
            "plugins.colorconverter",
            "plugins.geolocation",
            "plugins.cocktail",
            "plugins.moon_phase",
            "plugins.flightradar",
        ):
            with self.subTest(module=module_name):
                self.assertIsNotNone(importlib.import_module(module_name))

    def test_word_chain_plugin_does_not_download_data_during_import(self):
        import nltk
        from unittest import mock

        with mock.patch.object(nltk, "download") as download:
            module = importlib.import_module("plugins.word_chain_game")

        self.assertIsNotNone(module)
        download.assert_not_called()

    def test_color_conversions(self):
        from plugins.colorconverter import hex_to_rgb, rgb_to_hex, rgb_to_hsl

        self.assertEqual(hex_to_rgb("#ff0000"), (255, 0, 0))
        self.assertEqual(rgb_to_hex((255, 0, 0)), "#ff0000")
        self.assertEqual(rgb_to_hsl(255, 0, 0), (0, 100, 50))

    def test_packaged_game_data_loads_from_any_working_directory(self):
        from plugins import dnd, wordle

        self.assertTrue(dnd.loots)
        self.assertTrue(wordle.answers)
        self.assertTrue(wordle.guesses)

    def test_workspace_template_copy_can_merge_into_existing_folder(self):
        from plugins.workspace import copy_template

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "source"
            destination = root / "destination"
            source.mkdir()
            destination.mkdir()
            (source / "starter.txt").write_text("Jarvis")
            (destination / "existing.txt").write_text("keep")

            copy_template(str(source), str(destination))

            self.assertEqual((destination / "starter.txt").read_text(), "Jarvis")
            self.assertEqual((destination / "existing.txt").read_text(), "keep")

    def test_pdf_reader_handles_empty_pages_with_current_pypdf_api(self):
        from pypdf import PdfWriter
        from plugins.readpdf import extract_page_text

        with tempfile.TemporaryDirectory() as temporary_directory:
            filename = Path(temporary_directory) / "blank.pdf"
            writer = PdfWriter()
            writer.add_blank_page(width=72, height=72)
            writer.write(str(filename))

            self.assertEqual(extract_page_text(str(filename)), [""])

    def test_bootstrap_makes_package_importable_from_script_directory(self):
        project_directory = str(Path(__file__).resolve().parents[2])
        sys.path[:] = [entry for entry in sys.path if entry != project_directory]

        entrypoint = Path(__file__).resolve().parents[1] / "__main__.py"
        prepare_import_paths(str(entrypoint))
        module = importlib.import_module("jarviscli.plugins.message")

        self.assertTrue(hasattr(module, "send_join_message"))


if __name__ == "__main__":
    unittest.main()
