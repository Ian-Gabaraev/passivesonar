import asyncio
import pyaudio
import numpy as np
import websockets
import json

FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 1  # Mono audio
RATE = 48000  # Sampling rate (48 kHz)
CHUNK = 2048  # Buffer size (increased for better averaging)
BATCH_SIZE = 50
DURATION = 3600
DEVICE_INDEX = 3


async def get_audio_stream(p, device_index):
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        input_device_index=device_index,
    )
    return stream


async def send_audio_data(ws, p):
    stream = await get_audio_stream(p, DEVICE_INDEX)
    rms_values = []
    rms_for_analysis = []

    for i in range(0, int(RATE / CHUNK * DURATION)):
        data = stream.read(CHUNK)
        audio_data = np.frombuffer(data, dtype=np.int16)
        audio_data = audio_data.astype(np.int32)
        rms = np.sqrt(np.mean(audio_data**2))
        rms_values.append(rms)
        rms_for_analysis.append(float(rms))

        if len(rms_for_analysis) == BATCH_SIZE:
            print(f"Sending chunk {i}")
            await ws.send(json.dumps(rms_for_analysis))
            rms_for_analysis.clear()

    stream.stop_stream()
    stream.close()
    p.terminate()


async def on_receive_message(message):
    print("Received message:", message)


async def connect():
    uri = "ws://localhost:12000"
    async with websockets.connect(uri) as ws:
        await ws.send("Connection opened")
        p = pyaudio.PyAudio()
        await send_audio_data(ws, p)


async def main():
    await connect()


if __name__ == "__main__":
    asyncio.run(main())
