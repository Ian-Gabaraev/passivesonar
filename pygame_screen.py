# pygame_screen.py

import pygame
import redis
import json


def screen_process():
    print("Server Running")
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Celery-Controlled Pygame Screen')
    running = True

    r = redis.Redis(host='localhost', port=9812, db=0)
    p = r.pubsub()
    p.subscribe('pygame_commands')

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        message = p.get_message()
        if message and message['type'] == 'message':
            task = json.loads(message['data'])

            if task == 'clear':
                screen.fill((0, 0, 0))
            else:
                action, params = task
                if action == 'draw_circle':
                    color, position, radius = params
                    pygame.draw.circle(screen, color, position, radius)
                if action == 'alarm':
                    color, position, radius = params
                    screen.fill((0, 0, 0))
                    pygame.draw.circle(screen, color, position, radius)
                if action == "analyze":
                    rms_values = params

                    for rms in rms_values:
                        if rms > 250:
                            screen.fill((0, 0, 0))
                            pygame.draw.circle(screen, 'red', (400, 300), 50)
                        elif rms > 200:
                            screen.fill((0, 0, 0))
                            pygame.draw.circle(screen, 'orange', (400, 300), 50)
                        elif rms > 150:
                            screen.fill((0, 0, 0))
                            pygame.draw.circle(screen, 'yellow', (400, 300), 50)
                        elif rms > 100:
                            screen.fill((0, 0, 0))
                            pygame.draw.circle(screen, 'green', (400, 300), 50)
                        elif rms > 50:
                            screen.fill((0, 0, 0))
                            pygame.draw.circle(screen, 'blue', (400, 300), 50)
                        elif rms > 30:
                            screen.fill((0, 0, 0))
                            pygame.draw.circle(screen, 'purple', (400, 300), 50)
                        elif rms > 30:
                            screen.fill((0, 0, 0))
                            pygame.draw.circle(screen, 'grey', (400, 300), 50)


            pygame.display.flip()

        pygame.time.wait(100)

    pygame.quit()


if __name__ == '__main__':
    screen_process()
