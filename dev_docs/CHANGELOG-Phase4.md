# Changelog - Phase 4: Terminal Panel

## [0.5.0] - 2025-12-05

### Added
- `TerminalPanel` widget - integrated command runner panel.
- Terminal keybindings:
  - `Ctrl+J` - Toggle terminal panel / focus terminal input
  - `Escape` (in terminal) - Return focus to editor
  - `Up/Down` arrows - Navigate command history
- Command execution features:
  - Run shell commands and display stdout/stderr output
  - Working directory tracking with header display
  - Exit code display for failed commands (non-zero return)
  - Scrollable output log with auto-scroll
- Built-in commands:
  - `cd <path>` - Change working directory (supports `~` for home)
  - `pwd` - Print working directory
  - `clear` - Clear terminal output
- Command history - use Up/Down arrows to cycle through previous commands.
- Smart toggle behavior for `Ctrl+J`:
  - Terminal hidden → Show and focus input
  - Terminal visible, editor focused → Focus terminal input
  - Terminal visible, terminal focused → Hide terminal

### Technical Notes
- Uses Textual's `Log` widget for output display and `Input` widget for command entry.
- Commands executed via `asyncio.create_subprocess_shell()` for non-blocking execution.
- Terminal panel docked at bottom of workspace, height of 12 lines.
- Working directory changes update the terminal header display.
- Visibility controlled via CSS class toggle (`.hidden` with `display: none`).

### Design Decision
- Chose simple command runner (Log + Input) over full PTY terminal emulation.
- `textual-terminal` package was considered but has performance issues.
- Current approach covers common use cases: running builds, scripts, git commands.

### Known Limitations
- No support for interactive programs (vim, htop, etc.) that require full terminal control.
- No tab completion for shell commands (could be added in future).
- No support for commands that prompt for input mid-execution.
- Single terminal instance (no multiple terminal tabs).

### Files Added
- `onlycode/app/widgets/terminal_panel.py` - TerminalPanel widget

### Files Modified
- `onlycode/app/screens/main_screen.py` - Added terminal toggle, layout changes
- `onlycode/app/widgets/__init__.py` - Export TerminalPanel

