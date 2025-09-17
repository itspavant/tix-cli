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


if __name__ == '__main__':
    cli()