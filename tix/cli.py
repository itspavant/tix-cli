import click
from rich.console import Console
from rich.table import Table
from pathlib import Path

# Initialize console for pretty output
console = Console()

# Ensure tix directory exists in user's home
TIX_DIR = Path.home() / ".tix"
TIX_DIR.mkdir(exist_ok=True)

@click.group(invoke_without_command=True)
@click.version_option(version="0.1.0", prog_name="tix")
@click.pass_context
def cli(ctx):
    """⚡ TIX - Lightning-fast terminal task manager"""
    if ctx.invoked_subcommand is None:
        console.print("[bold cyan]TIX[/bold cyan] - Terminal Task Manager", style="bold")
        console.print("\nUse [green]tix --help[/green] to see available commands")
        console.print("Use [green]tix add 'task'[/green] to add your first task")

@cli.command()
@click.argument('task')
@click.option('--priority', '-p', default='medium',
              type=click.Choice(['low', 'medium', 'high']))
def add(task, priority):
    """Add a new task"""
    color = {'high': 'red', 'medium': 'yellow', 'low': 'green'}[priority]
    console.print(f"[green]✓[/green] Added: [{color}]{task}[/{color}]")

@cli.command()
def ls():
    """List all tasks"""
    console.print("[bold]📋 Your tasks:[/bold]")
    console.print("[dim]No tasks yet. Use 'tix add' to create one![/dim]")

@cli.command()
@click.argument('task_id', type=int)
def done(task_id):
    """Mark a task as done"""
    console.print(f"[green]✓[/green] Completed task #{task_id}")

@cli.command()
@click.argument('task_id', type=int)
def rm(task_id):
    """Remove a task"""
    console.print(f"[red]✗[/red] Removed task #{task_id}")

if __name__ == '__main__':
    cli()