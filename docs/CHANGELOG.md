# Changelog

## v1.1.0 - 2026-03-06

### New Features

#### Edit & Delete Custom Snippets
- Right-click any snippet in the **Custom** tab to open a context menu with **Edit** and **Delete** options.
- Edit opens a window pre-filled with the snippet's name and code for modification.
- Delete asks for confirmation before removing the snippet.

#### Code Preview Tooltip
- Hovering over any snippet button displays a tooltip with a preview of the code (up to 300 characters).
- The tooltip appears to the left of the sidebar (or to the right if there isn't enough space).

#### Paste Feedback
- After pasting a snippet, a brief green notification ("Pasted!") appears at the bottom of the sidebar.
- If an error occurs during paste, a red notification is shown with the error message.

#### New Language Tabs
Three new snippet categories added:
- **Python** (10 snippets): Main block, function, class, list comprehension, try/except, file open, lambda, dict comprehension, decorator, dataclass.
- **SQL** (8 snippets): SELECT, INSERT, UPDATE, DELETE, CREATE TABLE, JOIN, GROUP BY, subquery.
- **TypeScript** (8 snippets): Interface, type alias, enum, generic function, optional props, React FC, useState, useEffect.

#### Smart Search
- The search bar now filters by **snippet name and code content**, not just the name.
- Example: searching "flex" will match snippets whose code contains `display: flex` even if the name doesn't include "flex".

### Improvements

#### Error Handling
- Replaced all silent `except: pass` blocks with specific exception handling (`json.JSONDecodeError`, `IOError`).
- Users now see informative warning dialogs when `config.json` or `snippets.json` fail to load or save.

#### Code Refactoring
- Snippet save/refresh logic consolidated into `_save_and_refresh_custom()` to avoid code duplication.
- Button data now tracks code content and tab name (`btn, label, code, tab_name`) for richer functionality.

### Files Modified
- `main.py` — All changes applied here.
- `README.md` — Updated features section to reflect new capabilities.
