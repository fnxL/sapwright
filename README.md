# Sapwright

A typed, object-oriented Python wrapper around the SAP GUI Scripting API. Get IDE autocomplete, static type checking, and readable code instead of loosely-typed COM objects.

```python
from sapwright import Sapwright

with Sapwright(username="jdoe", password="secret", connection_name="PRD") as session:
    session.start_transaction("va01")
    session.find_by_id("wnd[0]/usr/ctxtVBAK-AUART").text = "ZWEO"
    session.press_enter()
```

## Features

- **Typed API** - full autocomplete and static typing
- **Hands-off connection management** - launches SAP Logon, reuses an open connection, logs in, handles multi-logon and forced password-change prompts, and closes cleanly on exit.
- **Smart elements** - `.text` handles dates, comboboxes and max length; `.click()` does the right thing for buttons, tabs, checkboxes and radios.
- **Tables made easy** - header lookup, iterable rows, absolute row indexing, row/column selection, scrolling.
- **Specific exceptions** - a clear `SAPGuiError` hierarchy instead of raw COM errors.
- **Recorder-friendly** - PascalCase aliases and COM attribute delegation keep recorded SAP scripts working.

## Requirements

- Windows (SAP GUI Scripting is COM-based)
- Python 3.11+
- SAP Logon 770+ with scripting enabled

## Installation

```bash
pip install sapwright
# or
uv add sapwright
```

## SAP GUI setup

In **SAP GUI Options**:

1. **Accessibility & Scripting → Scripting**
   - Check *Enable Scripting*
   - Uncheck *Notify when a script attaches to SAP GUI*
   - Uncheck *Notify when a script opens a connection*
2. **Security → Security Configuration**
   - Set *Status* to *Disabled*

## Usage

### Connecting

