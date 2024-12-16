#!/bin/bash

# Check if Python3 is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo "Error: Python3 is not installed"
        exit 1
    fi
}

# Check if ssh-keygen is installed
check_ssh_keygen() {
    if ! command -v ssh-keygen &> /dev/null; then
        echo "Error: ssh-keygen is not installed. Please install OpenSSH and try again."
        exit 1
    fi
}

# Setup virtual environment
setup_venv() {
    if [ ! -d "honeypot" ]; then
        echo "Creating virtual environment..."
        python3 -m venv honeypot
        if [ $? -ne 0 ]; then
            echo "Failed to create virtual environment"
            exit 1
        fi
    fi

    echo "Activating virtual environment..."
    source honeypot/bin/activate

    echo "Installing requirements..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Failed to install requirements"
        exit 1
    fi
}

# Generate SSH key
generate_key() {
    key_file="RSA_PRIVATE.key"
    passphrase="FakeSSH"

    if [ ! -f "$key_file" ]; then
        ssh-keygen -t rsa -b 2048 -f "$key_file" -N "$passphrase"
        echo "RSA key pair generated successfully: ${key_file} and ${key_file}.pub"
    else
        echo "RSA key already exists"
    fi
}

# Main execution
check_python
check_ssh_keygen
setup_venv
generate_key

echo "------------------------------------------------"
echo "Installation complete!"
echo "Run ./start.sh to start the honeypot server"
echo "------------------------------------------------"

