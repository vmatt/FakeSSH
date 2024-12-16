#!/bin/bash

check_ssh_keygen() {
    if ! command -v ssh-keygen &> /dev/null
    then
        echo "Error: ssh-keygen is not installed. Please install OpenSSH and try again."
        exit 1
    fi
}

generate_key() {
    key_file="RSA_PRIVATE.key"
    passphrase="FakeSSH"

    ssh-keygen -t rsa -b 2048 -f "$key_file" -N "$passphrase"

    echo "RSA key pair generated successfully: ${key_file} and ${key_file}.pub"
    echo "------------------------------------------------"
    echo "Run python3 fakessh.py to start fake SSH Server"
    echo "------------------------------------------------"
}
check_ssh_keygen
generate_key

