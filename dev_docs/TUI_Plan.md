# Only Code - Complete Development Plan

## TUI Code Editor Using Textual

---

## Executive Summary

**Only Code** is a terminal-based code editor that brings the philosophy and features of Just Code to the command line. Built with Textual, it will share core infrastructure with Just Code while providing a keyboard-first, terminal-native editing experience.

---

## Project Philosophy

### Inherit from Just Code:

- **"Only code already"** - Get to work fast
- **"It's only code"** - No clutter, pure focus
- **Configuration as code** - JSON configs edited in the editor itself
- **Minimal by default, powerful when needed**

### TUI-specific additions:

- **Keyboard-first** - Every feature accessible without mouse
- **Terminal-native** - Feels at home in the terminal ecosystem
- **Resource-light** - Fast startup, low memory footprint

---

## Architecture Overview

### Repository Structure

```
only-code/                          # New repository
├── onlycode/
│   ├── __init__.py
│   ├── main.py                     # Entry point
│   ├── app/
│   │   ├── __init__.py
│   │   ├── application.py          # Textual App class
│   │   └── screens/
│   │       ├── __init__.py
│   │       ├── main_screen.py      # Primary editing screen
│   │       ├── file_picker.py      # File open/save dialogs
│   │       ├── settings_screen.py  # Settings viewer
│   │       └── command_palette.py  # Quick command access
│   ├── editor/
│   │   ├── __init__.py
│   │   ├── editor_widget.py        # Custom TextArea subclass
│   │   ├── tab_bar.py              # Buffer/tab management
│   │   └── gutter.py               # Line numbers, git status
│   ├── panels/
│   │   ├── __init__.py
│   │   ├── file_browser.py         # Directory tree widget
│   │   ├── terminal.py             # Embedded terminal (PTY)
│   │   └── output.py               # Build/lint output panel
│   ├── themes/
│   │   ├── __init__.py
│   │   └── theme_adapter.py        # Convert JustCode themes → Textual
│   └── shared/                     # Symlink or submodule
│       ├── config/                 # → justcode/config/
│       └── plugins/                # → justcode/plugins/
├── themes/
│   └── *.tcss                      # Textual CSS theme files
├── tests/
│   ├── __init__.py
│   ├── test_editor.py
│   ├── test_file_browser.py
│   └── test_plugins.py
├── requirements.txt
├── pyproject.toml
├── README.md
└── run.sh
```

