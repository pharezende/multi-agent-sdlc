from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, cast

import pytest
from langchain.tools import ToolRuntime
from langchain_core.tools import BaseTool, StructuredTool

from multi_agent_sdlc.tools.coder.filesystem import (
    coder_create_directory,
    coder_delete_directory,
    coder_delete_file,
    coder_move_path,
    coder_write_file,
)
from multi_agent_sdlc.workflow.state import DevState


@pytest.fixture
def project_directory(tmp_path: Path) -> Path:
    project_directory = tmp_path / "sandbox" / "terminal-calculator"
    project_directory.mkdir(parents=True)
    return project_directory


@pytest.fixture
def tool_runtime(
    project_directory: Path,
) -> ToolRuntime[DevState]:
    state = cast(
        DevState,
        {
            "project_directory": project_directory,
        },
    )

    return cast(
        ToolRuntime[DevState],
        SimpleNamespace(state=state),
    )


def get_tool_function(
    tool: BaseTool,
) -> Callable[..., Any]:
    if not isinstance(tool, StructuredTool):
        raise TypeError(f"Expected StructuredTool, got {type(tool).__name__}")

    if tool.func is None:
        raise TypeError(f"Tool {tool.name} does not have a synchronous function")

    return tool.func


def test_write_file_creates_file(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
) -> None:
    function = get_tool_function(coder_write_file)

    result = function(
        path="main.py",
        content="print('hello')\n",
        runtime=tool_runtime,
    )

    file_path = project_directory / "main.py"

    assert file_path.is_file()
    assert file_path.read_text(encoding="utf-8") == "print('hello')\n"
    assert result == "Written production file: main.py"


def test_write_file_creates_parent_directories(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
) -> None:
    function = get_tool_function(coder_write_file)

    function(
        path="src/services/main.py",
        content="value = 1\n",
        runtime=tool_runtime,
    )

    file_path = project_directory / "src/services/main.py"

    assert file_path.is_file()
    assert file_path.read_text(encoding="utf-8") == "value = 1\n"


def test_write_file_overwrites_existing_file(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
) -> None:
    file_path = project_directory / "main.py"
    file_path.write_text("old", encoding="utf-8")

    function = get_tool_function(coder_write_file)

    function(
        path="main.py",
        content="new",
        runtime=tool_runtime,
    )

    assert file_path.read_text(encoding="utf-8") == "new"


def test_write_file_rejects_directory(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
) -> None:
    directory = project_directory / "main.py"
    directory.mkdir()

    function = get_tool_function(coder_write_file)

    with pytest.raises(IsADirectoryError):
        function(
            path="main.py",
            content="new",
            runtime=tool_runtime,
        )

    assert directory.is_dir()


def test_write_file_rejects_test_path(
    tool_runtime: ToolRuntime[DevState],
) -> None:
    function = get_tool_function(coder_write_file)

    with pytest.raises(PermissionError):
        function(
            path="tests/test_main.py",
            content="",
            runtime=tool_runtime,
        )


def test_write_file_rejects_path_escape(
    tool_runtime: ToolRuntime[DevState],
) -> None:
    function = get_tool_function(coder_write_file)

    with pytest.raises(PermissionError):
        function(
            path="../outside.py",
            content="",
            runtime=tool_runtime,
        )


def test_create_directory_creates_directory(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
) -> None:
    function = get_tool_function(coder_create_directory)

    result = function(
        path="src/services",
        runtime=tool_runtime,
    )

    assert (project_directory / "src/services").is_dir()
    assert result == "Created production directory: src/services"


def test_create_directory_creates_parent_directories(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
) -> None:
    function = get_tool_function(coder_create_directory)

    function(
        path="src/services/internal",
        runtime=tool_runtime,
    )

    assert (project_directory / "src/services/internal").is_dir()


def test_create_directory_allows_existing_directory(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
) -> None:
    directory = project_directory / "src"
    directory.mkdir()

    function = get_tool_function(coder_create_directory)

    result = function(
        path="src",
        runtime=tool_runtime,
    )

    assert directory.is_dir()
    assert result == "Created production directory: src"


def test_create_directory_rejects_existing_file(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
) -> None:
    file_path = project_directory / "src"
    file_path.write_text("content", encoding="utf-8")

    function = get_tool_function(coder_create_directory)

    with pytest.raises(FileExistsError):
        function(
            path="src",
            runtime=tool_runtime,
        )

    assert file_path.is_file()


def test_create_directory_rejects_test_path(
    tool_runtime: ToolRuntime[DevState],
) -> None:
    function = get_tool_function(coder_create_directory)

    with pytest.raises(PermissionError):
        function(
            path="tests/unit",
            runtime=tool_runtime,
        )


