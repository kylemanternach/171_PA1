import socket
import threading
import vector_clock

HOST = '127.0.0.1'

HOST = "127.0.0.1"
PORT = 5000
NUM_AGENTS = 3

agents = {}
agents_lock = threading.Lock()

def handle_incoming(conn):


def main(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, port))
    server.listen(1)

    
    while True:
        conn, addr = server.accept()