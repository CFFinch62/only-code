from textual.app import App, ComposeResult
from onlycode.app.screens.main_screen import MainScreen

class OnlyCodeApp(App):
    """A terminal-based code editor."""

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit"),
    ]

    def on_mount(self) -> None:
        self.push_screen(MainScreen())

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark
