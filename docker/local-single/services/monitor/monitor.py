import json
import os
import time

import numpy as np
from celeryapps import record_audio

import redis

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_MONITOR_Q_NAME = os.getenv("REDIS_MONITOR_Q_NAME")

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)


def start():
    print("Monitoring loud noises")
    streak = 0

    while True:
        if r.llen(REDIS_MONITOR_Q_NAME) > 0:
            audio_data = json.loads(r.rpop(REDIS_MONITOR_Q_NAME))
            mean = np.mean(audio_data)

            if streak >= 5:
                print("Consistent loud noise detected. Recording...")
                record_audio.delay()
                streak = 0

            if mean > 30:
                print("Loud noise detected")
                streak += 1
            else:
                if streak > 0:
                    streak = 0
        else:
            time.sleep(1)


if __name__ == "__main__":
    start()
