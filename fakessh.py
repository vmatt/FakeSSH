import socket
import paramiko
import threading
import sys
import time
import logging

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

def home_logo():
    logging.debug("""
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


def handle_client(client_socket, addr):
    client_ip = addr[0]
    transport = None
    try:
        transport = paramiko.Transport(client_socket)
        transport.add_server_key(host_key)
        server = SSHHoneypot(client_ip)
        
        try:
            transport.start_server(server=server)
            logging.info(f"{client_ip} - Connected (version {transport.remote_version})")
            chan = transport.accept(20)
            if chan is None:
                logging.debug(f"{client_ip} - No channel request")
                return
            
            logging.debug("[+] Channel opened")
            server.event.wait(10)
        except paramiko.ssh_exception.SSHException as e:
            logging.warning(f"{client_ip} - SSH protocol error during server start: {str(e)}")
            return
        except EOFError:
            logging.warning(f"{client_ip} - Client disconnected during channel setup")
            return


        if not server.event.is_set():
            logging.debug("[-] No shell request")
            return

        chan.send("$ ")


        # Send warning message immediately
        warning_msg = (
            "\r\n"
            "⠀⠀⠀⠀⠀⣠⠶⠚⠛⠛⠛⠲⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\r\n"
            "⠀⠀⠀⣴⠟⠁⠀⠀⠀⠀⠀⠀⠀⠻⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\r\n"
            "⠀⣠⣾⣷⣄⠀⠀⠀⢀⣠⣤⣤⡀⠀⢿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\r\n"
            "⢸⣿⡿⢃⣸⡶⠂⢠⣿⣿⡿⠁⣱⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\r\n"
            "⢸⡏⠉⠩⣏⣐⣦⠀⠛⠦⠴⠚⠁⠀⣸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\r\n"
            "⣼⠧⠶⠶⠶⠿⠶⠶⠖⠚⠛⠉⠁⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠶⠶⡄⠀⠀\r\n"
            "⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⢠⡟⠀⠀⢹⠀⠀\r\n"
            "⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⢤⢠⡆⠀⢸⡄⠀⠀⠀⠀⠀⠀⢀⡿⠁⠀⠀⡾⠀⠀\r\n"
            "⢹⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠈⡇⠀⠸⣧⣠⠴⠶⠖⠲⢶⡞⠁⠀⢈⡼⢃⠀⠀\r\n"
            "⠸⡆⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⡇⠀⠀⢿⠁⠄⣲⡶⠶⠿⢤⣄⡀⠛⢛⠉⢻⠀\r\n"
            "⠀⢿⡀⠀⠀⠀⠀⠀⠀⠀⢸⠠⣇⠀⠀⠀⠀⠊⠁⠀⠀⠀⠀⠀⠙⢦⠈⠙⠓⣆\r\n"
            "⠀⠈⢷⡀⠀⠀⠀⠀⠀⢠⠏⡀⣬⣹⣦⠀⠀⠀⠀⠀⠁⠀⠀⠀⠀⠈⡿⠶⠶⠋\r\n"
            "⠀⠀⠈⢷⡀⠀⠀⠀⠀⠘⠛⠛⠋⠀⠀⠀⠀⠀⠀⠄⠀⠀⠀⠀⠀⣼⠃⠀⠀⠀\r\n"
            "⠀⠀⠀⠀⠙⢦⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄⠀⠀⣠⡞⠁⠀⠀⠀⠀\r\n"
            "⠀⠀⠀⠀⠀⠀⠈⠛⣷⢶⣦⣤⣄⣀⣠⣤⣤⠀⣶⠶⠶⠶⠛⠁⠀⠀⠀⠀⠀⠀\r\n"
            "⠀⠀⠀⠀⣀⡀⠀⣰⠇⣾⠀⠀⠈⣩⣥⣄⣿⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\r\n"
            "⠀⠀⠀⠀⢿⡉⠳⡟⣸⠃⠀⠀⠀⠘⢷⣌⠉⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\r\n"
            "⠀⠀⠀⠀⠀⠙⢦⣴⠏⠀⠀⠀⠀⠀⠀⠉⠳⠶⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\r\n"
            "\r\n"
            "WARNING: Unauthorized Access Detected - All Activities Are Being Monitored and Logged\r\n"
        )

        chan.send(warning_msg)
        logging.info(f"{server.client_ip} - Sent warning message and closing connection")
        chan.close()
        transport.close()

    except paramiko.BadAuthenticationType as e:
        logging.warning(f"{client_ip} - Bad authentication type: {str(e)}")
    except paramiko.AuthenticationException as e:
        logging.warning(f"{client_ip} - Authentication failed: {str(e)}")
    except paramiko.ChannelException as e:
        logging.warning(f"{client_ip} - Channel error: {str(e)}")
    except paramiko.SSHException as e:
        logging.warning(f"{client_ip} - SSH Protocol error: {str(e)}")
    except EOFError:
        logging.warning(f"{client_ip} - Client disconnected during handshake")
    except TimeoutError:
        logging.warning(f"{client_ip} - Connection timed out")
    except socket.error as e:
        logging.warning(f"{client_ip} - Socket error: {str(e)}")
    except UnicodeDecodeError as e:
        logging.warning(f"{client_ip} - Invalid UTF-8 data received: {str(e)}")
    except ConnectionResetError:
        logging.warning(f"{client_ip} - Connection reset by peer")
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
            logging.debug("Exiting....")
            Ratan = False
            sys.exit()
            break
        except Exception as e:
            logging.error(f"Error accepting connection: {e}")

    sys.exit()

if __name__ == "__main__":
    home_logo()
    start_honeypot()

