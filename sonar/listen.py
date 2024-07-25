import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from celeryapps import (
    init_screen,
    analyze,
    draw_circle,
    display_device_name,
    kill_screen,
)


def plot(rms_values):
    plt.figure(figsize=(10, 6))
    plt.plot(rms_values)
    plt.xlabel("Time (chunks)")
    plt.ylabel("RMS (dBFS)")
    plt.title("RMS Values Over Time")
    plt.grid(True)
    plt.show()


def process_audio(duration=120, device_index=2):
    init_screen.delay()
    draw_circle.delay("green", (400, 300), 50)

    FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
    CHANNELS = 1  # Mono audio
    RATE = 48000  # Sampling rate (48 kHz)
    CHUNK = 2048  # Buffer size (increased for better averaging)
    RECORD_SECONDS = duration  # Duration of recording

    rms_values = []

    p = pyaudio.PyAudio()
    device_name = p.get_device_info_by_index(device_index)["name"]

    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        input_device_index=device_index,
    )

    rms_for_analysis = []

    print("Listening...")
    display_device_name.delay(device_name)
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        audio_data = np.frombuffer(data, dtype=np.int16)
        audio_data = audio_data.astype(np.int32)
        rms = np.sqrt(np.mean(audio_data**2))
        rms_values.append(rms)
        rms_for_analysis.append(float(rms))

        if len(rms_for_analysis) == 20:
            analyze.delay(rms_for_analysis)
            rms_for_analysis.clear()

    print("Finished listening")
    stream.stop_stream()
    stream.close()
    p.terminate()
    kill_screen.delay()


process_audio()
