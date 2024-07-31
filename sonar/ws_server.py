import asyncio
import json

import websockets
from _collections import deque

connected = set()


class ChunkControl:
    def __init__(self):
        self._chunk_size = None

    @property
    def chunk_size(self):
        return self._chunk_size

    @chunk_size.setter
    def chunk_size(self, value):
        self._chunk_size = value


cc = ChunkControl()
cc.chunk_size = 50


async def handler(websocket, path):
    print("Server running")
    connected.add(websocket)
    chunks = deque([])

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                if isinstance(data, dict):
                    ordered_chunk_size = data.get("content")
                    print("Received ordered chunk size:", ordered_chunk_size)
                    cc.chunk_size = ordered_chunk_size
                if isinstance(data, list):
                    chunks.append(data)
                    print("Received chunk size:", len(data))
            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)

            try:
                chunk = chunks.popleft()
            except IndexError:
                continue

            print("About to send a chunk of ", cc.chunk_size)
            for i in range(0, len(chunk), cc.chunk_size):
                chunks_to_send = chunk[i : i + cc.chunk_size]
                print("Sending chunks", len(chunks_to_send))
                message = json.dumps(chunks_to_send)
                websockets.broadcast(connected, message)
    finally:
        connected.remove(websocket)


start_server = websockets.serve(handler, "localhost", 12000, ping_interval=None)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
