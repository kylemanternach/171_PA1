# sad_agent
from node_components.agent_node import AgentNode
import asyncio

LOCALHOST = "127.0.0.1"
PORT = 5002

AGENTS = {
    "Poet": 5050,
    "Happy": 5001,
    "Love": 5003
}

total_lines = [1, 1, 1]

async def main():
    # Name is the Gemini mood. The last argument is this agent's vector-clock index.
    node = AgentNode("Sad", LOCALHOST, PORT, 1)

    await node.start_node(AGENTS)

    # Start listening for incoming agent connections.
    asyncio.create_task(node.accept_connection())
    await asyncio.Future()


if __name__ == "__main__":
    open("Sad.log", "w").close()
    asyncio.run(main())