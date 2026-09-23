import logging

from typing_extensions import override

from sapwright.exceptions import SAPElementNotFound, SAPTransactionError
from sapwright.models import SessionInfo, StatusBarMsg
from sapwright.objects.component import GuiComponent
from sapwright.types import GuiComponentType, VKey

logger = logging.getLogger(__name__)
STATUS_BAR_CTRL_ID = "wnd[0]/sbar"


class GuiSession(GuiComponent):
    @property
    def busy(self) -> bool:
        return bool(self._com.Busy)

    @property
    def error_list(self):
        return self._com.ErrorList

    @property
    def info(self) -> SessionInfo:
        """Information about the session, such as user, client and transaction."""
        info = self._com.Info
        return SessionInfo(
            application_server=info.ApplicationServer,
            client=info.Client,
            codepage=info.Codepage,
            flushes=info.Flushes,
            group=info.Group,
            gui_codepage=info.GuiCodepage,
            i18n_mode=info.I18nMode,
            interpretation_time=info.InterpretationTime,
            is_low_speed_connection=info.IsLowSpeedConnection,
            language=info.Language,
            message_server=info.MessageServer,
            program=info.Program,
            response_time=info.ResponseTime,
            round_trips=info.RoundTrips,
            screen_number=info.ScreenNumber,
            scripting_mode_read_only=info.ScriptingModeReadOnly,
            scripting_mode_recording_disabled=info.ScriptingModeRecordingDisabled,
            session_number=info.SessionNumber,
            system_name=info.SystemName,
            system_session_id=info.SystemSessionId,
            transaction=info.Transaction,
            ui_guideline=info.UI_GUIDELINE,
            user=info.User,
        )

    @property
    def is_active(self) -> bool:
        """True if the session window is active."""
        return bool(self._com.IsActive)

    @property
    def is_listbox_active(self) -> bool:
        """True if a listbox is currently open (for a GuiComboBox)."""
        return bool(self._com.IsListboxActive)

    @property
    def listbox_curr_entry(self) -> int:
        """The index of the currently selected listbox entry."""
        return int(self._com.ListboxCurrEntry)

    @property
    def passport_system_id(self) -> str:
        """The system ID. Part of the passport information."""
        return str(self._com.PassportSystemId)

    @property
    def passport_pre_system_id(self) -> str:
        """The pre-system ID. Part of the passport information."""
        return str(self._com.PassportPreSystemId)

    @property
    def passport_transaction_id(self) -> str:
        """The unique ID of the transaction. Part of the passport information."""
        return str(self._com.PassportTransactionId)

    @property
    def progress_percent(self) -> int:
        """The percentage displayed by the SAP GUI progress indicator."""
        return int(self._com.ProgressPercent)

    @property
    def progress_text(self) -> str:
        """The text displayed by the progress indicator."""
        return str(self._com.ProgressText)

    @property
    def show_dropdown_keys(self) -> bool:
        """If True, dropdowns show the keys of entries as well as their text."""
        return bool(self._com.ShowDropdownKeys)

    @show_dropdown_keys.setter
    def show_dropdown_keys(self, value: bool):
        self._com.ShowDropdownKeys = value

    @property
    def test_tool_mode(self) -> int:
        """During internal tests some aspects of the user interface proved to be difficult to handle with test tools using the Scripting API to automate SAP GUI. For this reason a special mode has been added in which the following changes are administered.
            - While success (S), warning (W) and error (E) messages are always displayed in the status bar, information (I) and abort (A) messages are displayed as pop-up windows unless testToolMode is set.
            - The update mode of the application server is changed to immediate mode for the connection.
            - System messages are ignored so that they do not interrupt the recording or playback of scripts.

        Currently only the following values are allowed for this property:

            - 0: Disable testToolMode
            - 1: Enable testToolMode
        """
        return int(self._com.TestToolMode)

    @test_tool_mode.setter
    def test_tool_mode(self, value: int):
        if value not in (0, 1):
            raise ValueError("test_tool_mode must be 0 or 1")
        self._com.TestToolMode = value

    def find_by_id(self, id: str, raise_error: bool = True) -> GuiComponent | None:
        element = self._com.findById(id, False)  # False = don't raise error
        if element is None:
            logger.debug("Element not found", extra={"id": id, "parent": self.id})
            if raise_error:
                raise SAPElementNotFound(f"Element not found: {id}")
            return None

        return GuiComponent(element)

    def findById(self, id: str, raise_error: bool = True):
        """Alias for find_by_id"""
        return self.find_by_id(id, raise_error)

    def create_session(self):
        """This function opens a new session, which is then visualized by a new main window. This resembles the “/o” command that can be executed from the command field."""
        return self._com.CreateSession()

    def get_vkey_description(self, vkey: VKey | int) -> str:
        """Translates a VKey number into readable text, e.g. 0 -> "Enter"."""
        return str(self._com.GetVKeyDescription(int(vkey)))

    def lock_session_ui(self):
        """Locks the session so no user interaction is possible until unlock_session_ui is called."""
        self._com.LockSessionUI()

    def unlock_session_ui(self):
        """Unlocks the session after it was locked using lock_session_ui."""
        self._com.UnlockSessionUI()

    def send_command(self, command: str):
        """Executes a command string, as if entered in the command field."""
        self._com.SendCommand(command)

    def start_transaction(self, tcode: str):
        """Starts a transaction. Same as send_command("/n<tcode>").

        Raises
        ------
        SAPTransactionError
            If the transaction code does not exist
        """
        self._com.StartTransaction(tcode)

        # Check if tcode was valid
        status = self.statusbar_msg()
        if "does not exist" in status.text:
            raise SAPTransactionError(
                f"Transaction code: {tcode} failed: {status.text}"
            )

    def end_transaction(self):
        """Ends the current transaction. Same as send_command("/n")."""
        self._com.EndTransaction()

    def close(self, window_depth: int = 10):
        """Closes the current session, confirming the logoff dialog if one appears."""
        self.send_command("/i")

        # If this is not the last session, the session closes here immediately.
        # At this point the COM object becomes invalid so find_by_id raises an error
        try:
            # The confirmation dialog may be in wnd[1], wnd[2] and so on.
            for i in range(1, window_depth + 1):
                button = self._com.findById(f"wnd[{i}]/usr/btnSPOP-OPTION1", False)
                if button:
                    button.press()
                    return
        except Exception as e:
            # This is expected if the session is not the last one.
            logger.debug(f"Session closed without confirmation dialog: {e}")

    @override
    def send_vkey(
        self,
        vkey: VKey | int,
        window_index: int = 0,
        repeat_count: int = 1,
    ):
        """Sends a VKey to a specific SAP window

        Parameters
        ----------
        vkey : VKey | int
            The virtual key to send
        window_index : int, optional
            Index of the SAP window, by default 0
        repeat_count : int, optional
            Number of times to send the key, by default 1

        Raises
        ------
        SAPElementNotFound
            If the window is not found
        """
        wnd_id = f"wnd[{window_index}]"
        wnd = self._com.findById(wnd_id, False)
        if not wnd:
            raise SAPElementNotFound(f"Window {wnd_id} not found to send key.")

        for _ in range(repeat_count):
            wnd.sendVKey(int(vkey))

    @override
    def sendVKey(
        self,
        vkey: VKey | int,
        window_index: int = 0,
        repeat_count: int = 1,
    ):
        """Alias for send_vkey"""
        return self.send_vkey(vkey, window_index, repeat_count)

    def press_enter(self, window_index: int = 0, repeat_count: int = 1):
        """Sends the ENTER key to a window."""
        return self.send_vkey(VKey.ENTER, window_index, repeat_count)

    def dismiss_popups(
        self,
        key: VKey = VKey.ENTER,
        window_index: int = 1,
        limit: int | None = None,
    ) -> int:
        """Dismisses popup dialogs by sending a key until none are left or limit is reached.

        Parameters
        ----------
        key : VKey, optional
            The key to send to dismiss the popup, by default VKey.ENTER
        window_index : int, optional
            The index of the popup dialog window, by default 1
        limit : int | None, optional
            The maximum number of popups to dismiss, by default None (no limit)

        Returns
        -------
        int
            Number of popups dismissed
        """
        window_id = f"wnd[{window_index}]"
        count = 0
        while limit is None or count < limit:
            wnd = self._com.findById(window_id, False)
            if (
                not wnd
                or wnd.Type != GuiComponentType.GuiModalWindow
                or not wnd.IsPopupDialog
            ):
                break

            logger.debug(
                f"Dismissing popup: title={wnd.Text!r} text={wnd.PopupDialogText!r}"
            )
            wnd.sendVKey(int(key))
            count += 1

        return count

    def statusbar_msg(self) -> StatusBarMsg:
        """Retrieves the current status bar message."""
        sbar = self._com.findById(STATUS_BAR_CTRL_ID, False)
        if not sbar:
            raise SAPElementNotFound("Status bar not found")

        return StatusBarMsg(
            id=sbar.MessageId,
            number=sbar.MessageNumber,
            text=sbar.Text,
            type=sbar.MessageType,
            has_longtext=sbar.MessageHasLongText,
            is_popup=sbar.MessageAsPopup,
        )
