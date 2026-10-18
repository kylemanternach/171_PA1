import asyncio
import json
import struct
import random

delay = (0.5, 3)

class MessageHandler:
    def __init__(self, node):
        self.node = node

    async def send_message(self, sock, data):
        """Send messages over stored connection sockets (logging and clock tick req)."""
        # "Shutdown" is a bare string, so the verse logger cannot index it.
        if data != "Shutdown":
            self.node.log_message(data, "SEND")
        payload = json.dumps(data).encode("utf-8")

        header = struct.pack("!I", len(payload))
        await asyncio.sleep(random.uniform(delay[0], delay[1]))
        await asyncio.to_thread(sock.sendall, header + payload)

    async def receive(self, conn):
        """Waiting for message to arrive and handling message processing."""
        while True:
            header = await asyncio.to_thread(self.recv_exact, conn, 4)

            if not header:
                break

            length = struct.unpack("!I", header)[0]
            data = self.recv_message(conn, length)
            asyncio.create_task(self.node.process(data))

        conn.close()

    def recv_exact(self, conn, n):
        """Read exactly n bytes from the socket."""
        chunks = []
        remaining = n

        while remaining > 0:
            chunk = conn.recv(remaining)

            if not chunk:
                raise ConnectionError("Connection closed")

            chunks.append(chunk)
            remaining -= len(chunk)

        return b"".join(chunks)

    def recv_message(self, conn, length):
        """Loading JSON message into a dictionary."""
        payload = self.recv_exact(conn, length)

        text = payload.decode("utf-8")
        data = json.loads(text)

        # json.dumps("Shutdown") is the quoted text "\"Shutdown\"", so compare
        # the parsed value rather than the raw payload.
        if data == "Shutdown":
            return data

        self.node.log_message(data, "RECV")

        return data