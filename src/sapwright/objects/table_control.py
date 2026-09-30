from collections.abc import Iterator
from typing import Any, overload

from sapwright.exceptions import SAPElementTypeMismatch
from sapwright.objects.component import ComponentT, GuiComponent, GuiComponentCollection
from sapwright.objects.scrollbar import GuiScrollbar
from sapwright.objects.session import GuiSession


class GuiTableRow(GuiComponent):
    def __getitem__(self, index: int) -> GuiComponent:
        return GuiComponent(self._com[index])

    def __iter__(self) -> Iterator[GuiComponent]:
        for i in range(self.count):
            yield self[i]

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
    def __init__(
        self,
        com_object: Any,
        session: "GuiSession | None" = None,
        control_id: str | None = None,
    ):
        super().__init__(com_object, session, control_id)
        self._headers = self.get_table_headers()

    @property
    def headers(self) -> dict[str, int]:
        """Mapping of table headers to header index"""
        return self._headers

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
        """Unlike the rows collection, the indexing supported by this function does not reset the index after scrolling, but counts the rows starting with the first row with respect to the first scroll position. If the selected row is not currently visible then it will try to go to the scroll position, refresh the table and return the row."""
        try:
            return GuiTableRow(self._com.GetAbsoluteRow(index))
        except Exception:
            # This is expected if the row is not visible
            # try to go to the scroll position
            self.vertical_scrollbar.position = index
            # refresh the table
            self.refresh()

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
        self,
        row: int,
        column: int,
        expected_type: type[GuiComponent] | None = None,
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

    def refresh(self):
        """Refreshes the table control. This method is useful when the table has been paginated, or scrolled, the old reference to table control com object is no longer valid. This method will refresh the table control and return the new reference to the com object."""
        if not self._session:
            return

        if not self._control_id:
            return

        self._com = self._session._com.FindById(self._control_id, False)

    def get_table_headers(
        self,
        headers: list[str] | None = None,
        exclude_headers: list[str] | None = None,
    ) -> dict[str, int]:
        """
        Creates a mapping of table headers (lowercase by default) to header index

        Parameters
        ----------
        headers : list[str] | None
            List of headers to include. If None, all headers of the table are included, by default None.
        exclude_headers : list[str] | None
            List of headers to exclude. If None, no headers are excluded, by default None.
        lowercase : bool, optional
            Whether to return the lowercase headers, by default True

        Returns
        -------
        dict[str, int]
            Mapping of header name to header index.
        """
        if headers and exclude_headers:
            raise ValueError("Cannot specify both headers and exclude_headers")

        full_map: dict[str, int] = {}
        for i, col in enumerate(self.columns):
            title = col.title.strip().lower()
            if title:
                full_map[title] = i

        if headers:
            whitelist = {c.lower() for c in headers}
            return {title: idx for title, idx in full_map.items() if title in whitelist}

        if exclude_headers:
            blacklist = {c.lower() for c in exclude_headers}
            return {
                title: idx for title, idx in full_map.items() if title not in blacklist
            }
        return full_map

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
