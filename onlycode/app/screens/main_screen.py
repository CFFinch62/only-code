import os
from textual.screen import Screen
from textual.widgets import Header, Footer
from textual.containers import Horizontal, Vertical
from textual.binding import Binding
from pathlib import Path
from onlycode.editor.editor_widget import OnlyCodeEditor
from onlycode.editor.buffer_manager import BufferManager, Buffer
from onlycode.app.widgets.status_bar import StatusBar
from onlycode.app.widgets.tab_bar import TabBar, TabInfo
from onlycode.app.widgets.file_browser import FileBrowser
from onlycode.app.widgets.terminal_panel import TerminalPanel
from onlycode.app.screens.file_dialogs import OpenFileDialog, SaveFileDialog, ConfirmCloseDialog
from onlycode.shared.config.session import SessionManager


class MainScreen(Screen):
    """The main screen of the application."""

    DEFAULT_CSS = """
    MainScreen {
        layout: vertical;
    }

    MainScreen #workspace {
        height: 1fr;
    }

    MainScreen #main-container {
        height: 1fr;
    }

    MainScreen #editor-container {
        width: 1fr;
    }
    """

    BINDINGS = [
        Binding("ctrl+o", "open_file", "Open", priority=True),
        Binding("ctrl+s", "save_file", "Save", priority=True),
        Binding("ctrl+t", "new_file", "New Tab", priority=True),
        Binding("ctrl+w", "close_buffer", "Close", priority=True),
        Binding("ctrl+b", "toggle_file_browser", "Browser", priority=True),
        Binding("ctrl+j", "toggle_terminal", "Terminal", priority=True),
        Binding("escape", "focus_editor", "Focus Editor", show=False, priority=True),
        # Tab navigation: ctrl+pagedown/pageup are standard in many editors
        Binding("ctrl+pagedown", "next_buffer", "Next Tab", show=False, priority=True),
        Binding("ctrl+pageup", "prev_buffer", "Prev Tab", show=False, priority=True),
        # F7/F8 as fallback for next/prev tab
        Binding("f8", "next_buffer", "Next Tab", show=False, priority=True),
        Binding("f7", "prev_buffer", "Prev Tab", show=False, priority=True),
        Binding("alt+1", "buffer_1", "Tab 1", show=False, priority=True),
        Binding("alt+2", "buffer_2", "Tab 2", show=False, priority=True),
        Binding("alt+3", "buffer_3", "Tab 3", show=False, priority=True),
        Binding("alt+4", "buffer_4", "Tab 4", show=False, priority=True),
        Binding("alt+5", "buffer_5", "Tab 5", show=False, priority=True),
        Binding("alt+6", "buffer_6", "Tab 6", show=False, priority=True),
        Binding("alt+7", "buffer_7", "Tab 7", show=False, priority=True),
        Binding("alt+8", "buffer_8", "Tab 8", show=False, priority=True),
        Binding("alt+9", "buffer_9", "Tab 9", show=False, priority=True),
        Binding("ctrl+q", "quit", "Quit", priority=True),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.buffer_manager = BufferManager()
        self.session_manager = SessionManager()
        self._loading_buffer = True  # Start True to prevent marking as modified during initial setup

    def compose(self):
        yield Header()
        # Start file browser at the directory from which the app was launched
        start_path = os.getcwd()
        with Vertical(id="workspace"):
            with Horizontal(id="main-container"):
                yield FileBrowser(path=start_path, id="file-browser", classes="hidden")
                with Vertical(id="editor-container"):
                    yield TabBar(id="tab-bar")
                    yield OnlyCodeEditor(id="editor")
            yield TerminalPanel(id="terminal-panel", classes="hidden")
            yield StatusBar(id="status-bar")
        yield Footer()

    def on_mount(self):
        # Try to restore session, or create initial buffer
        self._restore_session()
        if self.buffer_manager.buffer_count == 0:
            self._create_new_buffer()
        self.query_one(OnlyCodeEditor).focus()
        # Delay enabling change detection until after Textual finishes setup
        # Use set_timer to ensure this runs after all call_after_refresh callbacks
        self.set_timer(0.1, self._enable_change_detection)

    def _enable_change_detection(self):
        """Enable change detection after initial setup is complete."""
        self._loading_buffer = False
        # Reset any modified flags that may have been set during setup
        tab_bar = self.query_one(TabBar)
        for buffer in self.buffer_manager.get_all_buffers():
            if not buffer.path and buffer.content == "":
                # New empty buffer should not be marked as modified
                buffer.is_modified = False
                tab_bar.set_modified(buffer.id, False)

    def _create_new_buffer(self) -> Buffer:
        """Create a new buffer and add tab."""
        # Save current buffer content BEFORE creating new buffer
        self._save_current_buffer_state()

        buffer = self.buffer_manager.create_buffer()
        tab_bar = self.query_one(TabBar)
        tab_bar.add_tab(TabInfo(
            id=buffer.id,
            name=buffer.name,
            path=buffer.path,
            is_modified=buffer.is_modified,
        ))
        self._switch_to_buffer(buffer)
        return buffer

    def _save_current_buffer_state(self) -> None:
        """Save the current editor state to the active buffer."""
        current = self.buffer_manager.active_buffer
        if current:
            editor = self.query_one(OnlyCodeEditor)
            current.content = editor.text
            current.cursor_position = editor.selection.end

    def _switch_to_buffer(self, buffer: Buffer) -> None:
        """Switch editor to show the given buffer."""
        editor = self.query_one(OnlyCodeEditor)

        # Save current buffer state
        current = self.buffer_manager.active_buffer
        if current and current.id != buffer.id:
            current.content = editor.text
            current.cursor_position = editor.selection.end

        # Load new buffer - set flag to prevent marking as modified
        self._loading_buffer = True
        self.buffer_manager.set_active(buffer.id)
        editor.text = buffer.content
        editor.language = buffer.language

        # Update UI
        tab_bar = self.query_one(TabBar)
        tab_bar.set_active(buffer.id)

        # Detect line ending from content
        line_ending = "CRLF" if "\r\n" in buffer.content else "LF"

        self.update_status_bar(
            path=str(buffer.path) if buffer.path else buffer.name,
            modified=buffer.is_modified,
            language=buffer.language,
            encoding="UTF-8",
            line_ending=line_ending
        )

        # Delay re-enabling change detection until after events are processed
        # Use set_timer to ensure this runs after all async TextArea events
        def finish_switch():
            self._loading_buffer = False
            # Ensure the buffer's modified state is correct in the UI
            tab_bar.set_modified(buffer.id, buffer.is_modified)
        self.set_timer(0.05, finish_switch)

    def action_new_file(self):
        self._create_new_buffer()

    def action_open_file(self):
        def open_file_callback(path: str | None):
            if path:
                # Save current buffer state BEFORE opening new file
                self._save_current_buffer_state()

                buffer = self.buffer_manager.open_file(path)
                if buffer:
                    tab_bar = self.query_one(TabBar)
                    # Check if tab already exists
                    if buffer.id not in tab_bar.get_tab_ids():
                        tab_bar.add_tab(TabInfo(
                            id=buffer.id,
                            name=buffer.name,
                            path=buffer.path,
                            is_modified=buffer.is_modified,
                        ))
                    self._switch_to_buffer(buffer)
                    self.notify(f"Opened {path}")
                else:
                    self.notify(f"Failed to open {path}", severity="error")

        self.app.push_screen(OpenFileDialog(), open_file_callback)

    def action_save_file(self):
        buffer = self.buffer_manager.active_buffer
        if not buffer:
            return

        if buffer.path:
            self._save_buffer(buffer, buffer.path)
        else:
            self.action_save_as()

    def action_save_as(self):
        def save_file_callback(path: str | None):
            if path:
                buffer = self.buffer_manager.active_buffer
                if buffer:
                    self._save_buffer(buffer, path)

        self.app.push_screen(SaveFileDialog(), save_file_callback)

    def _save_buffer(self, buffer: Buffer, path: str) -> None:
        """Save buffer to file."""
        editor = self.query_one(OnlyCodeEditor)
        buffer.content = editor.text

        if editor.save_file(path):
            buffer.path = path
            buffer.name = Path(path).name
            buffer.is_modified = False

            tab_bar = self.query_one(TabBar)
            tab_bar.update_tab_name(buffer.id, buffer.name, buffer.path)
            tab_bar.set_modified(buffer.id, False)
            self.update_status_bar(path=path, modified=False)
            self.notify(f"Saved {path}")
        else:
            self.notify(f"Failed to save {path}", severity="error")

    def action_close_buffer(self):
        buffer = self.buffer_manager.active_buffer
        if not buffer:
            return

        if buffer.is_modified:
            # Show confirmation dialog for unsaved changes
            def handle_close_response(response: str | None):
                if response == "save":
                    # Save then close
                    if buffer.path:
                        self._save_buffer(buffer, buffer.path)
                        self._do_close_buffer(buffer.id)
                    else:
                        # Need to save as first
                        def save_then_close(path: str | None):
                            if path:
                                self._save_buffer(buffer, path)
                                self._do_close_buffer(buffer.id)
                        self.app.push_screen(SaveFileDialog(), save_then_close)
                elif response == "discard":
                    # Close without saving
                    self._do_close_buffer(buffer.id)
                # "cancel" or None - do nothing

            self.app.push_screen(
                ConfirmCloseDialog(buffer.name),
                handle_close_response
            )
        else:
            self._do_close_buffer(buffer.id)

    def _do_close_buffer(self, buffer_id: str):
        """Actually close a buffer (after confirmation if needed)."""
        tab_bar = self.query_one(TabBar)
        tab_bar.remove_tab(buffer_id)
        self.buffer_manager.close_buffer(buffer_id)

        # Switch to another buffer or create new one
        if self.buffer_manager.active_buffer:
            self._switch_to_buffer(self.buffer_manager.active_buffer)
        else:
            self._create_new_buffer()


    def action_next_buffer(self):
        """Switch to next buffer."""
        next_id = self.buffer_manager.get_next_buffer_id()
        if next_id:
            self._save_current_buffer_state()
            buffer = self.buffer_manager.get_buffer(next_id)
            if buffer:
                self._switch_to_buffer(buffer)

    def action_prev_buffer(self):
        """Switch to previous buffer."""
        prev_id = self.buffer_manager.get_prev_buffer_id()
        if prev_id:
            self._save_current_buffer_state()
            buffer = self.buffer_manager.get_buffer(prev_id)
            if buffer:
                self._switch_to_buffer(buffer)

    def _jump_to_buffer(self, index: int):
        """Jump to buffer by index (0-based)."""
        buffer_id = self.buffer_manager.get_buffer_by_index(index)
        if buffer_id:
            self._save_current_buffer_state()
            buffer = self.buffer_manager.get_buffer(buffer_id)
            if buffer:
                self._switch_to_buffer(buffer)

    def action_buffer_1(self): self._jump_to_buffer(0)
    def action_buffer_2(self): self._jump_to_buffer(1)
    def action_buffer_3(self): self._jump_to_buffer(2)
    def action_buffer_4(self): self._jump_to_buffer(3)
    def action_buffer_5(self): self._jump_to_buffer(4)
    def action_buffer_6(self): self._jump_to_buffer(5)
    def action_buffer_7(self): self._jump_to_buffer(6)
    def action_buffer_8(self): self._jump_to_buffer(7)
    def action_buffer_9(self): self._jump_to_buffer(8)

    def action_quit(self):
        # Check for unsaved changes
        unsaved = [b for b in self.buffer_manager.get_all_buffers() if b.is_modified]
        if unsaved:
            self.notify(f"{len(unsaved)} unsaved buffer(s). Save before quitting.", severity="warning")
            return
        # Save session before quitting
        self._save_session()
        self.app.exit()

    def update_status_bar(
        self,
        path: str = None,
        modified: bool = None,
        language: str = None,
        encoding: str = None,
        line_ending: str = None
    ):
        status_bar = self.query_one(StatusBar)
        if path is not None:
            status_bar.file_path = path
        if modified is not None:
            status_bar.is_modified = modified
        if language is not None:
            status_bar.language = language
        if encoding is not None:
            status_bar.encoding = encoding
        if line_ending is not None:
            status_bar.line_ending = line_ending

    def on_text_area_changed(self, event):
        """Handle text changes - mark buffer as modified."""
        # Skip if we're loading a buffer (programmatic text change)
        if self._loading_buffer:
            return

        buffer = self.buffer_manager.active_buffer
        if buffer:
            buffer.is_modified = True
            tab_bar = self.query_one(TabBar)
            tab_bar.set_modified(buffer.id, True)
            self.update_status_bar(modified=True)

    def on_text_area_selection_changed(self, event):
        """Handle cursor movement."""
        status_bar = self.query_one(StatusBar)
        status_bar.cursor_position = event.selection.end

    def on_tab_bar_tab_selected(self, event: TabBar.TabSelected):
        """Handle tab selection from tab bar."""
        self._save_current_buffer_state()
        buffer = self.buffer_manager.get_buffer(event.tab_id)
        if buffer:
            self._switch_to_buffer(buffer)

    def _restore_session(self) -> None:
        """Restore the previous session (open files)."""
        session = self.session_manager.load_session()
        if not session or not session.open_files:
            return

        tab_bar = self.query_one(TabBar)
        active_buffer = None

        for i, file_path_str in enumerate(session.open_files):
            file_path = Path(file_path_str)
            if file_path.exists():
                buffer = self.buffer_manager.open_file(str(file_path))
                if buffer:
                    tab_bar.add_tab(TabInfo(
                        id=buffer.id,
                        name=buffer.name,
                        path=buffer.path,
                        is_modified=buffer.is_modified,
                    ))
                    # Track which buffer to activate
                    if i == session.active_tab_index:
                        active_buffer = buffer

        # Activate the correct buffer
        if active_buffer:
            self._switch_to_buffer(active_buffer)
        elif self.buffer_manager.buffer_count > 0:
            first = self.buffer_manager.get_all_buffers()[0]
            self._switch_to_buffer(first)

    def _save_session(self) -> None:
        """Save current session (open files) for restoration."""
        # Collect file paths from buffers that have paths (not Untitled)
        open_files = []
        active_index = 0
        buffers = self.buffer_manager.get_all_buffers()
        active_buffer = self.buffer_manager.active_buffer

        for i, buffer in enumerate(buffers):
            if buffer.path:
                open_files.append(str(buffer.path))
                if active_buffer and buffer.id == active_buffer.id:
                    active_index = len(open_files) - 1

        self.session_manager.save_session(open_files, active_index)

    def action_focus_editor(self):
        """Return focus to the editor."""
        self.query_one(OnlyCodeEditor).focus()

    def action_toggle_file_browser(self):
        """Toggle the file browser panel, or focus it if visible but not focused."""
        file_browser = self.query_one(FileBrowser)

        if file_browser.is_visible:
            # Check if file browser tree already has focus
            focused = self.app.focused
            tree = file_browser.query_one("#file-tree")
            if focused == tree:
                # Already focused on tree - hide it
                file_browser.hide()
                self.query_one(OnlyCodeEditor).focus()
            else:
                # Visible but not focused - focus the tree
                file_browser.focus_tree()
        else:
            # Not visible - show and focus
            file_browser.show()
            file_browser.focus_tree()

    def action_toggle_terminal(self):
        """Toggle the terminal panel, or focus it if visible but not focused."""
        terminal = self.query_one(TerminalPanel)

        if terminal.is_visible:
            # Check if terminal already has focus
            focused = self.app.focused
            terminal_has_focus = False
            if focused:
                try:
                    terminal_has_focus = terminal in focused.ancestors_with_self
                except Exception:
                    pass

            if terminal_has_focus:
                # Terminal is focused - hide it and return to editor
                terminal.hide()
                self.query_one(OnlyCodeEditor).focus()
            else:
                # Terminal is visible but not focused - just focus it
                terminal.focus_input()
        else:
            # Terminal is hidden - show it and focus
            terminal.show()
            terminal.focus_input()

    def on_key(self, event):
        """Handle global key events."""
        # Escape in terminal returns focus to editor
        if event.key == "escape":
            terminal = self.query_one(TerminalPanel)
            if terminal.is_visible:
                # Check if focus is in terminal
                try:
                    focused = self.app.focused
                    if focused and terminal in focused.ancestors_with_self:
                        self.query_one(OnlyCodeEditor).focus()
                        event.prevent_default()
                        event.stop()
                except Exception:
                    pass

    def on_file_browser_file_selected(self, event: FileBrowser.FileSelected):
        """Handle file selection from file browser."""
        path = event.path
        # Check if file is already open
        existing = self.buffer_manager.get_buffer_by_path(path)
        if existing:
            self._save_current_buffer_state()
            buffer = self.buffer_manager.get_buffer(existing)
            if buffer:
                self._switch_to_buffer(buffer)
        else:
            # Open new file
            buffer = self.buffer_manager.open_file(path)
            if buffer:
                tab_bar = self.query_one(TabBar)
                if buffer.id not in tab_bar.get_tab_ids():
                    tab_bar.add_tab(TabInfo(
                        id=buffer.id,
                        name=buffer.name,
                        path=buffer.path,
                        is_modified=buffer.is_modified,
                    ))
                self._switch_to_buffer(buffer)
        # Return focus to editor
        self.query_one(OnlyCodeEditor).focus()
