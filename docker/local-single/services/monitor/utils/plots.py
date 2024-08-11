import datetime

import matplotlib.pyplot as plt
import numpy as np


def plot_stats(data, filename, chunk_size=100):
    stats = []
    for i in range(0, len(data), chunk_size):
        sublist = data[i: i + chunk_size]
        stats.append(np.mean(sublist))

    plt.figure(figsize=(20, 6))
    plt.plot(stats, linewidth=0.5, alpha=0.7)
    plt.xlabel("Chunk")
    plt.ylabel("Amplitude")
    plt.title(f"Amplitude Over Time {datetime.datetime.now()}")
    plt.savefig(filename)
