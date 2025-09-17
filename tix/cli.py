import click
from rich.console import Console
from rich.table import Table
from pathlib import Path
from tix.storage.json_storage import TaskStorage

# Initialize console and storage
console = Console()
storage = TaskStorage()


@click.group(invoke_without_command=True)
@click.version_option(version="0.1.0", prog_name="tix")
@click.pass_context
def cli(ctx):
    """⚡ TIX - Lightning-fast terminal task manager"""
    if ctx.invoked_subcommand is None:
        ctx.invoke(ls)


@cli.command()
@click.argument('task')
@click.option('--priority', '-p', default='medium',
              type=click.Choice(['low', 'medium', 'high']))
@click.option('--tag', '-t', multiple=True, help='Add tags to task')
def add(task, priority, tag):
    """Add a new task"""
    new_task = storage.add_task(task, priority, list(tag))
    color = {'high': 'red', 'medium': 'yellow', 'low': 'green'}[priority]
    console.print(f"[green]✓[/green] Added task #{new_task.id}: [{color}]{task}[/{color}]")


@cli.command()
@click.option('--all', '-a', is_flag=True, help='Show completed tasks too')
def ls(all):
    """List all tasks"""
    tasks = storage.load_tasks() if all else storage.get_active_tasks()

    if not tasks:
        console.print("[dim]No tasks found. Use 'tix add' to create one![/dim]")
        return

    table = Table(title="Tasks")
    table.add_column("ID", style="cyan", width=4)
    table.add_column("✓", width=3)
    table.add_column("Priority", width=8)
    table.add_column("Task")

    for task in sorted(tasks, key=lambda t: (t.completed, t.id)):
        status = "✓" if task.completed else "○"
        priority_color = {'high': 'red', 'medium': 'yellow', 'low': 'green'}[task.priority]
        table.add_row(
            str(task.id), status, f"[{priority_color}]{task.priority}[/{priority_color}]", task.text
        )

    console.print(table)


@cli.command()
@click.argument('task_id', type=int)
def done(task_id):
    """Mark a task as done"""
    task = storage.get_task(task_id)
    if not task:
        console.print(f"[red]✗[/red] Task #{task_id} not found")
        return

    if task.completed:
        console.print(f"[yellow]![/yellow] Task #{task_id} already completed")
        return

    task.mark_done()
    storage.update_task(task)
    console.print(f"[green]✓[/green] Completed: {task.text}")


@cli.command()
@click.argument('task_id', type=int)
def rm(task_id):
    """Remove a task"""
    task = storage.get_task(task_id)
    if not task:
        console.print(f"[red]✗[/red] Task #{task_id} not found")
        return

    if storage.delete_task(task_id):
        console.print(f"[red]✗[/red] Removed: {task.text}")


@cli.command()
@click.option('--completed/--active', default=True, help='Clear completed or active tasks')
@click.option('--force', '-f', is_flag=True, help='Skip confirmation')
def clear(completed, force):
    """Clear multiple tasks at once"""
    tasks = storage.load_tasks()

    if completed:
        to_clear = [t for t in tasks if t.completed]
        remaining = [t for t in tasks if not t.completed]
        task_type = "completed"
    else:
        to_clear = [t for t in tasks if not t.completed]
        remaining = [t for t in tasks if t.completed]
        task_type = "active"

    if not to_clear:
        console.print(f"[yellow]No {task_type} tasks to clear[/yellow]")
        return

    count = len(to_clear)

    if not force:
        console.print(f"[yellow]About to clear {count} {task_type} task(s):[/yellow]")
        for task in to_clear[:5]:  # Show first 5
            console.print(f"  - {task.text}")
        if count > 5:
            console.print(f"  ... and {count - 5} more")

        if not click.confirm("Continue?"):
            console.print("[dim]Cancelled[/dim]")
            return

    storage.save_tasks(remaining)
    console.print(f"[green]✓[/green] Cleared {count} {task_type} task(s)")


