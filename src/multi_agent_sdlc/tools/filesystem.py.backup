from multi_agent_sdlc.state import DevState
from langgraph.prebuilt import ToolRuntime
from multi_agent_sdlc.tools.path_validation import resolve_project_path
from pathlib import Path

from langchain_core.tools import tool

CODER_WRITE_FILE_DESCRIPTION = """
Create or replace a production-code file inside the current project.

The `path` argument must be relative to the project root.

Correct examples:
- pyproject.toml
- README.md
- src/calculator/__init__.py
- src/calculator/main.py

Incorrect examples:
- sandbox/terminal-calculator/src/calculator/main.py
- /absolute/path/main.py
- ../other-project/main.py
- tests/test_calculator.py
- src/calculator/test_main.py

Do not include the sandbox directory or project directory in `path`.

This tool is restricted to production files.

Do not create or modify:
- unit tests or integration tests;
- files under `test/`, `tests/`, `__tests__/`, `spec/`, or `specs/`;
- files named `test_*.py` or `*_test.py`;
- `conftest.py`, `pytest.ini`, `tox.ini`, or coverage configuration;
- test fixtures, mocks, test data, or test documentation.

Test implementation belongs exclusively to the Tester agent.
If test work is required, do not attempt it with another path or mechanism.
""".strip()

CODER_CREATE_DIRECTORY_DESCRIPTION = """
Create a directory inside the current project directory.

The `path` argument must be relative to the project root.

Correct examples:
- src
- src/calculator
- config

Incorrect examples:
- sandbox/terminal-calculator/src
- /home/user/project/src
- ../another-project

Do not include the sandbox directory or project directory in `path`.
""".strip()


@tool
def read_file(
    path: str,
    runtime: ToolRuntime[DevState],
) -> str:
    """Read a UTF-8 file inside the current project."""

    project_directory = get_project_directory(runtime)

    file_path = resolve_project_path(
        project_directory,
        path,
    )

    if not file_path.is_file():
        raise FileNotFoundError(path)

    return file_path.read_text(encoding="utf-8")


@tool(
    "write_file",
    description=CODER_WRITE_FILE_DESCRIPTION,
)
def write_file(
    path: str,
    content: str,
    runtime: ToolRuntime[DevState],
) -> str:
    reject_coder_test_path(path)

    project_directory = get_project_directory(runtime)
    file_path = resolve_project_path(project_directory, path)

    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")

    return f"Written production file: {path}"


@tool
def list_files(
    runtime: ToolRuntime[DevState],
    path: str = ".",
) -> list[str]:
    """List files recursively inside the current project."""

    project_directory = get_project_directory(runtime)

    directory = resolve_project_path(
        project_directory=project_directory,
        relative_path=path,
    )

    if not directory.is_dir():
        raise NotADirectoryError(f"Directory does not exist: {path}")

    project_root = project_directory.resolve()

    return sorted(
        str(file.relative_to(project_root))
        for file in directory.rglob("*")
        if file.is_file()
    )


@tool(
    "create_directory",
    description=CODER_CREATE_DIRECTORY_DESCRIPTION,
)
def create_directory(
    path: str,
    runtime: ToolRuntime[DevState],
) -> str:
    reject_coder_test_path(path)

    project_directory = get_project_directory(runtime)
    directory_path = resolve_project_path(project_directory, path)

    directory_path.mkdir(parents=True, exist_ok=True)

    return f"Created production directory: {path}"


def get_project_directory(
    runtime: ToolRuntime[DevState],
) -> Path:
    """Retrieve project directory"""

    project_directory = runtime.state.get("project_directory")

    if not project_directory:
        raise ValueError("project_directory is missing from the graph state.")

    directory = Path(project_directory)

    if not directory.is_dir():
        raise NotADirectoryError(f"Project directory does not exist: {directory}")

    return directory.resolve()


from pathlib import PurePosixPath


TEST_DIRECTORY_NAMES = {
    "test",
    "tests",
    "__tests__",
    "spec",
    "specs",
}


def is_test_related_path(path: str) -> bool:
    normalized_path = path.replace("\\", "/").strip("/")
    candidate = PurePosixPath(normalized_path)

    return any(part.lower() in TEST_DIRECTORY_NAMES for part in candidate.parts)


def reject_coder_test_path(path: str) -> None:
    if is_test_related_path(path):
        raise PermissionError(
            "The Coder cannot create or modify files or directories "
            f"inside test-related paths: {path}. "
            "Test implementation belongs to the Tester."
        )
