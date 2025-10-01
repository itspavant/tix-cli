from __future__ import annotations

from typing import List, Optional

from textual.app import App, ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Header, Footer, Input, DataTable, Static
from textual.reactive import reactive
from textual import events
from textual.containers import Container

from tix.storage.json_storage import TaskStorage
from tix.models import Task  # type: ignore


class Tix(App):
    CSS = """
    Screen { }
    #body { height: 1fr; }
    """

    BINDINGS = [
        ("a", "add_task", "add"),
        ("d", "toggle_done", "done"),
        ("e", "edit_task", "edit"),
        ("/", "search_tasks", "search"),
        ("q", "quit", "quit"),
    ]

    query_text: reactive[str] = reactive("")

    def __init__(self, show_all: bool = False) -> None:
        super().__init__()
        self._storage = TaskStorage()
        self._show_all = show_all
        self._all_tasks: List[Task] = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="body"):
            yield Static("tix interactive - arrows navigate, a add, d done, e edit, / search, q quit", id="help")
            yield Input(placeholder="search...", id="search")
            table = DataTable(id="table")
            table.add_columns("ID", "✔", "priority", "task", "tags")
            yield table
        yield Static("a add | d done | e edit | / search | q quit", id="footer_help")

    def on_mount(self) -> None:
        self._refresh()
        self.query_one("#search", Input).display = False
        self.query_one(DataTable).focus()

    def _load_tasks(self) -> List[Task]:
        return self._storage.load_tasks()

    def _refresh(self) -> None:
        self._all_tasks = self._load_tasks()
        table = self.query_one(DataTable)
        table.clear()
        for t in sorted(self._all_tasks, key=lambda x: (x.completed, x.id)):
            status = "✔" if t.completed else "○"
            tags = ", ".join(t.tags) if t.tags else ""
            table.add_row(str(t.id), status, t.priority, t.text, tags, key=t.id)

    def action_add_task(self) -> None:
        self.push_screen(PromptModal("add task:"), self._handle_add)

    def _handle_add(self, value: Optional[str]) -> None:
        if value:
            self._storage.add_task(value, "medium", [])
            self._refresh()

    def action_toggle_done(self) -> None:
        table = self.query_one(DataTable)
        if table.cursor_row is None or table.row_count == 0:
            return
        try:
            row_key = table.get_row_key(table.cursor_row)
            task_id = int(row_key)
        except Exception:
            # fallback: derive id from first cell when key isn't available
            try:
                cells = table.get_row_at(table.cursor_row)
                task_id = int(str(cells[0]))
            except Exception:
                return
        task = self._storage.get_task(task_id)
        if not task:
            return
        if task.completed:
            task.completed = False
            task.completed_at = None
        else:
            task.mark_done()
        self._storage.update_task(task)
        self._refresh()

    def action_edit_task(self) -> None:
        table = self.query_one(DataTable)
        if table.cursor_row is None or table.row_count == 0:
            return
        try:
            row_key = table.get_row_key(table.cursor_row)
            task_id = int(row_key)
        except Exception:
            # fallback: derive id from first cell when key isn't available
            try:
                cells = table.get_row_at(table.cursor_row)
                task_id = int(str(cells[0]))
            except Exception:
                return
        task = self._storage.get_task(task_id)
        if not task:
            return
        # if the cursor is on the tags column, edit tags; otherwise edit text
        try:
            col = table.cursor_column
        except Exception:
            col = 3
        if col == 4:
            existing = ", ".join(task.tags)
            self.push_screen(PromptModal("edit tags (comma-separated):", default=existing), lambda v: self._handle_edit_tags(task.id, v))
        else:
            self.push_screen(PromptModal("edit text:", default=task.text), lambda v: self._handle_edit(task.id, v))

    def _handle_edit(self, task_id: int, value: Optional[str]) -> None:
        if value is None:
            return
        task = self._storage.get_task(task_id)
        if not task:
            return
        task.text = value
        self._storage.update_task(task)
        self._refresh()

    def _handle_edit_tags(self, task_id: int, value: Optional[str]) -> None:
        task = self._storage.get_task(task_id)
        if not task:
            return
        if value is not None:
            tags = [t.strip() for t in value.split(",") if t.strip()]
            task.tags = tags
        self._storage.update_task(task)
        self._refresh()

    def action_search_tasks(self) -> None:
        search = self.query_one("#search", Input)
        search.display = True
        search.focus()

    def on_input_changed(self, message: Input.Changed) -> None:
        if message.input.id != "search":
            return
        self.query_text = message.value
        table = self.query_one(DataTable)
        table.clear()
        for t in self._all_tasks:
            if self.query_text.lower() in t.text.lower():
                status = "✔" if t.completed else "○"
                tags = ", ".join(t.tags) if t.tags else ""
                table.add_row(str(t.id), status, t.priority, t.text, tags, key=t.id)

    def on_key(self, event: events.Key) -> None:
        # esc closes search and resets list
        if event.key == "escape":
            search = self.query_one("#search", Input)
            if search.display:
                search.value = ""
                search.display = False
                self._refresh()

    # ensure clicking any cell selects the corresponding row for actions like 'd' and 'e'
    def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:  # type: ignore[attr-defined]
        table = self.query_one(DataTable)
        try:
            table.cursor_coordinate = (event.coordinate.row, event.coordinate.column)
        except Exception:
            pass


class PromptModal(ModalScreen[Optional[str]]):
    def __init__(self, prompt: str, default: str = "") -> None:
        super().__init__()
        self._prompt = prompt
        self._default = default

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(self._prompt)
        yield Input(value=self._default, placeholder=self._prompt, id="prompt")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)
