# Sapwright

A Python library for automating SAP GUI using the SAP GUI Scripting API. Sapwright wraps the raw, loosely-typed SAP scripting COM objects in a clean, object-oriented, type-safe interface, so you get IDE autocomplete, type checking, and readable code

## Requirements

- Python 3.11+
- SAP GUI Scripting Enabled
- SAP Logon 770+
- Windows (the SAP GUI Scripting API is COM-based and Windows-only)

## Installation

```bash
pip install sapwright
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv add sapwright
```

## Prerequisites

Follow these steps for a smooth scripting experience:

**SAP GUI Scripting Settings** — go to SAP GUI Options → Accessibility & Scripting → Scripting:

1. Check "Enable Scripting"
2. Uncheck "Notify when a script attaches to SAP GUI"
3. Uncheck "Notify when a script opens a connection"

**SAP GUI Security Settings** — go to SAP GUI Options → Security → Security Configuration:

1. Select "Disabled" for the Status option

## Features

- **Type-safe, object-oriented API** over the raw SAP Scripting COM objects, with full IDE autocomplete and static type checking (`py.typed` included).
- **Automatic connection management** — `Sapwright` is a context manager that:
  - Launches SAP Logon automatically if it isn't already running (resolved from the Windows registry, or a custom `exe_path`).
  - Attaches to the user's existing connection/session if one is already open, instead of opening a duplicate.
  - Logs in automatically with the given credentials, client, and language.
  - Handles multi-logon prompts ("already logged on") by terminating other sessions, or raises `SAPLoginError` if disabled.
  - Handles forced password-change dialogs via a pluggable `password_generator`.
  - Dismisses trailing popups after login.
  - Closes the session/connection automatically on `__exit__`.
- **Connect by connection string or connection name** — `connection_string` takes precedence over `connection_name` when opening a new connection.
- **`GuiComponent`** — a universal wrapper around any SAP GUI element (`find_by_id`) with:
  - `.text` get/set (with automatic date formatting, combobox selection by visible text, and max-length truncation).
  - `.click()` / `.press()` / `.select()` that dispatch to the right underlying action (button press, tab select, checkbox toggle, radio select) based on element type.
  - Common properties: `id`, `name`, `type`, `children`, `changeable`, `tooltip`, `width`, `height`, `left`, `top`, `modified`, etc.
  - `set_focus()`, `visualize()` (red highlight frame), `send_vkey()`.
  - Transparent attribute delegation (`__getattr__`/`__setattr__`) to the underlying COM object, plus PascalCase aliases (e.g. `Text`, `SendCommand`) so scripts recorded from SAP's own script recorder still work.
- **`GuiSession`** — high-level session/transaction control:
  - `find_by_id(id, raise_error=True, expected_type=...)` with an `expected_type` parameter that returns a typed wrapper (e.g. `GuiTableControl`) and validates the element's actual SAP type, raising `SAPElementTypeMismatch` on mismatch.
  - `start_transaction()` / `end_transaction()` / `send_command()`.
  - `statusbar_msg()` and `raise_for_status()` for reading and asserting on status bar messages.
  - `press_enter()`, `send_vkey()`, `dismiss_popups()` (repeatedly dismiss stacked popup dialogs), `title()`.
  - `close()`, `close_connection()`, session `info` (user, client, transaction, response time, round trips, etc. as a typed `SessionInfo` model).
- **Advanced `GuiTableControl` operations**:
  - Automatic, eagerly-cached column header map (`.headers`) mapping header text → column index.
  - Indexable/iterable `GuiTableRow` (iterate cells directly).
  - `.rows`, `.columns`, `.get_cell(row, col, expected_type=...)`, `.get_absolute_row()` (stable row indexing across scroll position).
  - Row selection helpers (`select_row`, `deselect_row`, `toggle_select_row`) and column helpers (`select_all_columns`, `deselect_all_columns`, `reorder_table`).
  - Horizontal/vertical `GuiScrollbar` access, `row_count` vs `visible_row_count`, `refresh()` to re-resolve a stale table reference after scrolling/pagination.
