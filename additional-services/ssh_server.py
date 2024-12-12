import socket
import paramiko
import threading

key_file = "/home/wattson/Documents/code/additional-services/server_key.pem"
host_key = paramiko.RSAKey(filename=key_file)

AUTHORIZED_USER = "testughxfghdfgzdgfdser"
AUTHORIZED_PASSWORD = "fgxhfghgxfhfgxhfgxhfghgh"


class SSHServer(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if (username == AUTHORIZED_USER) and (password == AUTHORIZED_PASSWORD):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED


def handle_connection(client):
    transport = paramiko.Transport(client)
    transport.add_server_key(host_key)
    server = SSHServer()
    try:
        transport.start_server(server=server)
        chan = transport.accept(20)
        if chan is None:
            raise Exception("No channel")
        chan.close()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        transport.close()


def start_server(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(100)
    print(f"Listening on {host}:{port}")

    while True:
        client, addr = sock.accept()
        print(f"Accepted connection from {addr}")
        threading.Thread(target=handle_connection, args=(client,)).start()


if __name__ == "__main__":
    start_server("0.0.0.0", 22)
