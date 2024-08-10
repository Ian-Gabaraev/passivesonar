import datetime
import os
import numpy as np
from celery import Celery
import redis
from record import Recording
from dotenv import load_dotenv
from bot import send_audio_message, send_plot
from aws import get_sampling_rate, get_chunk_size, get_recording_duration
from utils.plots import plot_stats

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_Q_NAME = os.getenv("REDIS_Q_NAME")
REDIS_AUDIO_Q_NAME = os.getenv("REDIS_AUDIO_Q_NAME")

SAMPLE_RATE = int(get_sampling_rate())
CHUNK_SIZE = int(get_chunk_size())
RECORDING_DURATION = int(get_recording_duration())
from plot import plot

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
def record_audio(seconds=RECORDING_DURATION, message=None):
    recording = Recording()
    recording.start()

    number_of_messages = calculate_chunks_per_second(SAMPLE_RATE, CHUNK_SIZE) * seconds
    latest_messages = r.lrange(REDIS_AUDIO_Q_NAME, -number_of_messages, -1)

    if len(latest_messages) == 0:
        return "Nothing to record"

    to_plot = []
    for data in latest_messages:
        audio_data = np.frombuffer(data, dtype=np.int16)
        recording.stream.writeframes(audio_data)
        to_plot.extend(audio_data)

    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    plot_file_name = f"graphs/{time}.png"
    plot_stats(to_plot, plot_file_name)

    with open(recording.file_name, "rb") as audio:
        send_audio_message(audio, message)
    with open(plot_file_name, "rb") as plot_file:
        send_plot(plot_file)

    recording.stop()
    return "Audio recorded"