- **`GuiShell`** wrapper for shell-based controls (GridView, TextEdit, Picture, etc.) with context-menu helpers.
- **Rich, specific exception hierarchy** rooted at `SAPGuiError` (`SAPLoginError`, `SAPConnectionError`, `SAPScriptingDisabled`, `SAPElementNotFound`, `SAPElementNotChangeable`, `SAPComboBoxOptionNotFound`, `SAPStatusBarError`, `SAPTransactionError`, `SAPElementTypeMismatch`, `SAPTableConfigurationError`) instead of raw COM exceptions.
- **`VKey`** enum for every SAP virtual key code (F1–F12, Ctrl/Shift combinations, etc.) and a `GuiComponentType` enum of all SAP GUI element types.
- **Pydantic models** (`SessionInfo`, `StatusBarMsg`) for structured, validated access to session and status bar data.

## Usage

### Quick start

```python
from sapwright import Sapwright

with Sapwright(
    username="jdoe",
    password="secret",
    connection_name="PRD",  # or connection_string="..."
) as session:
    session.start_transaction("va01")
    session.find_by_id("wnd[0]/usr/ctxtVBAK-AUART").text = "ZWEO"
    session.press_enter()
```

Using the context manager automatically connects on `__enter__` and closes the session on `__exit__`. If you need finer control, call `connect()` / `close_connection()` yourself:

```python
from sapwright import Sapwright

sap = Sapwright(
    username="jdoe",
    password="secret",
    connection_name="PRD",
    client=100,
    language="EN",
)
session = sap.connect()
try:
    session.start_transaction("va01")
    ...
finally:
    session.close_connection()
```

### Finding and interacting with elements

```python
# Plain element lookup
field = session.find_by_id("wnd[0]/usr/ctxtVBAK-AUART")
field.text = "ZWEO"

# Typed lookup — validates the SAP element type and gives you a typed wrapper
from sapwright.objects import GuiTableControl

table = session.find_by_id(
    "wnd[0]/usr/tblSAPMV45ATCTRL_U_ERF_AUFTRAG",
    expected_type=GuiTableControl,
)

# Optional lookup that returns None instead of raising
popup_ok = session.find_by_id("wnd[1]/usr/btnSPOP-OPTION1", raise_error=False)
if popup_ok:
    popup_ok.click()
```

### Working with tables

```python
from sapwright.objects import GuiTableControl

table = session.find_by_id("wnd[0]/usr/tblITEMS", expected_type=GuiTableControl)

print(table.headers)  # {"material": 0, "quantity": 1, ...}
print(table.row_count, table.visible_row_count)

for row in table.rows:
    for cell in row:
        print(cell.name, cell.text)

first_row = table.get_absolute_row(0)
material_col = table.headers["material"]
print(table.get_cell(0, material_col).text)
```

### Status bar and error handling

```python
from sapwright.exceptions import SAPTransactionError

try:
    session.start_transaction("invalid_tcode")
except SAPTransactionError as e:
    print(f"Transaction failed: {e}")

status = session.statusbar_msg()
if status.type == "E":
    print(f"Error {status.number}: {status.text}")

# Or raise directly from the status bar
session.raise_for_status(message="Order creation failed")
```

### Sending keys and dismissing popups

```python
from sapwright.types import VKey

session.press_enter()
session.send_vkey(VKey.CTRL_S)  # Save
session.dismiss_popups(limit=5)  # clears stacked confirmation dialogs
```

## Example scripts

### Basic navigation

```python
from sapwright import Sapwright

with Sapwright(
    username="jdoe",
    password="secret",
    connection_name="PRD",
) as session:
    session.start_transaction("va01")

    session.find_by_id("wnd[0]/usr/ctxtVBAK-AUART").text = "ZWEO"
    session.find_by_id("wnd[0]/usr/ctxtVBAK-VKORG").text = "2200"
    session.find_by_id("wnd[0]/usr/ctxtVBAK-VTWEG").text = "10"
    session.find_by_id("wnd[0]/usr/ctxtVBAK-SPART").text = "00"
    session.press_enter()
    session.dismiss_popups()

    session.raise_for_status(message="Failed to create sales order")
    print(f"Created order, status: {session.statusbar_msg().text}")
```

### Custom password generator for forced password changes

```python
from sapwright import Sapwright


def new_password() -> str:
    return "NewSecret@2026"


with Sapwright(
    username="jdoe",
    password="secret",
    connection_name="PRD",
    password_generator=new_password,
) as session:
    ...
```
