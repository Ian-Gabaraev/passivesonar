import json
import time

import redis


class LoudNoiseDetector:
    def __init__(self):
        self.launch_time = time.time()
        self.verbal_alert_start_time = None
        self.verbal_alert_duration = 2
        self.show_verbal_alert = False
        self.r = redis.Redis(host="localhost", port=9812, db=0)
        self.redis_channel = self.r.pubsub()
        self.redis_channel.subscribe("pygame_commands")

        self.total_chunks = 0
        self.loud_chunks = []

        self.alarm_fired = False

    def alert_constant_noise(self):
        if self.total_chunks > 250:
            loud_noise_percentage = (len(self.loud_chunks) / self.total_chunks) * 100

            print("Current loud noise percentage: ", loud_noise_percentage)

            if loud_noise_percentage > 80:
                print("Issuing a loud noise alert")
                self.r.publish("loud_noise", json.dumps("loud"))
                self.alarm_fired = True
                return

            if self.alarm_fired and loud_noise_percentage < 50:
                print("Resetting the loud noise alert")
                self.total_chunks = 0
                self.loud_chunks = []
                self.alarm_fired = False
                return

            if not self.alarm_fired and loud_noise_percentage < 30:
                print("Resetting the loud noise alert")
                self.total_chunks = 0
                self.loud_chunks = []
                self.alarm_fired = False
                return

    def analyze(self, rms_values):
        self.total_chunks += len(rms_values)
        self.loud_chunks.extend(
            list(filter(lambda x: x > 250, rms_values))
        )
        print(f"Total chunks: {self.total_chunks}")
        print(f"Loud chunks: {len(self.loud_chunks)}")
        self.alert_constant_noise()

    def run(self):
        print("Loud Noise Processing Server Running")

        while True:
            message = self.redis_channel.get_message()
            if message and message["type"] == "message":
                task = json.loads(message["data"])
                try:
                    action, params = task
                    if action == "analyze":
                        self.analyze(params)
                except ValueError:
                    pass


if __name__ == "__main__":
    process = LoudNoiseDetector()
    process.run()
