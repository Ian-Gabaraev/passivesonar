import datetime

from matplotlib import pyplot as plt


def plot(audio_values, name):
    plt.figure(figsize=(10, 5))
    plt.plot(audio_values)
    plt.xlabel("Samples")
    plt.ylabel("Amplitude")
    plt.title("Sound Amplitude Over Time")
    plt.grid(True)
    plt.savefig(fname=name)
    plt.show()
