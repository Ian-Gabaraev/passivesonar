import os
import time

import numpy as np
from celery import Celery
import redis
import json
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
def kill_screen():
    task = json.dumps("kill")
    r.publish("pygame_commands", task)
    return "Screen killed"


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


@app.task
def display_device_name(device_name):
    task = json.dumps(("display_device_name", device_name))
    r.publish("pygame_commands", task)
    return f"Device name displayed: {device_name}"


@app.task
def analyze(rms):
    task = json.dumps(("analyze", rms))
    r.publish("pygame_commands", task)
    return "RMS Analysis completed"


@app.task
def draw_circle(color, position, radius):
    task = json.dumps(("draw_circle", (color, position, radius)))
    r.publish("pygame_commands", task)
    return f"Circle drawn at {position} with radius {radius}"


@app.task
def clear_screen():
    task = json.dumps("clear")
    r.publish("pygame_commands", task)
    return "Screen cleared"
