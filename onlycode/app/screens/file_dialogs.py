from textual.screen import ModalScreen
from textual.widgets import DirectoryTree, Input, Button, Label
from textual.containers import Vertical, Horizontal
from textual.events import Mount
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

    def __init__(self, title: str, initial_path: str = "."):
        super().__init__()
        self.dialog_title = title
        self.initial_path = os.path.abspath(initial_path)
        self.selected_path = None

    def compose(self):
        with Vertical(id="dialog-container"):
            yield Label(self.dialog_title)
            yield DirectoryTree(self.initial_path, id="file-tree")
            yield Input(placeholder="Filename", id="filename-input")
            with Horizontal(id="buttons"):
                yield Button("Cancel", variant="error", id="cancel")
                yield Button("Select", variant="primary", id="select")

    def on_mount(self):
        self.query_one(DirectoryTree).focus()

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected):
        self.selected_path = event.path
        self.query_one(Input).value = os.path.basename(event.path)

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
        
        # If a file was selected in the tree, use its directory
        # Otherwise use the current directory of the tree
        tree = self.query_one(DirectoryTree)
        if self.selected_path:
             directory = os.path.dirname(self.selected_path)
        else:
             directory = tree.path
             
        full_path = os.path.join(directory, filename)
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
