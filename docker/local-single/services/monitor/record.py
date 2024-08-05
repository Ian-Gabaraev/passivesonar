from datetime import datetime
import wave

import pyaudio

FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 1  # Mono audio
RATE = 48000  # Sampling rate (48 kHz)


class Recording:

    def __init__(self):
        self.launch_time = None
        self.active = False
        self.file_name = None
        self.stream = None

    def get_filename(self):
        return f"waves/{self.launch_time.strftime('%Y-%m-%d_%H-%M-%S')}.wav"

    def get_output_stream(self):
        wf = wave.open(self.file_name, "wb")
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pyaudio.get_sample_size(FORMAT))
        wf.setframerate(RATE)

        return wf

    def start(self):
        self.launch_time = datetime.now()
        self.file_name = self.get_filename()
        self.stream = self.get_output_stream()
        self.active = True

    def stop(self):
        self.stream.close()
        self.active = False
        self.launch_time = None
        self.file_name = None
        self.stream = None