@cli.command()
@click.argument('task_id', type=int)
def undo(task_id):
    """Mark a completed task as active again"""
    task = storage.get_task(task_id)
    if not task:
        console.print(f"[red]✗[/red] Task #{task_id} not found")
        return

    if not task.completed:
        console.print(f"[yellow]![/yellow] Task #{task_id} is not completed")
        return

    task.completed = False
    task.completed_at = None
    storage.update_task(task)
    console.print(f"[green]✓[/green] Reactivated: {task.text}")


@cli.command()
@click.argument('task_ids', nargs=-1, type=int, required=True)
def done_all(task_ids):
    """Mark multiple tasks as done"""
    completed = []
    not_found = []
    already_done = []

    for task_id in task_ids:
        task = storage.get_task(task_id)
        if not task:
            not_found.append(task_id)
        elif task.completed:
            already_done.append(task_id)
        else:
            task.mark_done()
            storage.update_task(task)
            completed.append((task_id, task.text))

    # Report results
    if completed:
        console.print("[green]✓ Completed:[/green]")
        for tid, text in completed:
            console.print(f"  #{tid}: {text}")

    if already_done:
        console.print(f"[yellow]Already done: {', '.join(map(str, already_done))}[/yellow]")

    if not_found:
        console.print(f"[red]Not found: {', '.join(map(str, not_found))}[/red]")


@cli.command()
@click.argument('task_id', type=int)
@click.option('--text', '-t', help='New task text')
@click.option('--priority', '-p', type=click.Choice(['low', 'medium', 'high']))
@click.option('--add-tag', multiple=True, help='Add tags')
@click.option('--remove-tag', multiple=True, help='Remove tags')
def edit(task_id, text, priority, add_tag, remove_tag):
    """Edit a task"""
    task = storage.get_task(task_id)
    if not task:
        console.print(f"[red]✗[/red] Task #{task_id} not found")
        return

    changes = []

    if text:
        old_text = task.text
        task.text = text
        changes.append(f"text: '{old_text}' → '{text}'")

    if priority:
        old_priority = task.priority
        task.priority = priority
        changes.append(f"priority: {old_priority} → {priority}")

    for tag in add_tag:
        if tag not in task.tags:
            task.tags.append(tag)
            changes.append(f"+tag: '{tag}'")

    for tag in remove_tag:
        if tag in task.tags:
            task.tags.remove(tag)
            changes.append(f"-tag: '{tag}'")

    if changes:
        storage.update_task(task)
        console.print(f"[green]✓[/green] Updated task #{task_id}:")
        for change in changes:
            console.print(f"  • {change}")
    else:
        console.print("[yellow]No changes made[/yellow]")


@cli.command()
@click.argument('task_id', type=int)
@click.argument('priority', type=click.Choice(['low', 'medium', 'high']))
def priority(task_id, priority):
    """Quick priority change"""
    task = storage.get_task(task_id)
    if not task:
        console.print(f"[red]✗[/red] Task #{task_id} not found")
        return

    old_priority = task.priority
    task.priority = priority
    storage.update_task(task)

    color = {'high': 'red', 'medium': 'yellow', 'low': 'green'}[priority]
    console.print(f"[green]✓[/green] Changed priority: {old_priority} → [{color}]{priority}[/{color}]")


@cli.command()
@click.argument('from_id', type=int)
@click.argument('to_id', type=int)
def move(from_id, to_id):
    """Move/renumber a task to a different ID"""
    if from_id == to_id:
        console.print("[yellow]Source and destination IDs are the same[/yellow]")
        return

    source_task = storage.get_task(from_id)
    if not source_task:
        console.print(f"[red]✗[/red] Task #{from_id} not found")
        return

    # Check if destination ID exists
    dest_task = storage.get_task(to_id)
    if dest_task:
        console.print(f"[red]✗[/red] Task #{to_id} already exists")
        console.print("[dim]Tip: Remove the destination task first or use a different ID[/dim]")
        return

    # Create new task with new ID
    tasks = storage.load_tasks()
    tasks = [t for t in tasks if t.id != from_id]  # Remove old task

    # Create task with new ID
    source_task.id = to_id
    tasks.append(source_task)

    # Save all tasks
    storage.save_tasks(sorted(tasks, key=lambda t: t.id))
    console.print(f"[green]✓[/green] Moved task from #{from_id} to #{to_id}")


if __name__ == '__main__':
    cli()