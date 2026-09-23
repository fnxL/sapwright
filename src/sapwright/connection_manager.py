import logging
from typing import Any

from sapwright._utils import get_scripting_engine
from sapwright.exceptions import SAPConnectionError, SAPLogonError, SAPScriptingDisabled
from sapwright.objects import GuiSession

logger = logging.getLogger(__name__)


def _normalize(value: object) -> str:
    return str(value).strip().lower()


def _matches(
    connection: Any, connection_string: str | None, connection_name: str | None
) -> bool:
    """Match by connection string (substring) if given, otherwise by description."""
    if connection_string:
        # connection_string returned by SAP logon contains a lot more text and other details
        # we would only want to check for a substring match
        return connection_string.lower() in str(connection.ConnectionString).lower()

    # Case-insensitive connection name matching
    return _normalize(connection.Description) == _normalize(connection_name)


class ConnectionManager:
    @staticmethod
    def find_connection_by_user(
        username: str,
        connection_string: str | None = None,
        connection_name: str | None = None,
    ) -> Any | None:
        """Check if a connection for the specified user is already open.

        Returns
        -------
        object or None
            The underlying native GuiConnection COM object if a matching connection
            has a session logged in as the user, otherwise None

        Raises
        ------
        ValueError
            If neither connection_string nor connection_name is provided
        SAPScriptingDisabled
            If SAP GUI Scripting is disabled by the server
        """
        if not connection_string and not connection_name:
            raise ValueError("connection_string or connection_name must be provided.")

        application = get_scripting_engine()
        if application is None:
            return None

        user = _normalize(username)
        for i in range(application.Children.Count):
            connection = application.Children(i)
            if connection.DisabledByServer:
                raise SAPScriptingDisabled(
                    "SAP GUI Scripting is disabled by server. Contact your SAP basis team to enable it."
                )
            if not _matches(connection, connection_string, connection_name):
                continue

            sessions = connection.Children
            for j in range(sessions.Count):
                if _normalize(sessions(j).Info.User) == user:
                    return connection

        return None

    @staticmethod
    def open_connection(
        connection_string: str | None = None,
        connection_name: str | None = None,
    ) -> GuiSession:
        """Open a new connection and return its first session.

        connection_string takes precedence over connection_name.

        Raises
        ------
        SAPLogonError
            If SAP Logon is not running
        SAPConnectionError
            If the connection could not be opened
        """
        application = get_scripting_engine()
        if application is None:
            raise SAPLogonError("SAP Logon is not running")

        try:
            if connection_string:
                connection = application.OpenConnectionByConnectionString(
                    connection_string, True, True
                )
            else:
                connection = application.OpenConnection(connection_name, True, True)
            return GuiSession(connection.Children(0))
        except Exception as e:
            msg = f"Failed to open SAP connection: {e}"
            logger.error(msg)
            raise SAPConnectionError(msg) from e