def test_move_path_renames_file(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
) -> None:
    source = project_directory / "old.py"
    source.write_text("value = 1", encoding="utf-8")

    function = get_tool_function(coder_move_path)

    result = function(
        source_path="old.py",
        destination_path="new.py",
        runtime=tool_runtime,
    )

    destination = project_directory / "new.py"

    assert not source.exists()
    assert destination.is_file()
    assert destination.read_text(encoding="utf-8") == "value = 1"
    assert result == "Moved production path: old.py -> new.py"


def test_move_path_moves_file_between_directories(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
) -> None:
    source_directory = project_directory / "src"
    destination_directory = project_directory / "app"

    source_directory.mkdir()
    destination_directory.mkdir()

    source = source_directory / "main.py"
    source.write_text("value = 1", encoding="utf-8")

    function = get_tool_function(coder_move_path)

    function(
        source_path="src/main.py",
        destination_path="app/main.py",
        runtime=tool_runtime,
    )

    destination = destination_directory / "main.py"

    assert not source.exists()
    assert destination.is_file()
    assert destination.read_text(encoding="utf-8") == "value = 1"


def test_move_path_renames_directory(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
) -> None:
    source = project_directory / "old_package"
    source.mkdir()

    (source / "module.py").write_text("value = 1", encoding="utf-8")

    function = get_tool_function(coder_move_path)

    function(
        source_path="old_package",
        destination_path="new_package",
        runtime=tool_runtime,
    )

    destination = project_directory / "new_package"

    assert not source.exists()
    assert destination.is_dir()
    assert (destination / "module.py").is_file()


def test_move_path_rejects_missing_source(
    tool_runtime: ToolRuntime[DevState],
) -> None:
    function = get_tool_function(coder_move_path)

    with pytest.raises(FileNotFoundError):
        function(
            source_path="missing.py",
            destination_path="new.py",
            runtime=tool_runtime,
        )


def test_move_path_rejects_existing_destination(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
) -> None:
    source = project_directory / "old.py"
    destination = project_directory / "new.py"

    source.write_text("old", encoding="utf-8")
    destination.write_text("new", encoding="utf-8")

    function = get_tool_function(coder_move_path)

    with pytest.raises(FileExistsError):
        function(
            source_path="old.py",
            destination_path="new.py",
            runtime=tool_runtime,
        )

    assert source.exists()
    assert destination.read_text(encoding="utf-8") == "new"


def test_move_path_rejects_missing_destination_parent(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
) -> None:
    source = project_directory / "main.py"
    source.write_text("", encoding="utf-8")

    function = get_tool_function(coder_move_path)

    with pytest.raises(FileNotFoundError):
        function(
            source_path="main.py",
            destination_path="app/main.py",
            runtime=tool_runtime,
        )

    assert source.exists()


def test_move_path_rejects_directory_inside_itself(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
) -> None:
    directory = project_directory / "app"
    directory.mkdir()

    function = get_tool_function(coder_move_path)

    with pytest.raises(ValueError):
        function(
            source_path="app",
            destination_path="app/internal",
            runtime=tool_runtime,
        )

    assert directory.is_dir()


def test_move_path_rejects_test_source(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
) -> None:
    tests_directory = project_directory / "tests"
    tests_directory.mkdir()

    test_file = tests_directory / "test_app.py"
    test_file.write_text("", encoding="utf-8")

    function = get_tool_function(coder_move_path)

    with pytest.raises(PermissionError):
        function(
            source_path="tests/test_app.py",
            destination_path="test_app.py",
            runtime=tool_runtime,
        )

    assert test_file.exists()


def test_move_path_rejects_test_destination(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
) -> None:
    source = project_directory / "main.py"
    source.write_text("", encoding="utf-8")

    function = get_tool_function(coder_move_path)

    with pytest.raises(PermissionError):
        function(
            source_path="main.py",
            destination_path="tests/main.py",
            runtime=tool_runtime,
        )

    assert source.exists()


def test_delete_file_deletes_existing_file(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
) -> None:
    file_path = project_directory / "obsolete.py"
    file_path.write_text("value = 1", encoding="utf-8")

    function = get_tool_function(coder_delete_file)

    result = function(
        path="obsolete.py",
        runtime=tool_runtime,
    )

    assert not file_path.exists()
    assert result == "Deleted production file: obsolete.py"


def test_delete_file_deletes_nested_file(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
) -> None:
    directory = project_directory / "src" / "legacy"
    directory.mkdir(parents=True)

    file_path = directory / "obsolete.py"
    file_path.write_text("value = 1", encoding="utf-8")

    function = get_tool_function(coder_delete_file)

    function(
        path="src/legacy/obsolete.py",
        runtime=tool_runtime,
    )

    assert not file_path.exists()
    assert directory.is_dir()


