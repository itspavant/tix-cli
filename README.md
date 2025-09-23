# TIX - Lightning-fast Terminal Task Manager ⚡

A minimalist, powerful command-line task manager built with Python. Manage your todos efficiently without leaving your terminal.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)
![Shell Completion](https://img.shields.io/badge/completion-auto--enabled-success.svg)
![One-Command Install](https://img.shields.io/badge/install-one--command-ff69b4.svg)

## 🚀 Quick Install (One Command!)

```bash
curl -sSL https://raw.githubusercontent.com/TheDevOpsBlueprint/tix-cli/main/install.sh | bash
```

**That's it!** This smart installer will:
- ✅ Detect your OS and shell automatically
- ✅ Install Python dependencies if needed
- ✅ Install TIX with pip
- ✅ Configure shell completion automatically
- ✅ Add convenient alias (`t` for `tix`)
- ✅ Offer to restart your shell with everything ready

After installation, you can immediately use:
```bash
tix <TAB><TAB>  # Tab completion works!
t add "My task"  # Short alias works!
```

## ✨ Features

- **Fast & Simple**: Add tasks with a single command
- **Smart Installation**: One-command setup with auto-completion
- **Persistent Storage**: Tasks are saved locally in JSON format
- **Priority Levels**: Organize tasks by high, medium, or low priority
- **Tags**: Categorize tasks with custom tags
- **Search & Filter**: Find tasks quickly with powerful search
- **Statistics**: Track your productivity with built-in analytics
- **Reports**: Export your tasks in text or JSON format
- **Colored Output**: Beautiful terminal UI with rich formatting
- **Bulk Operations**: Mark multiple tasks as done at once
- **Auto Shell Completion**: Tab completion works out of the box for bash, zsh, and fish
- **Convenient Alias**: Use `t` instead of `tix` for faster typing

## 📖 Alternative Installation Methods

### From Source

```bash
# Clone
git clone https://github.com/TheDevOpsBlueprint/tix-cli.git
cd tix-cli

# Run installer
./install.sh

# Or use Make
make  # Runs smart installer
```

### Using pip (Manual Completion Setup)

```bash
# Install
pip install tix-cli

# Setup completion
tix --init-completion

# Enable completion (choose based on your shell)
source ~/.bashrc   # For bash
source ~/.zshrc    # For zsh
exec fish         # For fish
```

### For Developers

```bash
git clone https://github.com/TheDevOpsBlueprint/tix-cli.git
cd tix-cli
make quick-install  # Fast dev install
```

## 🎯 Usage Guide

### Basic Commands

#### Adding Tasks

```bash
# Simple task
tix add "Write documentation"
# Or use alias
t add "Write documentation"

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
# Or
t ls

# Show all tasks (including completed)
tix ls --all
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

## 🎨 Using Tab Completion

Tab completion works automatically after installation:

```bash
# Complete commands
tix <TAB><TAB>
# Shows: add clear completion done done-all edit filter ls move priority report rm search stats tags undo

# Complete options
tix add --<TAB><TAB>
# Shows: --priority --tag --help

# Complete option values
tix add --priority <TAB><TAB>
# Shows: high low medium

# Works with the alias too
t <TAB><TAB>
t add --<TAB><TAB>
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

### Aliases

The installer automatically adds `alias t='tix'` to your shell config.

You can add more aliases manually:

```bash
# Add to ~/.bashrc or ~/.zshrc
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

# Use make for easy setup
make setup  # Creates venv and installs everything

# Or manually
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .

# Run tests
make test
# Or
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=tix --cov-report=term-missing
```

### Project Structure

```
tix-cli/
├── install.sh              # Smart installer script
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
├── setup.py                # With post-install hooks
├── Makefile               # Developer commands
├── requirements.txt
└── README.md
```

## 📝 Examples

### Daily Workflow

```bash
# Morning: Add today's tasks (using alias for speed)
t add "Team standup meeting" -p high -t work
t add "Review pull requests" -p medium -t work
t add "Fix login bug" -p high -t bug -t urgent
t add "Update documentation" -p low -t docs

# Check your tasks
t ls

# Complete tasks using tab completion for IDs
t done<TAB> 1<TAB>  # Tab shows available task IDs
t done 3

# End of day: View progress
t stats

# Generate report
t report --output daily-report.txt
```

### Project Management

```bash
# Add project tasks with tags
t add "Design database schema" -p high -t project-x -t backend
t add "Create API endpoints" -p high -t project-x -t backend
t add "Write unit tests" -p medium -t project-x -t testing
t add "Setup CI/CD pipeline" -p medium -t project-x -t devops

# View project tasks
t filter -t project-x

# Search within project
t search "API" -t project-x
```

## 🐛 Troubleshooting

### Installation Issues

**Issue: One-command install fails**
```bash
# Try manual installation
git clone https://github.com/TheDevOpsBlueprint/tix-cli.git
cd tix-cli
pip install -e .
tix --init-completion
source ~/.bashrc
```

### Shell Completion Issues

**Issue: Tab completion not working**
```bash
# Reset and reconfigure
tix completion --reset
tix --init-completion
source ~/.bashrc  # or ~/.zshrc for zsh

# Verify completion is loaded
grep "TIX" ~/.bashrc
```

**Issue: `tix: command not found`**
```bash
# Ensure pip bin directory is in PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Or reinstall
pip install --user tix-cli
```

### Data Issues

**Issue: Tasks not persisting**
```bash
# Check storage file exists
ls -la ~/.tix/tasks.json

# Check permissions
chmod 644 ~/.tix/tasks.json
```

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Keep changes focused and small
4. Write tests for new features
5. Ensure all tests pass (`make test`)
6. Submit a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

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

## 🌟 Star History

If you find TIX useful, please consider giving it a star on GitHub!

[![Star History](https://img.shields.io/github/stars/TheDevOpsBlueprint/tix-cli?style=social)](https://github.com/TheDevOpsBlueprint/tix-cli)

---

**Made with ❤️ by TheDevOpsBlueprint**