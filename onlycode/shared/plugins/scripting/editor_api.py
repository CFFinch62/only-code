# Only Code Editor - Editor API for Scripts
# Provides a safe interface for scripts to interact with the editor

from typing import Dict, Any, Optional, Callable
from pathlib import Path


class EditorAPI:
    """
    API object passed to scripts for editor interaction.
    
    This class wraps the editor callbacks and provides a clean interface
    for Lua and Python scripts to interact with the editor.
    """

    def __init__(self,
                 get_text: Callable[[], str] = None,
                 set_text: Callable[[str], None] = None,
                 get_selection: Callable[[], str] = None,
                 replace_selection: Callable[[str], None] = None,
                 insert_text: Callable[[str], None] = None,
                 get_cursor_position: Callable[[], tuple] = None,
                 set_cursor_position: Callable[[int, int], None] = None,
                 get_file_path: Callable[[], Optional[Path]] = None,
                 get_language: Callable[[], str] = None,
                 show_notification: Callable[[str, str], None] = None):
        """
        Initialize the Editor API.
        
        Args:
            get_text: Callback to get full editor text
            set_text: Callback to set full editor text
            get_selection: Callback to get selected text
            replace_selection: Callback to replace selection
            insert_text: Callback to insert text at cursor
            get_cursor_position: Callback to get cursor (line, col)
            set_cursor_position: Callback to set cursor position
            get_file_path: Callback to get current file path
            get_language: Callback to get current language
            show_notification: Callback to show notification (title, message)
        """
        self._get_text = get_text
        self._set_text = set_text
        self._get_selection = get_selection
        self._replace_selection = replace_selection
        self._insert_text = insert_text
        self._get_cursor_position = get_cursor_position
        self._set_cursor_position = set_cursor_position
        self._get_file_path = get_file_path
        self._get_language = get_language
        self._show_notification = show_notification

    def get_text(self) -> str:
        """Get the full editor text."""
        if self._get_text:
            return self._get_text()
        return ""

    def set_text(self, text: str) -> None:
        """Replace the full editor text."""
        if self._set_text:
            self._set_text(str(text))

    def get_selection(self) -> str:
        """Get the currently selected text."""
        if self._get_selection:
            return self._get_selection()
        return ""

    def replace_selection(self, text: str) -> None:
        """Replace the current selection with new text."""
        if self._replace_selection:
            self._replace_selection(str(text))

    def insert_text(self, text: str) -> None:
        """Insert text at the current cursor position."""
        if self._insert_text:
            self._insert_text(str(text))

    def get_cursor_position(self) -> Dict[str, int]:
        """
        Get the current cursor position.
        
        Returns:
            Dictionary with 'line' and 'column' keys (1-based)
        """
        if self._get_cursor_position:
            line, col = self._get_cursor_position()
            return {"line": line + 1, "column": col + 1}  # Convert to 1-based
        return {"line": 1, "column": 1}

    def set_cursor_position(self, line: int, column: int) -> None:
        """
        Set the cursor position.
        
        Args:
            line: Line number (1-based)
            column: Column number (1-based)
        """
        if self._set_cursor_position:
            # Convert from 1-based to 0-based
            self._set_cursor_position(max(0, line - 1), max(0, column - 1))

    def get_file_path(self) -> str:
        """Get the current file path, or empty string if no file."""
        if self._get_file_path:
            path = self._get_file_path()
            return str(path) if path else ""
        return ""

    def get_language(self) -> str:
        """Get the current file's language."""
        if self._get_language:
            return self._get_language()
        return ""

    def show_notification(self, message: str, title: str = "Plugin") -> None:
        """
        Show a notification to the user.
        
        Args:
            message: The notification message
            title: The notification title (default: "Plugin")
        """
        if self._show_notification:
            self._show_notification(str(title), str(message))

