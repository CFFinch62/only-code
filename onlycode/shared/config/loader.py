# Only Code Editor - Config Loader
# JSON configuration loading and validation

import json
import os
import sys
import shutil
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Any, Optional, List

from .settings import Settings, EditorSettings, UISettings, BehaviorSettings, FileBrowserSettings


class ConfigLoader:
    """Loads and manages JSON configuration files."""

    def __init__(self):
        """Initialize the config loader."""
        self.config_dir = self._get_config_dir()
        self.default_config_dir = self._get_default_config_dir()

        # On first run, copy defaults to user config directory
        self._ensure_user_configs()

    def _get_config_dir(self) -> Path:
        """Get the user configuration directory."""
        # Use XDG standard: ~/.config/onlycode/
        config_home = os.environ.get('XDG_CONFIG_HOME')
        if config_home:
            return Path(config_home) / 'onlycode'
        return Path.home() / '.config' / 'onlycode'

    def _get_default_config_dir(self) -> Path:
        """Get the default configuration directory (bundled with app)."""
        # Check if running from PyInstaller bundle
        if getattr(sys, 'frozen', False):
            # Running in PyInstaller bundle
            base_path = Path(sys._MEIPASS)
            return base_path / 'onlycode' / 'resources' / 'default_configs'
        else:
            # Running in development
            return Path(__file__).parent.parent / 'resources' / 'default_configs'

    def _ensure_user_configs(self):
        """
        Ensure user config directory exists and has config files.
        On first run, copies defaults to user directory.
        """
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # List of config files to ensure exist
        config_files = [
            'settings.json',
            'ui-themes.json',
            'syntax-themes.json',
            'keybindings.json',
            'languages.json',
        ]

        for filename in config_files:
            user_file = self.config_dir / filename
            default_file = self.default_config_dir / filename

            # Copy default to user dir if user file doesn't exist
            if not user_file.exists() and default_file.exists():
                # For settings.json, sanitize paths before copying
                if filename == 'settings.json':
                    self._copy_sanitized_settings(default_file, user_file)
                else:
                    shutil.copy2(default_file, user_file)

    def _copy_sanitized_settings(self, src: Path, dst: Path):
        """Copy settings.json with sanitized paths for new users."""
        try:
            with open(src, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Reset paths to sensible defaults for new users
            if 'file_browser' in data:
                data['file_browser']['default_directory'] = str(Path.home())
                data['file_browser']['bookmarks'] = [str(Path.home())]

            with open(dst, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception:
            # Fall back to direct copy if sanitization fails
            shutil.copy2(src, dst)
    
    def _load_json(self, filename: str) -> Dict[str, Any]:
        """
        Load a JSON config file.
        
        Tries user config first, falls back to default config.
        """
        # Try user config first
        user_file = self.config_dir / filename
        if user_file.exists():
            try:
                with open(user_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load user config {filename}: {e}")
                # Fall through to default
        
        # Fall back to default config
        default_file = self.default_config_dir / filename
        if default_file.exists():
            with open(default_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Return empty dict if neither exists
        return {}
    
    def load_settings(self) -> Settings:
        """Load application settings from settings.json."""
        data = self._load_json('settings.json')

        # Extract nested settings with defaults
        editor_data = data.get('editor', {})
        ui_data = data.get('ui', {})
        behavior_data = data.get('behavior', {})
        file_browser_data = data.get('file_browser', {})

        return Settings(
            editor=EditorSettings(**editor_data) if editor_data else EditorSettings(),
            ui=UISettings(**ui_data) if ui_data else UISettings(),
            behavior=BehaviorSettings(**behavior_data) if behavior_data else BehaviorSettings(),
            file_browser=FileBrowserSettings(**file_browser_data) if file_browser_data else FileBrowserSettings()
        )
    
    def load_ui_theme(self, theme_name: str) -> Dict[str, str]:
        """Load a UI theme by name."""
        data = self._load_json('ui-themes.json')
        themes = data.get('themes', {})
        return themes.get(theme_name, themes.get('default-dark', {}))
    
    def load_syntax_theme(self, theme_name: str) -> Dict[str, str]:
        """Load a syntax theme by name."""
        data = self._load_json('syntax-themes.json')
        themes = data.get('themes', {})
        return themes.get(theme_name, themes.get('default', {}))
    
    def load_keybindings(self) -> Dict[str, str]:
        """Load keyboard shortcuts."""
        return self._load_json('keybindings.json')
    
    def load_language_config(self, language: str) -> Dict[str, Any]:
        """Load language-specific configuration."""
        data = self._load_json('languages.json')
        return data.get(language, {})
    
    def ensure_config_dir(self):
        """Ensure the user config directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def get_icon_path(self) -> Optional[Path]:
        """
        Get the path to the application icon.

        Returns PNG for Linux/macOS, ICO for Windows.
        Returns None if no icon is found.
        """
        # Determine which icon format to use
        if sys.platform == 'win32':
            icon_name = 'onlycode.ico'
        else:
            icon_name = 'onlycode.png'

        # Get the resources directory (handles both dev and bundled)
        if getattr(sys, 'frozen', False):
            base_path = Path(sys._MEIPASS)
            icons_dir = base_path / 'onlycode' / 'resources' / 'icons'
        else:
            icons_dir = Path(__file__).parent.parent / 'resources' / 'icons'

        icon_path = icons_dir / icon_name
        if icon_path.exists():
            return icon_path

        return None

    def get_ui_theme_names(self) -> List[str]:
        """Get list of all available UI theme names."""
        data = self._load_json('ui-themes.json')
        themes = data.get('themes', {})
        return list(themes.keys())

    def save_settings(self, settings: Settings):
        """
        Save settings to settings.json.

        Args:
            settings: Settings object to save
        """
        # Convert settings to dict
        data = {
            'editor': asdict(settings.editor),
            'ui': asdict(settings.ui),
            'behavior': asdict(settings.behavior),
            'file_browser': asdict(settings.file_browser)
        }

        # Save to default config location (for now)
        settings_file = self.default_config_dir / 'settings.json'

        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def get_config_file_path(self, filename: str) -> Path:
        """
        Get the path to a config file.

        Args:
            filename: Name of the config file

        Returns:
            Path to the config file
        """
        return self.default_config_dir / filename
