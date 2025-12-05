# Only Code Editor - Terminal Panel Widget
"""
Simple command runner panel using Log for output and Input for commands.
"""
from textual.widgets import Static, Input, Log
from textual.containers import Vertical
from textual.widget import Widget
from textual.message import Message
from textual.binding import Binding
from pathlib import Path
import subprocess
import asyncio
import os


class TerminalPanel(Widget):
    """Terminal panel with command input and output display."""

    DEFAULT_CSS = """
    TerminalPanel {
        height: 12;
        dock: bottom;
        border-top: solid $primary;
        background: $surface-darken-1;
    }

    TerminalPanel.hidden {
        display: none;
    }

    TerminalPanel #terminal-header {
        dock: top;
        height: 1;
        background: $primary;
        color: $text;
        padding: 0 1;
    }

    TerminalPanel #terminal-output {
        height: 1fr;
        background: $surface-darken-2;
        color: $text;
        padding: 0 1;
        scrollbar-gutter: stable;
    }

    TerminalPanel #terminal-input-container {
        dock: bottom;
        height: 3;
        padding: 0 1;
        background: $surface-darken-1;
    }

    TerminalPanel #terminal-prompt {
        width: auto;
        height: 1;
        color: $success;
        padding: 0;
    }

    TerminalPanel #terminal-input {
        height: 1;
        border: none;
        background: $surface-darken-2;
        padding: 0 1;
    }

    TerminalPanel #terminal-input:focus {
        border: none;
    }
    """

    BINDINGS = [
        Binding("escape", "focus_editor", "Back to Editor", show=False),
    ]

    class CommandExecuted(Message):
        """Message sent when a command is executed."""
        def __init__(self, command: str, output: str, return_code: int):
            super().__init__()
            self.command = command
            self.output = output
            self.return_code = return_code

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._working_dir = str(Path.home())
        self._command_history: list[str] = []
        self._history_index = -1
        self._running_process: asyncio.subprocess.Process | None = None

    def compose(self):
        yield Static(self._get_header(), id="terminal-header")
        yield Log(id="terminal-output", highlight=True, auto_scroll=True)
        with Vertical(id="terminal-input-container"):
            yield Static(self._get_prompt(), id="terminal-prompt")
            yield Input(placeholder="Enter command...", id="terminal-input")

    def _get_header(self) -> str:
        """Get terminal header with title and working directory."""
        return f"📟 Terminal - {self._working_dir}"

    def _get_prompt(self) -> str:
        """Get the command prompt."""
        return f"$ "

    def on_mount(self):
        """Set up terminal on mount."""
        output = self.query_one("#terminal-output", Log)
        output.write_line("Terminal ready. Type commands and press Enter.")
        output.write_line(f"Working directory: {self._working_dir}")
        output.write_line("")

    async def on_input_submitted(self, event: Input.Submitted):
        """Handle command submission."""
        if event.input.id != "terminal-input":
            return

        command = event.value.strip()
        if not command:
            return

        # Clear input
        event.input.value = ""

        # Add to history
        self._command_history.append(command)
        self._history_index = len(self._command_history)

        # Execute command
        await self._execute_command(command)

    async def _execute_command(self, command: str):
        """Execute a shell command and display output."""
        output = self.query_one("#terminal-output", Log)

        # Show the command being executed
        output.write_line(f"$ {command}")

        # Handle built-in commands
        if command.startswith("cd "):
            self._handle_cd(command[3:].strip())
            return
        elif command == "cd":
            self._handle_cd(str(Path.home()))
            return
        elif command == "clear":
            output.clear()
            return
        elif command == "pwd":
            output.write_line(self._working_dir)
            output.write_line("")
            return

        # Execute external command
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=self._working_dir,
            )
            self._running_process = process

            # Read output
            stdout, _ = await process.communicate()
            if stdout:
                for line in stdout.decode().splitlines():
                    output.write_line(line)

            # Show return code if non-zero
            if process.returncode != 0:
                output.write_line(f"[Exit code: {process.returncode}]")

            output.write_line("")
            self.post_message(self.CommandExecuted(command, stdout.decode() if stdout else "", process.returncode))

        except Exception as e:
            output.write_line(f"Error: {e}")
            output.write_line("")
        finally:
            self._running_process = None

    def _handle_cd(self, path: str):
        """Handle cd command."""
        output = self.query_one("#terminal-output", Log)

        # Handle ~ for home directory
        if path.startswith("~"):
            path = str(Path.home()) + path[1:]

        # Resolve relative paths
        if not os.path.isabs(path):
            path = os.path.join(self._working_dir, path)

        # Normalize path
        path = os.path.normpath(path)

        if os.path.isdir(path):
            self._working_dir = path
            # Update header
            header = self.query_one("#terminal-header", Static)
            header.update(self._get_header())
            output.write_line(f"Changed to: {path}")
        else:
            output.write_line(f"cd: {path}: No such directory")
        output.write_line("")

    def toggle(self) -> bool:
        """Toggle visibility of the terminal panel."""
        self.toggle_class("hidden")
        return not self.has_class("hidden")

    def show(self):
        """Show the terminal panel."""
        self.remove_class("hidden")

    def hide(self):
        """Hide the terminal panel."""
        self.add_class("hidden")

    def focus_input(self):
        """Focus the command input."""
        input_widget = self.query_one("#terminal-input", Input)
        input_widget.focus()

    @property
    def is_visible(self) -> bool:
        """Check if terminal panel is visible."""
        return not self.has_class("hidden")

    @property
    def working_directory(self) -> str:
        """Get the current working directory."""
        return self._working_dir

    def set_working_directory(self, path: str):
        """Set the working directory."""
        if os.path.isdir(path):
            self._working_dir = path
            header = self.query_one("#terminal-header", Static)
            header.update(self._get_header())

    def action_focus_editor(self):
        """Action to return focus to editor (handled by parent)."""
        # This will be handled by the parent screen
        pass

    def on_key(self, event):
        """Handle key events for command history."""
        input_widget = self.query_one("#terminal-input", Input)
        if not input_widget.has_focus:
            return

        if event.key == "up":
            # Previous command in history
            if self._command_history and self._history_index > 0:
                self._history_index -= 1
                input_widget.value = self._command_history[self._history_index]
                input_widget.cursor_position = len(input_widget.value)
            event.prevent_default()
            event.stop()
        elif event.key == "down":
            # Next command in history
            if self._history_index < len(self._command_history) - 1:
                self._history_index += 1
                input_widget.value = self._command_history[self._history_index]
                input_widget.cursor_position = len(input_widget.value)
            elif self._history_index == len(self._command_history) - 1:
                self._history_index = len(self._command_history)
                input_widget.value = ""
            event.prevent_default()
            event.stop()

