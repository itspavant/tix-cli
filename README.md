# TIX - Lightning-fast Terminal Task Manager ⚡

A minimalist, powerful command-line task manager built with Python. Manage your todos efficiently without leaving your terminal.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)
![Shell Completion](https://img.shields.io/badge/completion-auto--enabled-success.svg)

## ✨ Features

- **Fast & Simple**: Add tasks with a single command
- **Persistent Storage**: Tasks are saved locally in JSON format
- **Priority Levels**: Organize tasks by high, medium, or low priority
- **Tags**: Categorize tasks with custom tags
- **Search & Filter**: Find tasks quickly with powerful search
- **Statistics**: Track your productivity with built-in analytics
- **Reports**: Export your tasks in text or JSON format
- **Colored Output**: Beautiful terminal UI with rich formatting
- **Bulk Operations**: Mark multiple tasks as done at once
- **Auto Shell Completion**: Tab completion works out of the box for bash, zsh, and fish

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/TheDevOpsBlueprint/tix-cli.git
cd tix-cli

# Install with pip (auto-configures completion)
pip install -e .

# That's it! Shell completion is automatically configured
# Just start using tix:
tix <TAB><TAB>  # Auto-completion works immediately!
```

### Alternative Installation Methods

#### From PyPI (Coming Soon)

```bash
pip install tix-cli
# Shell completion auto-configures on first run!
```

#### Using Virtual Environment (Recommended)

```bash
# Clone the repository
git clone https://github.com/TheDevOpsBlueprint/tix-cli.git
cd tix-cli

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install tix
pip install -e .

# Shell completion is automatically configured!
tix <TAB><TAB>  # Works immediately
```

## 🎯 Auto-Completion

**TIX automatically configures shell completion on first run!** No manual setup needed.

### How It Works

1. Install tix: `pip install -e .`
2. Run any tix command: `tix`
3. Completion is automatically configured for your shell
4. Restart your terminal or source your shell config
5. Start using Tab completion!

### Supported Shells

- ✅ **Bash** - Auto-configures in ~/.bashrc or ~/.bash_profile
- ✅ **Zsh** - Auto-configures in ~/.zshrc
- ✅ **Fish** - Auto-configures in ~/.config/fish/config.fish

### Using Tab Completion

```bash
# Complete commands
tix <TAB><TAB>
# Shows: add clear done edit filter ls move priority report rm search stats tags undo

# Complete options
tix add --<TAB><TAB>
# Shows: --priority --tag --help

# Complete option values
tix add --priority <TAB><TAB>
# Shows: high low medium

# Complete task IDs
tix done <TAB><TAB>
# Shows: 1 2 3 (your actual task IDs)
```

### Manual Setup (If Needed)

If auto-configuration doesn't work, you can manually add completion:

```bash
# For Bash - add to ~/.bashrc
eval "$(_TIX_COMPLETE=bash_source tix)"

# For Zsh - add to ~/.zshrc
eval "$(_TIX_COMPLETE=zsh_source tix)"

# For Fish - add to ~/.config/fish/config.fish
_TIX_COMPLETE=fish_source tix | source
```

### Reset Completion

```bash
# Reset completion setup if needed
tix completion --reset

# Then run any tix command to reconfigure
tix
```

## 📖 Usage Guide

### Basic Commands

#### Adding Tasks

```bash
# Simple task
tix add "Write documentation"

# With priority (high/medium/low)
tix add "Fix critical bug" -p high

# With tags
tix add "Review PR" -t work -t urgent

# Multiple tags and priority
tix add "Deploy to production" -p high -t devops -t release
```

#### Listing Tasks

```bash
# Show active tasks
tix ls

# Show all tasks (including completed)
tix ls --all

# Short alias
tix ls -a
```

#### Completing Tasks

```bash
# Mark single task as done
tix done 1

# Mark multiple tasks as done
tix done-all 1 3 5

# Undo completion (reactivate)
tix undo 1
```

#### Removing Tasks

```bash
# Remove a single task
tix rm 1

# Force remove without confirmation
tix rm 2 --confirm

# Clear all completed tasks
tix clear --completed

# Clear all active tasks (careful!)
tix clear --active --force
```

### Advanced Features

#### Editing Tasks

```bash
# Change task text
tix edit 1 --text "Updated task description"

# Change priority
tix priority 1 high

# Add/remove tags
tix edit 1 --add-tag urgent --remove-tag low-priority

# Multiple edits at once
tix edit 1 --text "New text" --priority high --add-tag important
```

#### Searching and Filtering

```bash
# Search by text
tix search "bug"

# Search with filters
tix search "api" -p high -t backend

# Filter by criteria
tix filter -p high           # High priority tasks
tix filter -t urgent         # Tasks tagged "urgent"
tix filter --active          # Only active tasks
tix filter --completed       # Only completed tasks

# List all tags
tix tags

# Show untagged tasks
tix tags --no-tags
```

#### Statistics and Reports

```bash
# View statistics
tix stats

# Detailed statistics
tix stats --detailed

# Generate text report
tix report

# Export as JSON
tix report --format json --output tasks.json

# Export as text file
tix report --output my-tasks.txt
```

## 📁 Data Storage

Tasks are stored in `~/.tix/tasks.json` in your home directory.

Example structure:
```json
{
  "next_id": 4,
  "tasks": [
    {
      "id": 1,
      "text": "Fix critical bug",
      "priority": "high",
      "completed": false,
      "created_at": "2025-01-17T10:30:00",
      "completed_at": null,
      "tags": ["bug", "urgent"]
    }
  ]
}
```

## 🎨 Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `add` | Add a new task | `tix add "Task" -p high -t work` |
| `ls` | List tasks | `tix ls --all` |
| `done` | Complete a task | `tix done 1` |
| `done-all` | Complete multiple tasks | `tix done-all 1 2 3` |
| `rm` | Remove a task | `tix rm 1` |
| `clear` | Clear tasks in bulk | `tix clear --completed` |
| `edit` | Edit task properties | `tix edit 1 --text "New"` |
| `priority` | Change task priority | `tix priority 1 high` |
| `move` | Change task ID | `tix move 1 10` |
| `undo` | Reactivate completed task | `tix undo 1` |
| `search` | Search tasks by text | `tix search "bug"` |
| `filter` | Filter by criteria | `tix filter -p high` |
| `tags` | List all tags | `tix tags` |
| `stats` | Show statistics | `tix stats` |
| `report` | Generate report | `tix report --format json` |
| `completion` | Manage shell completion | `tix completion --reset` |

## 🔧 Configuration

### Environment Variables

```bash
# Set custom storage location (optional)
export TIX_HOME=/custom/path
```

### Aliases (Optional)

Add to your shell config file:

```bash
alias t='tix'
alias ta='tix add'
alias tl='tix ls'
alias td='tix done'
alias ts='tix search'
```

## 🧪 Development

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/TheDevOpsBlueprint/tix-cli.git
cd tix-cli

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -r requirements.txt
pip install -e .

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=tix --cov-report=term-missing
```

### Project Structure

```
tix-cli/
├── tix/
│   ├── __init__.py
│   ├── cli.py              # Main CLI with auto-completion
│   ├── models.py           # Task data model
│   ├── commands/
│   │   └── stats.py        # Statistics module
│   └── storage/
│       └── json_storage.py # Storage backend
├── tests/
│   ├── test_cli.py
│   ├── test_models.py
│   ├── test_storage.py
│   └── test_completion.py
├── setup.py                # With auto-completion setup
├── requirements.txt
└── README.md
```

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Keep changes focused and small
4. Write tests for new features
5. Ensure all tests pass
6. Submit a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📝 Examples

### Daily Workflow

```bash
# Morning: Add today's tasks (with tab completion!)
tix add<TAB> "Team standup meeting" -p<TAB> high -t<TAB> work
tix add "Review pull requests" -p medium -t work
tix add "Fix login bug" -p high -t bug -t urgent
tix add "Update documentation" -p low -t docs

# Check your tasks
tix ls

# Complete tasks using tab completion for IDs
tix done<TAB> 1<TAB>  # Tab shows available task IDs
tix done 3

# End of day: View progress
tix stats

# Generate report
tix report --output daily-report.txt
```

### Project Management

```bash
# Add project tasks with tags
tix add "Design database schema" -p high -t project-x -t backend
tix add "Create API endpoints" -p high -t project-x -t backend
tix add "Write unit tests" -p medium -t project-x -t testing
tix add "Setup CI/CD pipeline" -p medium -t project-x -t devops

# View project tasks with tab completion
tix filter<TAB> -t<TAB> project-x

# Search within project
tix search "API" -t project-x
```

## 🐛 Troubleshooting

### Common Issues

**Issue: Shell completion not working**
```bash
# Check if completion is configured
grep _TIX_COMPLETE ~/.bashrc  # or ~/.zshrc for zsh

# Reset and reconfigure
tix completion --reset
tix  # This will auto-configure again

# Manually source your shell config
source ~/.bashrc  # or ~/.zshrc for zsh
```

**Issue: `tix: command not found`**
```bash
# Ensure you're in virtual environment
source venv/bin/activate

# Or reinstall
pip install -e .
```

**Issue: Tasks not persisting**
```bash
# Check storage file exists
ls -la ~/.tix/tasks.json

# Check permissions
chmod 644 ~/.tix/tasks.json
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with:
- [Click](https://click.palletsprojects.com/) - CLI framework with native completion support
- [Rich](https://rich.readthedocs.io/) - Terminal formatting
- [Python](https://python.org/) - Programming language

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/TheDevOpsBlueprint/tix-cli/issues)
- **Discussions**: [GitHub Discussions](https://github.com/TheDevOpsBlueprint/tix-cli/discussions)
- **Email**: valentin.v.todorov@gmail.com

---

**Made with ❤️ by TheDevOpsBlueprint**