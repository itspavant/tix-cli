#!/bin/bash

# TIX Installer FIX2 - Handles all edge cases automatically
# Version 7.0 - Works with custom prompts and all environments
# Usage: curl -sSL https://raw.githubusercontent.com/TheDevOpsBlueprint/tix-cli/main/install.sh | bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                TIX - Smart Installer v7.0                 ║"
echo "║          Lightning-fast Terminal Task Manager             ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Detect OS and Architecture
OS=$(uname -s)
ARCH=$(uname -m)
echo -e "${YELLOW}📍 Detecting system...${NC}"
echo "   OS: $OS"
echo "   Architecture: $ARCH"

# Detect Shell
SHELL_NAME=$(basename "$SHELL")
echo "   Shell: $SHELL_NAME"
echo "   Bash Version: $BASH_VERSION"

# Detect Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ Python not found. Please install Python 3.7+ first.${NC}"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
echo "   Python: $PYTHON_VERSION"

# Detect if we're in a virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    echo -e "${GREEN}   Virtual Environment: Active${NC}"
    IN_VENV=true
else
    echo -e "${YELLOW}   Virtual Environment: Not active${NC}"
    IN_VENV=false
fi

# Function to install with pip
install_with_pip() {
    local pip_cmd="$1"
    local install_args="$2"

    if [ -f "setup.py" ] && [ -d "tix" ]; then
        echo "   Found local repository, installing in development mode..."
        $pip_cmd install -e . $install_args --quiet --upgrade
    else
        echo "   Installing from GitHub..."
        $pip_cmd install $install_args --quiet --upgrade git+https://github.com/TheDevOpsBlueprint/tix-cli.git
    fi
}

# Install or upgrade TIX
echo -e "\n${YELLOW}📦 Installing TIX...${NC}"

# Check if pip/pip3 is available
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    echo -e "${YELLOW}📦 Installing pip...${NC}"
    curl -sSL https://bootstrap.pypa.io/get-pip.py | $PYTHON_CMD
    PIP_CMD="pip"
fi

# Handle installation based on environment
INSTALL_SUCCESS=false
INSTALL_METHOD=""

if [ "$IN_VENV" = true ]; then
    # In virtual environment - direct install
    echo "   Installing in virtual environment..."
    install_with_pip "$PIP_CMD" ""
    INSTALL_SUCCESS=true
    INSTALL_METHOD="venv"

elif [ "$OS" = "Darwin" ]; then
    # macOS with potential brew Python
    echo "   Detected macOS with managed Python environment..."

    # Try pipx (recommended for managed environments)
    if command -v pipx &> /dev/null; then
        echo "   Using pipx for isolated installation..."
        if [ -f "setup.py" ] && [ -d "tix" ]; then
            pipx install -e . --force
        else
            pipx install tix-cli --force || pipx install git+https://github.com/TheDevOpsBlueprint/tix-cli.git --force
        fi
        INSTALL_SUCCESS=true
        INSTALL_METHOD="pipx"
    elif command -v brew &> /dev/null; then
        echo "   Installing pipx first..."
        brew install pipx
        pipx ensurepath
        export PATH="$HOME/.local/bin:$PATH"

        if [ -f "setup.py" ] && [ -d "tix" ]; then
            pipx install -e . --force
        else
            pipx install tix-cli --force || pipx install git+https://github.com/TheDevOpsBlueprint/tix-cli.git --force
        fi
        INSTALL_SUCCESS=true
        INSTALL_METHOD="pipx"
    else
        echo "   Using pip with --user flag..."
        install_with_pip "$PIP_CMD" "--user --break-system-packages"
        INSTALL_SUCCESS=true
        INSTALL_METHOD="pip-user"
    fi

else
    # Linux or other OS
    echo "   Installing for $OS..."

    if install_with_pip "$PIP_CMD" "--user" 2>/dev/null; then
        INSTALL_SUCCESS=true
        INSTALL_METHOD="pip-user"
    elif install_with_pip "$PIP_CMD" "" 2>/dev/null; then
        INSTALL_SUCCESS=true
        INSTALL_METHOD="pip-system"
    else
        install_with_pip "$PIP_CMD" "--user --break-system-packages"
        INSTALL_SUCCESS=true
        INSTALL_METHOD="pip-user"
    fi
fi

# Ensure PATH includes ~/.local/bin
export PATH="$HOME/.local/bin:$PATH"

