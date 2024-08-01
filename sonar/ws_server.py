import asyncio
import json
from collections import deque

import websockets

connected = set()
batch_size = 2  # Number of audio samples to send in a batch, eq to #of microphones


async def handler(websocket, path):
    print("Server running")
    connected.add(websocket)
    batch = deque([])

    try:
        async for message in websocket:
            try:
                print("Received message:", message)
                data = json.loads(message)
                for key, value in data.items():
                    batch.append(value)
            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)

            if len(batch) >= batch_size:
                print(
                    """
                    ***************************
                    ** Batch ready. Sending. **
                    ***************************
                    """
                )
                message = json.dumps([batch.popleft() for _ in range(batch_size)])
                websockets.broadcast(connected, message)

    finally:
        connected.remove(websocket)


start_server = websockets.serve(handler, "localhost", 12000, ping_interval=None)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
