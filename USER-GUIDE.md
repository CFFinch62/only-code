# Only Code - User Guide

A lightweight terminal-based code editor built with Python and Textual.

## Table of Contents

- [Getting Started](#getting-started)
- [Interface Overview](#interface-overview)
- [Working with Files](#working-with-files)
- [The Editor](#the-editor)
- [File Browser](#file-browser)
- [Terminal Panel](#terminal-panel)
- [Command Palette](#command-palette)
- [Theming](#theming)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Tips and Tricks](#tips-and-tricks)
- [Troubleshooting](#troubleshooting)

---

## Getting Started

### Installation

```bash
# Navigate to the project directory
cd Only_Code

# Run the setup script (creates virtual environment, installs dependencies)
./setup.sh

# Start the editor
./run.sh
```

### First Launch

Only Code starts with:
- An empty editor buffer ("Untitled")
- File browser showing the directory where you launched the app
- Status bar at the bottom

---

## Interface Overview

```
┌────────────────────────────────────────────────────────────────────┐
│  Tab 1  │  Tab 2  │  Tab 3                                         │  ← Tab Bar
├────────────────┬───────────────────────────────────────────────────┤
│                │                                                   │
│   File         │              Editor Area                          │
│   Browser      │                                                   │
│   Panel        │                                                   │
│                │                                                   │
│   (Ctrl+B)     │                                                   │
│                │                                                   │
├────────────────┴───────────────────────────────────────────────────┤
│  Terminal Panel (Ctrl+J)                                           │
├────────────────────────────────────────────────────────────────────┤
│  path/to/file.py                     │ Ln 42, Col 15 │ Python      │  ← Status Bar
└────────────────────────────────────────────────────────────────────┘
```

**Key areas:**
- **Tab Bar** - Open files, click to switch, shows modified indicator (*)
- **File Browser** - Toggle with Ctrl+B, navigate and open files
- **Editor** - Main editing area with syntax highlighting
- **Terminal** - Toggle with Ctrl+J, run shell commands
- **Status Bar** - File path, cursor position, detected language

---

## Working with Files

### Opening Files
- **Ctrl+O** - Opens file selection dialog
- **Double-click** in file browser
- Files open in new tabs

### Opening a Folder
- **Ctrl+Shift+O** - Opens a folder selection dialog and re-roots the file browser there
- Browse the tree and click **Select**, or type a path directly into the box
- Also available as **Open Folder...** in the command palette (Ctrl+P)
- Quicker alternative: **double-click any folder** in the file browser to jump straight into it (see [File Browser](#file-browser))

### Creating Files
- **Ctrl+T** - Create a new untitled tab
- New files are named "Untitled", "Untitled 2", etc.

### Saving Files
- **Ctrl+S** - Save current file
- If file is untitled, prompts for filename
- Modified files show **\*** in the tab

### Closing Files
- **Ctrl+W** - Close current tab
- Prompts to save if file has unsaved changes

### Tab Navigation
- **Click tab** - Switch to that file
- **Ctrl+PageDown** - Next tab
- **Ctrl+PageUp** - Previous tab
- **Alt+1-9** - Jump directly to tab 1-9
- **F7/F8** - Previous/Next tab (alternative)

---

## The Editor

### Syntax Highlighting

Automatic syntax highlighting based on file extension:

| Extensions | Language |
|------------|----------|
| `.py`, `.pyw`, `.pyi` | Python |
| `.js`, `.jsx`, `.ts`, `.tsx`, `.mjs`, `.cjs` | JavaScript |
| `.html`, `.htm` | HTML |
| `.css` | CSS |
| `.json` | JSON |
| `.yaml`, `.yml` | YAML |
| `.toml` | TOML |
| `.md`, `.markdown` | Markdown |
| `.rs` | Rust |
| `.go` | Go |
| `.java` | Java |
| `.sql` | SQL |
| `.sh`, `.bash`, `.zsh`, `.bashrc`, `.zshrc` | Bash |
| `.xml`, `.svg` | XML |

Files without a recognized extension display as plain text.

### Editor Features

- **Line numbers** - Always visible
- **Auto-indent** - Preserves indentation level when pressing Enter
- **Configurable indentation** - Choose 2, 4, or 8 spaces; or use tabs
- **Soft wrap** - Toggle line wrapping via command palette

---

## File Browser

Toggle with **Ctrl+B**. Shows files and directories in a tree view.

### Navigation
- **Click folder** - Expand/collapse
- **Double-click folder** - Open it as the new browser root (jump straight in, instead of drilling down manually)
- **Double-click file** - Open in editor
- **Arrow keys** - Navigate tree

### Changing Root Directory

Three ways to change what directory the file browser shows:

- **Double-click a folder** in the tree to make it the new root
- **Ctrl+Shift+O** (or **Open Folder...** in the command palette) opens a folder picker - browse or type a path, then Select
- Command palette (Ctrl+P) shortcuts for common locations:

| Command | Description |
|---------|-------------|
| Open Folder... | Pick any folder via a dialog (browse or type a path) |
| Browse: Home Directory | Switch to `~` (home folder) |
| Browse: Filesystem Root | Switch to `/` (entire filesystem) |
| Browse: Launch Directory | Return to where you started the app |

---

## Terminal Panel

Toggle with **Ctrl+J**. A real shell terminal inside the editor.

### Features
- Full shell access (bash/zsh)
- Run commands without leaving the editor
- Resizable panel

### Usage
1. Press **Ctrl+J** to open terminal
2. Type commands as normal
3. Press **Ctrl+J** again to close
4. Press **Escape** to return focus to editor

---

## Command Palette

Press **Ctrl+P** to open the command palette. Type to filter commands.

### Available Commands

**Themes:**
- `Syntax Theme: [name]` - Set syntax highlighting theme
- `Syntax Theme: Auto (match UI)` - Auto-match syntax to UI theme
- Built-in Textual themes via `theme` command

**Editor Settings:**
- `Indent Width: 2/4/8` - Set spaces per indent
- `Indent Type: Spaces/Tabs` - Choose indentation character
- `Toggle Soft Wrap` - Enable/disable line wrapping
- `Toggle Auto-Indent` - Enable/disable auto-indent on Enter

**File Browser:**
- `Open Folder...` - Pick a folder to browse (re-roots the file browser)
- `Browse: Home Directory` - Set browser to ~/
- `Browse: Filesystem Root` - Set browser to /
- `Browse: Launch Directory` - Set browser to launch directory

**System:**
- `Keys` - Show all keyboard shortcuts
- `Quit` - Exit the application

---

## Theming

### UI Themes

Only Code inherits Textual's theme system. Toggle dark/light mode with **d** key or use command palette.

### Syntax Themes

Available syntax themes:
- monokai
- dracula
- github_dark
- material
- nord
- one_dark (and more)

Syntax themes **auto-match** the UI theme (dark/light). To override:
1. Press **Ctrl+P**
2. Type "Syntax Theme"
3. Select your preferred theme

To reset to auto-matching: Select "Syntax Theme: Auto (match UI)"

---

## Keyboard Shortcuts

### File Operations

| Shortcut | Action |
|----------|--------|
| Ctrl+O | Open file |
| Ctrl+Shift+O | Open folder (re-root file browser) |
| Ctrl+S | Save file |
| Ctrl+T | New tab |
| Ctrl+W | Close tab |
| Ctrl+Q | Quit |

### Navigation

| Shortcut | Action |
|----------|--------|
| Ctrl+B | Toggle file browser |
| Ctrl+J | Toggle terminal |
| Ctrl+P | Open command palette |
| Escape | Focus editor |

### Tab Navigation

| Shortcut | Action |
|----------|--------|
| Ctrl+PageDown | Next tab |
| Ctrl+PageUp | Previous tab |
| Alt+1 through Alt+9 | Jump to tab 1-9 |
| F7 | Previous tab |
| F8 | Next tab |

### Other

| Shortcut | Action |
|----------|--------|
| d | Toggle dark mode |

---

## Tips and Tricks

1. **Quick file access** - Use Ctrl+O and type part of the filename to filter
2. **Navigate large projects** - Double-click a folder in the file browser to re-root there instantly, or use Ctrl+Shift+O / "Open Folder..." to jump to any path directly, instead of drilling down folder by folder
3. **Check shortcuts** - Press Ctrl+P, type "Keys" to see all keybindings
4. **Code vs prose** - Disable auto-indent when writing prose/markdown
5. **Terminal workflow** - Keep terminal open while editing, run tests quickly

---

## Troubleshooting

### Editor doesn't start

```bash
# Check Python version (3.10+ required)
python3 --version

# Reinstall dependencies
./setup.sh
```

### Display issues

Only Code requires a terminal with good Unicode and color support:
- **Recommended**: kitty, alacritty, iTerm2, Windows Terminal
- **May have issues**: very old xterm, basic TTY

```bash
# Check terminal color support
echo $TERM
# Should show something like xterm-256color
```

### Syntax highlighting not working

Make sure the file has a recognized extension. Check the status bar - it shows the detected language.

### Keybinding conflicts

Some terminal emulators capture certain shortcuts. If a shortcut doesn't work:
1. Check your terminal's settings
2. Use the command palette (Ctrl+P) as an alternative

Ctrl+Shift+O (Open Folder) is a common case: many terminals can't distinguish Ctrl+Shift+O from Ctrl+O, since Shift often doesn't change the byte sent for a Ctrl+letter combo unless the terminal supports an extended keyboard protocol. If Ctrl+Shift+O opens a file dialog instead of a folder dialog, use **Open Folder...** from the command palette (Ctrl+P) instead.

---

## Building from Source

### Development Setup

```bash
git clone <repository>
cd Only_Code
./setup.sh
./run.sh
```

### Creating Standalone Executable

```bash
pip install pyinstaller
python build.py

# Run the built executable
./dist/OnlyCode/OnlyCode
```

The standalone build includes all dependencies and syntax highlighting support (~38 MB).

---

For more information, see the [README](README.md) or [dev_docs/](dev_docs/) for development notes.

