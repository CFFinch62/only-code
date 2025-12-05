from textual.widget import Widget
from textual.reactive import reactive
from textual.widgets import Static


# Display names for languages
LANGUAGE_DISPLAY_NAMES = {
    "python": "Python",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "json": "JSON",
    "markdown": "Markdown",
    "html": "HTML",
    "css": "CSS",
    "rust": "Rust",
    "go": "Go",
    "bash": "Bash",
    "yaml": "YAML",
    "toml": "TOML",
    "text": "Plain Text",
    # Additional languages
    "c": "C",
    "cpp": "C++",
    "java": "Java",
    "scala": "Scala",
    "ruby": "Ruby",
    "lua": "Lua",
    "r": "R",
    "racket": "Racket",
    "scheme": "Scheme",
    "pascal": "Pascal",
    "basic": "BASIC",
    "fortran": "Fortran",
    "logo": "Logo",
    "xml": "XML",
    "ini": "INI",
    "sql": "SQL",
    "php": "PHP",
    "perl": "Perl",
    "swift": "Swift",
    "kotlin": "Kotlin",
}


class StatusBar(Widget):
    """A status bar widget showing file info, cursor position, language, encoding."""

    DEFAULT_CSS = """
    StatusBar {
        height: 1;
        background: $surface;
        color: $text;
        layout: horizontal;
    }

    StatusBar .status-item {
        padding: 0 1;
        width: auto;
    }

    StatusBar #file-path {
        width: 1fr;
    }

    StatusBar #modified {
        color: $warning;
        width: 2;
    }

    StatusBar #cursor-pos {
        width: auto;
        min-width: 14;
    }

    StatusBar #language {
        color: $success;
        width: auto;
        min-width: 10;
    }

    StatusBar #encoding {
        color: $text-muted;
        width: auto;
        min-width: 6;
    }

    StatusBar #line-ending {
        color: $text-muted;
        width: auto;
        min-width: 4;
    }
    """

    # Use init=False to prevent watchers from triggering before compose
    file_path = reactive("Untitled", init=False)
    cursor_position = reactive((1, 1), init=False)
    is_modified = reactive(False, init=False)
    language = reactive("text", init=False)
    encoding = reactive("UTF-8", init=False)
    line_ending = reactive("LF", init=False)

    def compose(self):
        yield Static(self.file_path, id="file-path", classes="status-item")
        yield Static("", id="modified", classes="status-item")
        yield Static(f"Ln {self.cursor_position[0]}, Col {self.cursor_position[1]}", id="cursor-pos", classes="status-item")
        yield Static(self._get_language_display(), id="language", classes="status-item")
        yield Static(self.encoding, id="encoding", classes="status-item")
        yield Static(self.line_ending, id="line-ending", classes="status-item")

    def _get_language_display(self) -> str:
        """Get display name for current language."""
        return LANGUAGE_DISPLAY_NAMES.get(self.language, self.language.title())

    def watch_file_path(self, path: str) -> None:
        try:
            self.query_one("#file-path", Static).update(path)
        except Exception:
            pass

    def watch_cursor_position(self, pos: tuple[int, int]) -> None:
        try:
            self.query_one("#cursor-pos", Static).update(f"Ln {pos[0]}, Col {pos[1]}")
        except Exception:
            pass

    def watch_is_modified(self, modified: bool) -> None:
        try:
            indicator = "●" if modified else ""
            self.query_one("#modified", Static).update(indicator)
        except Exception:
            pass

    def watch_language(self, lang: str) -> None:
        try:
            self.query_one("#language", Static).update(self._get_language_display())
        except Exception:
            pass

    def watch_encoding(self, enc: str) -> None:
        try:
            self.query_one("#encoding", Static).update(enc)
        except Exception:
            pass

    def watch_line_ending(self, ending: str) -> None:
        try:
            self.query_one("#line-ending", Static).update(ending)
        except Exception:
            pass
