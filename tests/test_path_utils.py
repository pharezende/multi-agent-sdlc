from multi_agent_sdlc.system.path_utils import resolve_project_path
from multi_agent_sdlc.system.path_utils import reject_repeated_project_prefix
from multi_agent_sdlc.system.path_utils import normalise_relative_path
from pathlib import Path, PurePosixPath

import pytest


@pytest.fixture
def project_directory(tmp_path: Path) -> Path:
    project_directory = tmp_path / "sandbox" / "terminal-calculator"
    project_directory.mkdir(parents=True)

    return project_directory


def test_normalise_relative_path_accepts_relative_path() -> None:
    result = normalise_relative_path("src/main.py")

    assert result == PurePosixPath("src/main.py")


def test_normalise_relative_path_strips_whitespace() -> None:
    result = normalise_relative_path("  src/main.py  ")

    assert result == PurePosixPath("src/main.py")


def test_normalise_relative_path_converts_backslashes() -> None:
    result = normalise_relative_path(r"src\services\calculator.py")

    assert result == PurePosixPath("src/services/calculator.py")


def test_normalise_relative_path_rejects_empty_path() -> None:
    with pytest.raises(
        ValueError,
        match="Path cannot be empty",
    ):
        normalise_relative_path("   ")


@pytest.mark.parametrize(
    "path",
    [
        "/etc/passwd",
        "/tmp/file.py",
        "/src/main.py",
    ],
)
def test_normalise_relative_path_rejects_absolute_path(
    path: str,
) -> None:
    with pytest.raises(
        PermissionError,
        match="Absolute paths are not allowed",
    ):
        normalise_relative_path(path)


@pytest.mark.parametrize(
    "path",
    [
        "../main.py",
        "../../main.py",
        "src/../main.py",
        "src/services/../../main.py",
    ],
)
def test_normalise_relative_path_rejects_parent_traversal(
    path: str,
) -> None:
    with pytest.raises(
        PermissionError,
        match="Parent-directory traversal is not allowed",
    ):
        normalise_relative_path(path)


def test_reject_repeated_project_prefix_allows_normal_path(
    project_directory: Path,
) -> None:
    reject_repeated_project_prefix(
        project_directory,
        PurePosixPath("src/main.py"),
    )


def test_reject_repeated_project_prefix_rejects_project_id(
    project_directory: Path,
) -> None:
    with pytest.raises(
        PermissionError,
        match="Do not include the project-directory prefix",
    ):
        reject_repeated_project_prefix(
            project_directory,
            PurePosixPath("terminal-calculator/src/main.py"),
        )


def test_reject_repeated_project_prefix_rejects_sandbox_and_project_id(
    project_directory: Path,
) -> None:
    with pytest.raises(
        PermissionError,
        match="Do not include the project-directory prefix",
    ):
        reject_repeated_project_prefix(
            project_directory,
            PurePosixPath("sandbox/terminal-calculator/src/main.py"),
        )


@pytest.mark.parametrize(
    "path",
    [
        "docs/terminal-calculator.md",
        "src/sandbox.py",
        "sandbox_helpers/utils.py",
    ],
)
def test_reject_repeated_project_prefix_allows_project_name_outside_prefix(
    project_directory: Path,
    path: str,
) -> None:
    reject_repeated_project_prefix(
        project_directory,
        PurePosixPath(path),
    )


def test_resolve_project_path_returns_resolved_project_path(
    project_directory: Path,
) -> None:
    result = resolve_project_path(
        project_directory,
        "src/main.py",
    )

    assert result == (project_directory / "src/main.py").resolve()


def test_resolve_project_path_normalises_backslashes(
    project_directory: Path,
) -> None:
    result = resolve_project_path(
        project_directory,
        r"src\services\calculator.py",
    )

    assert (
        result == (project_directory / "src" / "services" / "calculator.py").resolve()
    )


@pytest.mark.parametrize(
    "path",
    [
        "terminal-calculator/src/main.py",
        "sandbox/terminal-calculator/src/main.py",
    ],
)
def test_resolve_project_path_rejects_repeated_project_prefix(
    project_directory: Path,
    path: str,
) -> None:
    with pytest.raises(
        PermissionError,
        match="Do not include the project-directory prefix",
    ):
        resolve_project_path(
            project_directory,
            path,
        )


def test_resolve_project_path_rejects_parent_traversal(
    project_directory: Path,
) -> None:
    with pytest.raises(
        PermissionError,
        match="Parent-directory traversal is not allowed",
    ):
        resolve_project_path(
            project_directory,
            "../outside.py",
        )


def test_resolve_project_path_rejects_absolute_path(
    project_directory: Path,
) -> None:
    with pytest.raises(
        PermissionError,
        match="Absolute paths are not allowed",
    ):
        resolve_project_path(
            project_directory,
            "/tmp/outside.py",
        )


def test_resolve_project_path_rejects_symlink_escape(
    tmp_path: Path,
    project_directory: Path,
) -> None:
    outside_directory = tmp_path / "outside"
    outside_directory.mkdir()

    symlink = project_directory / "external"
    symlink.symlink_to(
        outside_directory,
        target_is_directory=True,
    )

    with pytest.raises(
        PermissionError,
        match="Path escapes the project directory",
    ):
        resolve_project_path(
            project_directory,
            "external/file.py",
        )


def test_resolve_project_path_allows_symlink_inside_project(
    project_directory: Path,
) -> None:
    target_directory = project_directory / "src"
    target_directory.mkdir()

    symlink = project_directory / "source"
    symlink.symlink_to(
        target_directory,
        target_is_directory=True,
    )

    result = resolve_project_path(
        project_directory,
        "source/main.py",
    )

    assert result == (target_directory / "main.py").resolve()
