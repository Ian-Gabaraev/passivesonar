import sounddevice as sd
import numpy as np

# Parameters for audio recording
RATE = 44100  # Sampling rate (44.1 kHz)
CHUNK = 2048  # Buffer size (increased for better averaging)
RECORD_SECONDS = 10  # Duration of recording


def print_rms(indata, frames, time, status):
    # Convert audio data to numpy array
    audio_data = np.frombuffer(indata, dtype=np.int16)

    # Print raw data values
    print(audio_data)

    # Calculate RMS
    rms = np.sqrt(np.mean(audio_data ** 2))

    if rms > 0:
        db = 20 * np.log10(rms)
    else:
        db = -np.inf  # To handle log(0) case

    print(f"RMS (dB): {db:.2f}")


print("Recording...")
with sd.InputStream(callback=print_rms, channels=1, samplerate=RATE, blocksize=CHUNK):
    sd.sleep(RECORD_SECONDS * 1000)
print("Recording finished.")
