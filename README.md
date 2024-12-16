# FakeSSH Honeypot

FakeSSH is an SSH honeypot that simulates a legitimate SSH server to monitor and log unauthorized access attempts. It's designed to help security researchers and system administrators understand attack patterns and collect data about potential threats.

## Features

- Simulates a basic Linux environment
- Accepts any username/password combination to lure attackers
- Logs all login attempts and commands for threat analysis and research
- Supports common Linux commands (ls, cd, pwd, uname, df, free, etc.)
- Runs in a virtual environment for isolation
- Includes warning messages for unauthorized access attempts
- Anti-attacker measures including bandwidth-consuming exit messages

## Requirements

- Python 3.x
- OpenSSH (for key generation)
- tmux (for session management)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/vmatt/fakessh.git
cd fakessh
```

2. Run the installation script:
```bash
./install.sh
```

This will:
- Create a Python virtual environment
- Install required dependencies
- Generate SSH keys
- Set up the environment

## Running the Honeypot

Start the honeypot using:
```bash
./start.sh
```

The server will run on port 2222 by default.

### Exit Behavior

By default, when an attacker attempts to exit the honeypot, it sends approximately 1MB of warning messages. This serves two purposes:
1. Discourages further attack attempts
2. Increases the cost (in terms of bandwidth and time) for automated attack tools

To disable this behavior and use simple exit handling instead, run:
```bash
python3 fakessh.py --simple-exit
```

Note: While the bandwidth-consuming exit messages can be effective against attackers, be mindful of your own bandwidth costs if deploying this honeypot at scale.

### Command Logging and Threat Analysis

All commands executed by attackers are logged in `ssh.log`. This logging is crucial for:
- Identifying new attack patterns and techniques
- Understanding attacker behavior and motivations
- Reverse engineering malicious tools and scripts
- Early detection of emerging threats
- Building better defense strategies

Regular analysis of these logs can provide valuable insights into current attack trends and help improve security measures.

## Port Forwarding Setup

To redirect traffic from the default SSH port (22) to the honeypot port (2222), you can use one of these methods:

### Using iptables:
```bash
sudo iptables -A PREROUTING -t nat -p tcp --dport 22 -j REDIRECT --to-port 2222
```

### Using firewall-cmd (FirewallD):
```bash
sudo firewall-cmd --permanent --add-forward-port=port=22:proto=tcp:toport=2222
sudo firewall-cmd --reload
```

To verify the forwarding rule:
```bash
sudo firewall-cmd --list-forward-ports
```

## Logging

All SSH connection attempts and commands are logged in `ssh.log`.

## Security Notice

This is a honeypot intended for research purposes. Important security considerations:

- The honeypot accepts ANY username/password combination to maximize data collection
- Do not run it on production systems
- Do not expose it to the internet without proper security measures in place
- Consider running it in an isolated network or container

## License

This project is licensed under the terms specified in the LICENSE file.
