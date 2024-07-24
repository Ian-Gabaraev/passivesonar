import pygame
import redis
import json
import time


class ScreenProcess:
    def __init__(self):
        self.launch_time = time.time()
        self.verbal_alert_start_time = None
        self.verbal_alert_duration = 2
        self.show_verbal_alert = False
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Celery-Controlled Screen")
        r = redis.Redis(host="localhost", port=9812, db=0)
        self.redis_channel = r.pubsub()
        self.redis_channel.subscribe("pygame_commands")
        self.device_name = ""

        self.chunks = 0
        self.alert_message = ""
        self.alert_duration_seconds = 2
        self.alert_fired = None

    def get_elapsed_time(self):
        return (time.time() - self.launch_time) / 60

    def display_alert_message(self):
        font = pygame.font.Font(None, 30)
        text_surface = font.render(f"{self.alert_message}", True, "red")
        text_rect = text_surface.get_rect()
        text_rect.bottomleft = (10, self.screen.get_height() - 50)

        self.screen.blit(text_surface, text_rect)

    def reset_alert(self):
        if self.alert_fired is not None:
            if (time.time() - self.alert_fired) > self.alert_duration_seconds:
                self.alert_message = ""
                self.alert_fired = None
                self.display_alert_message()

    def display_device_name(self):
        font = pygame.font.Font(None, 30)  # None uses the default font, 50 is the size
        text_surface = font.render(f"Listening from: {self.device_name}", True, "blue")
        text_rect = text_surface.get_rect()
        text_rect.topleft = (10, 10)

        self.screen.blit(text_surface, text_rect)

    def display_chunks(self):
        font = pygame.font.Font(None, 30)  # None uses the default font, 50 is the size
        text_surface = font.render(f"Chunks processed {self.chunks}", True, "green")
        text_rect = text_surface.get_rect()
        text_rect.bottomleft = (10, self.screen.get_height() - 30)

        self.screen.blit(text_surface, text_rect)

    def display_status(self, color):
        font = pygame.font.Font(None, 60)
        text_surface = font.render(f"NOISE REGISTERED", True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (self.screen.get_height() // 2, self.screen.get_width() // 2)
        self.screen.blit(text_surface, text_rect)

    def display_time(self):
        font = pygame.font.Font(None, 30)  # None uses the default font, 50 is the size
        text_surface = font.render(
            f"Time Elapsed: {self.get_elapsed_time():.2f} minutes", True, "green"
        )
        text_rect = text_surface.get_rect()
        text_rect.bottomleft = (10, self.screen.get_height() - 10)

        self.screen.blit(text_surface, text_rect)

    def analyze(self, rms_values):
        self.chunks += len(rms_values)
        for rms in rms_values:
            if rms > 250:
                # pygame.draw.circle(self.screen, 'red', (400, 300), 50)
                self.display_status("red")
                self.alert_fired = time.time()
                self.alert_message = "ALERT: Loud Noise Detected"
            elif rms > 200:
                self.display_status("orange")
                # pygame.draw.circle(self.screen, 'orange', (400, 300), 50)
            elif rms > 150:
                self.display_status("yellow")
                # pygame.draw.circle(self.screen, 'yellow', (400, 300), 50)
            elif rms > 100:
                self.display_status("green")
                # pygame.draw.circle(self.screen, 'green', (400, 300), 50)
            elif rms > 50:
                self.display_status("blue")
                # pygame.draw.circle(self.screen, 'blue', (400, 300), 50)
            elif rms > 30:
                self.display_status("purple")
                # pygame.draw.circle(self.screen, 'purple', (400, 300), 50)
            elif rms > 22:
                self.display_status("white")
                # pygame.draw.circle(self.screen, 'white', (400, 300), 50)

    def run(self):
        print("Server Running")
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.screen.fill((0, 0, 0))
            self.display_time()
            self.display_chunks()
            self.reset_alert()
            self.display_alert_message()
            self.display_device_name()

            message = self.redis_channel.get_message()

            if message and message["type"] == "message":
                task = json.loads(message["data"])

                if task == "clear":
                    self.screen.fill((0, 0, 0))
                else:
                    action, params = task
                    if action == "draw_circle":
                        color, position, radius = params
                        pygame.draw.circle(self.screen, color, position, radius)
                    if action == "analyze":
                        self.analyze(params)
                    if action == "display_device_name":
                        self.device_name = params

            pygame.display.flip()
            pygame.time.wait(40)

        pygame.quit()


if __name__ == "__main__":
    process = ScreenProcess()
    process.run()
