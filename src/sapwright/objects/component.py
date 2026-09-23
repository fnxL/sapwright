import logging
from datetime import date, datetime
from typing import Any

from typing_extensions import override

from sapwright.exceptions import SAPComboBoxOptionNotFound, SAPElementNotChangeable
from sapwright.types import GuiComponentType, VKey

logger = logging.getLogger(__name__)


class GuiComponent:
    def __init__(self, com_object: Any):
        self._com = com_object

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to the underlying SAP element."""
        # Private attributes are never delegated, so a missing `_com` can't recurse
        if name.startswith("_"):
            raise AttributeError(name)
        return getattr(self._com, name)

    @override
    def __setattr__(self, name: str, value: Any):
        """
        Set attributes on this class instance, or delegate to the underlying COM element if the attribute does not exist on the class.
        """
        if name.startswith("_") or hasattr(type(self), name):
            object.__setattr__(self, name, value)
        else:
            # Fallback
            setattr(self._com, name, value)

    @property
    def id(self) -> str:
        return str(self._com.Id)

    @property
    def name(self) -> str:
        return str(self._com.Name)

    @property
    def type(self) -> str:
        return str(self._com.Type)

    @property
    def children(self):
        return getattr(self._com, "Children", None)

    @property
    def changeable(self) -> bool:
        return bool(self._com.Changeable)

    @property
    def default_tooltip(self) -> str:
        return str(self._com.DefaultTooltip)

    @property
    def height(self) -> int:
        return int(self._com.Height)

    @property
    def icon_name(self) -> str:
        return str(self._com.IconName)

    @property
    def is_symbol_font(self) -> bool:
        return bool(self._com.IsSymbolFont)

    @property
    def left(self) -> int:
        return int(self._com.Left)

    @property
    def modified(self) -> bool:
        return bool(self._com.Modified)

    @property
    def screen_left(self) -> int:
        return int(self._com.ScreenLeft)

    @property
    def screen_top(self) -> int:
        return int(self._com.ScreenTop)

    @property
    def tooltip(self) -> str:
        return str(self._com.Tooltip)

    @property
    def top(self) -> int:
        return int(self._com.Top)

    @property
    def width(self) -> int:
        return int(self._com.Width)

    @property
    def text(self) -> str:
        return self.get_text()

    @text.setter
    def text(self, value: Any):
        _ = self.set_text(value, raise_error=True)

    def set_text(
        self,
        value: Any,
        raise_error: bool = False,
        date_format: str = "%d.%m.%Y",
        set_focus: bool = False,
        strip: bool = False,
    ) -> bool:
        """Sets the text of the element. Dates are formatted using date_format,
        combobox entries are selected by text, and text longer than the field's
        max length is truncated.

        Returns
        -------
        bool
            True if the text was set, False if the element is not changeable

        Raises
        ------
        SAPElementNotChangeable
            If the element is not changeable and raise_error is True
        """
        if not self.changeable:
            msg = f"Element of type {self.type} is not changeable: {self.id}"
            logger.warning(msg)
            if raise_error:
                raise SAPElementNotChangeable(msg)
            return False

        if isinstance(value, (date, datetime)):
            value = value.strftime(date_format)

        value = str(value)
        if strip:
            value = value.strip()

        if self.type == GuiComponentType.GuiComboBox:
            return self._select_combobox_entry(value)

        max_length = getattr(self._com, "MaxLength", None)
        if max_length:
            value = value[:max_length]

        if set_focus:
            self.set_focus()

        self._com.Text = value
        return True

    def get_text(self, strip: bool = False) -> str:
        """Gets the text property of the element

        Parameters
        ----------
        strip : bool, optional
            Whether to strip the leading and trailing whitespaces of the text, by default False

        Returns
        -------
        str
        """
        text = str(getattr(self._com, "Text", ""))
        return text.strip() if strip else text

    def click(self) -> bool:
        """Clicks/presses/selects/check/unchecks the SAP element based on its type if its clickable.

        This method performs the appropriate action for the following element types:
            - GuiButton: Presses the button
            - GuiTab: Selects the tab
            - GuiCheckBox: Toggles the checkbox
            - GuiRadioButton: Selects the radio button

        Returns
        -------
        bool
            True if the action was successful, False otherwise
        """
        # Try standard methods
        if hasattr(self._com, "press"):
            self._com.press()
            return True

        if hasattr(self._com, "select"):
            self._com.select()
            return True

        # Checkboxes  use 'selected' property
        if hasattr(self._com, "selected"):
            self._com.selected = not self._com.selected
            return True

        logger.warning(f"Element: {self.name} of type {self.type} is not clickable")
        return False

    def press(self):
        """Alias for click"""
        return self.click()

    def select(self):
        """Alias for click"""
        return self.click()

    def send_vkey(self, vkey: VKey | int):
        """Sends a virtual key to this element (usually a window)."""
        self._com.sendVKey(int(vkey))

    def sendVKey(self, vkey: VKey | int):
        """Alias for send_vkey"""
        return self.send_vkey(vkey)

    def visualize(self, on: bool = True):
        """Calling this method of a component will display a red frame around the specified component if the parameter on is true."""
        self._com.Visualize(on)

    def set_focus(self):
        """This function can be used to set the focus onto an object. If a user interacts with SAP GUI, it moves the focus whenever the interaction is with a new object. Interacting with an object through the scripting component does not change the focus. There are some cases in which the SAP application explicitly checks for the focus and behaves differently depending on the focused object."""
        self._com.SetFocus()

    def setFocus(self):
        """Alias for set_focus"""
        return self.set_focus()

    def _select_combobox_entry(self, text: str) -> bool:
        """
        Selects a ComboBox entry by matching option's text (case-insensitive)

        Parameters
        ----------
        text : str
            Text of the option to select

        Returns
        -------
        bool
            True if selected

        Raises
        ------
        SAPComboBoxOptionNotFound
            If no entry matches the text
        """
        target = text.strip().lower()
        for entry in self._com.Entries:
            if str(entry.Value).strip().lower() == target:
                self._com.Key = entry.Key
                return True

        raise SAPComboBoxOptionNotFound(
            f"Option '{text}' not found in ComboBox {self.name} with id: {self.id}"
        )
