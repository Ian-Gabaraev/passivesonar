import numpy as np
import matplotlib.pyplot as plt
import librosa
from functools import lru_cache


class AmplitudeEnvelope:

    def __init__(self, file_name: str):
        self.file_name = file_name
        self.signal, self.sampling_rate = librosa.load(file_name)
        self.duration = (1 / self.sampling_rate) * self.signal.size
        self.frame_size = 1024
        self.hop_length = self.frame_size // 2

    @lru_cache()
    def calculate_amplitude_envelope(self) -> np.ndarray:

        return np.array(
            [
                np.max(self.signal[i : i + self.frame_size])
                for i in range(0, self.signal.size, self.hop_length)
            ]
        )

    def calculate_time_indices(self) -> np.ndarray:
        ae = self.calculate_amplitude_envelope()
        frames = np.array(range(0, ae.size))
        t = librosa.frames_to_time(
            frames, sr=self.sampling_rate, hop_length=self.hop_length
        )
        return t

    def plot(self):
        plt.figure(figsize=(self.duration // 2, 5))
        plt.style.use("dark_background")
        plt.grid(color="gray", linestyle="--", linewidth=0.5, alpha=0.5)
        plt.title("Amplitude Envelope", color="white", fontsize=16, fontname="Ubuntu")

        librosa.display.waveshow(self.signal, sr=self.sampling_rate, color="b")
        ae = self.calculate_amplitude_envelope()
        t = self.calculate_time_indices()

        plt.plot(t, ae, color="cyan")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        xtick_positions = np.arange(0, np.max(t) + 1, 1)
        plt.xticks(xtick_positions, color="white")
        plt.legend(
            [
                f"Clip '{self.file_name}'\n"
                f"Signal duration: {round(self.duration)} sec\n"
                f"Sampling rate: {self.sampling_rate / 1_000} kHz"
            ],
            loc="best",
            frameon=True,
            shadow=True,
        )

        plt.savefig("envelope.png")


if __name__ == "__main__":
    ae = AmplitudeEnvelope("mars.wav")
    ae.plot()
