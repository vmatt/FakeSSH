import socket
import paramiko
import threading
import sys
import time
import logging
import file_read
import fake_uname
import diskfile
import sudo_cmd

# Configure logging
# File handler for ssh.log
file_handler = logging.FileHandler('ssh.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', '%Y-%m-%d %H:%M:%S'))

# Console handler for stdout
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(message)s', '%Y-%m-%d %H:%M:%S'))

# Configure root logger
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().addHandler(file_handler)
logging.getLogger().addHandler(console_handler)

# Suppress Paramiko logging
logging.getLogger('paramiko').setLevel(logging.WARNING)

pwd = ["/var/www/html"]

def home_logo():
    logging.debug("""
        ####   ##     ##      ###        #####      #######     ####### 
         ##    ##     ##     ## ##      ##   ##    ##     ##   ##     ##
         ##    ##     ##    ##   ##    ##     ##   ##     ##   ##     ##
         ##    #########   ##     ##   ##     ##    #######     ########
         ##    ##     ##   #########   ##     ##   ##     ##          ##
         ##    ##     ##   ##     ##    ##   ##    ##     ##   ##     ##
        ####   ##     ##   ##     ##     #####      #######     #######
    
IHA089: Navigating the Digital Realm with Code and Security - Where Programming Insights Meet Cyber Vigilance.
    """)

host_key = paramiko.RSAKey(filename='RSA_PRIVATE.key', password='FakeSSH')

class SSHHoneypot(paramiko.ServerInterface):
    def __init__(self, client_ip):
        self.event = threading.Event()
        self.client_ip = client_ip

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        logging.info(f"{self.client_ip} - Username: {username}, Password: {password}")
        logging.info(f"{self.client_ip} - Auth granted (password)")
        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        logging.info(f"{self.client_ip} - Auth rejected (none)")
        return "password"

    def get_allowed_auths(self, username):
        return "password"

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_shell_request(self, channel):
        self.event.set()  
        return True

def get_pwd():
    return pwd[0]

def change_directory(cmd):
    spl = cmd.split(" ")
    if spl[1] == "..":
        if pwd[0] == "/var/www/html":
            return f"\r\n$ "
        else:
            spl_pwd = pwd[0].split("/")
            pwd_len = len(spl_pwd)
            c_pwd=""
            for i in range(1, pwd_len-1):
                c_pwd = c_pwd+"/"+spl_pwd[i]
                pwd[0] = c_pwd
            return f"\r\n$ "
    elif spl[1] == "":
        pwd[0] = "/var/www/html"
        return f"\r\n$ "
    else:
        dir_name = spl[1]
        alf = file_read.change_directory(dir_name)
        print(alf)
        if isinstance(alf, dict):
            pwd[0]=pwd[0]+"/"+dir_name
            return f"\r\n$ "
        return f"\r\n{alf}\r\n$ "


def command_handler(cmd):
    if cmd == "pwd":
        return f"\r\n{get_pwd()} \r\n$ "
    elif cmd == "ls":
        pswd = get_pwd()
        files = file_read.Dir_Handler(pswd)
        return f"\r\n{files} \r\n$ "
    elif "cd " in cmd:
        return change_directory(cmd)
    elif cmd == "uname" or cmd == "uname -a" or cmd == "uname -s" or cmd == "uname -n" or cmd == "uname -r" or cmd == "uname -v" or cmd == "uname -m" or cmd == "uname -p" or cmd == "uname -i" or cmd == "uname -o":
        output = fake_uname.uname_handle(cmd)
        return f"\r\n{output} \r\n$ "
    elif cmd == "df -h":
        output = diskfile.disk_handler()
        return f"\r\n{output} \r\n$ "
    elif cmd == "free" or cmd == "free -b" or cmd == "free -k" or cmd == "free -m" or cmd == "free -g" or cmd == "free -h" or cmd == "free -l" or cmd == "free -L" or cmd == "free -t" or cmd == "free -c":
        output = diskfile.memory_haneler()
        return f"\r\n{output} \r\n$ "
    elif "sudo apt" in cmd or "apt install" in cmd or "apt remove" in cmd or "apt update" in cmd or "apt upgrade" in cmd:
        output = sudo_cmd.cmd_response()
        return f"\r\n{output} \r\n$ "
    else:
        return f"\r\nCommand '{cmd}' not found\r\n$ "
        

