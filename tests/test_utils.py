import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from sapwright import _utils
from sapwright._utils import is_process_running


@pytest.fixture
def fake_processes(monkeypatch: pytest.MonkeyPatch):
    def _set(*names: str | None):
        procs = [SimpleNamespace(info={"name": name}) for name in names]
        monkeypatch.setattr(
            _utils.psutil, "process_iter", lambda attrs=None: iter(procs)
        )

    return _set


@pytest.fixture
def saplogon_exe(tmp_path: Path) -> Path:
    exe = tmp_path / "saplogon.exe"
    exe.touch()
    return exe


@pytest.fixture
def fake_registry(monkeypatch: pytest.MonkeyPatch):
    """Maps registry key paths to their SAPsysdir value; missing keys raise FileNotFoundError."""

    def _set(entries: dict[str, str]):
        def open_key(_hive, key_path):
            if key_path not in entries:
                raise FileNotFoundError(key_path)
            return MagicMock(key_path=key_path)

        def query_value(key, _name):
            return entries[key.key_path], 1

        monkeypatch.setattr(_utils.winreg, "OpenKey", open_key)
        monkeypatch.setattr(_utils.winreg, "QueryValueEx", query_value)

    return _set


@pytest.fixture
def launch_env(monkeypatch: pytest.MonkeyPatch, fake_processes):
    """Windows platform, no running SAP Logon, and mocked Popen/Application."""
    monkeypatch.setattr(sys, "platform", "win32")
    fake_processes()

    popen = MagicMock(return_value=SimpleNamespace(pid=1234))
    application = MagicMock()
    monkeypatch.setattr(_utils.psutil, "Popen", popen)
    monkeypatch.setattr(_utils, "Application", application)
    return SimpleNamespace(
        popen=popen, app=application.return_value.connect.return_value
    )


# is_process_running


def test_is_process_running_found(fake_processes):
    fake_processes("python.exe", "saplogon.exe")
    assert is_process_running("saplogon.exe") is True


def test_is_process_running_case_insensitive(fake_processes):
    fake_processes("SAPLogon.EXE")
    assert is_process_running("saplogon.exe") is True


def test_is_process_running_not_found(fake_processes):
    fake_processes("python.exe", None)
    assert is_process_running("saplogon.exe") is False
