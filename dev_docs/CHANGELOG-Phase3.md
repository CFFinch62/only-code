# Changelog - Phase 3: File Browser Panel

## [0.4.0] - 2025-12-04

### Added
- `FileBrowser` widget with collapsible directory tree panel.
- `FilteredDirectoryTree` subclass that hides hidden files/folders (names starting with `.`).
- File browser keybinding:
  - `Ctrl+B` - Toggle file browser panel visibility
  - `R` (when browser focused) - Refresh directory tree
- File selection from browser opens file in new tab (or switches to existing tab if already open).
- Focus management - browser receives focus when opened, editor receives focus when file selected.
- Browser starts from user's home directory by default.
- Duplicate file detection - selecting an already-open file switches to its tab instead of opening again.

### Changed
- File dialogs (Open/Save) now start from home directory instead of app working directory.

### Fixed
- Initial untitled document showing modified indicator (dot) on startup.
- New tabs created with `Ctrl+T` showing modified indicator incorrectly.
- PosixPath type error when opening files (converted to string for status bar display).

### Technical Notes
- Used `set_timer()` instead of `call_after_refresh()` for more reliable async event handling.
- `FilteredDirectoryTree.filter_paths()` filters out hidden files at the widget level.
- File browser uses expand-in-place tree navigation (click folders to expand/collapse).
- Browser visibility controlled via CSS class toggle (`.hidden` with `display: none`).

### Known Limitations
- No context menu actions (new file, delete, rename from browser) - may be added in future phase.
- No folder navigation that changes tree root (causes Textual DirectoryTree reload issues).

