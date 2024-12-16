import socket
import paramiko
import threading
import sys
import logging
import file_read
import fake_uname
import diskfile
import sudo_cmd

# Configure logging
logging.basicConfig(
    filename='ssh.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

pwd = ["/var/www/html"]

def home_logo():
    print("""
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
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        logging.info(f"Login attempt - Username: {username}, Password: {password}")
        print(f"[+] {username} successfully logged in with {password}")
        return paramiko.AUTH_SUCCESSFUL

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
        

def handle_client(client_socket):
    transport = paramiko.Transport(client_socket)
    transport.add_server_key(host_key)
    server = SSHHoneypot()

    try:
        transport.start_server(server=server)
        chan = transport.accept(20) 

        if chan is None:
            print("[-] No channel request")
            return

        print("[+] Channel opened")
        server.event.wait(10) 

        if not server.event.is_set():
            print("[-] No shell request")
            return

        chan.send("$ ")

        command_buffer = ""

        while True:
            try:
                data = chan.recv(1024).decode('utf-8')

                if not data:
                    break

                if data == '\r' or data == '\n':
                    command = command_buffer.strip()  
                    if command:
                        print(f"Command received: {command}")
                        logging.info(f"Command executed: {command}")
                        if command == "exit":
                            logging.info("Client attempted to exit - starting warning message stream")
                            warning_msg = """
⚠️ WARNING: UNAUTHORIZED ACCESS DETECTED ⚠️
🚫 Stop attempting to hack random servers! 🚫
🔒 Your actions are being monitored and logged 🔒
🚔 Cybercrime is a serious offense 🚔
💻 Use your skills ethically - Learn cybersecurity legally 💻
"""
                            total_sent = 0
                            max_size = 1024 * 1024  # 1MB in bytes
                            
                            while total_sent < max_size:
                                try:
                                    # Mix warning message with random characters
                                    garbage = ''.join(chr((i * 7 + 33) % 126) for i in range(100))
                                    chunk = warning_msg + garbage + "\n"
                                    bytes_sent = chan.send(chunk)
                                    total_sent += bytes_sent
                                    logging.info(f"Sent warning message chunk, total: {total_sent}/{max_size} bytes")
                                except Exception as e:
                                    logging.error(f"Error sending data: {e}")
                                    break
                            
                            logging.info(f"Reached {total_sent} bytes sent, closing connection")
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
                print(f"Error: {e}")
                break
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        transport.close()

def start_honeypot():
    host="0.0.0.0"
    port=22
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"[+] SSH Honeypot running on {host}:{port}")

    Ratan = True
    while Ratan:
        try:
            client_socket, addr = server_socket.accept()
            print(f"[+] Connection from {addr}")
            client_thread = threading.Thread(target=handle_client, args=(client_socket,))
            client_thread.start()
        except KeyboardInterrupt:
            Ratan = False
            print("Exiting....")
            sys.exit()
    sys.exit()

if __name__ == "__main__":
    home_logo()
    start_honeypot()

