import matplotlib.pyplot as plt


def plot_stats(stats, filename=None):
    plt.plot(stats)
    plt.xlabel("Time")
    plt.ylabel("Audio")
    plt.title("Audio graph")
    plt.savefig(filename)
