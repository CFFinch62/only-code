from textual.screen import ModalScreen
from textual.widgets import DirectoryTree, Input, Button, Label
from textual.containers import Vertical, Horizontal
from textual.events import Mount
from pathlib import Path
import os

class FileDialog(ModalScreen[str]):
    """Base file dialog."""

    DEFAULT_CSS = """
    FileDialog {
        align: center middle;
    }
    #dialog-container {
        width: 80%;
        height: 80%;
        border: solid $accent;
        background: $surface;
        padding: 1;
    }
    #path-display {
        height: 1;
        background: $primary-darken-2;
        padding: 0 1;
    }
    #file-tree {
        height: 1fr;
        border: solid $secondary;
    }
    #filename-input {
        margin: 1 0;
    }
    #buttons {
        height: auto;
        align: right middle;
    }
    Button {
        margin-left: 1;
    }
    """

    def __init__(self, title: str, initial_path: str | None = None):
        super().__init__()
        self.dialog_title = title
        # Default to home directory if no path specified
        if initial_path is None:
            initial_path = str(Path.home())
        self.initial_path = os.path.abspath(initial_path)
        self.selected_path = None
        self.current_dir = self.initial_path

    def compose(self):
        with Vertical(id="dialog-container"):
            yield Label(self.dialog_title)
            yield Label(self.initial_path, id="path-display")
            yield DirectoryTree(self.initial_path, id="file-tree")
            yield Input(placeholder="Filename", id="filename-input")
            with Horizontal(id="buttons"):
                yield Button("Cancel", variant="error", id="cancel")
                yield Button("Select", variant="primary", id="select")

    def on_mount(self):
        self.query_one(DirectoryTree).focus()

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected):
        self.selected_path = event.path
        self.current_dir = os.path.dirname(str(event.path))
        self.query_one(Input).value = os.path.basename(event.path)
        self._update_path_display()

    def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected):
        """Track directory changes for path display."""
        self.current_dir = str(event.path)
        self._update_path_display()

    def _update_path_display(self):
        """Update the path display label."""
        path_label = self.query_one("#path-display", Label)
        path_label.update(self.current_dir)

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "select":
            self._on_select()
        elif event.button.id == "cancel":
            self.dismiss(None)

    def _on_select(self):
        # To be implemented by subclasses or handled here
        filename = self.query_one(Input).value
        if not filename:
             return

        # Use the tracked current directory
        full_path = os.path.join(self.current_dir, filename)
        self.dismiss(full_path)

class OpenFileDialog(FileDialog):
    def __init__(self):
        super().__init__("Open File")

class SaveFileDialog(FileDialog):
    def __init__(self):
        super().__init__("Save File")


class ConfirmCloseDialog(ModalScreen[str]):
    """Dialog to confirm closing an unsaved file."""

    DEFAULT_CSS = """
    ConfirmCloseDialog {
        align: center middle;
    }
    #dialog-container {
        width: 50;
        height: auto;
        border: solid $accent;
        background: $surface;
        padding: 1 2;
    }
    #message {
        margin: 1 0;
        text-align: center;
    }
    #buttons {
        height: auto;
        align: center middle;
        margin-top: 1;
    }
    Button {
        margin: 0 1;
    }
    """

    def __init__(self, filename: str):
        super().__init__()
        self.filename = filename

    def compose(self):
        with Vertical(id="dialog-container"):
            yield Label(f"Unsaved changes in '{self.filename}'", id="message")
            with Horizontal(id="buttons"):
                yield Button("Save", variant="primary", id="save")
                yield Button("Discard", variant="warning", id="discard")
                yield Button("Cancel", variant="default", id="cancel")

    def on_button_pressed(self, event: Button.Pressed):
        self.dismiss(event.button.id)
