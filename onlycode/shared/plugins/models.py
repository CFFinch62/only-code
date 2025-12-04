# Only Code Editor - Plugin Models
# Data structures for plugins, triggers, and actions

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from pathlib import Path


class TriggerType(Enum):
    """Types of triggers that can invoke plugin actions."""
    COMMAND = "command"      # Manual command (menu item)
    SHORTCUT = "shortcut"    # Keyboard shortcut
    ON_SAVE = "on_save"      # Triggered when file is saved
    ON_OPEN = "on_open"      # Triggered when file is opened


class ActionType(Enum):
    """Types of built-in actions."""
    EXTERNAL_COMMAND = "external_command"  # Run shell command
    SNIPPET = "snippet"                    # Insert text template
    TRANSFORM = "transform"                # Text transformation
    NOTIFY = "notify"                      # Show notification
    CHAIN = "chain"                        # Execute multiple actions
    SCRIPT = "script"                      # Run Lua/Python script (Phase 6)


@dataclass
class TriggerContext:
    """Context conditions for when a trigger should be active."""
    languages: List[str] = field(default_factory=list)  # File extensions/languages
    file_patterns: List[str] = field(default_factory=list)  # Glob patterns
    
    @classmethod
    def from_dict(cls, data: Optional[Dict]) -> 'TriggerContext':
        if not data:
            return cls()
        return cls(
            languages=data.get('languages', []),
            file_patterns=data.get('file_patterns', [])
        )
    
    def matches(self, language: Optional[str] = None, file_path: Optional[Path] = None) -> bool:
        """Check if context matches current conditions."""
        # If no restrictions, always match
        if not self.languages and not self.file_patterns:
            return True
        
        # Check language match
        if self.languages and language:
            if language.lower() in [lang.lower() for lang in self.languages]:
                return True
        
        # Check file pattern match
        if self.file_patterns and file_path:
            import fnmatch
            for pattern in self.file_patterns:
                if fnmatch.fnmatch(file_path.name, pattern):
                    return True
        
        # If we have restrictions but nothing matched
        if self.languages or self.file_patterns:
            return False
        
        return True


@dataclass
class Trigger:
    """A trigger that invokes a plugin action."""
    id: str                              # Unique ID within plugin
    type: TriggerType                    # Type of trigger
    action_id: str                       # ID of action to execute
    command_name: Optional[str] = None   # Display name for menu (command type)
    shortcut: Optional[str] = None       # Keyboard shortcut
    context: TriggerContext = field(default_factory=TriggerContext)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Trigger':
        return cls(
            id=data['id'],
            type=TriggerType(data['type']),
            action_id=data.get('action_id', data['id']),  # Default to trigger ID
            command_name=data.get('command_name'),
            shortcut=data.get('shortcut'),
            context=TriggerContext.from_dict(data.get('context'))
        )


@dataclass
class Action:
    """An action that a plugin can execute."""
    id: str                          # Unique ID within plugin
    type: ActionType                 # Type of action
    config: Dict[str, Any] = field(default_factory=dict)  # Action-specific config
    
    @classmethod
    def from_dict(cls, action_id: str, data: Dict) -> 'Action':
        action_type = ActionType(data['type'])
        # Store all other keys as config
        config = {k: v for k, v in data.items() if k != 'type'}
        return cls(
            id=action_id,
            type=action_type,
            config=config
        )


@dataclass
class Plugin:
    """A loaded plugin with its triggers and actions."""
    name: str
    version: str
    description: str
    author: str
    path: Path                           # Path to plugin directory
    triggers: List[Trigger] = field(default_factory=list)
    actions: Dict[str, Action] = field(default_factory=dict)
    enabled: bool = True
    error: Optional[str] = None          # Error message if loading failed
    
    @classmethod
    def from_dict(cls, data: Dict, plugin_path: Path) -> 'Plugin':
        """Create Plugin from parsed JSON."""
        triggers = [Trigger.from_dict(t) for t in data.get('triggers', [])]
        actions = {
            aid: Action.from_dict(aid, aconfig) 
            for aid, aconfig in data.get('actions', {}).items()
        }
        
        return cls(
            name=data.get('name', 'Unknown Plugin'),
            version=data.get('version', '0.0.0'),
            description=data.get('description', ''),
            author=data.get('author', 'Unknown'),
            path=plugin_path,
            triggers=triggers,
            actions=actions
        )
    
    def get_action(self, action_id: str) -> Optional[Action]:
        """Get action by ID."""
        return self.actions.get(action_id)
    
    def get_command_triggers(self) -> List[Trigger]:
        """Get all triggers that should appear as menu commands."""
        return [t for t in self.triggers 
                if t.type in (TriggerType.COMMAND, TriggerType.SHORTCUT)]
    
    def get_on_save_triggers(self) -> List[Trigger]:
        """Get all on_save triggers."""
        return [t for t in self.triggers if t.type == TriggerType.ON_SAVE]
    
    def get_on_open_triggers(self) -> List[Trigger]:
        """Get all on_open triggers."""
        return [t for t in self.triggers if t.type == TriggerType.ON_OPEN]

