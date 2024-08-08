import os
import numpy as np
from celery import Celery
import redis
from record import Recording
from dotenv import load_dotenv
from bot import send_audio_message

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_Q_NAME = os.getenv("REDIS_Q_NAME")
REDIS_AUDIO_Q_NAME = os.getenv("REDIS_AUDIO_Q_NAME")
SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", 48000))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 2048))

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


def calculate_chunks_per_second(sample_rate, chunk_size):
    chunk_duration = chunk_size / sample_rate
    chunks_per_second = 1 / chunk_duration
    return round(chunks_per_second)


@app.task
def record_audio(seconds=30):
    recording = Recording()
    recording.start()
    print("Recording audio")

    number_of_messages = calculate_chunks_per_second(SAMPLE_RATE, CHUNK_SIZE) * seconds
    latest_messages = r.lrange(REDIS_AUDIO_Q_NAME, -number_of_messages, -1)

    for data in latest_messages:
        audio_data = np.frombuffer(data, dtype=np.int16)
        recording.stream.writeframes(audio_data)

    with open(recording.file_name, "rb") as audio:
        send_audio_message(audio)
    print("Audio sent to the main chat")
    print("Recording stopped")
    recording.stop()
    return "Audio recorded"
