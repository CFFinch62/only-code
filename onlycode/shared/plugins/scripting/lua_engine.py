# Only Code Editor - Lua Scripting Engine
# Lua script execution and sandboxing

from typing import Optional, Any
from pathlib import Path

try:
    from lupa import LuaRuntime
    LUPA_AVAILABLE = True
except ImportError:
    LUPA_AVAILABLE = False

from .editor_api import EditorAPI


class LuaEngine:
    """
    Lua script execution engine with sandboxing.

    Provides a secure environment for running Lua scripts with
    access to the editor API but no file system or network access.
    """

    # Safe Lua builtins to expose
    SAFE_BUILTINS = [
        'assert', 'error', 'ipairs', 'next', 'pairs', 'pcall',
        'print', 'select', 'tonumber', 'tostring', 'type',
        'unpack', 'xpcall', '_VERSION',
    ]

    # Safe modules/tables to expose
    SAFE_MODULES = ['string', 'table', 'math']

    def __init__(self, editor_api: EditorAPI):
        """
        Initialize the Lua engine.

        Args:
            editor_api: EditorAPI instance for editor interaction
        """
        if not LUPA_AVAILABLE:
            raise ImportError("lupa library not available. Install with: pip install lupa")

        self.editor_api = editor_api
        self._lua: Optional[LuaRuntime] = None
        self._last_error: Optional[str] = None

    def _create_runtime(self) -> LuaRuntime:
        """Create a new sandboxed Lua runtime."""
        # Create Lua runtime with restricted globals
        lua = LuaRuntime(unpack_returned_tuples=True)

        # Get access to globals
        g = lua.globals()

        # Store original modules we want to keep
        safe_globals = {}
        for name in self.SAFE_BUILTINS:
            if g[name] is not None:
                safe_globals[name] = g[name]

        for name in self.SAFE_MODULES:
            if g[name] is not None:
                safe_globals[name] = g[name]

        # Clear dangerous globals
        dangerous = ['io', 'os', 'loadfile', 'dofile', 'load', 'loadstring',
                     'require', 'package', 'debug', 'rawget', 'rawset',
                     'rawequal', 'setfenv', 'getfenv', 'newproxy',
                     'collectgarbage', 'gcinfo', 'module']

        for name in dangerous:
            g[name] = None

        # Re-add safe globals (in case we cleared something we wanted)
        for name, value in safe_globals.items():
            g[name] = value

        # Add editor API
        self._expose_editor_api(lua)

        return lua

    def _expose_editor_api(self, lua: LuaRuntime) -> None:
        """Expose the editor API to Lua as a global 'editor' table."""
        g = lua.globals()

        # Create editor table using Lua
        lua.execute("""
            editor = {}
        """)

        editor_table = g.editor

        # Expose API methods
        editor_table.get_text = self.editor_api.get_text
        editor_table.set_text = self.editor_api.set_text
        editor_table.get_selection = self.editor_api.get_selection
        editor_table.replace_selection = self.editor_api.replace_selection
        editor_table.insert_text = self.editor_api.insert_text
        editor_table.get_file_path = self.editor_api.get_file_path
        editor_table.get_language = self.editor_api.get_language
        editor_table.show_notification = self.editor_api.show_notification

        # Cursor position needs special handling (returns table)
        def get_cursor_pos():
            pos = self.editor_api.get_cursor_position()
            # Return as a Lua table
            result = lua.table()
            result.line = pos['line']
            result.column = pos['column']
            return result

        def set_cursor_pos(line, column):
            self.editor_api.set_cursor_position(int(line), int(column))

        editor_table.get_cursor_position = get_cursor_pos
        editor_table.set_cursor_position = set_cursor_pos

    def execute_file(self, file_path: Path, entry_point: str = None) -> bool:
        """
        Execute a Lua script file.

        Args:
            file_path: Path to the Lua script
            entry_point: Optional function name to call after loading

        Returns:
            True if successful, False otherwise
        """
        try:
            if not file_path.exists():
                self._last_error = f"Script file not found: {file_path}"
                return False

            code = file_path.read_text(encoding='utf-8')
            return self.execute_string(code, entry_point)

        except Exception as e:
            self._last_error = f"Failed to read script: {e}"
            return False

    def execute_string(self, code: str, entry_point: str = None) -> bool:
        """
        Execute Lua code from a string.

        Args:
            code: Lua code to execute
            entry_point: Optional function name to call after loading

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create fresh runtime for each execution (security)
            self._lua = self._create_runtime()

            # Execute the code
            self._lua.execute(code)

            # Call entry point if specified
            if entry_point:
                g = self._lua.globals()
                func = g[entry_point]
                if func is None:
                    self._last_error = f"Entry point '{entry_point}' not found"
                    return False
                func()

            self._last_error = None
            return True

        except Exception as e:
            self._last_error = str(e)
            return False

    def get_last_error(self) -> Optional[str]:
        """Get the last error message, if any."""
        return self._last_error
