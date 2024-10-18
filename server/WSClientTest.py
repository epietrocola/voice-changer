import sys
import asyncio
import websockets

async def hello():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        while True:
            await websocket.send("7")
            await asyncio.sleep(0.5)  # Delay for 5 seconds
            await websocket.send("12")
            await asyncio.sleep(0.5)  # Delay for 5 seconds

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(hello())
