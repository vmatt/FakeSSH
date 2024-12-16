#!/bin/bash

# Detect OS and set package manager
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        if [[ "$ID_LIKE" == *"debian"* ]]; then
            OS="Debian-based"
            PKG_MANAGER="apt"
            PKG_INSTALL="sudo apt install -y"
        elif [[ "$ID_LIKE" == *"rhel"* ]] || [[ "$ID_LIKE" == *"fedora"* ]] || [[ "$ID_LIKE" == *"centos"* ]]; then
            OS="RHEL-based"
            PKG_MANAGER="yum"
            PKG_INSTALL="sudo yum install -y"
        else
            echo "Unsupported OS type: $ID_LIKE"
            exit 1
        fi
    else
        echo "Cannot detect OS type. /etc/os-release not found."
        exit 1
    fi
}

# Check and install tmux
check_tmux() {
    echo "Checking tmux installation..."
    if ! command -v tmux &> /dev/null; then
        echo "tmux is not installed"
        echo "Attempting to install tmux..."
        if [ "$PKG_MANAGER" = "apt" ]; then
            sudo apt update
            $PKG_INSTALL tmux
        elif [ "$PKG_MANAGER" = "yum" ]; then
            sudo yum check-update
            $PKG_INSTALL tmux
        fi
        
        # Verify installation
        if ! command -v tmux &> /dev/null; then
            echo "Failed to install tmux automatically."
            echo "Please install tmux manually using one of these commands:"
            echo "  Debian/Ubuntu: sudo apt install tmux"
            echo "  RHEL/CentOS:  sudo yum install tmux"
            exit 1
        fi
        echo "tmux installed successfully!"
    else
        echo "tmux is already installed"
    fi
    
    # Check tmux version
    TMUX_VERSION=$(tmux -V | cut -d' ' -f2)
    echo "tmux version: $TMUX_VERSION"
}

# Check if RSA key exists
check_key() {
    if [ ! -f "RSA_PRIVATE.key" ]; then
        echo "RSA key not found. Running install script..."
        bash install.sh
    fi
}

# Start honeypot in tmux session
start_honeypot() {
    SESSION_NAME="honeypot"
    
    # Check if session already exists
    if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
        echo "Honeypot is already running in a tmux session"
        echo "To attach to it, use: tmux attach -t $SESSION_NAME"
        exit 0
    fi
    
    echo "Starting honeypot in tmux session..."
    tmux new-session -d -s "$SESSION_NAME" "sudo python3 fakessh.py"
    echo "Honeypot started in background tmux session"
    echo "To view the honeypot:"
    echo "  - Attach to session: tmux attach -t $SESSION_NAME"
    echo "  - Detach from session: Ctrl+B, then D"
    echo "  - Kill the session: tmux kill-session -t $SESSION_NAME"
}

# Main execution
detect_os
echo "Detected OS: $OS"
echo "Using package manager: $PKG_MANAGER"
check_tmux
check_key
start_honeypot
