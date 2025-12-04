# Only Code Editor - Plugin Actions
# Built-in action implementations

import subprocess
import re
from typing import Dict, Any, Optional, Callable
from pathlib import Path

from .models import Action, ActionType
from .scripting import EditorAPI, LuaEngine, PythonEngine, LUPA_AVAILABLE


class ActionExecutor:
    """Executes plugin actions."""

    def __init__(self):
        """Initialize the action executor."""
        self._notify_callback: Optional[Callable[[str, str], None]] = None
        self._get_editor_text: Optional[Callable[[], str]] = None
        self._set_editor_text: Optional[Callable[[str], None]] = None
        self._get_selection: Optional[Callable[[], str]] = None
        self._replace_selection: Optional[Callable[[str], None]] = None
        self._insert_text: Optional[Callable[[str], None]] = None
        self._get_cursor_position: Optional[Callable[[], tuple]] = None
        self._set_cursor_position: Optional[Callable[[int, int], None]] = None
        self._get_file_path: Optional[Callable[[], Optional[Path]]] = None
        self._get_language: Optional[Callable[[], str]] = None
        self._plugin_base_path: Optional[Path] = None  # Set per-plugin execution

    def set_callbacks(self,
                      notify: Callable[[str, str], None] = None,
                      get_editor_text: Callable[[], str] = None,
                      set_editor_text: Callable[[str], None] = None,
                      get_selection: Callable[[], str] = None,
                      replace_selection: Callable[[str], None] = None,
                      insert_text: Callable[[str], None] = None,
                      get_cursor_position: Callable[[], tuple] = None,
                      set_cursor_position: Callable[[int, int], None] = None,
                      get_file_path: Callable[[], Optional[Path]] = None,
                      get_language: Callable[[], str] = None):
        """Set callbacks for editor interaction."""
        if notify:
            self._notify_callback = notify
        if get_editor_text:
            self._get_editor_text = get_editor_text
        if set_editor_text:
            self._set_editor_text = set_editor_text
        if get_selection:
            self._get_selection = get_selection
        if replace_selection:
            self._replace_selection = replace_selection
        if insert_text:
            self._insert_text = insert_text
        if get_cursor_position:
            self._get_cursor_position = get_cursor_position
        if set_cursor_position:
            self._set_cursor_position = set_cursor_position
        if get_file_path:
            self._get_file_path = get_file_path
        if get_language:
            self._get_language = get_language

    def set_plugin_base_path(self, path: Path):
        """Set the base path for the current plugin (for resolving script paths)."""
        self._plugin_base_path = path

    def execute(self, action: Action, context: Dict[str, Any]) -> bool:
        """
        Execute an action.

        Args:
            action: The action to execute
            context: Execution context (may contain editor, file_path, etc.)

        Returns:
            True if successful, False otherwise
        """
        try:
            if action.type == ActionType.EXTERNAL_COMMAND:
                return self._execute_external_command(action, context)
            elif action.type == ActionType.SNIPPET:
                return self._execute_snippet(action, context)
            elif action.type == ActionType.TRANSFORM:
                return self._execute_transform(action, context)
            elif action.type == ActionType.NOTIFY:
                return self._execute_notify(action, context)
            elif action.type == ActionType.CHAIN:
                return self._execute_chain(action, context)
            elif action.type == ActionType.SCRIPT:
                return self._execute_script(action, context)
            else:
                self._notify("Plugin Error", f"Unknown action type: {action.type}")
                return False
        except Exception as e:
            self._notify("Plugin Error", f"Action failed: {e}")
            return False

    def _notify(self, title: str, message: str):
        """Show a notification."""
        if self._notify_callback:
            self._notify_callback(title, message)
        else:
            print(f"[{title}] {message}")

    def _execute_external_command(self, action: Action, context: Dict[str, Any]) -> bool:
        """
        Execute an external shell command.

        Config options:
            command: The shell command to run
            input: "file_contents" | "selection" | "none"
            output: "replace_file_contents" | "replace_selection" | "insert" | "notify" | "none"
            working_dir: Optional working directory
        """
        config = action.config
        command = config.get('command')
        if not command:
            self._notify("Plugin Error", "No command specified")
            return False

        input_type = config.get('input', 'none')
        output_type = config.get('output', 'none')
        working_dir = config.get('working_dir')

        # Prepare input
        stdin_data = None
        if input_type == 'file_contents' and self._get_editor_text:
            stdin_data = self._get_editor_text()
        elif input_type == 'selection' and self._get_selection:
            stdin_data = self._get_selection()

        # Determine working directory
        cwd = None
        if working_dir:
            cwd = working_dir
        elif self._get_file_path:
            file_path = self._get_file_path()
            if file_path:
                cwd = str(file_path.parent)

        # Run command
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                input=stdin_data,
                cwd=cwd,
                timeout=30  # 30 second timeout
            )

            if result.returncode != 0:
                error_msg = result.stderr or f"Command exited with code {result.returncode}"
                self._notify("Command Failed", error_msg[:200])
                return False

            output = result.stdout

            # Handle output
            if output_type == 'replace_file_contents' and self._set_editor_text:
                self._set_editor_text(output)
            elif output_type == 'replace_selection' and self._replace_selection:
                self._replace_selection(output)
            elif output_type == 'insert' and self._insert_text:
                self._insert_text(output)
            elif output_type == 'notify':
                self._notify("Command Output", output[:500])

            return True

        except subprocess.TimeoutExpired:
            self._notify("Command Timeout", "Command took too long to execute")
            return False
        except Exception as e:
            self._notify("Command Error", str(e))
            return False

    def _execute_snippet(self, action: Action, context: Dict[str, Any]) -> bool:
        """
        Insert a snippet with variable substitution.

        Config options:
            template: The text template to insert
            variables: Dict of variable names to values (or "selection", "file_name", etc.)
        """
        config = action.config
        template = config.get('template', '')
        variables = config.get('variables', {})

        # Build variable values
        var_values = {}
        for var_name, var_source in variables.items():
            if var_source == 'selection' and self._get_selection:
                var_values[var_name] = self._get_selection()
            elif var_source == 'file_name' and self._get_file_path:
                file_path = self._get_file_path()
                var_values[var_name] = file_path.name if file_path else ''
            elif var_source == 'file_path' and self._get_file_path:
                file_path = self._get_file_path()
                var_values[var_name] = str(file_path) if file_path else ''
            elif var_source == 'date':
                from datetime import datetime
                var_values[var_name] = datetime.now().strftime('%Y-%m-%d')
            elif var_source == 'datetime':
                from datetime import datetime
                var_values[var_name] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            else:
                # Use as literal value
                var_values[var_name] = str(var_source)

        # Substitute variables in template
        result = template
        for var_name, var_value in var_values.items():
            result = result.replace(f'${{{var_name}}}', var_value)
            result = result.replace(f'${var_name}', var_value)

        # Insert the result
        if self._insert_text:
            self._insert_text(result)
            return True

        return False

    def _execute_transform(self, action: Action, context: Dict[str, Any]) -> bool:
        """
        Apply a text transformation.

        Config options:
            transform: The transformation to apply
                - "uppercase", "lowercase", "titlecase"
                - "sort_lines", "reverse_lines", "unique_lines"
                - "trim_whitespace", "remove_blank_lines"
            target: "selection" | "file_contents" (default: selection)
        """
        config = action.config
        transform = config.get('transform', '')
        target = config.get('target', 'selection')

        # Get text to transform
        if target == 'selection' and self._get_selection:
            text = self._get_selection()
            replace_func = self._replace_selection
        elif target == 'file_contents' and self._get_editor_text:
            text = self._get_editor_text()
            replace_func = self._set_editor_text
        else:
            return False

        if not text:
            return False

        # Apply transformation
        result = self._apply_transform(text, transform)

        # Replace with result
        if replace_func and result is not None:
            replace_func(result)
            return True

        return False

    def _apply_transform(self, text: str, transform: str) -> Optional[str]:
        """Apply a specific transformation to text."""
        if transform == 'uppercase':
            return text.upper()
        elif transform == 'lowercase':
            return text.lower()
        elif transform == 'titlecase':
            return text.title()
        elif transform == 'sort_lines':
            lines = text.split('\n')
            return '\n'.join(sorted(lines))
        elif transform == 'reverse_lines':
            lines = text.split('\n')
            return '\n'.join(reversed(lines))
        elif transform == 'unique_lines':
            lines = text.split('\n')
            seen = set()
            unique = []
            for line in lines:
                if line not in seen:
                    seen.add(line)
                    unique.append(line)
            return '\n'.join(unique)
        elif transform == 'trim_whitespace':
            lines = text.split('\n')
            return '\n'.join(line.rstrip() for line in lines)
        elif transform == 'remove_blank_lines':
            lines = text.split('\n')
            return '\n'.join(line for line in lines if line.strip())
        else:
            self._notify("Transform Error", f"Unknown transform: {transform}")
            return None

    def _execute_notify(self, action: Action, context: Dict[str, Any]) -> bool:
        """
        Show a notification message.

        Config options:
            title: Notification title
            message: Notification message
        """
        config = action.config
        title = config.get('title', 'Plugin')
        message = config.get('message', '')

        self._notify(title, message)
        return True

    def _execute_chain(self, action: Action, context: Dict[str, Any]) -> bool:
        """
        Execute multiple actions in sequence.

        Config options:
            actions: List of action configs to execute in order
        """
        config = action.config
        actions_list = config.get('actions', [])

        for i, action_config in enumerate(actions_list):
            try:
                # Create a temporary action from config
                action_type = ActionType(action_config.get('type'))
                temp_action = Action(
                    id=f"{action.id}_chain_{i}",
                    type=action_type,
                    config={k: v for k, v in action_config.items() if k != 'type'}
                )

                if not self.execute(temp_action, context):
                    return False

            except Exception as e:
                self._notify("Chain Error", f"Action {i} failed: {e}")
                return False

        return True

    def _execute_script(self, action: Action, context: Dict[str, Any]) -> bool:
        """
        Execute a Lua or Python script.

        Config options:
            engine: "lua" or "python"
            file: Path to script file (relative to plugin directory)
            entry_point: Optional function name to call
            code: Optional inline code (if file not specified)
        """
        config = action.config
        engine_type = config.get('engine', 'lua').lower()
        script_file = config.get('file')
        entry_point = config.get('entry_point')
        inline_code = config.get('code')

        # Create EditorAPI instance
        editor_api = EditorAPI(
            get_text=self._get_editor_text,
            set_text=self._set_editor_text,
            get_selection=self._get_selection,
            replace_selection=self._replace_selection,
            insert_text=self._insert_text,
            get_cursor_position=self._get_cursor_position,
            set_cursor_position=self._set_cursor_position,
            get_file_path=self._get_file_path,
            get_language=self._get_language,
            show_notification=self._notify_callback,
        )

        # Create appropriate engine
        if engine_type == 'lua':
            if not LUPA_AVAILABLE:
                self._notify("Script Error", "Lua engine not available. Install lupa: pip install lupa")
                return False
            engine = LuaEngine(editor_api)
        elif engine_type == 'python':
            engine = PythonEngine(editor_api)
        else:
            self._notify("Script Error", f"Unknown script engine: {engine_type}")
            return False

        # Execute script
        if script_file:
            # Resolve path relative to plugin directory
            if self._plugin_base_path:
                script_path = self._plugin_base_path / script_file
            else:
                script_path = Path(script_file)

            success = engine.execute_file(script_path, entry_point)
        elif inline_code:
            success = engine.execute_string(inline_code, entry_point)
        else:
            self._notify("Script Error", "No script file or inline code specified")
            return False

        if not success:
            error = engine.get_last_error()
            self._notify("Script Error", error or "Unknown error")
            return False

        return True
