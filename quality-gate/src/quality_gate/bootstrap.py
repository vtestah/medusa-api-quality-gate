"""Helpers for validating local virtual-environment bootstrap."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys


@dataclass(slots=True)
class BootstrapSnapshot:
    """Describe whether the current Python runtime matches the project venv."""

    project_root: str
    venv_directory: str
    expected_python_executable: str
    active_python_executable: str
    python_version: str
    venv_exists: bool
    is_virtual_environment: bool
    active_python_matches_project_venv: bool
    create_command: str
    activate_command: str


def _normalize_executable_path(path_like: str | Path) -> Path:
    """Return an absolute path without collapsing venv symlinks."""

    path = Path(path_like).expanduser()
    if path.is_absolute():
        return path
    return Path.cwd() / path


def collect_bootstrap_snapshot(
    project_root: Path | None = None,
    active_python_executable: str | None = None,
    is_virtual_environment: bool | None = None,
) -> BootstrapSnapshot:
    """Collect the bootstrap facts that matter for local QA setup."""

    resolved_project_root = (
        project_root.resolve() if project_root is not None else Path(__file__).resolve().parents[3]
    )
    venv_directory = resolved_project_root / ".venv"
    expected_python_executable = venv_directory / "bin" / "python"
    active_python_path = _normalize_executable_path(active_python_executable or sys.executable)
    venv_python_exists = expected_python_executable.exists()
    expected_python_path = _normalize_executable_path(expected_python_executable)

    return BootstrapSnapshot(
        project_root=str(resolved_project_root),
        venv_directory=str(venv_directory),
        expected_python_executable=str(expected_python_path),
        active_python_executable=str(active_python_path),
        python_version=sys.version.split()[0],
        venv_exists=venv_python_exists,
        is_virtual_environment=(
            sys.prefix != sys.base_prefix
            if is_virtual_environment is None
            else is_virtual_environment
        ),
        active_python_matches_project_venv=venv_python_exists
        and active_python_path == expected_python_path,
        create_command="python3 -m venv .venv",
        activate_command="source .venv/bin/activate",
    )


def main() -> None:
    """Print the current bootstrap snapshot as readable JSON."""

    snapshot = collect_bootstrap_snapshot()
    print(json.dumps(asdict(snapshot), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
