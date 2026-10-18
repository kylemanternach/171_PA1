import json
import asyncio

from node_components.node import Node
from helpers.vector_clock import vector_clock, concurrent, happens_next

clock_pos = {"Happy": 0, "Sad": 1, "Love": 2}

class PoetNode(Node):
    def __init__(self, name, host, port):
        super().__init__(name, host, port)
        self.wait_queue = []
        self.clock = [0, 0, 0]
        self.shutdown_counter = 0

    def kickoff(self, line_nums):
        # Agents parse clk with json.loads, so send the list as a string like "[0, 0, 0]".
        messages = [
            self.build_message("Happy", "Poet", "FIRST", "REQUEST", str(self.clock), remaining=line_nums[0]),
            self.build_message("Sad", "Poet", "SECOND", "REQUEST", str(self.clock), remaining=line_nums[1]),
            self.build_message("Love", "Poet", "THIRD", "REQUEST", str(self.clock), remaining=line_nums[2])
        ]

        asyncio.create_task(self.message_handler.send_message(self.connections["Happy"], messages[0]))
        asyncio.create_task(self.message_handler.send_message(self.connections["Sad"], messages[1]))
        asyncio.create_task(self.message_handler.send_message(self.connections["Love"], messages[2]))

    async def output_line(self, data, held):
        """Output message to poem.txt and log output in poet.log."""
        with open("poet.txt", "a") as file:
            file.write(
                f"{data["stream_num"] + " " + data["content"]: <40}{data["clk"]: >20}\n"
            )

        with open(f"{self.name}.log", "a") as file:
            file.write(
                f"#{self.message_count}   OUTPUT  {data["from"]}  "
                f"{data['clk'] + "   " + data["stream_num"] + " " + data['content']}"
                f"    poet_clock={self.clock}      held={held}\n"
            )

        if data["remaining"] == 0:
            self.shutdown_counter += 1
            if self.shutdown_counter == 3:
                asyncio.create_task(self.message_handler.send_message(self.connections["Happy"], "Shutdown"))
                asyncio.create_task(self.message_handler.send_message(self.connections["Sad"], "Shutdown"))
                asyncio.create_task(self.message_handler.send_message(self.connections["Love"], "Shutdown"))
                
                await asyncio.sleep(5)
                print("Shutting down Poet")
                self.shutdown()
        
    async def release_next(self):
        """Output next messages in sequence if any exist and are waiting."""
        old_clk = [0, 0, 0]
        while old_clk != self.clock:
            old_clk = self.clock
            for message in self.wait_queue:
                other_clk = json.loads(message['clk'])
                if (
                    happens_next(self.clock, other_clk)
                ):
                    # output_line is async because the last line waits, then shuts down.
                    self.clock = [max(a, b) for a, b in zip(self.clock, other_clk)]
                    await self.output_line(message, True)
                    

    async def process(self, data):
        """
        1. Compare clock with most recently outputted line.
           If no line, check distances.
        2. If line is good to output, output to poem.txt, log output,
           and check the waiting queue with the most recently output
           line clock position in mind. Repeat until no more lines
           are ready to output.
        Otherwise, add to the waiting queue.

        a. Output conditions: What agent did the line come from?
           If new line clock - current clock > 1 (for our agent),
           cannot output; add to waiting queue.
           Else if new line clock - current clock > 0 (for other agents).

        b. Local clock updates at main, elementwise max of current time
           and recently output time.
        """
        other_clk = json.loads(data["clk"])
        curr_clk_pos = clock_pos[data["from"]]
        if (
            happens_next(self.clock, other_clk)
        ):
            # Both are async; awaiting them is what lets the shutdown counter run.
            await self.output_line(data, False)
            self.clock = [max(a, b) for a, b in zip(self.clock, other_clk)]
            await self.release_next()
        else:
            self.wait_queue.append(data)