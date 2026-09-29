from typing import overload

from sapwright.exceptions import SAPElementTypeMismatch
from sapwright.objects.collection import GuiComponentCollection
from sapwright.objects.component import ComponentT, GuiComponent
from sapwright.objects.scrollbar import GuiScrollbar


class GuiTableRow(GuiComponent):
    @property
    def count(self) -> int:
        """Number of cells in row"""
        return int(self._com.Count)

    @property
    def length(self) -> int:
        """Number of cells in row"""
        return int(self._com.Length)

    @property
    def selectable(self) -> bool:
        """This property is True if the row can be selected."""
        return bool(self._com.Selectable)

    @property
    def selected(self) -> bool:
        """This property is true if the row is selected."""
        return bool(self._com.Selected)

    @selected.setter
    def selected(self, value: bool) -> None:
        self._com.Selected = value

    def select_row(self):
        self.selected = True

    def deselect_row(self):
        self.selected = False

    def toggle_select_row(self):
        self.selected = not self.selected

    # Aliases
    Count = count
    Length = length
    Selectable = selectable
    Selected = selected


class GuiTableColumn(GuiComponent):
    @property
    def title(self) -> str:
        """This is the caption of the column/Column Header Title Text"""
        return str(self._com.Title)

    @property
    def selected(self) -> bool:
        """This property is true if the column is selected."""
        return bool(self._com.Selected)

    @selected.setter
    def selected(self, value: bool) -> None:
        self._com.Selected = value

    @property
    def count(self) -> int:
        """Number of cells in the column."""
        return int(self._com.Count)

    @property
    def fixed(self) -> bool:
        """Some columns may be fixed, which means that they will not be scrolled with the rest of the columns."""
        return bool(self._com.Fixed)

    @property
    def length(self) -> int:
        """Number of cells in the column."""
        return int(self._com.Length)

    # Aliases
    Title = title
    Count = count
    Length = length
    Fixed = fixed
    Selected = selected


class GuiTableControl(GuiComponent):
    @property
    def columns(self):
        return GuiComponentCollection(self._com.Columns, expected_type=GuiTableColumn)

    @property
    def current_col(self) -> int:
        """
        Zero-based index of the current column.

        Special values:
            -1: The focus is not inside the table control

            -2: The focus is either on the 'Select All' button or the 'Configuration' button. Check the ID of the respective object for more details

        Returns
        -------
        int
            Zero-based index of the current column
        """
        return int(self._com.CurrentCol)

    @property
    def current_row(self) -> int:
        """
        Zero-based index of the current row.

        Special values:
            -1: The focus is not inside the table control

            -2: The focus is on the column header or on the 'Configuration' button in the table control's title

        Returns
        -------
        int
            Zero-based index of the current row.
        """
        return int(self._com.CurrentRow)

    @property
    def horizontal_scrollbar(self):
        return GuiScrollbar(self._com.HorizontalScrollbar)

    @property
    def row_count(self) -> int:
        """Number of rows in the table. This includes invisible rows. For the number of visible rows the property VisibleRowCount is available."""
        return int(self._com.RowCount)

    @property
    def rows(self):
        return GuiComponentCollection(self._com.Rows, expected_type=GuiTableRow)

    @property
    def table_field_name(self) -> str:
        """The name property of the table control contains the ABAP program name in addition to the plain field name. This property contains just the field name."""
        return str(self._com.TableFieldName)

    @property
    def vertical_scrollbar(self):
        return GuiScrollbar(self._com.VerticalScrollbar)

    @property
    def visible_row_count(self) -> int:
        """Number of visible rows in the table. For the number of all rows the property RowCount is available."""
        return int(self._com.VisibleRowCount)

    def select_all_columns(self):
        """This function can be used for table controls with a button that allows, to select all columns in one step."""
        self._com.SelectAllColumns()

    def deselect_all_columns(self):
        """This function can be used for table controls with a button that allows, to deselect all columns in one step."""
        self._com.DeselectAllColumns()

    def reorder_table(self, permutation: str):
        """The parameter permutation describes a new ordering of the columns. For example “0 2 1” will move the third column to second position.
        Note:
            - Columns start at index 0
            - Fixed columns cannot be reordered"""
        self._com.ReorderTable(permutation)

    def get_absolute_row(self, index: int) -> GuiTableRow:
        """Unlike the rows collection, the indexing supported by this function does not reset the index after scrolling, but counts the rows starting with the first row with respect to the first scroll position. If the selected row is not currently visible then an exception is raised."""
        return GuiTableRow(self._com.GetAbsoluteRow(index))

    @overload
    def get_cell(
        self, row: int, column: int, expected_type: type[ComponentT]
    ) -> ComponentT: ...

    @overload
    def get_cell(
        self, row: int, column: int, expected_type: None = None
    ) -> GuiComponent: ...

    def get_cell(
        self, row: int, column: int, expected_type: type[GuiComponent] | None = None
    ) -> GuiComponent:
        """This method returns a given table cell. It is more efficient than accessing a single cell using the rows or columns collections. Syntax


        Parameters
        ----------
        row : int
            Zero-based index of the row
        column : int
            Zero-based index of the column
        expected_type : type[GuiComponent] | None, optional
            Wrapper class to return, e.g. GuiTableControl. The element's SAP type
            must match the class or one of its subclasses. By default a plain
            GuiComponent is returned.

        Returns
        -------
        GuiComponent
            The table cell

        Raises
        ------
        SAPElementTypeMismatch
            If the element's type does not match expected_type

        """
        if expected_type is None:
            return GuiComponent(self._com.GetCell(row, column))

        cell = self._com.GetCell(row, column)

        if not expected_type.matches(cell):
            raise SAPElementTypeMismatch(
                f"Element '{cell.Id}' is of type {cell.Type}, expected {expected_type.__name__}"
            )

        return expected_type(cell)

    # Aliases
    Columns = columns
    Rows = rows
    CurrentCol = current_col
    CurrentRow = current_row
    HorizontalScrollbar = horizontal_scrollbar
    VerticalScrollbar = vertical_scrollbar
    RowCount = row_count
    VisibleRowCount = visible_row_count
    TableFieldName = table_field_name

    SelectAllColumns = select_all_columns
    DeselectAllColumns = deselect_all_columns
    ReorderTable = reorder_table
    GetAbsoluteRow = get_absolute_row
    GetCell = get_cell
