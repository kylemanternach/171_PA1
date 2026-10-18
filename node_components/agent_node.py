import json
import random
from helpers.vector_clock import vector_clock
import asyncio

from node_components.node import Node
from helpers.gemini_prompt import generate_verse


class AgentNode(Node):
    def __init__(self, name, host, port, clk_num):
        super().__init__(name, host, port)
        self.clock = vector_clock(3, clk_num)

    async def process(self, data):
        # Seed and follow-up messages store the verse in "content".
        # Poet sends this after every stream has been output. Stop here so
        # the string is not read as a verse.
        if data == "Shutdown":
            print(f"Shutting down {self.name}")
            self.shutdown()
            return

        line_arr = data["content"].split(" ")
        next_length = 1 if data["content"] == "REQUEST" else len(line_arr) + 1
        remaining = data["remaining"] - 1
        other_clk = json.loads(data["clk"])
        stream = data["stream_num"]

        self.clock.receive(other_clk)
        stamp = str(self.clock.V)   # take the stamp before any await
        next_line = await asyncio.to_thread(generate_verse, next_length, self.name)

        if remaining != 0:
            random_agent = random.choice(list(self.connections.keys())[1:])
            message = self.build_message(
                random_agent, self.name, stream, next_line, stamp, remaining
            )
            self.send_both_messages(self.connections[random_agent], self.connections["Poet"], message)
        else:
            message = self.build_message(
                'Poet', self.name, stream, next_line, stamp, remaining
            )
            asyncio.create_task(self.message_handler.send_message(self.connections["Poet"], message))
            print(f"Stream {stream} has finished writing")