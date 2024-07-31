import datetime

import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from celeryapps import (
    analyze,
    display_device_name,
)
from aws import upload_file_to_s3
from redis_q import push_rms_to_redis

FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 1  # Mono audio
RATE = 48000  # Sampling rate (48 kHz)
CHUNK = 2048  # Buffer size (increased for better averaging)

DURATION = None
DEVICE_INDEX = None
BATCH_SIZE = 20


def convert_to_db(rms_value, reference=32767):
    """Convert an RMS value to decibels."""
    if rms_value == 0:
        return -np.inf  # Logarithm of zero is undefined, represents silence.
    return 20 * np.log10(rms_value / reference)


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
    if DEVICE_INDEX:
        return DEVICE_INDEX

    print("Choose the device index for recording")
    get_input_device_options(p)
    return int(input("Enter the device index: "))


def get_duration():
    if DURATION:
        return DURATION

    print("Choose duration of recording")
    return int(input("Duration: "))


def get_device_info(p, device_index):
    return [
        p.get_device_info_by_index(device_index)["name"],
        p.get_device_info_by_index(device_index)["maxInputChannels"],
    ]


def get_audio_stream(p, device_index):
    print("Using ", get_device_info(p, device_index))
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


def order_device_info_display(p, device_index):
    device_name = p.get_device_info_by_index(device_index)["name"]
    display_device_name.delay(device_name)


def relay_audio_to_celery(data):
    analyze.delay(data)


def collect_rms(p, device_index, stream, duration, relay=None):
    rms_values = []
    rms_for_analysis = []

    for i in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        audio_data = np.frombuffer(data, dtype=np.int16)
        audio_data = audio_data.astype(np.int32)
        rms = np.sqrt(np.mean(audio_data**2))
        rms_values.append(rms)
        rms_for_analysis.append(float(rms))

        if len(rms_for_analysis) == BATCH_SIZE:
            print(f"Collected a batch of {BATCH_SIZE} RMS values")
            if relay is not None:
                relay(rms_for_analysis, device_index)
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
    collect_rms(p, device_index, stream, duration, push_rms_to_redis)


if __name__ == "__main__":
    launch()
