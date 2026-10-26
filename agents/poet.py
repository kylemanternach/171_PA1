# poet_node
from node_components.poet_node import PoetNode
import asyncio

LOCALHOST = "127.0.0.1"
PORT = 5050

AGENTS = {
    "Happy": 5001,
    "Sad": 5002,
    "Love": 5003
}

async def main():
    node = PoetNode("Poet", LOCALHOST, PORT)

    await node.start_node(AGENTS)
    # Peers are connected now. Each number is how many lines that stream still has to write.
    node.kickoff([2, 2, 2])

    # Start listening for incoming agent connections.
    asyncio.create_task(node.accept_connection())
    await asyncio.Future()


if __name__ == "__main__":
    open("Poet.log", "w").close()
    open("poet.txt", "w").close()
    asyncio.run(main())