#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$repo_root/env/bin/activate" ]]; then
    # shellcheck disable=SC1091
    source "$repo_root/env/bin/activate"
fi

cd "$repo_root/jarviscli"
if [[ "${1:-}" == "--all" ]]; then
    python -m unittest discover
else
    python -m flake8 --select E9,F63,F7,F82 \
        __main__.py bootstrap.py \
        plugins/colorconverter.py plugins/geolocation.py plugins/cocktail.py \
        plugins/moon_phase.py plugins/dnd.py plugins/wordle.py plugins/readpdf.py \
        plugins/word_chain_game.py plugins/workspace.py plugins/dictionary.py \
        plugins/translate.py utilities/GeneralUtilities.py utilities/nltk_loader.py \
        tests/test_project_health.py ../installer/steps/a_setup_virtualenv.py \
        ../installer/unix_windows.py
    python -m unittest tests.test_project_health tests.test_lazy_nltk
fi