def test_delete_file_does_not_delete_sibling(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
) -> None:
    directory = project_directory / "src"
    directory.mkdir()

    target = directory / "obsolete.py"
    sibling = directory / "keep.py"

    target.write_text("delete", encoding="utf-8")
    sibling.write_text("keep", encoding="utf-8")

    function = get_tool_function(coder_delete_file)

    function(
        path="src/obsolete.py",
        runtime=tool_runtime,
    )

    assert not target.exists()
    assert sibling.exists()
    assert sibling.read_text(encoding="utf-8") == "keep"
    assert directory.is_dir()


def test_delete_file_rejects_missing_file(
    tool_runtime: ToolRuntime[DevState],
) -> None:
    function = get_tool_function(coder_delete_file)

    with pytest.raises(FileNotFoundError):
        function(
            path="missing.py",
            runtime=tool_runtime,
        )


def test_delete_file_rejects_directory(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
) -> None:
    directory = project_directory / "src"
    directory.mkdir()

    marker = directory / "marker.py"
    marker.write_text("keep", encoding="utf-8")

    function = get_tool_function(coder_delete_file)

    with pytest.raises(IsADirectoryError):
        function(
            path="src",
            runtime=tool_runtime,
        )

    assert directory.is_dir()
    assert marker.exists()


def test_delete_file_rejects_test_file(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
) -> None:
    tests_directory = project_directory / "tests"
    tests_directory.mkdir()

    test_file = tests_directory / "test_app.py"
    test_file.write_text("keep", encoding="utf-8")

    function = get_tool_function(coder_delete_file)

    with pytest.raises(PermissionError):
        function(
            path="tests/test_app.py",
            runtime=tool_runtime,
        )

    assert test_file.exists()
    assert test_file.read_text(encoding="utf-8") == "keep"


@pytest.mark.parametrize(
    "path",
    [
        "../outside.py",
        "../../outside.py",
        "/tmp/outside.py",
    ],
)
def test_delete_file_rejects_path_escape(
    tool_runtime: ToolRuntime[DevState],
    path: str,
) -> None:
    function = get_tool_function(coder_delete_file)

    with pytest.raises(PermissionError):
        function(
            path=path,
            runtime=tool_runtime,
        )


@pytest.mark.parametrize(
    "path",
    [
        "terminal-calculator/file.py",
        "sandbox/terminal-calculator/file.py",
    ],
)
def test_delete_file_rejects_project_prefix(
    tool_runtime: ToolRuntime[DevState],
    path: str,
) -> None:
    function = get_tool_function(coder_delete_file)

    with pytest.raises(PermissionError):
        function(
            path=path,
            runtime=tool_runtime,
        )


def test_delete_file_rejects_external_symlink(
    tmp_path: Path,
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
) -> None:
    outside_file = tmp_path / "outside.py"
    outside_file.write_text("keep", encoding="utf-8")

    alias = project_directory / "external.py"
    alias.symlink_to(outside_file)

    function = get_tool_function(coder_delete_file)

    with pytest.raises(PermissionError):
        function(
            path="external.py",
            runtime=tool_runtime,
        )

    assert outside_file.exists()
    assert outside_file.read_text(encoding="utf-8") == "keep"
    assert alias.is_symlink()


def test_delete_file_allows_internal_symlink_target(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
) -> None:
    target = project_directory / "real.py"
    target.write_text("value = 1", encoding="utf-8")

    alias = project_directory / "alias.py"
    alias.symlink_to(target)

    function = get_tool_function(coder_delete_file)

    function(
        path="alias.py",
        runtime=tool_runtime,
    )

    assert not target.exists()
    assert alias.is_symlink()


def test_delete_directory_deletes_empty_directory(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
) -> None:
    directory = project_directory / "obsolete"
    directory.mkdir()

    function = get_tool_function(coder_delete_directory)

    result = function(
        path="obsolete",
        runtime=tool_runtime,
    )

    assert not directory.exists()
    assert result == "Deleted production directory: obsolete"


def test_delete_directory_deletes_nonempty_directory(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
) -> None:
    directory = project_directory / "obsolete"
    directory.mkdir()

    file_path = directory / "module.py"
    file_path.write_text("value = 1", encoding="utf-8")

    function = get_tool_function(coder_delete_directory)

    function(
        path="obsolete",
        runtime=tool_runtime,
    )

    assert not directory.exists()
    assert not file_path.exists()


def test_delete_directory_deletes_nested_tree(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
) -> None:
    directory = project_directory / "obsolete"
    nested_directory = directory / "package" / "internal"
    nested_directory.mkdir(parents=True)

    root_file = directory / "README.md"
    nested_file = nested_directory / "module.py"

    root_file.write_text("obsolete", encoding="utf-8")
    nested_file.write_text("value = 1", encoding="utf-8")

    function = get_tool_function(coder_delete_directory)

    function(
        path="obsolete",
        runtime=tool_runtime,
    )

    assert not directory.exists()
    assert not root_file.exists()
    assert not nested_directory.exists()
    assert not nested_file.exists()


