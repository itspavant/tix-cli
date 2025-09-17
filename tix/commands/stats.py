from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from datetime import datetime, timedelta
from collections import Counter

console = Console()


def show_stats(storage):
    """Display comprehensive task statistics"""
    tasks = storage.load_tasks()

    if not tasks:
        console.print("[dim]No tasks to analyze. Add some tasks first![/dim]")
        return

    active = [t for t in tasks if not t.completed]
    completed = [t for t in tasks if t.completed]

    # Priority breakdown
    priority_counts = Counter(t.priority for t in active)

    # Tags analysis
    all_tags = []
    for task in tasks:
        all_tags.extend(task.tags)
    tag_counts = Counter(all_tags)

    # Time analysis
    today = datetime.now().date()
    today_completed = len([
        t for t in completed
        if t.completed_at and
           datetime.fromisoformat(t.completed_at).date() == today
    ])

    # Create stats panel
    stats_text = f"""[bold cyan]📊 Task Statistics[/bold cyan]

[bold]Overview:[/bold]
  • Total tasks: {len(tasks)}
  • Active: {len(active)} ({len(active) / max(len(tasks), 1) * 100:.0f}%)
  • Completed: {len(completed)} ({len(completed) / max(len(tasks), 1) * 100:.0f}%)

[bold]Priority Distribution (Active):[/bold]
  • 🔴 High: {priority_counts.get('high', 0)}
  • 🟡 Medium: {priority_counts.get('medium', 0)}
  • 🟢 Low: {priority_counts.get('low', 0)}

[bold]Today's Progress:[/bold]
  • Completed today: {today_completed} task(s)

[bold]Top Tags:[/bold]"""

    if tag_counts:
        for tag, count in tag_counts.most_common(3):
            stats_text += f"\n  • {tag}: {count} task(s)"
    else:
        stats_text += "\n  • No tags used yet"

    panel = Panel(stats_text, expand=False, border_style="cyan")
    console.print(panel)

    # Progress bar
    if tasks:
        console.print("\n[bold]Completion Progress:[/bold]")
        with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:
            progress.add_task(
                "Overall",
                total=len(tasks),
                completed=len(completed)
            )