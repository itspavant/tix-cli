#!/bin/bash

# TIX Smart Installer - One command to rule them all
# Version 2.0 - Handles externally-managed-environment (PEP 668)
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
echo "║                TIX - Smart Installer v2.0                 ║"
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

# Try different installation methods
if [ "$IN_VENV" = true ]; then
    # In virtual environment - direct install
    echo "   Installing in virtual environment..."
    install_with_pip "$PIP_CMD" ""
    INSTALL_SUCCESS=true

elif [ "$OS" = "Darwin" ]; then
    # macOS with potential brew Python
    echo "   Detected macOS with managed Python environment..."

    # Method 1: Try pipx (recommended for managed environments)
    if command -v pipx &> /dev/null; then
        echo "   Using pipx for isolated installation..."
        if [ -f "setup.py" ] && [ -d "tix" ]; then
            pipx install -e . --force
        else
            pipx install tix-cli --force || pipx install git+https://github.com/TheDevOpsBlueprint/tix-cli.git --force
        fi
        INSTALL_SUCCESS=true

        # Ensure pipx bin directory is in PATH
        PIPX_BIN_DIR="$HOME/.local/bin"
        if [[ ":$PATH:" != *":$PIPX_BIN_DIR:"* ]]; then
            echo -e "${YELLOW}📝 Adding pipx bin directory to PATH...${NC}"

            # Add to appropriate shell config
            if [ "$SHELL_NAME" = "bash" ]; then
                if [ -f "$HOME/.bashrc" ]; then
                    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
                fi
                if [ -f "$HOME/.bash_profile" ]; then
                    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bash_profile"
                fi
            elif [ "$SHELL_NAME" = "zsh" ]; then
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
            fi

            export PATH="$PIPX_BIN_DIR:$PATH"
        fi

    # Method 2: Create temporary venv for installation
    elif command -v brew &> /dev/null; then
        echo "   pipx not found. Installing pipx first..."
        brew install pipx
        pipx ensurepath
        export PATH="$HOME/.local/bin:$PATH"

        echo "   Using pipx for isolated installation..."
        if [ -f "setup.py" ] && [ -d "tix" ]; then
            pipx install -e . --force
        else
            pipx install tix-cli --force || pipx install git+https://github.com/TheDevOpsBlueprint/tix-cli.git --force
        fi
        INSTALL_SUCCESS=true

    # Method 3: Use --user flag with --break-system-packages
    else
        echo "   Using pip with --user flag..."
        install_with_pip "$PIP_CMD" "--user --break-system-packages"
        INSTALL_SUCCESS=true

        # Ensure user bin directory is in PATH
        USER_BIN_DIR="$HOME/.local/bin"
        if [[ ":$PATH:" != *":$USER_BIN_DIR:"* ]]; then
            echo -e "${YELLOW}📝 Adding user bin directory to PATH...${NC}"

            if [ "$SHELL_NAME" = "bash" ]; then
                if [ -f "$HOME/.bashrc" ]; then
                    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
                fi
                if [ -f "$HOME/.bash_profile" ]; then
                    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bash_profile"
                fi
            elif [ "$SHELL_NAME" = "zsh" ]; then
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
            fi

            export PATH="$USER_BIN_DIR:$PATH"
        fi
    fi

else
    # Linux or other OS
    echo "   Installing for $OS..."

    # Try with --user flag first (safer)
    if install_with_pip "$PIP_CMD" "--user" 2>/dev/null; then
        INSTALL_SUCCESS=true

        # Ensure user bin directory is in PATH
        USER_BIN_DIR="$HOME/.local/bin"
        if [[ ":$PATH:" != *":$USER_BIN_DIR:"* ]]; then
            echo -e "${YELLOW}📝 Adding user bin directory to PATH...${NC}"

            if [ "$SHELL_NAME" = "bash" ]; then
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
            elif [ "$SHELL_NAME" = "zsh" ]; then
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
            fi

            export PATH="$USER_BIN_DIR:$PATH"
        fi
    # Fallback to system install
    elif install_with_pip "$PIP_CMD" "" 2>/dev/null; then
        INSTALL_SUCCESS=true
    # Last resort with --break-system-packages
    else
        echo "   Attempting installation with --break-system-packages..."
        install_with_pip "$PIP_CMD" "--user --break-system-packages"
        INSTALL_SUCCESS=true
    fi
fi

# Verify installation
if [ "$INSTALL_SUCCESS" = false ]; then
    echo -e "${RED}❌ Installation failed. Trying alternative method...${NC}"

    # Create a temporary virtual environment as last resort
    echo -e "${YELLOW}📦 Creating temporary virtual environment...${NC}"
    TEMP_VENV="$HOME/.tix-venv"
    $PYTHON_CMD -m venv "$TEMP_VENV"
    source "$TEMP_VENV/bin/activate"

    install_with_pip "pip" ""

    # Create wrapper script
    echo -e "${YELLOW}📝 Creating wrapper script...${NC}"
    cat > "$HOME/.local/bin/tix" << 'EOF'
#!/bin/bash
source "$HOME/.tix-venv/bin/activate" 2>/dev/null
exec tix "$@"
EOF
    chmod +x "$HOME/.local/bin/tix"

    deactivate
fi

# Update PATH for current session
export PATH="$HOME/.local/bin:$PATH"

# Verify tix is now available
if ! command -v tix &> /dev/null; then
    echo -e "${RED}❌ Installation completed but 'tix' command not found in PATH.${NC}"
    echo -e "${YELLOW}Please add this to your shell configuration:${NC}"
    echo -e "${GREEN}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
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
    echo -e "${YELLOW}   Run: tix --init-completion${NC}"
fi

# Ensure PATH export is in shell config
if [ -n "$CONFIG_FILE" ]; then
    if ! grep -q "export PATH.*\.local/bin" "$CONFIG_FILE" 2>/dev/null; then
        echo "" >> "$CONFIG_FILE"
        echo "# Add local bin to PATH for TIX" >> "$CONFIG_FILE"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$CONFIG_FILE"
    fi
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