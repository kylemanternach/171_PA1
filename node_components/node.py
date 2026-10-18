import asyncio
import os
import socket

from helpers.vector_clock import vector_clock
from helpers.message_handler import MessageHandler

class Node:
    def __init__(self, name, host, port):
        self.message_count = 0
        self.name = name
        self.host = host
        self.port = port
        self.connections = {}
        self.message_handler = MessageHandler(self)
        self.server = socket.socket()

    async def start_node(self, ports):
        """Initialize for message reception."""
        # A restart can bind while the previous listener's port is still in TIME_WAIT.
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen()

        asyncio.create_task(self.accept_connection())

        for name, port in ports.items():
            # Peers can start in any order. Dial until that port is listening.
            announced = False
            while True:
                sock = socket.socket()
                try:
                    await asyncio.to_thread(sock.connect, (self.host, port))
                except ConnectionRefusedError:
                    sock.close()
                    if not announced:
                        print(f"{self.name} waiting for {name} on port {port}")
                        announced = True
                    await asyncio.sleep(0.5)
                    continue
                self.connections[name] = sock
                break

    def shutdown(self):
        for sock in self.connections.values():
            sock.close()

        if self.server:
            self.server.close()

        # main is still waiting, and accept/recv are blocked in threads.
        # Exit the process here instead of trying to unwind those waits.
        os._exit(0)

    def send_both_messages(self, sock1, sock2, data):
        """Delegate message sending to the message handler."""
        asyncio.create_task(self.message_handler.send_message(sock1, data))
        data["to"] = "Poet"
        asyncio.create_task(self.message_handler.send_message(sock2, data))

    def receive(self, conn):
        """Delegate message reception to the message handler."""
        return self.message_handler.receive(conn)

    def log_message(self, data, m_type):
        """Log message to poet.log."""
        self.message_count += 1
        with open(f"{self.name}.log", "a") as file:
            file.write(
                f"#{self.message_count}   {m_type} -> {data["from"]}  "
                f"{data['clk']}  remaining={data['remaining']}  "
                f"{data["stream_num"] + " " + data['content']}  poet_clock={self.clock}\n"
            )

    def build_message(self, to_node, from_node, stream, content, clock, remaining):
        """Build JSON structured message for sending."""
        return {
            "to": to_node,
            "from": from_node,
            "stream_num": stream,
            "content": content,
            "clk": clock,
            "remaining": remaining
        }

    async def accept_connection(self):
        """Accept connections to server for receiving messages."""
        while True:
            conn, addr = await asyncio.to_thread(self.server.accept)
            asyncio.create_task(self.receive(conn))