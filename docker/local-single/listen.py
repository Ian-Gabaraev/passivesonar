from __future__ import annotations

import os
import sys
import time
from typing import Callable

import numpy as np

from utils.aws import (
    get_batch_size,
    get_listening_duration,
)
from utils.redis_q import (
    push_rms_to_redis,
    push_audio_to_redis,
    redis_online,
    get_control_message,
)
from dotenv import load_dotenv
from stream import PyAudioStream

load_dotenv()

REDIS_AUDIO_Q_NAME = os.getenv("REDIS_AUDIO_Q_NAME")
BATCH_SIZE = int(get_batch_size())
DURATION = int(get_listening_duration())


def convert_to_rms(audio_data: np.ndarray) -> float:
    audio_data = audio_data.astype(np.int32)
    rms = np.sqrt(np.mean(audio_data**2))
    return float(rms)


def read_audio_input(
    stream: PyAudioStream,
    relay: Callable = None,
    noise_func: Callable = None,
):
    rms_values = []
    rms_for_analysis = []
    stream.open()

    for i in range(0, int(stream.rate / stream.chunk * DURATION)):

        if get_control_message() == b"stop":
            stream.stream.stop_stream()
            print("Stopping stream")
        if get_control_message() == b"start":
            stream.stream.start_stream()
            print("Starting stream")

        if stream.stream.is_stopped():
            continue

        data = stream.stream.read(stream.chunk)
        audio_data = np.frombuffer(data, dtype=np.int16)

        if noise_func is not None:
            noise_func(audio_data, REDIS_AUDIO_Q_NAME)

        rms = convert_to_rms(audio_data)
        rms_values.append(rms)
        rms_for_analysis.append(rms)

        # This is not good
        if len(rms_for_analysis) == BATCH_SIZE:
            if relay is not None:
                relay(rms_for_analysis, stream.device.index)
            if noise_func is not None:
                noise_func(rms_for_analysis)
            rms_for_analysis.clear()

    stream.p.terminate()

    return rms_values


def launch():
    retries = 0

    while not redis_online():
        print("Redis is not online. Waiting for 10 seconds before retrying.")
        time.sleep(10)
        retries += 1

        if retries > 10:
            print("Max retries reached. Exiting.")
            sys.exit(1)

    read_audio_input(
        stream=stream, relay=push_rms_to_redis, noise_func=push_audio_to_redis
    )


stream = PyAudioStream()


if __name__ == "__main__":
    launch()
