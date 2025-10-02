import click
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.markdown import Markdown
from datetime import datetime

from .storage import storage
from .config import CONFIG
from .context import context_storage

console = Console()


@click.group()
def cli():
    """TIX - Lightning-fast Terminal Task Manager ⚡"""
    pass


@cli.command()
@click.argument("task")
@click.option("--priority", type=click.Choice(["low", "medium", "high"]))
@click.option("--tag", multiple=True, help="Add one or more tags")
@click.option("--date", help="Due date (YYYY-MM-DD)")
@click.option("--global", "is_global", is_flag=True, help="Make this a global task")
@click.option("--attach", multiple=True, help="File attachments")
@click.option("--link", multiple=True, help="Links to attach")
def add(task, priority, tag, date, is_global, attach, link):
    """Add a new task"""

    # Apply config defaults if not provided
    if priority is None:
        priority = CONFIG.get("defaults", {}).get("priority", "medium")

    # Merge config default tags with provided tags
    default_tags = CONFIG.get("defaults", {}).get("tags", [])
    all_tags = list(set(list(tag) + default_tags))

    # Add task
    new_task = storage.add_task(task, priority, all_tags, due=date, is_global=is_global)

    # Handle attachments and links
    if attach:
        storage.add_attachments(new_task.id, attach)
    if link:
        storage.add_links(new_task.id, link)

    storage.update_task(new_task)

    # Priority colors (configurable, fallback to defaults)
    priority_colors = CONFIG.get("colors", {}).get("priority", {})
    color = priority_colors.get(priority, {"high": "red", "medium": "yellow", "low": "green"}[priority])

    global_indicator = " [dim](global)[/dim]" if is_global else ""
    console.print(f"[green]✔[/green] Added task #{new_task.id}: [{color}]{task}[/{color}]{global_indicator}")

    if all_tags:
        tag_color = CONFIG.get("colors", {}).get("tags", "cyan")
        console.print(f"[dim]  Tags: [{tag_color}]{', '.join(all_tags)}[/{tag_color}][/dim]")
    if attach or link:
        console.print(f"[dim]  Attachments/Links added[/dim]")

    # Show current context if not default
    active_context = context_storage.get_active_context()
    if active_context != "default":
        console.print(f"[dim]  Context: {active_context}[/dim]")


@cli.command()
@click.option("--all", "show_all", is_flag=True, help="Show all tasks including completed")
def ls(show_all):
    """List tasks"""
    active_context = context_storage.get_active_context()
    title = "Tasks" if not show_all else "All Tasks"
    if active_context != "default":
        title += f" [dim]({active_context})[/dim]"

    # Display + color settings
    display_config = CONFIG.get("display", {})
    show_ids = display_config.get("show_ids", True)
    show_dates = display_config.get("show_dates", False)
    compact_mode = display_config.get("compact_mode", False)
    max_text_length = display_config.get("max_text_length", 0)

    priority_colors = CONFIG.get("colors", {}).get("priority", {})
    status_colors = CONFIG.get("colors", {}).get("status", {})
    tag_color = CONFIG.get("colors", {}).get("tags", "cyan")

    table = Table(title=title)
    if show_ids:
        table.add_column("ID", style="cyan", width=4)
    table.add_column("✔", width=3)
    table.add_column("Priority", width=8)
    table.add_column("Task")
    if not compact_mode:
        table.add_column("Tags", style=tag_color)
    if show_dates:
        table.add_column("Created", style="dim")
    table.add_column("Due Date")
    table.add_column("Scope", style="dim", width=6)

    tasks = storage.list_tasks(include_completed=show_all, context=active_context)

    if not tasks:
        console.print("[yellow]No tasks found.[/yellow]")
        return

    now = datetime.now().date()

    for t in tasks:
        status_symbol = "✔" if t.status == "done" else " "
        color = priority_colors.get(t.priority, {"high": "red", "medium": "yellow", "low": "green"}[t.priority])
        status_color = status_colors.get(t.status, "white")

        task_text = t.task
        if max_text_length and len(task_text) > max_text_length:
            task_text = task_text[: max_text_length - 3] + "..."

        row = []
        if show_ids:
            row.append(str(t.id))
        row.append(status_symbol)
        row.append(f"[{color}]{t.priority}[/{color}]")
        row.append(f"[{status_color}]{task_text}[/{status_color}]")
        if not compact_mode:
            row.append(", ".join(t.tags))
        if show_dates:
            row.append(t.created.strftime("%Y-%m-%d"))
        due_display = ""
        if t.due:
            try:
                due_date = datetime.strptime(t.due, "%Y-%m-%d").date()
                if due_date < now and t.status != "done":
                    due_display = f"[red]{t.due} (OVERDUE)[/red]"
                elif due_date == now:
                    due_display = f"[yellow]{t.due} (TODAY)[/yellow]"
                else:
                    due_display = t.due
            except ValueError:
                due_display = t.due
        row.append(due_display)
        row.append("Global" if t.is_global else "Local")

        table.add_row(*row)

    console.print(table)
    console.print(f"[dim]{len(tasks)} tasks listed[/dim]")


@cli.command()
@click.argument("task_id", type=int)
def done(task_id):
    """Mark a task as done"""
    task = storage.get_task(task_id)
    if not task:
        console.print(f"[red]Task {task_id} not found[/red]")
        return
    storage.mark_done(task_id)
    console.print(f"[green]✔ Task {task_id} marked as done[/green]")


@cli.command()
@click.argument("task_id", type=int)
def rm(task_id):
    """Remove a task"""
    task = storage.get_task(task_id)
    if not task:
        console.print(f"[red]Task {task_id} not found[/red]")
        return
    storage.remove_task(task_id)
    console.print(f"[red]✖ Task {task_id} removed[/red]")


@cli.command()
@click.argument("name")
def context(name):
    """Switch or create context"""
    context_storage.set_active_context(name)
    console.print(f"[blue]Switched to context:[/blue] {name}")


@cli.command()
def contexts():
    """List all contexts"""
    contexts = context_storage.list_contexts()
    active = context_storage.get_active_context()
    for c in contexts:
        if c == active:
            console.print(f"[cyan]> {c} (active)[/cyan]")
        else:
            console.print(f"  {c}")
