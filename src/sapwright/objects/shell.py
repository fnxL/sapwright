from sapwright.objects.component import GuiComponent


class GuiShell(GuiComponent):
    @property
    def sub_type(self) -> str:
        """Additional type information to identify the control represented by the shell, for example Picture, TextEdit, GridView…"""
        return str(self._com.SubType)

    @property
    def drag_drop_supported(self) -> bool:
        """This property is True if the shell allows drag and drop operations."""
        return bool(self._com.DragDropSupported)

    @property
    def acc_description(self) -> str:
        """Accessibility description of the shell. This description can be used for shells that do not have a title element."""
        return str(self._com.AccDescription)

    @property
    def handle(self) -> int:
        """The window handle of the control that is connected to the GuiShell."""
        return self._com.Handle

    def select_context_menu_item(self, function_code: str):
        """Select an item from the control’s context menu."""
        self._com.SelectContextMenuItem(function_code)

    def select_context_menu_item_by_position(self, position_desc: str):
        """This method allows you to select a context menu item using the position of the item. It is therefore independent of the menu item text."""
        self._com.SelectContextMenuItemByPosition(position_desc)

    def select_context_menu_item_by_text(self, text: str):
        """Select a menu item of a context menu using the text of the item and possible higher level menus."""
        self._com.SelectContextMenuItemByText(text)

    # Aliases
    SubType = sub_type
    DragDropSupported = drag_drop_supported
    AccDescription = acc_description
    Handle = handle

    SelectContextMenuItem = select_context_menu_item
    SelectContextMenuItemByPosition = select_context_menu_item_by_position
    SelectContextMenuItemByText = select_context_menu_item_by_text
