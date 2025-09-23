#!/bin/bash

# TIX Smart Installer - One command to rule them all
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
echo "║                TIX - Smart Installer                      ║"
echo "║          Lightning-fast Terminal Task Manager             ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Detect OS
OS=$(uname -s)
echo -e "${YELLOW}📍 Detecting system...${NC}"
echo "   OS: $OS"

# Detect Shell
SHELL_NAME=$(basename "$SHELL")
echo "   Shell: $SHELL_NAME"

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

# Check if pip is installed
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}📦 Installing pip...${NC}"
    curl -sSL https://bootstrap.pypa.io/get-pip.py | $PYTHON_CMD
fi

PIP_CMD=$(command -v pip3 || command -v pip)

# Install or upgrade TIX
echo -e "\n${YELLOW}📦 Installing TIX...${NC}"

# Check if we're in the repo directory
if [ -f "setup.py" ] && [ -d "tix" ]; then
    echo "   Found local repository, installing in development mode..."
    $PIP_CMD install -e . --quiet --upgrade
else
    # Install from PyPI or GitHub
    echo "   Installing from GitHub..."
    $PIP_CMD install --quiet --upgrade git+https://github.com/TheDevOpsBlueprint/tix-cli.git
fi

# Verify installation
if ! command -v tix &> /dev/null; then
    echo -e "${RED}❌ Installation failed. Please check the error messages above.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ TIX installed successfully!${NC}"

# Trigger completion setup by running tix once
echo -e "\n${YELLOW}🔧 Setting up shell completion...${NC}"
tix --version > /dev/null 2>&1 || true

# Determine shell config file
case "$SHELL_NAME" in
    bash)
        if [ -f "$HOME/.bashrc" ]; then
            CONFIG_FILE="$HOME/.bashrc"
        elif [ -f "$HOME/.bash_profile" ]; then
            CONFIG_FILE="$HOME/.bash_profile"
        else
            CONFIG_FILE="$HOME/.bashrc"
            touch "$CONFIG_FILE"
        fi
        ;;
    zsh)
        CONFIG_FILE="$HOME/.zshrc"
        [ ! -f "$CONFIG_FILE" ] && touch "$CONFIG_FILE"
        ;;
    fish)
        CONFIG_FILE="$HOME/.config/fish/config.fish"
        mkdir -p "$(dirname "$CONFIG_FILE")"
        [ ! -f "$CONFIG_FILE" ] && touch "$CONFIG_FILE"
        ;;
    *)
        echo -e "${YELLOW}⚠️  Unknown shell: $SHELL_NAME${NC}"
        CONFIG_FILE=""
        ;;
esac

# Check if completion was added
if [ -n "$CONFIG_FILE" ] && grep -q "_TIX_COMPLETE\|_tix_completion" "$CONFIG_FILE" 2>/dev/null; then
    echo -e "${GREEN}✅ Shell completion configured!${NC}"
else
    echo -e "${YELLOW}⚠️  Shell completion may need manual setup${NC}"
fi

# Create alias for convenience (optional)
if [ -n "$CONFIG_FILE" ] && ! grep -q "alias t=" "$CONFIG_FILE" 2>/dev/null; then
    echo -e "\n${YELLOW}📝 Adding convenient alias 't' for 'tix'...${NC}"
    echo "" >> "$CONFIG_FILE"
    echo "# TIX alias for convenience" >> "$CONFIG_FILE"
    echo "alias t='tix'" >> "$CONFIG_FILE"
    echo -e "${GREEN}✅ Alias added: 't' → 'tix'${NC}"
fi

# Final message
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         🎉 TIX Installation Complete! 🎉                  ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}To start using TIX with tab completion, do ONE of:${NC}"
echo ""
echo -e "  ${GREEN}Option 1:${NC} Start a new terminal session"
echo -e "  ${GREEN}Option 2:${NC} Run: ${YELLOW}source $CONFIG_FILE${NC}"
echo -e "  ${GREEN}Option 3:${NC} Run: ${YELLOW}exec $SHELL_NAME${NC}"
echo ""
echo -e "${BLUE}Quick start:${NC}"
echo -e "  ${YELLOW}tix add \"My first task\" -p high${NC}  # Add a task"
echo -e "  ${YELLOW}tix ls${NC}                            # List tasks"
echo -e "  ${YELLOW}tix <TAB><TAB>${NC}                    # See all commands"
echo -e "  ${YELLOW}t ls${NC}                              # Use short alias"
echo ""

# Offer to restart shell automatically
if [ -t 0 ] && [ -t 1 ]; then  # Check if interactive terminal
    echo -e "${YELLOW}Would you like to restart your shell now to enable completion? (y/N)${NC}"
    read -r -n 1 -s answer
    echo
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}🔄 Restarting shell...${NC}"
        exec $SHELL
    fi
fi

echo -e "${BLUE}Happy task managing! 🚀${NC}"