import re
from pathlib import Path
from textual.widgets import TextArea
from textual.binding import Binding
from textual.events import Key

# File extension to language mapping
# Languages supported by Textual: python, markdown, json, toml, yaml, html, css,
#                                  javascript, rust, go, regex, sql, java, bash, xml
EXTENSION_TO_LANGUAGE = {
    # Python
    ".py": "python",
    ".pyw": "python",
    ".pyi": "python",
    # JavaScript/TypeScript (use javascript for both)
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "javascript",
    ".tsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    # Web
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".xml": "xml",
    ".svg": "xml",
    # Data formats
    ".json": "json",
    ".toml": "toml",
    ".yaml": "yaml",
    ".yml": "yaml",
    # Markdown
    ".md": "markdown",
    ".markdown": "markdown",
    # Rust
    ".rs": "rust",
    # Go
    ".go": "go",
    # Java
    ".java": "java",
    # SQL
    ".sql": "sql",
    # Shell/Bash
    ".sh": "bash",
    ".bash": "bash",
    ".zsh": "bash",
    ".bashrc": "bash",
    ".zshrc": "bash",
    # Regex (unlikely but supported)
    ".regex": "regex",
}

# Mapping from UI themes to syntax themes
UI_TO_SYNTAX_THEME = {
    # Exact matches
    "dracula": "dracula",
    "monokai": "monokai",
    # Light themes
    "textual-light": "github_light",
    "solarized-light": "github_light",
    "catppuccin-latte": "github_light",
    # Dark themes (default to vscode_dark)
    "textual-dark": "vscode_dark",
    "nord": "vscode_dark",
    "gruvbox": "vscode_dark",
    "tokyo-night": "vscode_dark",
    "catppuccin-mocha": "vscode_dark",
    "textual-ansi": "vscode_dark",
    "flexoki": "vscode_dark",
}

# Available syntax themes for manual selection
SYNTAX_THEMES = ["dracula", "monokai", "vscode_dark", "github_light"]


class OnlyCodeEditor(TextArea):
    """The core editor widget for Only Code."""

    BINDINGS = [
        Binding("ctrl+s", "save", "Save File"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.show_line_numbers = True
        # Tab inserts indentation instead of moving focus
        self.tab_behavior = "indent"
        # No language by default (plain text) - set when file loads
        self.language = None
        self.theme = "vscode_dark"  # Default syntax theme
        self._user_syntax_theme = None  # User override, if set
        self._auto_indent = True  # Auto-indent on Enter (for code editing)

    async def _on_key(self, event: Key) -> None:
        """Handle key events, including auto-indent on Enter."""
        if event.key == "enter" and self._auto_indent and not self.read_only:
            # Get current line's leading whitespace
            cursor_row = self.cursor_location[0]
            current_line = self.document.get_line(cursor_row)
            # Extract leading whitespace
            match = re.match(r'^(\s*)', current_line)
            indent = match.group(1) if match else ""
            # Insert newline + indent
            self.insert(f"\n{indent}")
            event.prevent_default()
            event.stop()
        else:
            await super()._on_key(event)

    @property
    def auto_indent(self) -> bool:
        """Whether auto-indent is enabled."""
        return self._auto_indent

    @auto_indent.setter
    def auto_indent(self, value: bool) -> None:
        """Set auto-indent on or off."""
        self._auto_indent = value

    def set_syntax_theme_for_ui(self, ui_theme: str) -> None:
        """Set syntax theme to match UI theme, unless user has overridden."""
        if self._user_syntax_theme is None:
            self.theme = UI_TO_SYNTAX_THEME.get(ui_theme, "vscode_dark")

    def set_user_syntax_theme(self, theme: str) -> None:
        """Set a user-selected syntax theme (overrides auto-matching)."""
        if theme in SYNTAX_THEMES:
            self._user_syntax_theme = theme
            self.theme = theme

    def clear_user_syntax_theme(self) -> None:
        """Clear user override and return to auto-matching."""
        self._user_syntax_theme = None

    def detect_language(self, path: str) -> str | None:
        """Detect language from file extension."""
        p = Path(path)
        ext = p.suffix.lower()
        # Also check for dotfiles like .bashrc
        if not ext and p.name.startswith("."):
            ext = p.name.lower()
        return EXTENSION_TO_LANGUAGE.get(ext)

    def load_file(self, path: str) -> bool:
        """Load a file into the editor and set language from extension."""
        try:
            with open(path, "r") as f:
                self.text = f.read()
            # Auto-detect language from file extension
            self.language = self.detect_language(path)
            return True
        except Exception as e:
            # TODO: Show error notification
            return False

    def save_file(self, path: str) -> bool:
        """Save the current content to a file."""
        try:
            with open(path, "w") as f:
                f.write(self.text)
            return True
        except Exception as e:
            return False
