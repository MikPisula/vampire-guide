import pygame
import sys
import math
import numpy as np

pygame.init()

WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Draw Polygon')

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

points = [(200, 200), (250, 300), (300, 250), (400, 400), (200, 400)]

# def rotate2d(x, y, angle):
#     cos_a = math.cos(angle)
#     sin_a = math.sin(angle)
#     return x * cos_a - y * sin_a, x * sin_a + y * cos_a


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    window.fill(WHITE)
    
    sun_pos = pygame.mouse.get_pos()

    
    # height = 10
    # light_angle = math.pi/4
    # shadow_length = math.atan(light_angle) * height

    # shadow_points = points
    shadow_points = []
    for point in points:
        vec = np.array([point[0] - sun_pos[0], point[1] - sun_pos[1]])
        normalized_vec = (vec / np.linalg.norm(vec)) * 30
        shadow_points.append((normalized_vec[0] + point[0], normalized_vec[1] + point[1]))    
    
    pygame.draw.polygon(window, BLACK, shadow_points)
    pygame.draw.circle(window, YELLOW, sun_pos, 20)
    pygame.draw.polygon(window, BLUE, points)

    pygame.display.flip()