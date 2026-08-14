import os


def build_sandbox_environment() -> dict[str, str]:
    """Create an environment isolated from the orchestrator's Python setup."""
    environment = os.environ.copy()
    environment.pop("VIRTUAL_ENV", None)

    environment.pop("PYTHONPATH", None)
    environment.pop("PYTHONHOME", None)

    environment["PYTHONNOUSERSITE"] = "1"

    return environment