### Shared Code Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│                         SHARED LAYER                            │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────────────────┐   │
│  │   config/   │  │   plugins/  │  │   resources/          │   │
│  │  loader.py  │  │  models.py  │  │   default_configs/    │   │
│  │ settings.py │  │  loader.py  │  │   settings.json       │   │
│  │ session.py  │  │  actions.py │  │   keybindings.json    │   │
│  │  themes.py  │  │ scripting/* │  │   ui-themes.json      │   │
│  └─────────────┘  └─────────────┘  └───────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐
│   JUST CODE     │  │   ONLY CODE     │
│   (PyQt6 GUI)   │  │   (Textual TUI) │
│                 │  │                 │
│  app/           │  │  app/           │
│  editor/        │  │  editor/        │
│  panels/        │  │  panels/        │
└─────────────────┘  └─────────────────┘
```

---

## Development Phases

### Phase 0: Project Setup (Week 1)

**Goal:** Establish project structure and shared code mechanism

**Tasks:**
- [ ] Create `only-code` repository
- [ ] Set up Python project structure with `pyproject.toml`
- [ ] Create git submodule or shared package for `config/` and `plugins/`
- [ ] Set up Textual development environment
- [ ] Create basic `run.sh` launcher
- [ ] Configure pytest for testing

**Deliverables:**
- Working project skeleton
- Shared config loading from Just Code's JSON files
- Basic Textual app that starts and exits

---

### Phase 1: Core Editor (Weeks 2-3)

**Goal:** Basic text editing with syntax highlighting

**Tasks:**
- [ ] Create `OnlyCodeEditor` widget (extends Textual's `TextArea`)
  - Syntax highlighting via tree-sitter (built into Textual)
  - Line numbers
  - Current line highlighting
  - Selection support
- [ ] Implement basic file operations
  - New file
  - Open file
  - Save / Save As
  - Detect unsaved changes
- [ ] Create main application screen layout
- [ ] Implement status bar
  - Current file path
  - Line:Column position
  - File type/language
  - Modified indicator
- [ ] Basic keybindings
  - `Ctrl+S` - Save
  - `Ctrl+O` - Open
  - `Ctrl+N` - New
  - `Ctrl+Q` - Quit
  - `Ctrl+W` - Close buffer

**Key Textual Widgets:**
- `TextArea` - Core editor (built-in syntax highlighting!)
- `Footer` - Keybinding hints
- `Header` - App title
- `Static` - Status bar

**Deliverables:**
- Single-file editing with syntax highlighting
- File operations (new, open, save)
- Clean, minimal interface

---
### Phase 2: Multi-Buffer Support (Week 4)

**Goal:** Edit multiple files with tab-like navigation

**Tasks:**
- [ ] Create `TabBar` widget
  - Horizontal list of open buffers
  - Visual indicator for active buffer
  - Modified indicator (•)
  - Clickable (mouse support)
- [ ] Buffer management
  - `Ctrl+Tab` / `Ctrl+Shift+Tab` - Cycle buffers
  - `Alt+1-9` - Jump to buffer by number
  - Close buffer with unsaved changes warning
- [ ] Session persistence
  - Integrate with shared `SessionManager`
  - Restore open files on startup

**Deliverables:**
- Multiple files open simultaneously
- Tab bar for buffer navigation
- Session restore

---

### Phase 3: File Browser Panel (Week 5)

**Goal:** Directory tree navigation

**Tasks:**
- [ ] Create `FileBrowser` widget
  - Tree view using Textual's `Tree` widget
  - Directory expansion/collapse
  - File type icons (using Unicode/emoji)
  - Current file highlighting
- [ ] Panel toggling
  - `Ctrl+B` - Toggle file browser
  - Smooth show/hide (Textual animations)
- [ ] File operations
  - Enter to open file
  - Context actions (new file, new folder, delete, rename)
- [ ] Bookmarks support
  - Load from shared settings
  - Quick jump to bookmarked directories

**Key Textual Widgets:**
- `Tree` - Directory tree
- `DirectoryTree` - Built-in file browser (may extend)

**Deliverables:**
- Collapsible file browser panel
- File operations via keyboard
- Bookmark support

---

### Phase 4: Terminal Panel (Week 6)

**Goal:** Integrated terminal emulator

**Tasks:**
- [ ] Research PTY integration with Textual
  - Consider `pyte` for terminal emulation
  - Or use Textual's upcoming terminal widget
- [ ] Create `TerminalPanel` widget
  - Full terminal emulation
  - Command history
  - Working directory sync with file browser
- [ ] Panel toggling
  - `` Ctrl+` `` (backtick) - Toggle terminal
  - `` Ctrl+Shift+` `` - New terminal
- [ ] Integration features
  - Auto-cd when changing directories in file browser
  - Send selection to terminal
  - Copy terminal output

**Alternative (simpler):**
- Command input line with output display
- Run commands and show results
- Less complex than full PTY

**Deliverables:**
- Terminal panel with shell access
- Working directory synchronization

---

### Phase 5: Configuration System (Week 7)

**Goal:** Full config integration with Just Code

**Tasks:**
- [ ] Theme adaptation
  - Create `ThemeAdapter` to convert `ui-themes.json` → Textual CSS
  - Map color keys to Textual CSS variables
  - Support all existing Just Code themes
- [ ] Settings integration
  - Load editor settings (tab width, word wrap, etc.)
  - Apply to `TextArea` configuration
- [ ] Keybindings
  - Load `keybindings.json`
  - Map to Textual bindings
- [ ] Live reload
  - Watch config files for changes
  - Apply changes without restart
- [ ] Settings screen
  - View current settings
  - Open config file in editor

**Deliverables:**
- All Just Code themes working in TUI
- Full settings integration
- Live config reload

---

### Phase 6: Plugin System (Week 8)

**Goal:** Plugin support matching Just Code

**Tasks:**
- [ ] Create TUI-specific `EditorAPI` implementation
  - `get_text()`, `set_text()`
  - `get_selection()`, `replace_selection()`
  - `get_cursor_position()`, `set_cursor_position()`
  - `show_notification()` → Toast/notification widget
- [ ] Integrate shared `PluginManager`
  - Load plugins from `~/.config/justcode/plugins/`
  - Execute plugin actions
- [ ] Plugin triggers
  - `on_save` hooks
  - `on_open` hooks
  - Keyboard shortcuts
- [ ] Lua/Python scripting
  - Reuse `LuaEngine` and `PythonEngine`
  - Same sandbox restrictions

**Deliverables:**
- Full plugin compatibility with Just Code
- Existing plugins work in both GUI and TUI

---

### Phase 7: Command Palette (Week 9)

**Goal:** Quick command access à la VS Code

**Tasks:**
- [ ] Create `CommandPalette` screen
  - Fuzzy search for commands
  - Show keybinding hints
  - Recent commands
- [ ] Command sources
  - Built-in commands (file ops, navigation)
  - Plugin commands
  - Open files (quick switch)
  - Settings
- [ ] Activation
  - `Ctrl+Shift+P` - Command palette
  - `Ctrl+P` - Quick file open

**Key Textual Widgets:**
- `CommandPalette` - Built into Textual!

**Deliverables:**
- Full command palette
- Fuzzy search
- Plugin command integration

---

### Phase 8: Advanced Features (Weeks 10-11)

**Goal:** Parity features and polish

**Tasks:**
- [ ] Markdown preview
  - Split view with rendered markdown
  - Use `rich` for rendering
  - `Ctrl+Shift+M` toggle
- [ ] Find and Replace
  - `Ctrl+F` - Find in file
  - `Ctrl+H` - Find and replace
  - Regex support
- [ ] Go to line
  - `Ctrl+G` - Jump to line number
- [ ] Syntax highlighting themes
  - Load from `syntax-themes.json`
  - Apply to TextArea
- [ ] Mouse support polish
  - Click to position cursor
  - Drag to select
  - Scroll
- [ ] Clipboard integration
  - System clipboard support
  - `Ctrl+C/V/X`

**Deliverables:**
- Feature parity with Just Code
- Polished user experience

---

### Phase 9: Testing & Documentation (Week 12)

**Goal:** Production-ready release

**Tasks:**
- [ ] Unit tests
  - Editor operations
  - File operations
  - Plugin system
  - Config loading
- [ ] Integration tests
  - Full user workflows
  - Textual snapshot testing
- [ ] Documentation
  - README with installation instructions
  - User guide
  - Keybinding reference
- [ ] Release preparation
  - PyPI packaging
  - GitHub releases
  - Installation via `pip install onlycode`

**Deliverables:**
- Comprehensive test suite
- Complete documentation
- PyPI package

---

## Feature Mapping: Just Code → Only Code

| Just Code Feature | Only Code Implementation |
|-------------------|--------------------------|
| QScintilla editor | Textual TextArea + tree-sitter |
| Multi-tab editing | TabBar widget + buffer list |
| File browser panel | Textual Tree/DirectoryTree |
| Terminal panel | PTY integration or command runner |
| Markdown preview | Rich markdown rendering in split |
| JSON config | Shared config module (identical) |
| Plugin system | Shared plugin module + TUI EditorAPI |
| Lua/Python scripts | Shared scripting engines (identical) |
| UI themes | Theme adapter: JSON → Textual CSS |
| Syntax themes | TextArea theme mapping |
| Session persistence | Shared SessionManager (identical) |
| Keybindings | Shared JSON + Textual binding system |

---

## Technical Decisions

### 1. Shared Code Approach

**Decision:** Git submodule pointing to `justcode/config` and `justcode/plugins`

**Rationale:**
- Single source of truth for config/plugin code
- Changes in Just Code automatically available
- Clear separation of concerns

**Alternative considered:** Copy code
- Rejected: Leads to drift and maintenance burden

### 2. Theme Adaptation

**Decision:** Runtime conversion of `ui-themes.json` to Textual CSS

**Implementation:**

```python
class ThemeAdapter:
    def convert(self, justcode_theme: dict) -> str:
        """Convert Just Code theme to Textual CSS."""
        return f"""
        Screen {{
            background: {justcode_theme['background']};
        }}
        TextArea {{
            background: {justcode_theme['background']};
            color: {justcode_theme['foreground']};
        }}
        .panel {{
            background: {justcode_theme['panel_background']};
            border: solid {justcode_theme['panel_border']};
        }}
        """
```

### 3. Editor Widget

**Decision:** Extend Textual's `TextArea` rather than build custom

**Rationale:**
- TextArea has built-in:
  - Syntax highlighting (tree-sitter)
  - Undo/redo
  - Selection
  - Word wrap
  - Line numbers (gutter)
- Well-tested and maintained
- Saves 2-3 weeks of development

### 4. Terminal Integration

**Decision:** Phase 1 - Simple command runner; Phase 2 - Full PTY

**Rationale:**
- Full PTY is complex
- Command runner covers 80% of use cases
- Can iterate to full terminal later

---

## Dependencies

```toml
[project]
dependencies = [
    "textual>=2.1.0",        # TUI framework
    "tree-sitter>=0.20.0",   # Syntax highlighting (comes with Textual)
    "rich>=13.0.0",          # Rich text (comes with Textual)
    "lupa>=2.0",             # Lua scripting (shared with Just Code)
    "watchfiles>=0.20.0",    # Config file watching
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-textual-snapshot>=0.4.0",
]
```

---

## Milestones & Timeline

| Week | Phase | Milestone |
|------|-------|-----------|
| 1 | 0 | Project setup, shared code integration |
| 2-3 | 1 | Basic editor with syntax highlighting |
| 4 | 2 | Multi-buffer support with tabs |
| 5 | 3 | File browser panel |
| 6 | 4 | Terminal panel |
| 7 | 5 | Full config/theme integration |
| 8 | 6 | Plugin system working |
| 9 | 7 | Command palette |
| 10-11 | 8 | Advanced features, polish |
| 12 | 9 | Testing, docs, release |

**Total estimated time:** 12 weeks

---

## Success Criteria

1. **Functional parity:** All major Just Code features available in TUI
2. **Plugin compatibility:** Existing plugins work without modification
3. **Config sharing:** Same `~/.config/justcode/` directory for both apps
4. **Performance:** Startup in <500ms, responsive on large files
5. **Test coverage:** >80% for core functionality
6. **Documentation:** Complete user guide and keybinding reference

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Textual TextArea limitations | High | Evaluate early; fallback to custom widget |
| PTY complexity | Medium | Start with simple command runner |
| Theme conversion edge cases | Low | Test with all existing themes early |
| Plugin API differences | Medium | Abstract EditorAPI interface clearly |

---

## Next Steps

1. **Create repository** and set up project structure
2. **Prototype Phase 1** - Basic editor with file operations
3. **Validate TextArea** - Ensure it meets requirements
4. **Design shared code** - Finalize submodule approach