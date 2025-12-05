# Changelog - Phase 5: Configuration & Editor Settings

## [0.6.0] - 2025-12-05

### Added

#### Syntax Highlighting
- Installed `textual[syntax]` for proper syntax highlighting support.
- **Auto theme sync** - Syntax theme automatically matches UI theme:
  - Light UI themes → `github_light` syntax theme
  - Dark UI themes → `vscode_dark` syntax theme
  - Dracula/Monokai UI → matching syntax themes
- **Manual override** - Command palette options to set syntax theme manually:
  - "Syntax Theme: Dracula/Monokai/VS Code Dark/GitHub Light"
  - "Syntax Theme: Auto (match UI)" - return to auto-matching

#### File Extension → Language Mapping
- Automatic language detection from file extensions for syntax highlighting:
  - Python: `.py`, `.pyw`, `.pyi`
  - JavaScript: `.js`, `.jsx`, `.ts`, `.tsx`, `.mjs`, `.cjs`
  - Web: `.html`, `.htm`, `.css`, `.xml`, `.svg`
  - Data: `.json`, `.toml`, `.yaml`, `.yml`
  - Markdown: `.md`, `.markdown`
  - Systems: `.rs` (Rust), `.go` (Go), `.java`, `.sql`
  - Shell: `.sh`, `.bash`, `.zsh`, `.bashrc`, `.zshrc`

#### Editor Settings (Command Palette)
- **Indent Width** - "Indent Width: 2/4/8" to change spaces per indent level
- **Indent Type** - "Indent Type: Spaces" or "Indent Type: Tabs"
- **Soft Wrap** - "Toggle Soft Wrap" to turn line wrapping on/off
- **Auto-Indent** - "Toggle Auto-Indent" for automatic indentation on Enter
- Fixed `tab_behavior = "indent"` so Tab key inserts indentation (not focus change)

#### File Browser Enhancements
- **Start directory** - File browser now opens at the directory where app was launched (cwd)
- **Root switching** - Command palette options to change file browser root:
  - "Browse: Home Directory" - Switch to `~`
  - "Browse: Filesystem Root" - Switch to `/`
  - "Browse: Launch Directory" - Return to original cwd

### Technical Notes

#### Theme Synchronization
- `watch_theme(old_theme, new_theme)` method watches for UI theme changes
- `UI_TO_SYNTAX_THEME` mapping in `editor_widget.py` defines theme relationships
- `_user_syntax_theme` tracks manual overrides vs auto-matching

#### Auto-Indent Implementation
- Overrides `_on_key()` to intercept Enter key
- Extracts leading whitespace from current line via regex
- Inserts newline + preserved indentation
- Toggleable via `auto_indent` property (default: on)

#### Language Detection
- `EXTENSION_TO_LANGUAGE` dictionary maps extensions to tree-sitter language names
- `detect_language()` method extracts extension and looks up language
- Called automatically in `load_file()` method

### Default Editor Settings
| Setting | Default |
|---------|---------|
| `tab_behavior` | `"indent"` |
| `indent_width` | 4 |
| `indent_type` | `"spaces"` |
| `soft_wrap` | True |
| `auto_indent` | True |
| `show_line_numbers` | True |

### Files Modified
- `onlycode/app/application.py` - Added command palette entries for all settings
- `onlycode/app/screens/main_screen.py` - File browser starts at cwd
- `onlycode/app/widgets/file_browser.py` - Added `set_root()` method
- `onlycode/app/widgets/status_bar.py` - Minor updates
- `onlycode/editor/buffer_manager.py` - Language detection integration
- `onlycode/editor/editor_widget.py` - Theme sync, auto-indent, extension mapping
- `pyproject.toml` - Added `textual[syntax]` dependency

### Features Intentionally Skipped
- **Font settings** - Controlled by terminal emulator
- **Current line highlight** - Not needed for this use case
- **Session persistence** - User prefers fresh start each session
- **Custom keybindings** - Built-in Keys display is sufficient
- **Comment string toggle** - Nice-to-have, not essential

