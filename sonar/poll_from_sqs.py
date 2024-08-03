import asyncio

import boto3
import os
import json

import websockets
from dotenv import load_dotenv

from aws import get_sqs_url

load_dotenv()


aws_sqs_queue_url = get_sqs_url()
aws_region = os.getenv("AWS_REGION")

session = boto3.Session(region_name=aws_region)
sqs = session.resource("sqs")
queue = sqs.Queue(aws_sqs_queue_url)


def poll_queue(number_of_messages=10):
    print(f"Polling from {aws_sqs_queue_url}")
    messages = queue.receive_messages(
        MaxNumberOfMessages=number_of_messages,
        WaitTimeSeconds=5,
    )
    print(f"Received {len(messages)} messages")

    for message in messages:
        message.delete()

    return [json.loads(message.body) for message in messages]


async def send_audio_data(ws):
    while True:
        result = poll_queue()
        if result is not None:
            for message in result:
                await ws.send(json.dumps(message))
        await asyncio.sleep(0.01)


async def connect():
    uri = "ws://localhost:12000"
    async with websockets.connect(uri, ping_interval=None) as ws:
        await ws.send("Connection opened")
        await send_audio_data(ws)


async def main():
    await connect()


if __name__ == "__main__":
    asyncio.run(main())
