"""Smoke checks for the local Python bootstrap."""

import pytest

from quality_gate.doctor import collect_environment_snapshot

pytestmark = [pytest.mark.smoke, pytest.mark.bootstrap]


def test_doctor_snapshot_contains_python_bootstrap_details() -> None:
    """The helper should expose enough data to debug the local environment."""

    snapshot = collect_environment_snapshot()

    assert snapshot.python_executable
    assert snapshot.python_version
    assert snapshot.package_version == "0.1.0"
    assert snapshot.project_root.endswith("quality-gate")
