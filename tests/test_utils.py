import sys
from unittest.mock import MagicMock

import pytest

from sapwright import _utils


@pytest.fixture(autouse=True)
def _windows(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(sys, "platform", "win32")


def test_launch_skipped_when_already_running(monkeypatch: pytest.MonkeyPatch):
    popen = MagicMock()
    monkeypatch.setattr(_utils, "get_scripting_engine", lambda: object())
    monkeypatch.setattr(_utils.subprocess, "Popen", popen)
    _utils.launch_saplogon()
    popen.assert_not_called()


def test_launch_missing_exe(monkeypatch: pytest.MonkeyPatch, tmp_path):
    monkeypatch.setattr(_utils, "get_scripting_engine", lambda: None)
    with pytest.raises(FileNotFoundError):
        _utils.launch_saplogon(tmp_path / "nope.exe")


def test_launch_waits_for_engine(monkeypatch: pytest.MonkeyPatch, tmp_path):
    exe = tmp_path / "saplogon.exe"
    exe.touch()
    engines = iter([None, None, object(), object()])
    monkeypatch.setattr(_utils, "get_scripting_engine", lambda: next(engines))
    monkeypatch.setattr(_utils.subprocess, "Popen", MagicMock())
    monkeypatch.setattr(_utils.time, "sleep", lambda _: None)
    _utils.launch_saplogon(exe)
