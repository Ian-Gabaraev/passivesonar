import asyncio
import websockets
import os

import json
from dotenv import load_dotenv
from redis_q import aggregate

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_Q_NAME = os.getenv("REDIS_Q_NAME")


async def send_audio_data(ws):
    while True:
        result = aggregate(1)
        if result is not None:
            print("Sending aggregated data")
            await ws.send(json.dumps(result))
        await asyncio.sleep(0.01)


async def connect():
    uri = "ws://0.0.0.0:12000"
    async with websockets.connect(uri, ping_interval=None) as ws:
        await ws.send("Connection opened")
        await send_audio_data(ws)


async def main():
    await connect()


if __name__ == "__main__":
    asyncio.run(main())
