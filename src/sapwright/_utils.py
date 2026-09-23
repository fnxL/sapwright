import logging
import sys
import winreg
from pathlib import Path
from typing import Any

import psutil
import pywintypes
import win32com.client as win32
from pywinauto import Application
from pywinauto.timings import TimeoutError as PywinautoTimeoutError

from sapwright.exceptions import SAPLogonError

logger = logging.getLogger(__name__)

SAPLOGON_EXE = "saplogon.exe"
DEFAULT_TIMEOUT = 60
REGISTRY_KEYS = (
    r"SOFTWARE\SAP\SAP Shared",
    r"SOFTWARE\WOW6432Node\SAP\SAP Shared",
)


def launch_saplogon(exe_path: str | Path | None = None, timeout: int = 60) -> None:
    """Launches the SAP Logon Pad executable and waits for it to become ready.
    If no exe_path is provided, saplogon.exe is resolved from windows registry.

    Parameters
    ----------
    exe_path : str | Path | None, optional
        Path to the saplogon executable, by default None
    timeout : int, optional
        Maximum time to wait for the application to become ready, by default 30

    Raises
    ------
    NotImplementedError
        If called on non-windows platform
    FileNotFoundError
        If the saplogon executable cannot be found
    TimeoutError
        If timeout waiting for the main window after launching.
    SAPLogonError
        If the SAP Logon fails to launch
    """
    if sys.platform != "win32":
        raise NotImplementedError("Launch SAP Logon only supported on Windows")

    if is_process_running(SAPLOGON_EXE):
        logger.debug("SAP Logon is already running")
        return

    path = Path(exe_path) if exe_path else get_saplogon_path()
    if path is None or not path.is_file():
        raise FileNotFoundError(
            f"SAP Logon executable not found at {path or 'registry'}"
        )

    logger.debug(f"Launching SAP Logon from '{path}'")
    try:
        process = psutil.Popen([path])
        app = Application().connect(process=process.pid, timeout=timeout)
        app.top_window().wait("ready", timeout=timeout)
    except PywinautoTimeoutError as e:
        raise TimeoutError(f"Timeout waiting for SAP Logon to become ready: {e}") from e
    except Exception as e:
        msg = f"Failed to connect to SAP Logon: {e}"
        logger.error(msg)
        raise SAPLogonError(msg) from e

    logger.debug("SAP Logon launched and ready")


def is_process_running(process_name: str) -> bool:
    """Checks if a process with the given name is running.

    Parameters
    ----------
    process_name : str
        Name of the process

    Returns
    -------
    bool
        True if the process is running

    Example
    -------
    >>> is_process_running("saplogon.exe")
    True
    """
    target = process_name.lower()
    for proc in psutil.process_iter(["name"]):
        if (proc.info["name"] or "").lower() == target:
            return True
    return False


def get_saplogon_path() -> Path | None:
    """Finds the saplogon executable path from the windows registry, or None if not found.

    Returns
    -------
    Path | None
        Path to the saplogon.exe or None if not found
    """
    for key_path in REGISTRY_KEYS:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                install_dir, _ = winreg.QueryValueEx(key, "SAPsysdir")
        except FileNotFoundError:
            continue

        path = Path(install_dir) / SAPLOGON_EXE
        if path.is_file():
            return path

    return None


def get_scripting_engine() -> Any | None:
    """Returns the SAP GUI scripting engine, or None if SAP Logon is not running."""
    try:
        rot_entry = win32.GetObject("SAPGUI")
    except pywintypes.com_error:
        return None
    return rot_entry.GetScriptingEngine
