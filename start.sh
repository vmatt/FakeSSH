#!/bin/bash

# Detect OS and set package manager
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        if [[ "$ID_LIKE" == *"debian"* ]]; then
            OS="Debian-based"
            PKG_MANAGER="apt"
            PKG_UPDATE="sudo apt update"
            PKG_INSTALL="sudo apt install -y"
        elif [[ "$ID_LIKE" == *"rhel"* ]] || [[ "$ID_LIKE" == *"fedora"* ]] || [[ "$ID_LIKE" == *"centos"* ]]; then
            OS="RHEL-based"
            PKG_MANAGER="yum"
            PKG_UPDATE="sudo yum update"
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

# Check if screen is installed
check_screen() {
    if ! command -v screen &> /dev/null; then
        echo "Error: screen is not installed"
        echo "Installing screen..."
        $PKG_UPDATE
        $PKG_INSTALL screen
        if [ $? -ne 0 ]; then
            echo "Failed to install screen. Please install it manually."
            exit 1
        fi
    fi
}

# Check if RSA key exists
check_key() {
    if [ ! -f "RSA_PRIVATE.key" ]; then
        echo "RSA key not found. Running install script..."
        bash install.sh
    fi
}

# Start honeypot in screen session
start_honeypot() {
    SESSION_NAME="honeypot"
    
    # Check if session already exists
    if screen -list | grep -q "$SESSION_NAME"; then
        echo "Honeypot is already running in a screen session"
        echo "To attach to it, use: screen -r $SESSION_NAME"
        exit 0
    fi
    
    echo "Starting honeypot in screen session..."
    screen -dmS "$SESSION_NAME" sudo python3 fakessh.py
    echo "Honeypot started in background screen session"
    echo "To view the honeypot:"
    echo "  - Attach to screen: screen -r $SESSION_NAME"
    echo "  - Detach from screen: Ctrl+A, then D"
    echo "  - Kill the session: Ctrl+A, then K"
}

# Main execution
detect_os
echo "Detected OS: $OS"
echo "Using package manager: $PKG_MANAGER"
check_screen
check_key
start_honeypot
