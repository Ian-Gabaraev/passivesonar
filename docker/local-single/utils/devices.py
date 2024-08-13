import numpy as np
import pyaudio

p = pyaudio.PyAudio()


def get_peak_frequency(audio_data: np.ndarray) -> float:
    fft_data = np.fft.fft(audio_data)
    magnitude = np.abs(fft_data)
    frequencies = np.fft.fftfreq(len(magnitude), 1.0 / 48_000)
    peak_freq = frequencies[np.argmax(magnitude)]

    return peak_freq


def get_input_device_options():
    for i in range(p.get_device_count()):
        name = p.get_device_info_by_index(i)["name"]
        channels = p.get_device_info_by_index(i)["maxInputChannels"]
        print(f"Index: {i}, Name: {name}, Channels: {channels}")


class InputDevice:
    def __init__(self, index, name, sample_rate, channels):
        self.index = index
        self.name = name
        self.sample_rate = sample_rate
        self.channels = channels

    def __str__(self):
        return f"{self.index}: {self.name} " f"@ {self.sample_rate // 1_000}kHz"


def get_device(index=None, max_channels=None, sample_rate=None):
    if index is not None:
        dev = p.get_device_info_by_index(index)
        return InputDevice(
            index, dev["name"], dev["defaultSampleRate"], dev["maxInputChannels"]
        )

    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if (
            dev["maxInputChannels"] == max_channels
            and dev["defaultSampleRate"] == sample_rate
        ):
            return InputDevice(
                i, dev["name"], dev["defaultSampleRate"], dev["maxInputChannels"]
            )
    return None
