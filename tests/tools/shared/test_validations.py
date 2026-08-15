import pytest
from packaging.requirements import Requirement

from multi_agent_sdlc.tools.shared.validation import (
    create_dependency_validator,
    create_entry_point_validator,
    create_module_name_validator,
    parse_dependency,
    validate_application_arguments,
    validate_file_content,
    validate_project_relative_path,
)


@pytest.mark.parametrize(
    ("arguments", "expected"),
    [
        ([], []),
        (["--help"], ["--help"]),
        (["--name", "value"], ["--name", "value"]),
        ([""], [""]),
        (["hello world"], ["hello world"]),
        (["--value=a=b"], ["--value=a=b"]),
    ],
)
def test_validate_application_arguments_accepts_valid_arguments(
    arguments: list[str],
    expected: list[str],
) -> None:
    assert validate_application_arguments(arguments) == expected


@pytest.mark.parametrize(
    "argument",
    [
        "line1\nline2",
        "line1\rline2",
        "line1\r\nline2",
    ],
)
def test_validate_application_arguments_rejects_multiline_arguments(
    argument: str,
) -> None:
    with pytest.raises(
        PermissionError,
        match="Multiline application arguments are not allowed",
    ):
        validate_application_arguments([argument])


def test_validate_application_arguments_rejects_null_bytes() -> None:
    with pytest.raises(
        PermissionError,
        match="Null bytes are not allowed",
    ):
        validate_application_arguments(["value\x00other"])


@pytest.mark.parametrize(
    "argument",
    [
        1,
        None,
        True,
        object(),
    ],
)
def test_validate_application_arguments_rejects_non_string_arguments(
    argument: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="Every application argument must be a string",
    ):
        validate_application_arguments([argument])  # type: ignore[list-item]


def test_validate_application_arguments_preserves_argument_order() -> None:
    arguments = ["--first", "one", "--second", "two"]

    assert validate_application_arguments(arguments) == arguments


def test_validate_application_arguments_returns_new_list() -> None:
    arguments = ["--help"]

    result = validate_application_arguments(arguments)

    assert result == arguments
    assert result is not arguments


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("src/main.py", "src/main.py"),
        ("tests/test_cli.py", "tests/test_cli.py"),
        (" ./src/main.py ", "src/main.py"),
        ("src/./main.py", "src/main.py"),
        ("src//main.py", "src/main.py"),
    ],
)
def test_validate_project_relative_path_accepts_and_normalises_valid_paths(
    path: str,
    expected: str,
) -> None:
    assert validate_project_relative_path(path) == expected


@pytest.mark.parametrize(
    "path",
    [
        "../outside.py",
        "src/../../outside.py",
    ],
)
def test_validate_project_relative_path_rejects_parent_traversal(
    path: str,
) -> None:
    with pytest.raises(
        PermissionError,
        match="Parent-directory traversal is not allowed",
    ):
        validate_project_relative_path(path)


@pytest.mark.parametrize(
    "path",
    [
        "/tmp/file.py",
        "/etc/passwd",
    ],
)
def test_validate_project_relative_path_rejects_absolute_paths(
    path: str,
) -> None:
    with pytest.raises(
        PermissionError,
        match="Absolute paths are not allowed",
    ):
        validate_project_relative_path(path)


@pytest.mark.parametrize(
    "content",
    [
        "",
        "hello",
        "hello\nworld",
        "print('hello')\n",
        "áéíóú",
    ],
)
def test_validate_file_content_accepts_valid_content(
    content: str,
) -> None:
    assert validate_file_content(content) == content


def test_validate_file_content_rejects_null_bytes() -> None:
    with pytest.raises(
        ValueError,
        match="File content cannot contain null bytes",
    ):
        validate_file_content("before\x00after")


def test_entry_point_validator_accepts_allowed_entry_point() -> None:
    validator = create_entry_point_validator(
        role="Coder",
        prohibited_entry_points={"pytest", "ruff"},
    )

    assert validator("expense-tracker") == "expense-tracker"


def test_entry_point_validator_strips_surrounding_whitespace() -> None:
    validator = create_entry_point_validator(
        role="Coder",
        prohibited_entry_points=set(),
    )

    assert validator("  expense-tracker  ") == "expense-tracker"


@pytest.mark.parametrize(
    "entry_point",
    [
        "",
        " ",
        "\t",
        "\n",
    ],
)
def test_entry_point_validator_rejects_empty_entry_point(
    entry_point: str,
) -> None:
    validator = create_entry_point_validator(
        role="Coder",
        prohibited_entry_points=set(),
    )

    with pytest.raises(
        ValueError,
        match="Entry point cannot be empty",
    ):
        validator(entry_point)


@pytest.mark.parametrize(
    "entry_point",
    [
        "pytest",
        "PYTEST",
        "PyTest",
        " pytest ",
    ],
)
def test_entry_point_validator_rejects_prohibited_entry_point_case_insensitively(
    entry_point: str,
) -> None:
    validator = create_entry_point_validator(
        role="Coder",
        prohibited_entry_points={"pytest"},
    )

    with pytest.raises(
        ValueError,
        match="The Coder cannot execute",
    ):
        validator(entry_point)


@pytest.mark.parametrize(
    ("module", "expected"),
    [
        ("app", "app"),
        ("app.cli", "app.cli"),
        ("package.subpackage.module", "package.subpackage.module"),
        ("_private", "_private"),
        ("package._internal", "package._internal"),
        ("  app.cli  ", "app.cli"),
    ],
)
def test_module_name_validator_accepts_valid_module_names(
    module: str,
    expected: str,
) -> None:
    validator = create_module_name_validator(
        role="Coder",
        prohibited_python_modules=set(),
    )

    assert validator(module) == expected