# Verify tix is available
if ! command -v tix &> /dev/null; then
    echo -e "${RED}❌ Installation completed but 'tix' command not found.${NC}"
    echo -e "${YELLOW}Add this to your shell configuration:${NC}"
    echo -e "${GREEN}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
    exit 1
fi

echo -e "${GREEN}✅ TIX installed successfully!${NC}"

# Setup shell completion
echo -e "\n${YELLOW}🔧 Setting up shell completion...${NC}"

# Determine shell config file
case "$SHELL_NAME" in
    bash)
        CONFIG_FILE="$HOME/.bash_profile"
        [ "$OS" != "Darwin" ] && [ -f "$HOME/.bashrc" ] && CONFIG_FILE="$HOME/.bashrc"
        ;;
    zsh)
        CONFIG_FILE="$HOME/.zshrc"
        ;;
    fish)
        CONFIG_FILE="$HOME/.config/fish/config.fish"
        mkdir -p "$(dirname "$CONFIG_FILE")"
        ;;
    *)
        echo -e "${YELLOW}⚠️  Unknown shell: $SHELL_NAME${NC}"
        CONFIG_FILE=""
        ;;
esac

# For bash: Clean up ANY old TIX completion entries
if [ "$SHELL_NAME" = "bash" ] && [ -f "$CONFIG_FILE" ]; then
    # Create backup
    cp "$CONFIG_FILE" "${CONFIG_FILE}.backup.$(date +%s)" 2>/dev/null || true

    # Remove ALL TIX-related lines using a Python script for reliability
    $PYTHON_CMD << 'PYTHON_CLEANUP'
import sys
import os

config_file = os.path.expanduser("~/.bash_profile")
if not os.path.exists(config_file):
    sys.exit(0)

with open(config_file, 'r') as f:
    lines = f.readlines()

# Remove any TIX-related content
new_lines = []
skip_until_empty = False

for line in lines:
    # Check if this line starts a TIX section
    if any(marker in line for marker in ['TIX Command Completion', '_tix_completion', 'complete -F _tix', 'TIX_COMPLETE']):
        skip_until_empty = True
        continue

    # If we're skipping, continue until we hit an empty line or end of function
    if skip_until_empty:
        if line.strip() == '' or line.strip() == '}' or 'complete -F' in line:
            if 'complete -F' in line and 'tix' in line:
                continue  # Skip the complete command too
            skip_until_empty = False
            if line.strip() == '}':
                continue  # Skip the closing brace
        else:
            continue

    new_lines.append(line)

# Write back
with open(config_file, 'w') as f:
    f.writelines(new_lines)

print("Cleaned up old TIX entries")
PYTHON_CLEANUP
fi

# Add fresh completion for bash
COMPLETION_ADDED=false

if [ "$SHELL_NAME" = "bash" ] && [ -n "$CONFIG_FILE" ]; then
    # Ensure PATH is in config
    if ! grep -q "export PATH.*\.local/bin" "$CONFIG_FILE" 2>/dev/null; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$CONFIG_FILE"
    fi

    # Create a separate TIX completion file that will load reliably
    TIX_COMPLETION_FILE="$HOME/.tix_bash_completion"

    cat > "$TIX_COMPLETION_FILE" << 'TIX_COMPLETION_CONTENT'
# TIX Bash Completion v7.0
# This file is sourced at the end of bash_profile to ensure it loads after custom prompts

_tix_completion_function() {
    local cur prev
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Main commands
    local commands="add ls done rm clear undo done-all edit priority move search filter tags stats report"

    # First argument - show commands and global options
    if [ $COMP_CWORD -eq 1 ]; then
        COMPREPLY=( $(compgen -W "${commands} --help --version" -- ${cur}) )
        return 0
    fi

    # Command-specific completions
    case "${COMP_WORDS[1]}" in
        add)
            if [[ ${cur} == -* ]]; then
                COMPREPLY=( $(compgen -W "--priority -p --tag -t" -- ${cur}) )
            elif [[ ${prev} == "-p" ]] || [[ ${prev} == "--priority" ]]; then
                COMPREPLY=( $(compgen -W "low medium high" -- ${cur}) )
            fi
            ;;
        ls)
            COMPREPLY=( $(compgen -W "--all -a" -- ${cur}) )
            ;;
        rm)
            COMPREPLY=( $(compgen -W "--confirm -y" -- ${cur}) )
            ;;
        clear)
            COMPREPLY=( $(compgen -W "--completed --active --force -f" -- ${cur}) )
            ;;
        edit)
            COMPREPLY=( $(compgen -W "--text -t --priority -p --add-tag --remove-tag" -- ${cur}) )
            ;;
        filter)
            COMPREPLY=( $(compgen -W "--priority -p --tag -t --completed -c --active -a" -- ${cur}) )
            ;;
        search)
            COMPREPLY=( $(compgen -W "--tag -t --priority -p --completed -c" -- ${cur}) )
            ;;
        stats)
            COMPREPLY=( $(compgen -W "--detailed -d" -- ${cur}) )
            ;;
        report)
            if [[ ${cur} == -* ]]; then
                COMPREPLY=( $(compgen -W "--format -f --output -o" -- ${cur}) )
            elif [[ ${prev} == "-f" ]] || [[ ${prev} == "--format" ]]; then
                COMPREPLY=( $(compgen -W "text json" -- ${cur}) )
            fi
            ;;
        tags)
            COMPREPLY=( $(compgen -W "--no-tags" -- ${cur}) )
            ;;
        priority)
            if [ $COMP_CWORD -eq 3 ]; then
                COMPREPLY=( $(compgen -W "low medium high" -- ${cur}) )
            fi
            ;;
        *)
            COMPREPLY=( $(compgen -W "--help" -- ${cur}) )
            ;;
    esac
}