def handle_client(client_socket, addr):
    client_ip = addr[0]
    last_activity = time.time()
    transport = None
    try:
        transport = paramiko.Transport(client_socket)
        transport.add_server_key(host_key)
        server = SSHHoneypot(client_ip)

        # Set a timeout for the SSH banner exchange
        transport.banner_timeout = 10
        transport.handshake_timeout = 10
        
        # Log the connection with IP
        logging.info(f"{client_ip} - Connected (version {transport.remote_version})")
        transport.start_server(server=server)
        chan = transport.accept(20) 

        if chan is None:
            logging.debug("[-] No channel request")
            return

        logging.debug("[+] Channel opened")
        server.event.wait(10) 

        if not server.event.is_set():
            logging.debug("[-] No shell request")
            return

        chan.send("$ ")

        command_buffer = ""

        while True:
            try:
                # Check for timeout
                if time.time() - last_activity > 60:  # 60 seconds timeout
                    logging.info(f"{server.client_ip} - Connection timed out after 60 seconds of inactivity")
                    chan.send("\r\nConnection timed out due to inactivity\r\n")
                    break

                # Set socket timeout to allow checking for inactivity
                chan.settimeout(1.0)
                try:
                    data = chan.recv(1024).decode('utf-8')
                    last_activity = time.time()  # Update activity timestamp
                except socket.timeout:
                    continue

                if not data:
                    break

                if data == '\r' or data == '\n':
                    command = command_buffer.strip()  
                    if command:
                        logging.info(f"{server.client_ip}: {command}")
                        if command == "exit":
                            logging.info(f"{server.client_ip} - Client attempted to exit - starting warning message stream")
                            import random
                            import string

                            warning_msg = (
                                "⚠️ WARNING UNAUTHORIZED ACCESS DETECTED ⚠️\n"
                                "🚫 STOP ATTEMPTING TO HACK RANDOM SERVERS 🚫\n"
                                "🔒 YOUR ACTIONS ARE BEING MONITORED AND LOGGED 🔒\n"
                                "🚔 CYBERCRIME IS A SERIOUS OFFENSE 🚔\n"
                                "💻 USE YOUR SKILLS ETHICALLY - LEARN CYBERSECURITY LEGALLY 💻\n"
                            )
                            def create_warning_line(line):
                                words = line.split()
                                if not words:
                                    return line
                                special_chars = 'ŘßąŔŁļŠ¥§ŦŽĶ@#$'
                                result = words[0]
                                for word in words[1:]:
                                    rand_chars = ''.join(random.choice(special_chars) for _ in range(3))
                                    result += f" {rand_chars} {word}"
                                return result + "\n"

                            warning_msg = ''.join(create_warning_line(line) for line in warning_msg.splitlines() if line.strip())
                            total_sent = 0
                            max_size = 1024 * 1024  # 1MB in bytes

                            while total_sent < max_size:
                                try:
                                    bytes_sent = chan.send(warning_msg)
                                    total_sent += bytes_sent
                                except Exception as e:
                                    logging.error(f"Error sending data: {e}")
                                    break
                            
                            logging.info(f"{server.client_ip} - closing connection")
                            chan.close()
                            transport.close()
                            break
                        else:
                            data = command_handler(command)
                            chan.send(data)
                    command_buffer = ""  
                else:
                    command_buffer += data
                    chan.send(data)

            except Exception as e:
                logging.debug(f"Error: {e}")
                break
    except paramiko.SSHException as e:
        logging.warning(f"{client_ip} - SSH Protocol error: {str(e)}")
    except EOFError:
        logging.warning(f"{client_ip} - Client disconnected during handshake")
    except socket.error as e:
        logging.warning(f"{client_ip} - Socket error: {str(e)}")
    except paramiko.AuthenticationException as e:
        logging.warning(f"{client_ip} - Authentication failed: {str(e)}")
    except paramiko.BadAuthenticationType as e:
        logging.warning(f"{client_ip} - Bad authentication type: {str(e)}")
    except paramiko.ChannelException as e:
        logging.warning(f"{client_ip} - Channel error: {str(e)}")
    except UnicodeDecodeError as e:
        logging.warning(f"{client_ip} - Invalid UTF-8 data received: {str(e)}")
    except ConnectionResetError:
        logging.warning(f"{client_ip} - Connection reset by peer")
    except TimeoutError:
        logging.warning(f"{client_ip} - Connection timed out")
    except Exception as e:
        logging.error(f"{client_ip} - Unexpected error: {str(e)}", exc_info=True)
    finally:
        try:
            if transport:
                transport.close()
            if client_socket:
                client_socket.close()
        except Exception as e:
            logging.error(f"{client_ip} - Error during cleanup: {str(e)}")

def start_honeypot():
    host="0.0.0.0"
    port=2222
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)

    logging.debug(f"[+] SSH Honeypot running on {host}:{port}")

    Ratan = True
    while Ratan:
        try:
            client_socket, addr = server_socket.accept()
            logging.debug(f"[+] Connection from {addr}")
            client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            client_thread.start()
        except KeyboardInterrupt:
            Ratan = False
            logging.debug("Exiting....")
            sys.exit()
    sys.exit()

if __name__ == "__main__":
    home_logo()
    start_honeypot()

