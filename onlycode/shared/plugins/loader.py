# Only Code Editor - Plugin Loader
# Plugin discovery and loading

import json
from pathlib import Path
from typing import List, Dict, Optional, Callable, Any

from .models import Plugin, Trigger, Action, TriggerType


class PluginManager:
    """Manages plugin discovery, loading, and execution."""

    def __init__(self, plugins_dir: Optional[Path] = None):
        """
        Initialize the plugin manager.

        Args:
            plugins_dir: Directory containing plugins. Defaults to ~/.config/onlycode/plugins/
        """
        if plugins_dir is None:
            plugins_dir = Path.home() / ".config" / "onlycode" / "plugins"

        self._plugins_dir = plugins_dir
        self._plugins: Dict[str, Plugin] = {}  # name -> Plugin
        self._action_executor: Optional['ActionExecutor'] = None

        # Ensure plugins directory exists
        self._plugins_dir.mkdir(parents=True, exist_ok=True)

    def set_action_executor(self, executor: 'ActionExecutor'):
        """Set the action executor for running plugin actions."""
        self._action_executor = executor

    def load_plugins(self) -> List[Plugin]:
        """
        Discover and load all plugins from the plugins directory.

        Returns:
            List of loaded plugins (including those with errors)
        """
        self._plugins.clear()

        if not self._plugins_dir.exists():
            return []

        for plugin_dir in self._plugins_dir.iterdir():
            if plugin_dir.is_dir():
                plugin = self._load_plugin(plugin_dir)
                if plugin:
                    self._plugins[plugin.name] = plugin

        return list(self._plugins.values())

    def _load_plugin(self, plugin_dir: Path) -> Optional[Plugin]:
        """
        Load a single plugin from a directory.

        Args:
            plugin_dir: Path to the plugin directory

        Returns:
            Loaded Plugin or None if invalid
        """
        plugin_json = plugin_dir / "plugin.json"

        if not plugin_json.exists():
            return None

        try:
            with open(plugin_json, 'r', encoding='utf-8') as f:
                data = json.load(f)

            plugin = Plugin.from_dict(data, plugin_dir)
            return plugin

        except json.JSONDecodeError as e:
            # Return plugin with error
            return Plugin(
                name=plugin_dir.name,
                version="0.0.0",
                description="",
                author="",
                path=plugin_dir,
                enabled=False,
                error=f"Invalid JSON: {e}"
            )
        except Exception as e:
            return Plugin(
                name=plugin_dir.name,
                version="0.0.0",
                description="",
                author="",
                path=plugin_dir,
                enabled=False,
                error=f"Failed to load: {e}"
            )

    def get_plugins(self) -> List[Plugin]:
        """Get all loaded plugins."""
        return list(self._plugins.values())

    def get_enabled_plugins(self) -> List[Plugin]:
        """Get all enabled plugins without errors."""
        return [p for p in self._plugins.values() if p.enabled and not p.error]

    def get_plugin(self, name: str) -> Optional[Plugin]:
        """Get a plugin by name."""
        return self._plugins.get(name)

    def get_all_commands(self) -> List[Dict[str, Any]]:
        """
        Get all command triggers from enabled plugins.

        Returns:
            List of dicts with plugin_name, trigger, command_name, shortcut
        """
        commands = []
        for plugin in self.get_enabled_plugins():
            for trigger in plugin.get_command_triggers():
                commands.append({
                    'plugin_name': plugin.name,
                    'trigger': trigger,
                    'command_name': trigger.command_name or trigger.id,
                    'shortcut': trigger.shortcut
                })
        return commands

    def execute_trigger(self, plugin_name: str, trigger_id: str, context: Dict[str, Any]) -> bool:
        """
        Execute a trigger's action.

        Args:
            plugin_name: Name of the plugin
            trigger_id: ID of the trigger
            context: Execution context (editor, file_path, etc.)

        Returns:
            True if successful, False otherwise
        """
        plugin = self.get_plugin(plugin_name)
        if not plugin or not plugin.enabled or plugin.error:
            return False

        # Find the trigger
        trigger = next((t for t in plugin.triggers if t.id == trigger_id), None)
        if not trigger:
            return False

        # Get the action
        action = plugin.get_action(trigger.action_id)
        if not action:
            return False

        # Execute via action executor
        if self._action_executor:
            # Set plugin base path for script resolution
            self._action_executor.set_plugin_base_path(plugin.path)
            return self._action_executor.execute(action, context)

        return False

    def on_file_save(self, file_path: Path, language: Optional[str], context: Dict[str, Any]):
        """
        Handle file save event - execute on_save triggers.

        Args:
            file_path: Path of saved file
            language: Detected language/file type
            context: Execution context
        """
        for plugin in self.get_enabled_plugins():
            for trigger in plugin.get_on_save_triggers():
                if trigger.context.matches(language, file_path):
                    action = plugin.get_action(trigger.action_id)
                    if action and self._action_executor:
                        self._action_executor.set_plugin_base_path(plugin.path)
                        self._action_executor.execute(action, context)

    def on_file_open(self, file_path: Path, language: Optional[str], context: Dict[str, Any]):
        """
        Handle file open event - execute on_open triggers.

        Args:
            file_path: Path of opened file
            language: Detected language/file type
            context: Execution context
        """
        for plugin in self.get_enabled_plugins():
            for trigger in plugin.get_on_open_triggers():
                if trigger.context.matches(language, file_path):
                    action = plugin.get_action(trigger.action_id)
                    if action and self._action_executor:
                        self._action_executor.set_plugin_base_path(plugin.path)
                        self._action_executor.execute(action, context)