def test_delete_directory_does_not_delete_sibling(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
) -> None:
    target = project_directory / "obsolete"
    sibling = project_directory / "keep"

    target.mkdir()
    sibling.mkdir()

    target_file = target / "delete.py"
    sibling_file = sibling / "keep.py"

    target_file.write_text("delete", encoding="utf-8")
    sibling_file.write_text("keep", encoding="utf-8")

    function = get_tool_function(coder_delete_directory)

    function(
        path="obsolete",
        runtime=tool_runtime,
    )

    assert not target.exists()
    assert sibling.is_dir()
    assert sibling_file.exists()
    assert sibling_file.read_text(encoding="utf-8") == "keep"


def test_delete_directory_rejects_missing_directory(
    tool_runtime: ToolRuntime[DevState],
) -> None:
    function = get_tool_function(coder_delete_directory)

    with pytest.raises(FileNotFoundError):
        function(
            path="missing",
            runtime=tool_runtime,
        )


def test_delete_directory_rejects_file(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
) -> None:
    file_path = project_directory / "main.py"
    file_path.write_text("keep", encoding="utf-8")

    function = get_tool_function(coder_delete_directory)

    with pytest.raises(NotADirectoryError):
        function(
            path="main.py",
            runtime=tool_runtime,
        )

    assert file_path.exists()
    assert file_path.read_text(encoding="utf-8") == "keep"


@pytest.mark.parametrize(
    "path",
    [
        ".",
        "./",
    ],
)
def test_delete_directory_rejects_project_root(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
    path: str,
) -> None:
    marker = project_directory / "marker.txt"
    marker.write_text("keep", encoding="utf-8")

    function = get_tool_function(coder_delete_directory)

    with pytest.raises(PermissionError):
        function(
            path=path,
            runtime=tool_runtime,
        )

    assert project_directory.is_dir()
    assert marker.exists()
    assert marker.read_text(encoding="utf-8") == "keep"


@pytest.mark.parametrize(
    "path",
    [
        "tests",
        "tests/unit",
        "tests/integration",
    ],
)
def test_delete_directory_rejects_test_directory(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
    path: str,
) -> None:
    target = project_directory / path
    target.mkdir(parents=True)

    marker = target / "test_marker.py"
    marker.write_text("keep", encoding="utf-8")

    function = get_tool_function(coder_delete_directory)

    with pytest.raises(PermissionError):
        function(
            path=path,
            runtime=tool_runtime,
        )

    assert target.is_dir()
    assert marker.exists()
    assert marker.read_text(encoding="utf-8") == "keep"


@pytest.mark.parametrize(
    "path",
    [
        "../outside",
        "../../outside",
        "/tmp/outside",
    ],
)
def test_delete_directory_rejects_path_escape(
    tool_runtime: ToolRuntime[DevState],
    path: str,
) -> None:
    function = get_tool_function(coder_delete_directory)

    with pytest.raises(PermissionError):
        function(
            path=path,
            runtime=tool_runtime,
        )


@pytest.mark.parametrize(
    "path",
    [
        "terminal-calculator/obsolete",
        "sandbox/terminal-calculator/obsolete",
    ],
)
def test_delete_directory_rejects_project_prefix(
    tool_runtime: ToolRuntime[DevState],
    path: str,
) -> None:
    function = get_tool_function(coder_delete_directory)

    with pytest.raises(PermissionError):
        function(
            path=path,
            runtime=tool_runtime,
        )


def test_delete_directory_rejects_external_symlink(
    tmp_path: Path,
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
) -> None:
    outside_directory = tmp_path / "outside"
    outside_directory.mkdir()

    marker = outside_directory / "marker.txt"
    marker.write_text("keep", encoding="utf-8")

    alias = project_directory / "external"
    alias.symlink_to(
        outside_directory,
        target_is_directory=True,
    )

    function = get_tool_function(coder_delete_directory)

    with pytest.raises(PermissionError):
        function(
            path="external",
            runtime=tool_runtime,
        )

    assert outside_directory.is_dir()
    assert marker.exists()
    assert marker.read_text(encoding="utf-8") == "keep"
    assert alias.is_symlink()


def test_delete_directory_allows_internal_symlink_target(
    project_directory: Path,
    tool_runtime: ToolRuntime[DevState],
) -> None:
    target = project_directory / "real_directory"
    target.mkdir()

    target_file = target / "module.py"
    target_file.write_text("value = 1", encoding="utf-8")

    alias = project_directory / "alias"
    alias.symlink_to(
        target,
        target_is_directory=True,
    )

    function = get_tool_function(coder_delete_directory)

    function(
        path="alias",
        runtime=tool_runtime,
    )

    assert not target.exists()
    assert not target_file.exists()
    assert alias.is_symlink()
