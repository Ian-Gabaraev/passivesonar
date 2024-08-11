import os

import numpy as np
import redis
import json
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_Q_NAME = os.getenv("REDIS_Q_NAME")
REDIS_MONITOR_Q_NAME = os.getenv("REDIS_MONITOR_Q_NAME")
SYSTEM_Q_NAME = os.getenv("SYSTEM_Q_NAME")

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)


def redis_online():
    try:
        return r.ping() is True
    except redis.exceptions.ConnectionError:
        return False


def push_system_metrics_to_redis(system_metrics):
    try:
        r.rpush(SYSTEM_Q_NAME, json.dumps(system_metrics))
    except redis.ConnectionError:
        print("Redis not connected")
        return
    else:
        return True


def push_rms_to_redis(rms_values, mic_id, q_name=REDIS_Q_NAME):
    try:
        message = {"mic_id": mic_id, "rms_values": rms_values}
        r.lpush(q_name, json.dumps(message))
    except redis.ConnectionError:
        print("Redis not connected")
        return


def push_audio_to_redis(audio_data, q_name=REDIS_MONITOR_Q_NAME):
    try:
        if isinstance(audio_data, np.ndarray):
            r.rpush(q_name, audio_data.tobytes())
        else:
            r.rpush(q_name, json.dumps(audio_data))
    except redis.ConnectionError:
        print("Redis not connected")
        return


def aggregate(aggregate_size):
    if r.llen(REDIS_Q_NAME) >= aggregate_size:
        data = dict()
        for i in range(aggregate_size):
            mic_message = json.loads(r.rpop(REDIS_Q_NAME))
            data[f'{mic_message["mic_id"]}'] = mic_message
        return data
    return None
