import logging
from pathlib import Path
from types import TracebackType
from typing import final

from sapwright._utils import launch_saplogon
from sapwright.connection_manager import ConnectionManager
from sapwright.exceptions import SAPLoginError
from sapwright.objects import GuiSession

logger = logging.getLogger(__name__)


class SAPLoginScreenElements:
    client = "wnd[0]/usr/txtRSYST-MANDT"
    username = "wnd[0]/usr/txtRSYST-BNAME"
    password = "wnd[0]/usr/pwdRSYST-BCODE"
    language = "wnd[0]/usr/txtRSYST-LANGU"
    terminate_other_sessions_radio = "wnd[1]/usr/radMULTI_LOGON_OPT1"


@final
class Sapwright:
    def __init__(
        self,
        username: str,
        password: str,
        connection_string: str | None = None,
        connection_name: str | None = None,
        client: int | None = None,
        language: str | None = None,
        terminate_other_sessions: bool = True,
        exe_path: str | Path | None = None,
    ):
        """
        First preference is given to the connection_string, then connection_name.
        """
        if not connection_string and not connection_name:
            raise ValueError("connection_string or connection_name must be provided.")

        self._username = username
        self._password = password
        self._connection_string = connection_string
        self._connection_name = connection_name
        self._client = client
        self._language = language
        self._terminate_other_sessions = terminate_other_sessions
        self._exe_path = exe_path
        self._session: GuiSession | None = None

    def __enter__(self):
        self._session = self.connect()
        return self._session

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._session:
            self._session.close()

    def connect(self) -> GuiSession:
        """Attach to the user's existing connection, or open a new one if none is found.

        When opening, connection_string takes precedence over connection_name.
        """
        session = self._attach_existing() or self._open_new()
        self._login(session)
        return session

    def _attach_existing(self) -> GuiSession | None:
        # find existing connections of the user
        connection = ConnectionManager.find_connection_by_user(
            self._username,
            connection_string=self._connection_string,
            connection_name=self._connection_name,
        )
        if not connection:
            return None

        logger.debug(
            f"Attaching to existing connection '{connection.Description}' for user: {self._username}"
        )
        return GuiSession(connection.Children(0))

    def _open_new(self) -> GuiSession:
        logger.info(
            f"No existing connection with given connection_string or connection_name found for user: {self._username}, opening a new one"
        )
        launch_saplogon(self._exe_path)
        return ConnectionManager.open_connection(
            connection_string=self._connection_string,
            connection_name=self._connection_name,
        )

    def _login(self, session: GuiSession):
        """Performs SAP login with provided credentials

        This method performs SAP login with the provided credentials, handling
        multiple login attempts, incorrect password attempts, terminating other
        sessions logged in other computers, and dismissing any additional popups
        that may appear after login.

        Raises
        ------
        SAPLoginError
            If the login process fails
        """
        user_field = session.find_by_id(
            SAPLoginScreenElements.username, raise_error=False
        )
        if not user_field:
            logger.debug("Login screen not found, assuming user is already logged in")
            return

        logger.debug(f"Logging in as: {self._username}")
        user_field.text = self._username
        session.find_by_id(SAPLoginScreenElements.password).text = self._password

        if self._client:
            session.find_by_id(SAPLoginScreenElements.client).text = self._client

        if self._language:
            session.find_by_id(SAPLoginScreenElements.language).text = self._language

        session.press_enter()

        # Check for immediate login errors (e.g invalid credentials)
        status = session.raise_for_status(
            message="Login failed", exception=SAPLoginError
        )

        # Handle multi-logon
        if status.text and "already logged on" in status.text.lower():
            self._handle_multi_logon(session)

        # Dismiss any other popups
        session.dismiss_popups(limit=10)

    def _handle_multi_logon(self, session: GuiSession):
        # TODO: If server supports multi-logon, allow user to multi-logon

        logger.debug("Multi-logon detected")
        if not self._terminate_other_sessions:
            raise SAPLoginError("User already logged on in some other session.")

        logger.debug("Terminating other sessions")
        try:
            rb = session.find_by_id(
                SAPLoginScreenElements.terminate_other_sessions_radio, raise_error=False
            )
            if rb:
                rb.select()
        except Exception as e:
            logger.warning(
                f"Could not find multi-logon terminate radio button, attempting to press enter key: {e}"
            )
        session.press_enter(1)
