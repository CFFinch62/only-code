from textual.widget import Widget
from textual.reactive import reactive
from textual.widgets import Static

class StatusBar(Widget):
    """A status bar widget."""

    DEFAULT_CSS = """
    StatusBar {
        dock: bottom;
        height: 1;
        background: $surface;
        color: $text;
        layout: horizontal;
    }
    .status-item {
        padding: 0 1;
    }
    #file-path {
        width: 1fr;
    }
    """

    # Use init=False to prevent watchers from triggering before compose
    file_path = reactive("Untitled", init=False)
    cursor_position = reactive((1, 1), init=False)
    is_modified = reactive(False, init=False)

    def compose(self):
        yield Static(self.file_path, id="file-path", classes="status-item")
        yield Static(f"Ln {self.cursor_position[0]}, Col {self.cursor_position[1]}", id="cursor-pos", classes="status-item")
        yield Static("", id="modified", classes="status-item")

    def watch_file_path(self, path: str) -> None:
        self.query_one("#file-path", Static).update(path)

    def watch_cursor_position(self, pos: tuple[int, int]) -> None:
        self.query_one("#cursor-pos", Static).update(f"Ln {pos[0]}, Col {pos[1]}")

    def watch_is_modified(self, modified: bool) -> None:
        indicator = "●" if modified else ""
        self.query_one("#modified", Static).update(indicator)
