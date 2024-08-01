import os

import redis
import json
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_Q_NAME = os.getenv("REDIS_Q_NAME")


def push_rms_to_redis(rms_values, mic_id):
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    message = {"mic_id": mic_id, "rms_values": rms_values}
    r.lpush(REDIS_Q_NAME, json.dumps(message))
    print(f"Pushed RMS values to Redis queue: {message}")


def aggregate(aggregate_size, r=None):
    if r is None:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    if r.llen(REDIS_Q_NAME) >= aggregate_size:
        data = dict()
        for i in range(aggregate_size):
            mic_message = json.loads(r.rpop(REDIS_Q_NAME))
            data[f'{mic_message["mic_id"]}'] = mic_message
        return data
    return None
