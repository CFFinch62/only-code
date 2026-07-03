# Only Code Editor - File Browser Widget
from textual import events
from textual.widgets import DirectoryTree, Static
from textual.containers import Vertical, ScrollableContainer
from textual.widget import Widget
from textual.reactive import reactive
from textual.message import Message
from textual.binding import Binding
from pathlib import Path
from typing import Iterable
import os


class FilteredDirectoryTree(DirectoryTree):
    """DirectoryTree that hides hidden files (starting with .)"""

    class DirectoryOpened(Message):
        """Sent when a directory node is double-clicked."""
        def __init__(self, path: str):
            super().__init__()
            self.path = path

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        """Filter out hidden files and directories."""
        return [p for p in paths if not p.name.startswith(".")]

    async def _on_click(self, event: events.Click) -> None:
        """Double-clicking a directory opens it as the new browser root."""
        if event.chain == 2:
            line = event.style.meta.get("line")
            if line is not None:
                node = self.get_node_at_line(line)
                if node is not None and node.data is not None and node.data.path.is_dir():
                    event.stop()
                    event.prevent_default()
                    self.post_message(self.DirectoryOpened(str(node.data.path)))
                    return
        await super()._on_click(event)


class FileBrowser(Widget):
    """File browser panel with directory tree."""

    DEFAULT_CSS = """
    FileBrowser {
        width: 35;
        height: 100%;
        border-right: solid $primary;
        background: $surface;
    }

    FileBrowser.hidden {
        display: none;
    }

    FileBrowser #browser-header {
        dock: top;
        height: 1;
        background: $primary;
        color: $text;
        padding: 0 1;
    }

    FileBrowser #browser-path {
        dock: top;
        height: 1;
        background: $surface-darken-1;
        color: $text-muted;
        padding: 0 1;
        text-style: italic;
    }

    FileBrowser #tree-container {
        height: 1fr;
        overflow-x: auto;
        overflow-y: auto;
    }

    FileBrowser DirectoryTree {
        width: auto;
        min-width: 100%;
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
        yield Static("📁 Files", id="browser-header")
        yield Static(self._get_short_path(), id="browser-path")
        with ScrollableContainer(id="tree-container"):
            yield FilteredDirectoryTree(self.root_path, id="file-tree")

    def _get_short_path(self) -> str:
        """Get shortened path for display (replace home with ~)."""
        path = self.root_path
        home = str(Path.home())
        if path.startswith(home):
            path = "~" + path[len(home):]
        # Truncate if too long
        if len(path) > 32:
            path = "..." + path[-29:]
        return path

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected):
        """Handle file selection - open in editor."""
        self.post_message(self.FileSelected(str(event.path)))

    def on_filtered_directory_tree_directory_opened(
        self, event: FilteredDirectoryTree.DirectoryOpened
    ) -> None:
        """Handle a double-clicked directory - make it the new browser root."""
        event.stop()
        self.set_root(event.path)
        self.post_message(self.DirectoryChanged(event.path))
        self.notify(f"Browse: {self._get_short_path()}")

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

    def get_target_directory(self) -> str:
        """Directory to create new files/folders in: the directory
        highlighted in the tree (or its parent, if a file is highlighted),
        falling back to the browser root."""
        tree = self.query_one(FilteredDirectoryTree)
        node = tree.cursor_node
        if node is not None and node.data is not None:
            path = node.data.path
            return str(path if path.is_dir() else path.parent)
        return self.root_path

    def reload(self) -> None:
        """Refresh the directory tree contents."""
        self.query_one(FilteredDirectoryTree).reload()

    def set_root(self, path: str) -> None:
        """Change the root directory of the file browser."""
        self.root_path = os.path.abspath(path)
        # Update the path display
        path_label = self.query_one("#browser-path", Static)
        path_label.update(self._get_short_path())
        # Update the directory tree path (reactive property handles the rest)
        tree = self.query_one(FilteredDirectoryTree)
        tree.path = self.root_path

