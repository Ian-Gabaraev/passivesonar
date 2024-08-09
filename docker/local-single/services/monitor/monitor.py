import json
import os
import time

import numpy as np
from celeryapps import record_audio
from aws import get_loudness_threshold, get_audio_q_size_threshold, get_streak_threshold

import redis

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_MONITOR_Q_NAME = os.getenv("REDIS_MONITOR_Q_NAME")
REDIS_AUDIO_Q_NAME = os.getenv("REDIS_AUDIO_Q_NAME")

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

LOUDNESS_THRESHOLD = int(get_loudness_threshold())
RESET_AUDIO_Q_THRESHOLD = int(get_audio_q_size_threshold())
STREAK_THRESHOLD = int(get_streak_threshold())


def start():
    print("Monitor loaded setting from AWS")
    print(f"LOUDNESS_THRESHOLD: {LOUDNESS_THRESHOLD}")
    print(f"RESET_AUDIO_Q_THRESHOLD: {RESET_AUDIO_Q_THRESHOLD}")
    print(f"STREAK_THRESHOLD: {STREAK_THRESHOLD}")
    print("Monitoring loud noises")
    streak = 0

    while True:
        if r.llen(REDIS_MONITOR_Q_NAME) > 0:
            audio_data = json.loads(r.rpop(REDIS_MONITOR_Q_NAME))
            mean = np.mean(audio_data)

            if streak == 0 and r.llen(REDIS_AUDIO_Q_NAME) >= RESET_AUDIO_Q_THRESHOLD:
                r.ltrim(REDIS_AUDIO_Q_NAME, 1, 0)
                print("Audio Q is full. Clearing it...")

            if streak >= STREAK_THRESHOLD:
                print("Consistent loud noise detected. Recording...")
                record_audio.delay()
                streak = 0

            if mean > LOUDNESS_THRESHOLD:
                print("Loud noise detected")
                streak += 1
            else:
                if streak > 0:
                    streak = 0
        else:
            time.sleep(1)


if __name__ == "__main__":
    start()
