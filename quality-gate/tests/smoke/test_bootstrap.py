"""Smoke checks for project-local virtual-environment bootstrap."""

from pathlib import Path

import pytest

from quality_gate.bootstrap import collect_bootstrap_snapshot

pytestmark = [pytest.mark.smoke, pytest.mark.bootstrap]


def test_bootstrap_snapshot_matches_project_venv_when_expected_python_is_active(
    tmp_path: Path,
) -> None:
    """The helper should recognize the project venv as the active interpreter."""

    project_root = tmp_path / "ecom-quality-gate"
    expected_python = project_root / ".venv" / "bin" / "python"
    expected_python.parent.mkdir(parents=True)
    expected_python.write_text("#!/usr/bin/env python3\n", encoding="utf-8")

    snapshot = collect_bootstrap_snapshot(
        project_root=project_root,
        active_python_executable=str(expected_python),
        is_virtual_environment=True,
    )

    assert snapshot.venv_exists is True
    assert snapshot.active_python_matches_project_venv is True
    assert snapshot.expected_python_executable.endswith(".venv/bin/python")
    assert snapshot.create_command == "python3 -m venv .venv"
    assert snapshot.activate_command == "source .venv/bin/activate"


def test_bootstrap_snapshot_detects_unactivated_shell_when_system_python_is_used(
    tmp_path: Path,
) -> None:
    """The helper should flag the shell when it still runs outside the project venv."""

    project_root = tmp_path / "ecom-quality-gate"
    expected_python = project_root / ".venv" / "bin" / "python"
    expected_python.parent.mkdir(parents=True)
    expected_python.write_text("#!/usr/bin/env python3\n", encoding="utf-8")

    snapshot = collect_bootstrap_snapshot(
        project_root=project_root,
        active_python_executable="/usr/bin/python3",
        is_virtual_environment=False,
    )

    assert snapshot.venv_exists is True
    assert snapshot.is_virtual_environment is False
    assert snapshot.active_python_matches_project_venv is False
    assert snapshot.active_python_executable == "/usr/bin/python3"
