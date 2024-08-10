import os
import time

import numpy as np
from celery import Celery
import redis
from record import Recording
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_Q_NAME = os.getenv("REDIS_Q_NAME")
REDIS_AUDIO_Q_NAME = os.getenv("REDIS_AUDIO_Q_NAME")

app = Celery(
    "audio_processor",
    broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/0",
    backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/0",
)

app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)


r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)


@app.task
def record_audio(seconds=30):
    started_at = time.time()
    recording = Recording()
    recording.start()
    print("Recording audio")

    while time.time() - started_at < seconds:
        data = r.lpop(REDIS_AUDIO_Q_NAME)
        if data:
            audio_data = np.frombuffer(data, dtype=np.int16)
            recording.stream.writeframes(audio_data)

    print("Recording stopped")
    recording.stop()
    return "Audio recorded"
