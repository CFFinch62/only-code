# Only Code Editor - File Browser Widget
from textual.widgets import DirectoryTree, Static
from textual.containers import Vertical
from textual.widget import Widget
from textual.reactive import reactive
from textual.message import Message
from textual.binding import Binding
from pathlib import Path
from typing import Iterable
import os


class FilteredDirectoryTree(DirectoryTree):
    """DirectoryTree that hides hidden files (starting with .)"""

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        """Filter out hidden files and directories."""
        return [p for p in paths if not p.name.startswith(".")]


class FileBrowser(Widget):
    """File browser panel with directory tree."""

    DEFAULT_CSS = """
    FileBrowser {
        width: 30;
        height: 100%;
        border-right: solid $primary;
        background: $surface;
    }

    FileBrowser.hidden {
        display: none;
    }

    FileBrowser #browser-title {
        dock: top;
        height: 1;
        background: $primary;
        color: $text;
        text-align: center;
        text-style: bold;
    }

    FileBrowser DirectoryTree {
        height: 1fr;
        scrollbar-gutter: stable;
    }
    """

    BINDINGS = [
        Binding("r", "refresh", "Refresh", show=False),
    ]

    class FileSelected(Message):
        """Message sent when a file is selected."""
        def __init__(self, path: str):
            super().__init__()
            self.path = path

    class DirectoryChanged(Message):
        """Message sent when directory changes."""
        def __init__(self, path: str):
            super().__init__()
            self.path = path

    current_path = reactive("")

    def __init__(self, path: str | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Default to home directory if no path specified
        if path is None:
            path = str(Path.home())
        self.root_path = os.path.abspath(path)

    def compose(self):
        yield Static(self._get_title(), id="browser-title")
        yield FilteredDirectoryTree(self.root_path, id="file-tree")

    def _get_title(self) -> str:
        """Get the title showing current directory."""
        return f"📁 {Path(self.root_path).name}"

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected):
        """Handle file selection - open in editor."""
        self.post_message(self.FileSelected(str(event.path)))

    def toggle(self):
        """Toggle visibility of the file browser."""
        self.toggle_class("hidden")
        return not self.has_class("hidden")

    def show(self):
        """Show the file browser."""
        self.remove_class("hidden")

    def hide(self):
        """Hide the file browser."""
        self.add_class("hidden")

    def focus_tree(self):
        """Focus the directory tree for keyboard navigation."""
        tree = self.query_one(FilteredDirectoryTree)
        tree.focus()

    @property
    def is_visible(self) -> bool:
        """Check if file browser is visible."""
        return not self.has_class("hidden")

