import sys
import asyncio
import websockets

async def hello(number):
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        await websocket.send(number)
        response = await websocket.recv()
        print(f"Received from server: {response}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python WSClientTest.py <number>")
        sys.exit(1)

    # Get the number from command-line arguments
    number = sys.argv[1]

    # Run the WebSocket client
    asyncio.run(hello(number))