@pytest.mark.parametrize(
    "module",
    [
        "",
        " ",
        "1module",
        "module-name",
        "module/name",
        ".module",
        "module.",
        "module..submodule",
        "module submodule",
        "module;other",
        "module\nother",
    ],
)
def test_module_name_validator_rejects_invalid_module_names(
    module: str,
) -> None:
    validator = create_module_name_validator(
        role="Coder",
        prohibited_python_modules=set(),
    )

    with pytest.raises(ValueError):
        validator(module)


@pytest.mark.parametrize(
    "module",
    [
        "pytest",
        "pytest.main",
        "PyTest",
        "PYTEST.main",
    ],
)
def test_module_name_validator_rejects_prohibited_root_module(
    module: str,
) -> None:
    validator = create_module_name_validator(
        role="Coder",
        prohibited_python_modules={"pytest"},
    )

    with pytest.raises(
        PermissionError,
        match="The Coder cannot execute Python module",
    ):
        validator(module)


def test_module_name_validator_allows_prohibited_name_as_non_root_module() -> None:
    validator = create_module_name_validator(
        role="Coder",
        prohibited_python_modules={"pytest"},
    )

    assert validator("application.pytest") == "application.pytest"


@pytest.mark.parametrize(
    ("dependency", "expected"),
    [
        ("requests", "requests"),
        ("requests==2.32.0", "requests==2.32.0"),
        ("requests>=2.0", "requests>=2.0"),
        ("requests~=2.32", "requests~=2.32"),
        ("requests[security]", "requests[security]"),
        ("requests>=2,<3", "requests>=2,<3"),
        ("requests===custom-version", "requests===custom-version"),
        ("  requests>=2.0  ", "requests>=2.0"),
    ],
)
def test_dependency_validator_accepts_valid_dependencies(
    dependency: str,
    expected: str,
) -> None:
    validator = create_dependency_validator(
        role="Coder",
        prohibited_dependencies=set(),
    )

    assert validator(dependency) == expected


@pytest.mark.parametrize(
    "dependency",
    [
        "",
        " ",
        "\t",
    ],
)
def test_dependency_validator_rejects_empty_dependency(
    dependency: str,
) -> None:
    validator = create_dependency_validator(
        role="Coder",
        prohibited_dependencies=set(),
    )

    with pytest.raises(
        ValueError,
        match="Dependency specification cannot be empty",
    ):
        validator(dependency)


@pytest.mark.parametrize(
    "dependency",
    [
        "--editable",
        "--index-url=https://example.com",
        "-e",
    ],
)
def test_dependency_validator_rejects_command_line_options(
    dependency: str,
) -> None:
    validator = create_dependency_validator(
        role="Coder",
        prohibited_dependencies=set(),
    )

    with pytest.raises(
        PermissionError,
        match="Dependency command-line options are not allowed",
    ):
        validator(dependency)


@pytest.mark.parametrize(
    "dependency",
    [
        "package @ https://example.com/package.whl",
        "package @ file:///tmp/package",
        "package @ git+https://github.com/example/package.git",
        "package @ git+ssh://git@example.com/package.git",
    ],
)
def test_dependency_validator_rejects_url_dependencies(
    dependency: str,
) -> None:
    validator = create_dependency_validator(
        role="Coder",
        prohibited_dependencies=set(),
    )

    with pytest.raises(
        PermissionError,
        match="Git, URL, SSH, and local-file dependencies are not allowed",
    ):
        validator(dependency)


@pytest.mark.parametrize(
    "dependency",
    [
        "pytest",
        "pytest==8.0.0",
        "PYTEST",
        "pytest[testing]",
    ],
)
def test_dependency_validator_rejects_prohibited_dependency(
    dependency: str,
) -> None:
    validator = create_dependency_validator(
        role="Coder",
        prohibited_dependencies={"pytest"},
    )

    with pytest.raises(
        PermissionError,
        match="The Coder cannot add dependency",
    ):
        validator(dependency)


@pytest.mark.parametrize(
    "dependency",
    [
        "my-package",
        "my_package",
        "MY.PACKAGE",
    ],
)
def test_dependency_validator_canonicalizes_prohibited_dependency_names(
    dependency: str,
) -> None:
    validator = create_dependency_validator(
        role="Coder",
        prohibited_dependencies={"my-package"},
    )

    with pytest.raises(PermissionError):
        validator(dependency)


@pytest.mark.parametrize(
    "dependency",
    [
        "not a valid requirement",
        "package @",
        "package[",
        "package=>1.0",
    ],
)
def test_dependency_validator_rejects_invalid_requirement(
    dependency: str,
) -> None:
    validator = create_dependency_validator(
        role="Coder",
        prohibited_dependencies=set(),
    )

    with pytest.raises(
        ValueError,
        match="Invalid dependency specification",
    ):
        validator(dependency)


@pytest.mark.parametrize(
    "specification",
    [
        "requests",
        "requests==2.32.0",
        "requests>=2,<3",
        "requests[security]>=2.0",
        "requests===custom-version",
    ],
)
def test_parse_dependency_returns_requirement(
    specification: str,
) -> None:
    result = parse_dependency(specification)

    assert isinstance(result, Requirement)
    assert result.name == "requests"


@pytest.mark.parametrize(
    "specification",
    [
        "",
        "not a valid requirement",
        "package @",
        "package[",
        "package=>1.0",
    ],
)
def test_parse_dependency_rejects_invalid_requirement(
    specification: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="Invalid dependency specification",
    ):
        parse_dependency(specification)
