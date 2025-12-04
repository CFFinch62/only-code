"""Buffer manager for multi-file editing."""

from dataclasses import dataclass, field
from pathlib import Path
import uuid


@dataclass
class Buffer:
    """Represents an open file/buffer."""
    id: str
    name: str
    content: str = ""
    path: str | None = None
    is_modified: bool = False
    cursor_position: tuple[int, int] = (0, 0)
    language: str = "python"

    @classmethod
    def create_new(cls, name: str = "Untitled") -> "Buffer":
        """Create a new untitled buffer."""
        return cls(
            id=str(uuid.uuid4())[:8],
            name=name,
            content="",
            path=None,
            is_modified=False,
        )

    @classmethod
    def from_file(cls, path: str) -> "Buffer":
        """Create a buffer from a file."""
        file_path = Path(path)
        content = file_path.read_text()
        language = cls._detect_language(file_path.suffix)
        return cls(
            id=str(uuid.uuid4())[:8],
            name=file_path.name,
            content=content,
            path=path,
            is_modified=False,
            language=language,
        )

    @staticmethod
    def _detect_language(suffix: str) -> str:
        """Detect language from file extension."""
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".json": "json",
            ".md": "markdown",
            ".html": "html",
            ".css": "css",
            ".rs": "rust",
            ".go": "go",
            ".sh": "bash",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".toml": "toml",
        }
        return language_map.get(suffix.lower(), "text")


class BufferManager:
    """Manages multiple open buffers."""

    def __init__(self) -> None:
        self._buffers: dict[str, Buffer] = {}
        self._active_buffer_id: str | None = None
        self._buffer_order: list[str] = []

    @property
    def active_buffer(self) -> Buffer | None:
        """Get the currently active buffer."""
        if self._active_buffer_id:
            return self._buffers.get(self._active_buffer_id)
        return None

    @property
    def buffer_count(self) -> int:
        """Get the number of open buffers."""
        return len(self._buffers)

    def create_buffer(self, name: str = "Untitled") -> Buffer:
        """Create and add a new buffer."""
        # If name is Untitled, make it unique
        if name == "Untitled":
            count = sum(1 for b in self._buffers.values() if b.name.startswith("Untitled"))
            if count > 0:
                name = f"Untitled-{count + 1}"

        buffer = Buffer.create_new(name)
        self._buffers[buffer.id] = buffer
        self._buffer_order.append(buffer.id)
        self._active_buffer_id = buffer.id
        return buffer

    def open_file(self, path: str) -> Buffer | None:
        """Open a file into a buffer. Returns existing buffer if already open."""
        # Check if file is already open
        for buffer in self._buffers.values():
            if buffer.path == path:
                self._active_buffer_id = buffer.id
                return buffer

        try:
            buffer = Buffer.from_file(path)
            self._buffers[buffer.id] = buffer
            self._buffer_order.append(buffer.id)
            self._active_buffer_id = buffer.id
            return buffer
        except Exception:
            return None

    def close_buffer(self, buffer_id: str) -> bool:
        """Close a buffer. Returns False if buffer has unsaved changes."""
        if buffer_id not in self._buffers:
            return True

        buffer = self._buffers[buffer_id]
        del self._buffers[buffer_id]
        self._buffer_order.remove(buffer_id)

        # Update active buffer
        if self._active_buffer_id == buffer_id:
            if self._buffer_order:
                self._active_buffer_id = self._buffer_order[-1]
            else:
                self._active_buffer_id = None

        return True

    def set_active(self, buffer_id: str) -> None:
        """Set the active buffer."""
        if buffer_id in self._buffers:
            self._active_buffer_id = buffer_id

    def get_buffer(self, buffer_id: str) -> Buffer | None:
        """Get a buffer by ID."""
        return self._buffers.get(buffer_id)

    def get_all_buffers(self) -> list[Buffer]:
        """Get all buffers in order."""
        return [self._buffers[bid] for bid in self._buffer_order if bid in self._buffers]

    def get_next_buffer_id(self) -> str | None:
        """Get the next buffer ID (for Ctrl+Tab)."""
        if not self._buffer_order or not self._active_buffer_id:
            return None
        idx = self._buffer_order.index(self._active_buffer_id)
        next_idx = (idx + 1) % len(self._buffer_order)
        return self._buffer_order[next_idx]

    def get_prev_buffer_id(self) -> str | None:
        """Get the previous buffer ID (for Ctrl+Shift+Tab)."""
        if not self._buffer_order or not self._active_buffer_id:
            return None
        idx = self._buffer_order.index(self._active_buffer_id)
        prev_idx = (idx - 1) % len(self._buffer_order)
        return self._buffer_order[prev_idx]

    def get_buffer_by_index(self, index: int) -> str | None:
        """Get buffer ID by index (0-based, for Alt+1-9)."""
        if 0 <= index < len(self._buffer_order):
            return self._buffer_order[index]
        return None

    def get_buffer_by_path(self, path: str) -> str | None:
        """Get buffer ID by file path. Returns None if not found."""
        for buffer in self._buffers.values():
            if buffer.path == str(path):
                return buffer.id
        return None

