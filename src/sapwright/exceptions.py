class SAPGuiError(Exception):
    """Base class for all SAP GUI related errors"""


class SAPLogonError(SAPGuiError):
    """Raised when SAP Logon fails to launch"""


class SAPConnectionError(SAPGuiError):
    """Raised when a connection to SAP Logon fails"""


class SAPScriptingDisabled(SAPGuiError):
    """Raised when SAP GUI Scripting is disabled by server"""


class SAPElementNotFound(SAPGuiError):
    """Raised when a SAP GUI element is not found"""


class SAPElementNotChangeable(SAPGuiError):
    """Raised when attempting to modify a read-only element."""


class SAPComboBoxOptionNotFound(SAPGuiError):
    """Raised when a specified option is not available in a ComboBox."""


class SAPStatusBarError(SAPGuiError):
    """Raised when there is an error in the status bar."""


class SAPTransactionError(SAPGuiError):
    """Raised when a transaction fails to start or encounters a critical error."""


class SAPLoginError(SAPGuiError):
    """Raised when the login process fails."""


class SAPElementTypeMismatch(SAPGuiError):
    """Raised when the element type does not match the expected type."""


class SAPTableConfigurationError(SAPGuiError):
    """Raised when there is a mismatch or error in table configuration/population."""
