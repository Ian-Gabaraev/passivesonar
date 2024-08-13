import pyaudio

from utils.aws import (
    get_batch_size,
    get_chunk_size,
    get_sampling_rate,
    get_listening_duration,
)

from utils.devices import get_device, InputDevice

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = int(get_sampling_rate())
CHUNK = int(get_chunk_size())

BATCH_SIZE = int(get_batch_size())
DEVICE_INDEX = 3 or None
DEVICE = get_device(DEVICE_INDEX, CHANNELS, RATE)
DURATION = int(get_listening_duration())


class PyAudioStream:

    def __init__(self, device: InputDevice = DEVICE):
        self.p = pyaudio.PyAudio()
        self.stream: pyaudio.Stream = None
        self.device = device
        self.rate = RATE
        self.chunk = CHUNK

    def get_time_running(self):
        return self.stream.get_time()

    def get_latency(self):
        return round(self.stream.get_input_latency() * 1000)

    def open(self):
        self.stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            input_device_index=self.device.index,
        )
        print(
            f"""
-----------------------Start---------------------------
Stream opened with device {str(self.device)}
Input latency: {self.get_latency()} ms
Sampling rate: {RATE}Hz
Chunk size: {CHUNK}
Duration: {DURATION} seconds
Batch size: {BATCH_SIZE} RMS
-------------------------------------------------------
"""
        )

    def restart(self):
        self.p.terminate()
        self.p = pyaudio.PyAudio()
        self.open()

    def __str__(self):
        return (
            f"PyAudioStream(device_index={self.device.index}, "
            f"sampling_rate={RATE}, "
            f"chunk_size={CHUNK}, "
            f"duration={DURATION}, "
            f"batch_size={BATCH_SIZE})"
        )