# Register the completion
complete -F _tix_completion_function tix

# Verify it's registered (for debugging)
if complete -p tix &>/dev/null; then
    : # Success - completion is registered
else
    # Fallback registration
    complete -W "add ls done rm clear undo done-all edit priority move search filter tags stats report --help --version" tix
fi
TIX_COMPLETION_CONTENT

    # Now ensure this file is sourced at the END of bash_profile
    # First remove any existing source line for it
    grep -v "source.*tix_bash_completion" "$CONFIG_FILE" > "$CONFIG_FILE.tmp" 2>/dev/null || true
    mv "$CONFIG_FILE.tmp" "$CONFIG_FILE" 2>/dev/null || true

    # Add the source line at the very end
    echo "" >> "$CONFIG_FILE"
    echo "# TIX Completion - Load at end to work with custom prompts" >> "$CONFIG_FILE"
    echo "[ -f ~/.tix_bash_completion ] && source ~/.tix_bash_completion" >> "$CONFIG_FILE"

    COMPLETION_ADDED=true

elif [ "$SHELL_NAME" = "zsh" ] && [ -n "$CONFIG_FILE" ]; then
    if ! grep -q "_TIX_COMPLETE" "$CONFIG_FILE" 2>/dev/null; then
        echo "" >> "$CONFIG_FILE"
        echo "# TIX Command Completion" >> "$CONFIG_FILE"
        echo 'eval "$(_TIX_COMPLETE=zsh_source tix)"' >> "$CONFIG_FILE"
        COMPLETION_ADDED=true
    fi

elif [ "$SHELL_NAME" = "fish" ]; then
    FISH_COMPLETIONS="$HOME/.config/fish/completions"
    mkdir -p "$FISH_COMPLETIONS"
    echo '_TIX_COMPLETE=fish_source tix | source' > "$FISH_COMPLETIONS/tix.fish"
    COMPLETION_ADDED=true
fi

if [ "$COMPLETION_ADDED" = true ]; then
    echo -e "${GREEN}✅ Shell completion configured!${NC}"

    # For bash, immediately source the completion in current session
    if [ "$SHELL_NAME" = "bash" ] && [ -f "$HOME/.tix_bash_completion" ]; then
        source "$HOME/.tix_bash_completion" 2>/dev/null || true
    fi
else
    echo -e "${YELLOW}ℹ️  Completion setup skipped${NC}"
fi

# Final message
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         🎉 TIX Installation Complete! 🎉                  ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$SHELL_NAME" = "bash" ]; then
    echo -e "${BLUE}To activate TIX with tab completion:${NC}"
    echo -e "  ${YELLOW}source ~/.bash_profile${NC}"
    echo ""
    echo -e "${BLUE}Or open a new terminal window.${NC}"
else
    echo -e "${BLUE}To activate TIX:${NC}"
    echo -e "  ${YELLOW}source $CONFIG_FILE${NC}"
fi

echo ""
echo -e "${BLUE}Test completion:${NC}"
echo -e "  ${YELLOW}tix <TAB><TAB>${NC}  # Should show commands"
echo ""
echo -e "${BLUE}Quick start:${NC}"
echo -e "  ${YELLOW}tix add \"My first task\" -p high${NC}"
echo -e "  ${YELLOW}tix ls${NC}"
echo ""
echo -e "${BLUE}Happy task managing! 🚀${NC}"