from multi_agent_sdlc.tools.coder.dependencies import (
    coder_install_runtime_dependencies,
)
from multi_agent_sdlc.tools.coder.execution import (
    coder_run_application,
    coder_run_python_module,
    coder_run_verification_command,
    coder_sync_project,
)
from multi_agent_sdlc.tools.coder.filesystem import (
    coder_create_directory,
    coder_write_file,
)
from multi_agent_sdlc.tools.coder.finalization import submit_coder_summary
from multi_agent_sdlc.tools.shared.filesystem import list_files, read_file

CODER_TOOLS = [
    list_files,
    read_file,
    coder_write_file,
    coder_create_directory,
    coder_sync_project,
    coder_run_application,
    coder_run_python_module,
    coder_install_runtime_dependencies,
    coder_run_verification_command,
    submit_coder_summary,
]
