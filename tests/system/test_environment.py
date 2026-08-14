import os
from unittest.mock import patch

from multi_agent_sdlc.system.environment import build_sandbox_environment


import os
from unittest.mock import patch

from multi_agent_sdlc.system.environment import build_sandbox_environment


def test_build_sandbox_environment_removes_virtual_env() -> None:
    with patch.dict(
        os.environ,
        {
            "VIRTUAL_ENV": "/tmp/orchestrator/.venv",
        },
        clear=True,
    ):
        environment = build_sandbox_environment()

    assert "VIRTUAL_ENV" not in environment


def test_build_sandbox_environment_removes_python_configuration() -> None:
    with patch.dict(
        os.environ,
        {
            "PYTHONPATH": "/custom/python/path",
            "PYTHONHOME": "/custom/python/home",
        },
        clear=True,
    ):
        environment = build_sandbox_environment()

    assert "PYTHONPATH" not in environment
    assert "PYTHONHOME" not in environment


def test_build_sandbox_environment_disables_user_site_packages() -> None:
    with patch.dict(
        os.environ,
        {
            "PYTHONNOUSERSITE": "0",
        },
        clear=True,
    ):
        environment = build_sandbox_environment()

    assert environment["PYTHONNOUSERSITE"] == "1"


def test_build_sandbox_environment_preserves_other_variables() -> None:
    with patch.dict(
        os.environ,
        {
            "PATH": "/usr/bin",
            "HOME": "/home/test",
            "CUSTOM_VARIABLE": "value",
        },
        clear=True,
    ):
        environment = build_sandbox_environment()

    assert environment["PATH"] == "/usr/bin"
    assert environment["HOME"] == "/home/test"
    assert environment["CUSTOM_VARIABLE"] == "value"


def test_build_sandbox_environment_does_not_modify_os_environ() -> None:
    with patch.dict(
        os.environ,
        {
            "VIRTUAL_ENV": "/tmp/orchestrator/.venv",
            "PYTHONPATH": "/custom/python/path",
            "PYTHONHOME": "/custom/python/home",
            "PYTHONNOUSERSITE": "0",
        },
        clear=True,
    ):
        build_sandbox_environment()

        assert os.environ["VIRTUAL_ENV"] == "/tmp/orchestrator/.venv"
        assert os.environ["PYTHONPATH"] == "/custom/python/path"
        assert os.environ["PYTHONHOME"] == "/custom/python/home"
        assert os.environ["PYTHONNOUSERSITE"] == "0"
