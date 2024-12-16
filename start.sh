#!/bin/bash

# Check if screen is installed
check_screen() {
    if ! command -v screen &> /dev/null; then
        echo "Error: screen is not installed"
        echo "Installing screen..."
        if command -v apt &> /dev/null; then
            sudo apt update && sudo apt install -y screen
        elif command -v yum &> /dev/null; then
            sudo yum install -y screen
        else
            echo "Could not install screen. Please install it manually."
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
check_screen
check_key
start_honeypot
