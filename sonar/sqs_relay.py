import os
import time

import redis

from aws import send_rms_to_sqs
from dotenv import load_dotenv

from redis_q import aggregate

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_Q_NAME = os.getenv("REDIS_Q_NAME")


def relay(aggregate_size=2):
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    print("Listening for mic data from Redis")

    while True:
        if (aggregated_message := aggregate(aggregate_size, r)) is not None:
            send_rms_to_sqs(aggregated_message)
            print("Sent aggregated data to SQS")
        time.sleep(0.01)


if __name__ == "__main__":
    relay()
