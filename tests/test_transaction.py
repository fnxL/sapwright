import sys

import pytest

from sapwright.exceptions import SAPTransactionError
from sapwright.objects import GuiSession

pytestmark = pytest.mark.skipif(
    sys.platform != "win32", reason="SAP GUI COM is Windows-only"
)

def test_start_transaction(session: GuiSession):
    session.start_transaction("va01")
    assert "create sales order" in session.title().lower()


def test_start_transaction_invalid(session: GuiSession):
    with pytest.raises(SAPTransactionError):
        session.start_transaction("invalid")


def test_end_transaction(session: GuiSession):
    session.start_transaction("va01")
    session.end_transaction()
    assert "sap easy access" in session.title().lower()
