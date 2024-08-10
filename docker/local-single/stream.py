import pyaudio

from utils.aws import (
    get_batch_size,
    get_chunk_size,
    get_sampling_rate,
    get_listening_duration,
)

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = int(get_sampling_rate())
CHUNK = int(get_chunk_size())

BATCH_SIZE = int(get_batch_size())
DEVICE_INDEX = 3
DURATION = int(get_listening_duration())


class PyAudioStream:

    def __init__(self, device_index: int):
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.device_index = device_index

    def open(self):
        self.stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            input_device_index=self.device_index,
        )
        print("Stream opened with device index", self.device_index)
        print("Sampling rate:", RATE)
        print("Chunk size:", CHUNK)
        print("Duration:", DURATION)
        print("Batch size:", BATCH_SIZE)

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def restart(self):
        self.p.terminate()
        self.p = pyaudio.PyAudio()
        self.open()
