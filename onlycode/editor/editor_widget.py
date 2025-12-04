from textual.widgets import TextArea
from textual.binding import Binding

class OnlyCodeEditor(TextArea):
    """The core editor widget for Only Code."""

    BINDINGS = [
        Binding("ctrl+s", "save", "Save File"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.show_line_numbers = True
        # Default to python for now, will be dynamic later
        self.language = "python" 
        self.theme = "dracula" # Built-in textual theme

    def load_file(self, path: str) -> bool:
        """Load a file into the editor."""
        try:
            with open(path, "r") as f:
                self.text = f.read()
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
