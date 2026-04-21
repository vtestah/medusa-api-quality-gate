"""Utilities for checking the active Python runtime."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys

from quality_gate import __version__


@dataclass(slots=True)
class EnvironmentSnapshot:
    """Small runtime snapshot for debugging the active virtual environment."""

    python_executable: str
    python_version: str
    project_root: str
    package_version: str
    is_virtual_environment: bool


def collect_environment_snapshot() -> EnvironmentSnapshot:
    """Collect the runtime details that matter for local QA bootstrap."""

    package_root = Path(__file__).resolve().parents[2]
    return EnvironmentSnapshot(
        python_executable=sys.executable,
        python_version=sys.version.split()[0],
        project_root=str(package_root),
        package_version=__version__,
        is_virtual_environment=sys.prefix != sys.base_prefix,
    )


def main() -> None:
    """Print the current runtime snapshot as readable JSON."""

    snapshot = collect_environment_snapshot()
    print(json.dumps(asdict(snapshot), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
