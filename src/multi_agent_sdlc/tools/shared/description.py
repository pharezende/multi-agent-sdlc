LIST_FILES_DESCRIPTION = """
List the immediate files and directories at a path inside the current project.

Path rules:
- `path` must be relative to the current project root.
- Use `.` to list the project root.
- Do not include `sandbox/`, the project name, or an absolute path.
- Do not use `..`.

Correct examples:
- .
- src
- src/calculator

Incorrect examples:
- sandbox/terminal-calculator
- /home/user/project
- ../other-project

This tool lists one directory level at a time. It does not recursively inspect
subdirectories or execute shell commands.
""".strip()


READ_FILE_DESCRIPTION = """
Read the complete contents of a UTF-8 text file inside the current project.

Path rules:
- `path` must be relative to the current project root.
- Do not include `sandbox/`, the project name, or an absolute path.
- Do not use `..`.

Correct examples:
- pyproject.toml
- README.md
- src/calculator/main.py

Incorrect examples:
- sandbox/terminal-calculator/pyproject.toml
- /home/user/project/main.py
- ../other-project/main.py

Use this tool to inspect project files before implementation, test creation,
verification, or review. This tool does not modify files.
""".strip()
