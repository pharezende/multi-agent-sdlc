from multi_agent_sdlc.tools.shared.filesystem import list_files, read_file
from multi_agent_sdlc.tools.tester.dependencies import (
    tester_install_verification_dependencies,
)
from multi_agent_sdlc.tools.tester.execution import (
    tester_run_application,
    tester_run_project_verification,
    tester_run_python_module,
    tester_run_verification_command,
    tester_sync_project,
)
from multi_agent_sdlc.tools.tester.filesystem import (
    tester_create_directory,
    tester_write_file,
)
from multi_agent_sdlc.tools.tester.finalization import submit_tester_summary

TESTER_TOOLS = [
    tester_run_application,
    tester_run_python_module,
    tester_sync_project,
    tester_install_verification_dependencies,
    tester_write_file,
    tester_create_directory,
    list_files,
    read_file,
    submit_tester_summary,
    tester_run_verification_command,
    tester_run_project_verification,
]
