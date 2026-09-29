import logging
from collections.abc import Iterator
from datetime import date, datetime
from typing import Any, ClassVar, Generic, TypeVar, cast, overload

from typing_extensions import override

from sapwright.exceptions import (
    SAPComboBoxOptionNotFound,
    SAPElementNotChangeable,
    SAPElementTypeMismatch,
)
from sapwright.types import GuiComponentType, VKey

logger = logging.getLogger(__name__)


class GuiComponent:
    # SAP SubType this wrapper represents, None matches anything
    _subtype: ClassVar[str | None] = None

    @override
    def __init_subclass__(
        cls,
        subtype: str | None = None,
    ):
        """Declares which SAP element a wrapper class represents.

        By default the class name is used as the SAP Type, e.g. GuiTableControl.
        Shell controls report Type "GuiShell" with the kind in SubType, so they
        only declare the subtype and inherit the type from their parent, e.g.
        ``class GuiGridView(GuiShell, sap_subtype="GridView")``.
        """
        cls._subtype = subtype

    @classmethod
    def matches(cls, com_object: Any) -> bool:
        """Return whether a SAP GUI COM object matches this class.

        A COM object normally matches when its ``Type`` attribute is equal to
        the class name. SAP ``GuiShell`` controls are an exception: they report
        ``Type == "GuiShell"`` and use the ``SubType`` attribute to identify the
        specific control type. Therefore, ``SubType`` is also checked when the
        attribute is available.

        Parameters
        ----------
        com_object : Any
            The SAP GUI COM object to check

        Returns
        -------
        bool
            True if the object's Type matches the class name or its SubType matches cls._subtype; otherwise, False.
        """
        own = com_object.Type == cls.__name__ or (
            com_object.SubType == cls._subtype
            if hasattr(com_object, "SubType")
            else False
        )
        # or any(sub.matches(com_object) for sub in cls.__subclasses__())
        return own

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
        child = getattr(self._com, "Children", None)
        if child is None:
            return None
        return GuiComponentCollection(child)

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

    def visualize(self, on: bool = True):
        """Calling this method of a component will display a red frame around the specified component if the parameter on is true."""
        self._com.Visualize(on)

    def set_focus(self):
        """This function can be used to set the focus onto an object. If a user interacts with SAP GUI, it moves the focus whenever the interaction is with a new object. Interacting with an object through the scripting component does not change the focus. There are some cases in which the SAP application explicitly checks for the focus and behaves differently depending on the focused object."""
        self._com.SetFocus()

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

    # Aliases
    Id = id
    Name = name
    Type = type
    Children = children
    Changeable = changeable
    DefaultTooltip = default_tooltip
    Height = height
    IconName = icon_name
    IsSymbolFont = is_symbol_font
    Left = left
    Modified = modified
    ScreenLeft = screen_left
    ScreenTop = screen_top
    Tooltip = tooltip
    Top = top
    Width = width
    Text = text

    SetFocus = set_focus
    sendVKey = send_vkey
    Visualize = visualize


ComponentT = TypeVar("ComponentT", bound=GuiComponent)
_InitT = TypeVar("_InitT", bound=GuiComponent)


def get_com_collection_item(com_collection: Any, index: int) -> Any:
    """Returns the COM object at the given index in the collection."""
    try:
        return com_collection.Item(index)
    except Exception:
        element_at = getattr(com_collection, "ElementAt", None)
        if element_at is not None:
            try:
                return element_at(index)
            except Exception as e:
                logger.debug(
                    f"Item(index) and ElementAt(index) failed: {e}, falling back to direct index access"
                )
        try:
            return com_collection(index)  # default member: collection(index)
        except Exception as e:
            logger.error(f"Failed to get element at index {index}: {e}")
        raise


class GuiComponentCollection(Generic[ComponentT]):
    """The GuiComponentCollection is used for collections elements such as the Children property of containers. Each element of the collection is an extension of GuiComponent."""

    @overload
    def __init__(
        self: "GuiComponentCollection[GuiComponent]",
        com_collection: Any,
        expected_type: None = None,
    ) -> None: ...

    @overload
    def __init__(
        self: "GuiComponentCollection[_InitT]",
        com_collection: Any,
        expected_type: type[_InitT],
    ) -> None: ...

    def __init__(
        self,
        com_collection: Any,
        expected_type: type[ComponentT] | None = None,
    ) -> None:
        self._com = com_collection
        self._expected_type = expected_type

    def __len__(self):
        return int(self._com.Count)

    def __getitem__(self, index: int) -> ComponentT:
        length = self._com.Count
        if index < 0:
            index += length

        if index < 0 or index >= length:
            raise IndexError(
                f"Index {index} out of range for collection of length {length}"
            )

        element = get_com_collection_item(self._com, index)

        expected_type = self._expected_type
        if expected_type is None:
            return cast(ComponentT, GuiComponent(element))

        if not expected_type.matches(element):
            raise SAPElementTypeMismatch(
                f"Element at index {index} is of type {element.Type}, expected {expected_type.__name__}"
            )

        return expected_type(element)

    def __iter__(self) -> Iterator[ComponentT]:
        """Iterate over all wrapped components."""
        for i in range(self._com.Count):
            yield self[i]
