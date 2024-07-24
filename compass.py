
def draw_compass(screen, direction):
    screen.fill((0, 0, 0))
    center = (screen.get_width() // 2, screen.get_height() // 2)
    outer_radius = min(center) - 20
    pygame.draw.circle(screen, 'green', center, outer_radius, 1)
    div = 1.1

    angle_in_radians = math.radians(180)
    end_pos = (
        center[0] + outer_radius * math.tan(angle_in_radians),
        center[1] + outer_radius * math.tanh(angle_in_radians)
    )
    pygame.draw.line(screen, 'green', (300, 20), end_pos, 2)

    angle_in_radians = math.radians(1)
    end_pos = (
        center[0] + outer_radius * math.cos(angle_in_radians),
        center[1] + outer_radius * math.sin(angle_in_radians)
    )
    pygame.draw.line(screen, 'green', (300, 100), end_pos, 2)

    angle_in_radians = math.radians(direction)
    end_pos = (
        center[0] + outer_radius * math.cos(angle_in_radians),
        center[1] - outer_radius * math.sin(angle_in_radians)
    )
    pygame.draw.line(screen, 'green', center, end_pos, 2)
    pygame.display.flip()

pygame.init()

screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption("Sonar Demo")

running = True
direction = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    direction = (direction + 1) % 360
    draw_compass(screen, direction)
    pygame.time.delay(10)

pygame.quit()
