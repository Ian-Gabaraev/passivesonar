import datetime
import os

import pyaudio
import numpy as np
import matplotlib.pyplot as plt

from services.wsserver.aws import upload_file_to_s3
from services.wsserver.redis_q import push_rms_to_redis, push_audio_to_redis
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_Q_NAME = os.getenv("REDIS_Q_NAME")
REDIS_AUDIO_Q_NAME = os.getenv("REDIS_AUDIO_Q_NAME")

FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 1  # Mono audio
RATE = 48000  # Sampling rate (48 kHz)
CHUNK = 2048  # Buffer size (increased for better averaging)

BATCH_SIZE = 20


def plot(rms_values, upload=False, show=True):
    plt.figure(figsize=(10, 6))
    plt.plot(rms_values)
    plt.xlabel("Time (chunks)")
    plt.ylabel("RMS")
    plt.title("Root Median Square (RMS) Values Over Time")
    plt.grid(True)

    if upload:
        plt.savefig("rms_values.png")
        upload_file_to_s3("rms_values.png", f"rms-{datetime.datetime.now()}.png")

    if show:
        plt.show()


def get_input_device_options(p: pyaudio.PyAudio):
    for i in range(p.get_device_count()):
        name = p.get_device_info_by_index(i)["name"]
        channels = p.get_device_info_by_index(i)["maxInputChannels"]
        print(f"Index: {i}, Name: {name}, Channels: {channels}")


def get_device_index(p):
    print("Choose the device index for recording")
    get_input_device_options(p)
    return int(input("Enter the device index: "))


def get_duration():
    print("Choose duration of recording")
    return int(input("Duration: "))


def get_device_info(p, device_index):
    return [
        p.get_device_info_by_index(device_index)["name"],
        p.get_device_info_by_index(device_index)["maxInputChannels"],
    ]


def get_audio_stream(p, device_index):
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        input_device_index=device_index,
    )
    print("Stream opened")
    return stream


def collect_rms(p, device_index, stream, duration, relay=None, noise_func=None):
    rms_values = []
    rms_for_analysis = []

    for i in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        audio_data = np.frombuffer(data, dtype=np.int16)

        if noise_func is not None:
            noise_func(audio_data, REDIS_AUDIO_Q_NAME)

        audio_data = audio_data.astype(np.int32)
        rms = np.sqrt(np.mean(audio_data**2))
        rms_values.append(rms)
        rms_for_analysis.append(float(rms))

        if len(rms_for_analysis) == BATCH_SIZE:
            if relay is not None:
                relay(rms_for_analysis, device_index)
            if noise_func is not None:
                noise_func(rms_for_analysis)
            rms_for_analysis.clear()

    stream.stop_stream()
    stream.close()
    p.terminate()

    return rms_values


def launch():
    p = pyaudio.PyAudio()
    device_index = get_device_index(p)
    duration = get_duration()
    stream = get_audio_stream(p, device_index)
    collect_rms(p, device_index, stream, duration, push_rms_to_redis, push_audio_to_redis)


if __name__ == "__main__":
    launch()
