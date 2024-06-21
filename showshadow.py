import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Draw Polygon')

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

points = [(100, 100), (150, 200), (200, 150), (300, 300), (100, 300)]

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    window.fill(WHITE)
    
    sun_pos = pygame.mouse.get_pos()

    pygame.draw.polygon(window, BLUE, points)

    shadow_points = []
    for point in points:
        shadow_point = (point[0] - sun_pos[0], point[1] - sun_pos[1]) # TODO: normalize this
        shadow_points.append(shadow_point)    
    
    pygame.draw.polygon(window, BLACK, shadow_points)
    pygame.draw.circle(window, YELLOW, sun_pos, 20)

    pygame.display.flip()