The context manager connects on enter and closes the session on exit either using connection_name or connection_string [(click here to read docs)](https://help.sap.com/docs/sap_gui_for_windows/b47d018c3b9b45e897faf66a6c0885a8/5704456a1fbd43139311dab0e1175060.html)

```python
with Sapwright(
    username="jdoe",
    password="secret",
    connection_name="PRD",  # or connection_string="..."
    client=100,
    language="EN",
) as session:
    ...
```

For finer control, call `connect()` and `close_connection()` yourself:

```python
sap = Sapwright(username="jdoe", password="secret", connection_name="PRD")
session = sap.connect()
try:
    session.start_transaction("va01")
finally:
    session.close_connection()
```

If a password change is forced at login, pass a `password_generator`. Make sure your password_generator returns a valid string. This handles automatic password management/reset.

```python
Sapwright(..., password_generator=lambda: date.today().strftime("%b@%Y"))
```

### Finding elements

```python
from sapwright.objects import GuiTableControl

field = session.find_by_id("wnd[0]/usr/ctxtVBAK-AUART")
field.text = "ZWEO"

# Typed lookup: validates the SAP element type and returns a typed wrapper
table = session.find_by_id("wnd[0]/usr/tblITEMS", expected_type=GuiTableControl)

# Optional lookup: returns None instead of raising
ok = session.find_by_id("wnd[1]/usr/btnSPOP-OPTION1", raise_error=False)
if ok:
    ok.click()
```

### Tables

```python
print(table.headers)  # {"material": 0, "quantity": 1, ...}
print(table.row_count, table.visible_row_count)

print(
    table.vertical_scrollbar.maximum
)  # You can also use this to find number of rows in the table, Often find this more accurate than table.row_count

for row in table.rows:
    for cell in row:
        print(cell.name, cell.text)

col = table.headers["material"]  # header keys are lowercase
print(table.get_cell(0, col).text)
table.set_cell_text(0, col, "MAT-100")
row = table.get_absolute_row(250)  # scrolls if the row isn't visible
```

### Status bar, keys and popups

```python
from sapwright.exceptions import SAPTransactionError
from sapwright.types import VKey

try:
    session.start_transaction("bad_tcode")
except SAPTransactionError as e:
    print(e)

msg = session.statusbar_msg()
if msg.type == "E":
    print(f"Error {msg.number}: {msg.text}")

session.raise_for_status(message="Order creation failed")  # raises on type "E"

session.send_vkey(VKey.CTRL_S)  # save
session.dismiss_popups(limit=5)  # clear popup dialogs
```

---

## API reference

### `Sapwright`

`from sapwright import Sapwright`

```python
Sapwright(
    username: str,
    password: str,
    connection_string: str | None = None,
    connection_name: str | None = None,
    client: int | None = None,
    language: str | None = None,
    terminate_other_sessions: bool = True,
    exe_path: str | Path | None = None,
    password_generator: Callable[[], str] | None = None,
)
```

One of `connection_string` or `connection_name` is required (`ValueError` otherwise). When opening a new connection, `connection_string` wins. If SAP Logon isn't running it is launched from the registry path, or from `exe_path`.

| Parameter                    | Description                                                                                                |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `terminate_other_sessions` | On the "already logged on" prompt, terminate other sessions. If`False`, raises `SAPLoginError`.        |
| `password_generator`       | Called to produce a new password when SAP forces a change. Defaults to month and year, e.g.`"Jan@2026"`. |

| Method                       | Description                                                               |
| ---------------------------- | ------------------------------------------------------------------------- |
| `connect() -> GuiSession`  | Attach to the user's existing connection, or open a new one, then log in. |
| `close_connection()`       | Close the SAP connection and all its sessions.                            |
| `__enter__` / `__exit__` | Call`connect()`, then close the session on exit.                        |

### `GuiComponent`

Wrapper for any SAP GUI element. Unknown attributes are delegated to the underlying COM object.

**Properties:** `id`, `name`, `type`, `children`, `changeable`, `modified`, `tooltip`, `default_tooltip`, `icon_name`, `is_symbol_font`, `width`, `height`, `left`, `top`, `screen_left`, `screen_top`, and `text` (get/set).

| Method                                                                                               | Description                                                                                                                                                                                      |
| ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `set_text(value, raise_error=False, date_format="%d.%m.%Y", set_focus=False, strip=False) -> bool` | Set text. Formats dates, selects combobox entries by visible text, truncates to max length. Returns`False` if not changeable, or raises `SAPElementNotChangeable` when `raise_error=True`. |
| `get_text(strip=False) -> str`                                                                     | Read text, optionally stripped.                                                                                                                                                                  |
| `click() -> bool`                                                                                  | Press, select, or toggle based on element type (button, tab, checkbox, radio).                                                                                                                   |
| `press()` / `select()`                                                                           | Explicit press / select.                                                                                                                                                                         |
| `send_vkey(vkey)`                                                                                  | Send a virtual key to the element.                                                                                                                                                               |
| `set_focus()`                                                                                      | Focus the element.                                                                                                                                                                               |
| `visualize(on=True)`                                                                               | Draw or remove a red highlight frame.                                                                                                                                                            |
| `GuiComponent.matches(com_object) -> bool`                                                         | Class method; whether a COM object fits this wrapper.                                                                                                                                            |

### `GuiSession`

Returned by `Sapwright.connect()`. Extends `GuiComponent`.

**Elements and navigation**

| Method                                                      | Description                                                                                                                           |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `find_by_id(id, raise_error=True, *, expected_type=None)` | Find an element. Raises`SAPElementNotFound` or `SAPElementTypeMismatch`. Returns `None` if not found and `raise_error=False`. |
| `start_transaction(tcode)`                                | Start a transaction (like`/n<tcode>`). Raises `SAPTransactionError` if it doesn't exist.                                          |
| `end_transaction()`                                       | End the current transaction (like`/n`).                                                                                             |
| `send_command(command)`                                   | Run a command as if typed in the command field.                                                                                       |
| `title() -> str`                                          | Title bar text.                                                                                                                       |
| `maximize()`                                              | Maximize the main window.                                                                                                             |

**Keys and popups**

| Method                                                                | Description                                          |
| --------------------------------------------------------------------- | ---------------------------------------------------- |
| `send_vkey(vkey, window_index=0, repeat_count=1)`                   | Send a`VKey` to a window.                          |
| `press_enter(window_index=0, repeat_count=1)`                       | Send Enter.                                          |
| `dismiss_popups(key=VKey.ENTER, window_index=1, limit=None) -> int` | Dismiss stacked popups; returns the count dismissed. |

**Status bar**

| Method                                                                          | Description                                                        |
| ------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| `statusbar_msg() -> StatusBarMsg`                                             | Current status bar message.                                        |
| `raise_for_status(message=None, exception=SAPStatusBarError) -> StatusBarMsg` | Raise if the message type is`"E"`; otherwise return the message. |

**Session lifecycle**

| Method                                            | Description                                                          |
| ------------------------------------------------- | -------------------------------------------------------------------- |
| `create_session()`                              | Open a new session (like`/o`).                                     |
| `close(window_depth=10)`                        | Close this session, confirming the logoff dialog.                    |
| `close_connection()` / `close_all_sessions()` | Close the connection and all its sessions. Unsaved changes are lost. |
| `lock_session_ui()` / `unlock_session_ui()`   | Block or allow user interaction.                                     |
| `get_vkey_description(vkey) -> str`             | Readable name of a virtual key.                                      |

**Properties:** `info` (`SessionInfo`), `busy`, `is_active`, `error_list`, `progress_percent`, `progress_text`, `is_listbox_active`, `listbox_curr_entry`, `passport_system_id`, `passport_pre_system_id`, `passport_transaction_id`, `show_dropdown_keys` (get/set), `test_tool_mode` (get/set).

### `GuiTableControl`

`from sapwright.objects import GuiTableControl`

**Properties:** `headers` (lowercase title → column index), `rows`, `columns`, `row_count`, `visible_row_count`, `current_row`, `current_col`, `horizontal_scrollbar`, `vertical_scrollbar`, `table_field_name`.

| Method                                                                                                        | Description                                                               |
| ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `get_cell(row, column, expected_type=None)`                                                                 | Get a cell by zero-based indexes, optionally typed.                       |
| `set_cell_text(row, column, value, strip=False, date_format="%d.%m.%Y", set_focus=False, raise_error=True)` | Set a cell's text.                                                        |
| `get_absolute_row(index) -> GuiTableRow`                                                                    | Row by absolute index, independent of scroll position. Scrolls if needed. |
| `select_all_columns()` / `deselect_all_columns()`                                                         | Column selection.                                                         |
| `reorder_table(permutation)`                                                                                | Reorder columns (e.g.`"1 0 2"`). Fixed columns can't move.              |
| `get_table_headers() -> dict[str, int]`                                                                     | Rebuild the header map.                                                   |
| `refresh()`                                                                                                 | Re-resolve a stale table reference after scrolling or pagination.         |

**`GuiTableRow`** — iterable and indexable over its cells. Properties: `count`, `length`, `selectable`, `selected` (get/set). Methods: `select_row()`, `deselect_row()`, `toggle_select_row()`.

**`GuiTableColumn`** — properties: `title`, `selected` (get/set), `count`, `fixed`, `length`.

**`GuiScrollbar`** — `minimum`, `maximum`, `page_size`, `range`, `position` (get/set).

### `GuiShell`

For shell-based controls (GridView, TextEdit, Picture, ...).

**Properties:** `sub_type`, `drag_drop_supported`, `acc_description`, `handle`.
**Methods:** `select_context_menu_item(function_code)`, `select_context_menu_item_by_position(position_desc)`, `select_context_menu_item_by_text(text)`.

### Models

`from sapwright.models import StatusBarMsg, SessionInfo` (dataclasses)

- **`StatusBarMsg`** — `id`, `type`, `text`, `number`, `has_longtext`, `is_popup`.
- **`SessionInfo`** — `user`, `client`, `language`, `transaction`, `program`, `screen_number`, `system_name`, `application_server`, `message_server`, `group`, `session_number`, `system_session_id`, `response_time`, `interpretation_time`, `round_trips`, `flushes`, `codepage`, `gui_codepage`, `i18n_mode`, `is_low_speed_connection`, `ui_guideline`, and scripting-mode flags.

### Types

`from sapwright.types import VKey, GuiComponentType`

- **`VKey`** — `IntEnum` of SAP virtual keys (Enter, F1–F12, Ctrl/Shift combinations, e.g. `VKey.CTRL_S`).
- **`GuiComponentType`** — `StrEnum` of every SAP GUI element type.

### Exceptions

`from sapwright.exceptions import ...` — all inherit from `SAPGuiError`.

| Exception                      | Raised when                                                                |
| ------------------------------ | -------------------------------------------------------------------------- |
| `SAPLogonError`              | SAP Logon can't be launched or used.                                       |
| `SAPConnectionError`         | A connection can't be found or opened.                                     |
| `SAPScriptingDisabled`       | Scripting is disabled in SAP GUI.                                          |
| `SAPLoginError`              | Login fails, or multi-logon is hit with`terminate_other_sessions=False`. |
| `SAPElementNotFound`         | An element ID doesn't resolve.                                             |
| `SAPElementTypeMismatch`     | An element's type doesn't match`expected_type`.                          |
| `SAPElementNotChangeable`    | Writing to a read-only element.                                            |
| `SAPComboBoxOptionNotFound`  | No combobox entry matches the given text.                                  |
| `SAPStatusBarError`          | `raise_for_status` finds an error message.                               |
| `SAPTransactionError`        | A transaction code doesn't exist.                                          |
| `SAPTableConfigurationError` | A table control is misconfigured.                                          |
