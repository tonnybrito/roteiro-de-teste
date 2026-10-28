"""Shared fixtures and hooks for the BDD run.

- `ctx`: a per-scenario dict the steps use to hand values to each other.
- `run`: runs a command from the project root and returns (returncode, output).
- `@manual` scenarios are skipped: a person checks them by hand.
Steps for each area go in their own module next to this one (steps/terminal.py,
steps/site.py, ...), added to `addopts` in pytest.ini as `-p steps.<name>`.
"""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))  # the project's own modules import from the root


def run(cmd, cwd=ROOT, timeout=300, **kw):
    """Runs a command list and returns (returncode, stdout + stderr)."""
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, **kw)
    return p.returncode, p.stdout + p.stderr


@pytest.fixture
def ctx():
    return {}


def pytest_collection_modifyitems(items):
    for item in items:
        if item.get_closest_marker("manual"):
            item.add_marker(pytest.mark.skip(reason="manual: checked by hand"))
