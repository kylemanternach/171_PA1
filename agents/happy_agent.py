# happy_node
from node_components.agent_node import AgentNode
import asyncio

LOCALHOST = "127.0.0.1"
PORT = 5001

AGENTS = {
    "Poet": 5050,
    "Sad": 5002,
    "Love": 5003
}

async def main():
    # Name is the Gemini mood. The last argument is this agent's vector-clock index.
    node = AgentNode("Happy", LOCALHOST, PORT, 0)

    await node.start_node(AGENTS)

    # Start listening for incoming agent connections.
    asyncio.create_task(node.accept_connection())
    await asyncio.Future()


if __name__ == "__main__":
    open("Happy.log", "w").close()
    asyncio.run(main())