class SAPGuiError(Exception):
    """Base class for all SAP GUI related errors"""


class SAPLogonError(SAPGuiError):
    """Raised when SAP Logon fails to launch"""
