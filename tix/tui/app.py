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
        # if the cursor is on the priority column, cycle priority; if on the tags column, edit tags; otherwise edit text
        try:
            col = table.cursor_column
        except Exception:
            col = 3
        if col == 2:
            cycle = ["low", "medium", "high"]
            try:
                idx = cycle.index(task.priority)
            except ValueError:
                idx = 0
            task.priority = cycle[(idx + 1) % len(cycle)]
            self._storage.update_task(task)
            self._refresh()
        elif col == 4:
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
        filters, free_text = self._parse_search(self.query_text)
        for t in self._all_tasks:
            if self._task_matches(t, filters, free_text):
                status = "✔" if t.completed else "○"
                tags = ", ".join(t.tags) if t.tags else ""
                table.add_row(str(t.id), status, t.priority, t.text, tags, key=t.id)

    def _parse_search(self, query: str):
        # supports key:value tokens for columns (except id), plus free-text
        # keys: p/priority, tags, text/task, status/s
        filters = {"priority": None, "tags": None, "text": None, "status": None}
        free_parts = []
        for raw in query.split():
            if ":" in raw:
                key, value = raw.split(":", 1)
                key = key.strip().lower()
                value = value.strip()
                if key in ("p", "priority"):
                    v = value.lower()
                    # support short forms: l/m/h
                    if v in ("l", "low"):
                        v = "low"
                    elif v in ("m", "med", "medium"):
                        v = "medium"
                    elif v in ("h", "hi", "high"):
                        v = "high"
                    if v in ("low", "medium", "high"):
                        filters["priority"] = v
                elif key in ("t", "tags"):
                    # accept array form like [a,b]
                    vals = value
                    if vals.startswith("[") and vals.endswith("]"):
                        vals = vals[1:-1]
                    tag_list = [x.strip() for x in vals.split(",") if x.strip()]
                    filters["tags"] = tag_list
                elif key in ("text", "task"):
                    filters["text"] = value
                elif key in ("status", "s", "done"):
                    v = value.lower()
                    if v in ("done", "completed", "true", "yes"):
                        filters["status"] = True
                    elif v in ("active", "open", "false", "no"):
                        filters["status"] = False
            else:
                free_parts.append(raw)
        free_text = " ".join(free_parts).strip()
        return filters, free_text

    def _task_matches(self, task: Task, filters, free_text: str) -> bool:
        # priority
        p = filters.get("priority")
        if p and task.priority != p:
            return False
        # status
        status = filters.get("status")
        if status is True and not task.completed:
            return False
        if status is False and task.completed:
            return False
        # tags: match if ANY of the specified tags is present
        tags = filters.get("tags")
        if tags:
            task_tags = set(task.tags or [])
            if not any(tag in task_tags for tag in tags):
                return False
        # text explicit
        text_filter = filters.get("text")
        if text_filter and text_filter.lower() not in (task.text or "").lower():
            return False
        # free text fallback matches task text too
        if free_text and free_text.lower() not in (task.text or "").lower():
            return False
        return True

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
