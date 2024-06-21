import math
import numpy as np
import random
from shapely.geometry import Polygon

NYC_CENTER = (40.7128, -74.0060)

def generate_random_polygon(center, radius):
    x, y = center
    points = []
    for _ in range(6):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, radius)
        point_x = x + distance * math.cos(angle)
        point_y = y + distance * math.sin(angle)
        points.append((point_x, point_y))
    return Polygon(points)

def generate_random_polygons_around_new_york(num_polygons = 10, radius = 0.1):
    """
        NYC Center is (40.7128, -74.0060).
        
    """
    new_york_center = (40.7128, -74.0060)  # New York City coordinates
    polygons = []
    for _ in range(num_polygons):
        polygon = generate_random_polygon(new_york_center, radius)
        polygons.append(polygon)
    return polygons

def generate_tests_for_simon(distance = 0.1, polygon_size = 0.01):

    random_polygons = generate_random_polygons_around_new_york(10, polygon_size)

    start = np.random.rand(2) * distance + np.array(NYC_CENTER)
    end = np.random.rand(2) * distance + np.array(NYC_CENTER)

    return start, end, random_polygons

# # Example usage
# num_polygons = 10
# radius = 0.1  # Adjust this value to control the size of the polygons
# polygons = generate_random_polygons_around_new_york(num_polygons, radius)
# for polygon in polygons:
#     print(polygon)