## Noise Monitoring System

### What is it?
The Noise Monitoring System is a system that listens to the environment and detects noise levels. It can be used in various applications like monitoring noise levels in a room, monitoring noise levels in a factory, etc. The system can be set up in two modes: locally-processed, single-mic mode and remotely-processed, multi-mic mode.

Another possible application is for AirBnb hosts to monitor noise levels in their properties. The system can be set up in the property and the host can monitor the noise levels remotely.
When the noise levels exceed a certain pre-defined threshold, the system sends a notification to the host with a recording of the noise and a frequency plot.

This has been tested on a Raspberry Pi 4 b with a USB microphone.

In active mode it consumes about 700mb of RAM and 15% of CPU. Temperature of the chip stays around 30 degrees celsius.

### Advantages
- The system is real-time with negligible delay.
- You own your data. The system does not send or store any audio data to the cloud.
- The system is modular, open-source and can be easily extended.
- The system is easily configured to match your requirements.
- The code is in Python, and it runs on a variaty of hardware. On top of that, it uses docker-compose.
- It is easy on the hardware. It can run on a Raspberry Pi 4 b with a USB microphone.
- It is easily controlled via a Telegram bot.

### Challenges
- You need to have some technical knowledge to set up the system.
- You will need to configure the system to match your microphone. E.g. cheaper microphones require lower loudness thresholds. This is because they are less sensitive and require more gain.
- **It can be misused to spy on people**. Please use it responsibly. **Beware of the legal implications of using this system to eavesdrop on people**.


### Features
- Real-time automatic noise monitoring
- On-demand noise monitoring
- System data monitoring
- Telegram bot for control and notifications

### Screenshots
See the screenshots in the `screenshots` directory.

## Modes

- Locally-processed, single-mic mode
- Remotely-processed, multi-mic mode `WIP`

### Locally-processed, single-mic mode

In this mode, the noise detection is done on the device itself. The device has a single microphone and the noise detection is done on the audio data from this microphone. The device can be a mini pc like Raspberry Pi or another macOS/Linux machine.

To set up the locally-processed, single-mic mode, follow the steps below:

1. Clone the repository
2. Navigate to ``docker/local-single``
3. Create a python virtual environment and activate it
4. Install the required packages using the command ``pip install -r requirements.txt``
5. Create a ``.env`` file and add the following environment variables:
    ```
    AWS_ACCESS_KEY_ID='key'
    AWS_SECRET_ACCESS_KEY='secret'
    AWS_REGION='region'
    REDIS_PORT=9595
    REDIS_Q_NAME='SonarMessages'
    REDIS_HOST='localhost'
    REDIS_MONITOR_Q_NAME='LoudnessMonitor'
    REDIS_AUDIO_Q_NAME='Audio'
    REDIS_CONTROL_Q_NAME='Control'
    SAMPLE_RATE=48000
    CHUNK_SIZE=2048
    SYSTEM_Q_NAME='SystemQ'
    ```
6. Daemonize `listen.py` and `system.py` using the template `systemd_listen.service`. Use systemd or supervisord. This will spawn two python processes. `listen.py` does the actual listening and `system.py` collects system information.
7. The project relies on AWS SSM Parameter Store for flexible settings. You can still hard-code your preferences if you like.
8. Navigate to `telegram`. Create a `.env` file and add the following environment variables:
    ```
    BOT_TOKEN='token'
    MAIN_CHAT_ID='chat id'
    ```
   You can get the `chat_id` by sending a message to the bot and logging message details.
9. Navigate to `services/monitor`. Create a `.env` file and add the following environment variables:
    ```
    AWS_ACCESS_KEY_ID='key'
    AWS_SECRET_ACCESS_KEY='secret'
    AWS_DEFAULT_REGION='region'
    
    REDIS_PORT=6379
    REDIS_Q_NAME='SonarMessages'
    REDIS_HOST='redis'
    REDIS_MONITOR_Q_NAME='LoudnessMonitor'
    REDIS_AUDIO_Q_NAME='Audio'
    REDIS_SYSTEM_Q_NAME='SystemQ'
    REDIS_CONTROL_Q_NAME='Control'
    
    SAMPLE_RATE=48000
    CHUNK_SIZE=2048
    
    BOT_TOKEN='token'
    MAIN_CHAT_ID='chat_id'
    ```
   
10. Navigate to `services/wsserver`. Create a `.env` file and add the following environment variables:
    ```
    REDIS_PORT=6379
    REDIS_Q_NAME='SonarMessages'
    REDIS_HOST='redis'
    REDIS_MONITOR_Q_NAME='LoudnessMonitor'
    REDIS_AUDIO_Q_NAME='Audio'
    ```
    
11. Navigate back to `docker/local-single` and run `docker-compose up --build`
12. If set up corrently, you will receive a message from the bot.