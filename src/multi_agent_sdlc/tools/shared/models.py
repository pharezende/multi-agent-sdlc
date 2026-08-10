from typing import Annotated, NotRequired, TypedDict

from pydantic import AfterValidator, Field

from multi_agent_sdlc.system.validation import (
    validate_application_arguments,
    validate_file_content,
    validate_project_relative_path,
)

ProjectRelativePath = Annotated[
    str,
    Field(
        min_length=1,
        max_length=500,
        description=(
            "A path relative to the project directory. "
            "Absolute paths and parent-directory traversal are prohibited."
        ),
    ),
    AfterValidator(validate_project_relative_path),
]

FileContent = Annotated[
    str,
    Field(
        max_length=500_000,
        description="Complete UTF-8 text content to write to the file.",
    ),
    AfterValidator(validate_file_content),
]

ExecutionTimeout = Annotated[
    int,
    Field(
        ge=1,
        le=200,
        description="Maximum application execution time in seconds.",
    ),
]

StandardInput = Annotated[
    str,
    Field(
        min_length=1,
        max_length=10_000,
        description=(
            "Text sent to the application's standard input. Separate "
            "interactive responses with newline characters. Omit this "
            "argument when no standard input is required."
        ),
    ),
]

ApplicationArguments = Annotated[
    list[str],
    Field(
        max_length=50,
        description="Arguments passed directly to the application.",
    ),
    AfterValidator(validate_application_arguments),
]


class ProcessResult(TypedDict):
    command: list[str]
    exit_code: int | None
    stdout: str
    stderr: str
    timed_out: bool
    message: NotRequired[str]
