import datetime

from matplotlib import pyplot as plt


def plot(audio_values, name):
    plt.figure(figsize=(20, 5))
    plt.plot(audio_values)
    plt.xlabel("Samples")
    plt.ylabel("Amplitude")
    plt.title(f"Sound Amplitude Over Time: {datetime.datetime.now()}")
    plt.grid(True)
    plt.savefig(fname=name)
    plt.show()
