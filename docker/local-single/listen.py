from __future__ import annotations

import datetime
import os
from typing import Callable

import pyaudio
import numpy as np
import matplotlib.pyplot as plt

from utils.aws import upload_file_to_s3
from utils.redis_q import push_rms_to_redis, push_audio_to_redis
from dotenv import load_dotenv

load_dotenv()

REDIS_AUDIO_Q_NAME = os.getenv("REDIS_AUDIO_Q_NAME")

FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 1
RATE = int(os.getenv("SAMPLE_RATE", 48000))
CHUNK = int(os.getenv("CHUNK_SIZE", 2048))

BATCH_SIZE = 100
DEVICE_INDEX = 3
DURATION = 3600


def plot(rms_values: list[int | float], upload=False, show=True):
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


def get_device_index(p: pyaudio.PyAudio) -> int:
    if DEVICE_INDEX:
        return DEVICE_INDEX
    print("Choose the device index for recording")
    get_input_device_options(p)
    return int(input("Enter the device index: "))


def get_duration() -> int:
    if DURATION:
        return DURATION
    print("Choose duration of recording")
    return int(input("Duration: "))


def get_audio_stream(p: pyaudio.PyAudio, device_index: int) -> pyaudio.Stream:
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


def collect_rms(
    p: pyaudio.PyAudio,
    device_index: int,
    stream: pyaudio.Stream,
    duration: int,
    relay: Callable = None,
    noise_func: Callable = None,
):
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

        # This is not good
        if len(rms_for_analysis) == BATCH_SIZE:
            if relay is not None:
                relay(rms_for_analysis, device_index)
            if noise_func is not None:
                noise_func(rms_for_analysis)

            print(
                f"{datetime.datetime.now()} Pushed a batch of {BATCH_SIZE} RMS values to relay service"
            )
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
    collect_rms(
        p, device_index, stream, duration, push_rms_to_redis, push_audio_to_redis
    )


if __name__ == "__main__":
    launch()
