import datetime
import logging
import subprocess
import sys
import time
import winreg
from pathlib import Path
from typing import Any

import pywintypes
import win32com.client as win32

from sapwright.exceptions import SAPLogonError

logger = logging.getLogger(__name__)

SAPLOGON_EXE = "saplogon.exe"
DEFAULT_TIMEOUT = 60
REGISTRY_KEYS = (
    r"SOFTWARE\SAP\SAP Shared",
    r"SOFTWARE\WOW6432Node\SAP\SAP Shared",
)


def launch_saplogon(
    exe_path: str | Path | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> None:
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

    if get_scripting_engine() is not None:
        logger.debug("SAP Logon is already running")
        return

    path = Path(exe_path) if exe_path else get_saplogon_path()
    if path is None or not path.is_file():
        raise FileNotFoundError(
            f"SAP Logon executable not found at {path or 'registry'}"
        )

    logger.debug(f"Launching SAP Logon from '{path}'")
    try:
        subprocess.Popen([path])
    except OSError as e:
        msg = f"Failed to launch SAP Logon: {e}"
        logger.error(msg)
        raise SAPLogonError(msg) from e

    # The scripting engine registers in the ROT once SAP Logon is ready
    deadline = time.monotonic() + timeout
    while get_scripting_engine() is None:
        if time.monotonic() > deadline:
            raise TimeoutError("Timeout waiting for SAP Logon to become ready")
        time.sleep(0.5)

    logger.debug("SAP Logon launched and ready")


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


def default_password_generator() -> str:
    """Generates a password from the current month abbreviation and year.

    Example
    -------
    >>> default_password_generator()  # on 2026-01-15
    'Jan@2026'
    """
    return datetime.date.today().strftime("%b@%Y")  # noqa: DTZ011


def get_scripting_engine() -> Any | None:
    """Returns the SAP GUI scripting engine, or None if SAP Logon is not running."""
    try:
        rot_entry = win32.GetObject("SAPGUI")
    except pywintypes.com_error:
        return None
    return rot_entry.GetScriptingEngine
