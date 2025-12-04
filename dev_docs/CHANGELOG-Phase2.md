# Changelog - Phase 2: Multi-Buffer Support

## [0.3.0] - 2025-12-04

### Added
- `TabBar` widget displaying open buffers with active/modified indicators.
- `BufferManager` class for managing multiple file buffers.
- `Buffer` dataclass storing content, path, cursor position, language, and modified state.
- `ConfirmCloseDialog` for handling unsaved changes (Save/Discard/Cancel options).
- Session persistence - open files saved to `~/.config/onlycode/session.json` and restored on startup.
- Tab navigation keybindings:
  - `Ctrl+T` - New tab
  - `Ctrl+W` - Close tab (with confirmation if unsaved)
  - `Ctrl+PageDown` / `F8` - Next tab
  - `Ctrl+PageUp` / `F7` - Previous tab
  - `Alt+1-9` - Jump to tab by number

### Changed
- `Ctrl+N` changed to `Ctrl+T` for new tab (terminal ASCII conflict with Ctrl+N).
- Tab navigation changed from `Ctrl+Tab`/`Ctrl+Shift+Tab` to `Ctrl+PageDown`/`Ctrl+PageUp` (terminal compatibility).

### Fixed
- StatusBar reactive watchers triggering before widget composition (`init=False`).
- Buffer content lost when switching tabs (added `_save_current_buffer_state()`).
- Tab name not updating after save (added `update_tab_name()` method).
- False modified indicators on new/switched buffers (used `_loading_buffer` flag with `call_after_refresh()`).
- Files unable to close when modified (added confirmation dialog with discard option).

### Technical Notes
- Used `call_after_refresh()` to handle async TextArea.Changed events properly.
- Added `priority=True` to keybindings to ensure they take precedence over TextArea bindings.
- Project is fully self-contained - no dependencies on Just_Code project.

