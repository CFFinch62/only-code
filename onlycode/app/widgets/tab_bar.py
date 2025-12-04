"""Tab bar widget for multi-buffer support."""

from textual.widget import Widget
from textual.widgets import Static
from textual.reactive import reactive
from textual.message import Message
from textual.containers import Horizontal
from dataclasses import dataclass


@dataclass
class TabInfo:
    """Information about a tab/buffer."""
    id: str
    name: str
    path: str | None = None
    is_modified: bool = False


class Tab(Static):
    """A single tab in the tab bar."""

    DEFAULT_CSS = """
    Tab {
        padding: 0 2;
        height: 1;
        width: auto;
        background: $surface;
        color: $text-muted;
    }
    Tab:hover {
        background: $surface-lighten-1;
    }
    Tab.active {
        background: $primary;
        color: $text;
    }
    Tab .modified {
        color: $warning;
    }
    """

    is_active = reactive(False)
    is_modified = reactive(False)

    class Selected(Message):
        """Message sent when a tab is selected."""
        def __init__(self, tab_id: str) -> None:
            self.tab_id = tab_id
            super().__init__()

    class CloseRequested(Message):
        """Message sent when a tab close is requested."""
        def __init__(self, tab_id: str) -> None:
            self.tab_id = tab_id
            super().__init__()

    def __init__(self, tab_info: TabInfo, **kwargs) -> None:
        super().__init__(**kwargs)
        self.tab_info = tab_info
        self.is_modified = tab_info.is_modified

    def compose(self):
        return []  # Content set via render

    def render(self) -> str:
        modified = "● " if self.is_modified else ""
        return f"{modified}{self.tab_info.name}"

    def watch_is_active(self, active: bool) -> None:
        self.set_class(active, "active")

    def watch_is_modified(self, modified: bool) -> None:
        self.tab_info.is_modified = modified
        self.refresh()

    def on_click(self) -> None:
        self.post_message(self.Selected(self.tab_info.id))


class TabBar(Widget):
    """A horizontal bar showing open buffers as tabs."""

    DEFAULT_CSS = """
    TabBar {
        dock: top;
        height: 1;
        background: $surface-darken-1;
        layout: horizontal;
    }
    """

    class TabSelected(Message):
        """Message sent when a tab is selected."""
        def __init__(self, tab_id: str) -> None:
            self.tab_id = tab_id
            super().__init__()

    class TabCloseRequested(Message):
        """Message sent when a tab close is requested."""
        def __init__(self, tab_id: str) -> None:
            self.tab_id = tab_id
            super().__init__()

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._tabs: dict[str, Tab] = {}
        self._active_tab_id: str | None = None

    def add_tab(self, tab_info: TabInfo) -> None:
        """Add a new tab."""
        tab = Tab(tab_info, id=f"tab-{tab_info.id}")
        self._tabs[tab_info.id] = tab
        self.mount(tab)
        self.set_active(tab_info.id)

    def remove_tab(self, tab_id: str) -> None:
        """Remove a tab."""
        if tab_id in self._tabs:
            tab = self._tabs.pop(tab_id)
            tab.remove()
            # If we removed the active tab, activate another
            if self._active_tab_id == tab_id and self._tabs:
                self.set_active(next(iter(self._tabs)))

    def set_active(self, tab_id: str) -> None:
        """Set the active tab."""
        if self._active_tab_id and self._active_tab_id in self._tabs:
            self._tabs[self._active_tab_id].is_active = False
        if tab_id in self._tabs:
            self._tabs[tab_id].is_active = True
            self._active_tab_id = tab_id

    def set_modified(self, tab_id: str, modified: bool) -> None:
        """Set the modified state of a tab."""
        if tab_id in self._tabs:
            self._tabs[tab_id].is_modified = modified

    def update_tab_name(self, tab_id: str, name: str, path: str | None = None) -> None:
        """Update the name and path of a tab."""
        if tab_id in self._tabs:
            tab = self._tabs[tab_id]
            tab.tab_info.name = name
            tab.tab_info.path = path
            tab.refresh()

    def get_tab_ids(self) -> list[str]:
        """Get list of tab IDs in order."""
        return list(self._tabs.keys())

    def on_tab_selected(self, event: Tab.Selected) -> None:
        """Handle tab selection."""
        event.stop()
        self.set_active(event.tab_id)
        self.post_message(self.TabSelected(event.tab_id))

