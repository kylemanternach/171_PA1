# main_node.py
import socket
import threading
import vector_clock

HOST = "127.0.0.1"
PORT = 5000
NUM_AGENTS = 3

agents = {}                      # agent_id -> connected socket
agents_lock = threading.Lock()   # protects the dict (threads add/read it)


def handle_agent(conn):
    """One thread per agent. Runs for the life of that connection."""
    # 1. recv the first message to learn the agent's ID
    # 2. with agents_lock: agents[agent_id] = conn
    # 3. loop:
    #      data = conn.recv(1024)
    #      if data == b"": break          # agent disconnected
    #      process(agent_id, data)
    # 4. on exit: remove from agents, close conn
    pass


def process(sender_id, data):
    """What M does with a received poem fragment."""
    # decode, print/store it, then relay to the other agents
    # by calling send_to_others(sender_id, data)
    pass


def send_to_others(sender_id, data):
    """Relay a message to every agent except the sender."""
    # with agents_lock: loop over agents, sendall to each id != sender_id
    pass


def main():
    # 1. create the listening socket (SO_REUSEADDR, bind, listen)
    # 2. loop NUM_AGENTS times:
    #      conn, addr = server.accept()
    #      start threading.Thread(target=handle_agent, args=(conn,), daemon=True)
    # 3. keep the main thread alive (join the threads or wait on input)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    for _ in range(NUM_AGENTS):
        client.connect(HOST, )


if __name__ == "__main__":
    main()