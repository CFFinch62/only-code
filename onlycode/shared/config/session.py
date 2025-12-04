# Only Code Editor - Session Management
# Save and restore open files between sessions

import json
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass, asdict


@dataclass
class SessionData:
    """Data stored in session file."""
    open_files: List[str]  # List of file paths
    active_tab_index: int = 0
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SessionData':
        return cls(
            open_files=data.get('open_files', []),
            active_tab_index=data.get('active_tab_index', 0)
        )


class SessionManager:
    """Manages session persistence."""
    
    def __init__(self):
        """Initialize session manager."""
        self._session_file = self._get_session_file_path()
    
    def _get_session_file_path(self) -> Path:
        """Get the session file path."""
        # Use XDG_CONFIG_HOME or default to ~/.config
        config_home = Path.home() / ".config" / "onlycode"
        config_home.mkdir(parents=True, exist_ok=True)
        return config_home / "session.json"
    
    def save_session(self, open_files: List[Path], active_tab_index: int = 0):
        """
        Save session data to file.
        
        Args:
            open_files: List of open file paths
            active_tab_index: Index of the currently active tab
        """
        # Convert paths to strings, only save files that exist
        file_paths = []
        for f in open_files:
            if f and f.exists():
                file_paths.append(str(f))
        
        session = SessionData(
            open_files=file_paths,
            active_tab_index=active_tab_index
        )
        
        try:
            with open(self._session_file, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save session: {e}")
    
    def load_session(self) -> Optional[SessionData]:
        """
        Load session data from file.
        
        Returns:
            SessionData if file exists and is valid, None otherwise
        """
        if not self._session_file.exists():
            return None
        
        try:
            with open(self._session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return SessionData.from_dict(data)
        except Exception as e:
            print(f"Warning: Could not load session: {e}")
            return None
    
    def clear_session(self):
        """Clear the session file."""
        if self._session_file.exists():
            try:
                self._session_file.unlink()
            except Exception:
                pass

