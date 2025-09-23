.PHONY: install dev test clean build venv smart-install quick-install pipx-install help

# Virtual environment name
VENV_NAME := tix-venv
VENV := ./$(VENV_NAME)
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# Detect if pipx is available
PIPX := $(shell command -v pipx 2> /dev/null)

# Default target - smart install
all: smart-install

# Smart install - Everything in one command (v3.0)
smart-install:
	@echo "🚀 Starting TIX Smart Installation v3.0..."
	@if [ ! -f "./install.sh" ]; then \
		echo "Downloading installer..."; \
		curl -sSL https://raw.githubusercontent.com/TheDevOpsBlueprint/tix-cli/main/install.sh -o install.sh; \
		chmod +x install.sh; \
	fi
	@./install.sh

# Install using pipx (recommended for Python 3.12+)
pipx-install:
	@echo "📦 Installing TIX with pipx (isolated environment)..."
	@if [ -z "$(PIPX)" ]; then \
		echo "⚠️  pipx not found. Installing pipx first..."; \
		if command -v brew > /dev/null; then \
			brew install pipx; \
			pipx ensurepath; \
		else \
			python3 -m pip install --user pipx; \
			python3 -m pipx ensurepath; \
		fi; \
	fi
	@pipx install -e . --force
	@echo ""
	@echo "✅ Installation complete!"
	@echo ""
	@echo "📝 Tab completion should work automatically."
	@echo "   If not, run: eval \"\$$(_TIX_COMPLETE=bash_source tix)\""

# Quick install for developers
quick-install:
	@echo "⚡ Quick Install for Developers"
	@# Try different installation methods based on environment
	@if [ -n "$$VIRTUAL_ENV" ]; then \
		echo "   Installing in virtual environment..."; \
		pip install -e . --upgrade; \
	elif command -v pipx > /dev/null 2>&1; then \
		echo "   Using pipx for isolated installation..."; \
		pipx install -e . --force; \
	else \
		echo "   Installing with --user flag..."; \
		pip install -e . --user --upgrade || pip install -e . --user --break-system-packages --upgrade; \
	fi
	@tix --version > /dev/null 2>&1 || true
	@echo ""
	@echo "✅ Installation complete!"

# Create virtual environment
venv:
	python3 -m venv $(VENV_NAME)
	@echo "✅ Virtual environment '$(VENV_NAME)' created"
	@echo "Run 'source $(VENV_NAME)/bin/activate' to activate"

# Install package in venv
install: venv
	$(PIP) install -e .
	@echo ""
	@echo "📝 Note: Activate venv first: source $(VENV_NAME)/bin/activate"

# Development setup (install deps + package)
dev: venv
	$(PIP) install -r requirements.txt
	$(PIP) install -e .
	@echo ""
	@echo "✅ Development environment ready!"
	@echo "   Activate: source $(VENV_NAME)/bin/activate"

# Run tests
test:
	@if [ -d "$(VENV)" ]; then \
		$(PYTHON) -m pytest tests/ -v; \
	else \
		python3 -m pytest tests/ -v; \
	fi

# Run tests with coverage
test-coverage:
	@if [ -d "$(VENV)" ]; then \
		$(PYTHON) -m pytest tests/ -v --cov=tix --cov-report=term-missing; \
	else \
		python3 -m pytest tests/ -v --cov=tix --cov-report=term-missing; \
	fi

# Clean build artifacts
clean:
	rm -rf build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .coverage

# Clean everything including venv
clean-all: clean
	rm -rf $(VENV_NAME)
	rm -rf ~/.tix-venv  # Clean temporary venv if created by installer

# Build distribution packages
build:
	python3 setup.py sdist bdist_wheel

# Uninstall TIX completely
uninstall:
	@echo "🗑️  Uninstalling TIX..."
	@pip uninstall tix-cli -y 2>/dev/null || true
	@pip3 uninstall tix-cli -y 2>/dev/null || true
	@pipx uninstall tix-cli 2>/dev/null || true
	@rm -rf ~/.tix
	@rm -f ~/.local/bin/tix
	@echo "✅ TIX uninstalled"

# Setup for new developers - one command to get started
setup: venv
	$(PIP) install -r requirements.txt
	$(PIP) install -e .
	@echo "✅ Setup complete! Run 'source $(VENV_NAME)/bin/activate'"

# Help target
help:
	@echo "TIX Makefile Commands:"
	@echo ""
	@echo "  make              # Smart install v3.0 (handles all environments)"
	@echo "  make pipx-install # Install with pipx (Python 3.12+ recommended)"
	@echo "  make quick-install# Quick install for developers"
	@echo "  make setup        # Full dev environment setup with venv"
	@echo "  make test         # Run tests"
	@echo "  make test-coverage# Run tests with coverage report"
	@echo "  make clean        # Clean build artifacts"
	@echo "  make clean-all    # Clean everything including venv"
	@echo "  make uninstall    # Completely remove TIX"
	@echo "  make help         # Show this help"
	@echo ""
	@echo "Installation methods by Python version:"
	@echo "  Python 3.7-3.11:  make  # Uses standard pip"
	@echo "  Python 3.12+:     make  # Auto-detects and uses pipx"
	@echo ""
	@echo "After installation, use:"
	@echo "  tix <TAB><TAB>    # Tab completion"