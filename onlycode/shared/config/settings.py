# Only Code Editor - Settings
# Settings dataclasses and schemas

from dataclasses import dataclass
from typing import Optional


@dataclass
class EditorSettings:
    """Editor behavior settings."""
    font_family: str = "JetBrains Mono"
    font_size: int = 14
    tab_width: int = 4
    use_spaces: bool = True
    word_wrap: bool = False
    line_numbers: bool = True
    highlight_current_line: bool = True
    auto_indent: bool = True


@dataclass
class FileBrowserSettings:
    """File browser settings."""
    font_size: int = 11
    default_directory: str = ""
    bookmarks: list = None  # List of bookmark paths

    def __post_init__(self):
        if self.bookmarks is None:
            self.bookmarks = []


@dataclass
class UISettings:
    """UI appearance and behavior settings."""
    theme: str = "default-dark"
    show_status_bar: bool = True
    panel_animation_duration_ms: int = 250
    enable_panel_animations: bool = True
    hover_edge_threshold_px: int = 5


@dataclass
class BehaviorSettings:
    """Application behavior settings."""
    remember_open_files: bool = True


@dataclass
class Settings:
    """Complete application settings."""
    editor: EditorSettings
    ui: UISettings
    behavior: BehaviorSettings
    file_browser: FileBrowserSettings = None

    def __post_init__(self):
        if self.file_browser is None:
            self.file_browser = FileBrowserSettings()

    @classmethod
    def default(cls) -> 'Settings':
        """Create settings with default values."""
        return cls(
            editor=EditorSettings(),
            ui=UISettings(),
            behavior=BehaviorSettings(),
            file_browser=FileBrowserSettings()
        )
