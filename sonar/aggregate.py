import os
import time

import redis
import json

from aws import send_rms_to_sqs
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_Q_NAME = os.getenv("REDIS_Q_NAME")


def aggregate_and_send():
    print("Listening for RMS values from Redis")
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

    while True:
        if r.llen(REDIS_Q_NAME) >= 2:
            print("Aggregating RMS values")
            mic1_message = json.loads(r.rpop(REDIS_Q_NAME))
            mic2_message = json.loads(r.rpop(REDIS_Q_NAME))

            aggregated_message = {
                f'{mic1_message["mic_id"]}': mic1_message,
                f'{mic2_message["mic_id"]}': mic2_message,
            }
            send_rms_to_sqs(aggregated_message)

        time.sleep(0.01)


if __name__ == "__main__":
    aggregate_and_send()
