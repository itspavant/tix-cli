.PHONY: install dev test clean build venv

# Virtual environment name
VENV_NAME := tix-venv
VENV := ./$(VENV_NAME)
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# Create virtual environment
venv:
	python3 -m venv $(VENV_NAME)
	@echo "✅ Virtual environment '$(VENV_NAME)' created"
	@echo "Run 'source $(VENV_NAME)/bin/activate' to activate"

# Install package only
install:
	pip install -e .

# Development setup (install deps + package)
dev:
	pip install -r requirements.txt
	pip install -e .

# Run tests (works even outside venv)
test:
	$(PYTHON) -m pytest tests/ -v

# Clean build artifacts
clean:
	rm -rf build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .pytest_cache

# Clean everything including venv
clean-all: clean
	rm -rf $(VENV_NAME)

# Build distribution packages
build:
	python setup.py sdist bdist_wheel

# Quick setup for new developers
setup: venv
	$(PIP) install -r requirements.txt
	$(PIP) install -e .
	@echo "✅ Setup complete! Run 'source $(VENV_NAME)/bin/activate'"