import numpy as np
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import split

CENTER_LOCATION = (50, 50)
GRID_DIMENSIONS_METERS = 1000
CELL_SIZE_METERS = 1

def calculate_shade_map(list_of_polygons, sun_position: np.ndarray, cell_size: float):
    """
        Gets a list of polygons in a city, the sun position, and the cell size of the output

        Returns a 2D array of the shade map of the city (0 - no shade, 1 - full shade)
    """

    grid = np.zeros((GRID_DIMENSIONS_METERS // CELL_SIZE_METERS, GRID_DIMENSIONS_METERS // CELL_SIZE_METERS))

    return grid

def find_path(start, end):
    """
        Start, end are geo-coordinates of the start and end of the path
        Finds the path based on the shade map and actual map
    """

    pass


def calc_shadow_sum_along_path(path: [(float, float)], polygons: [Polygon]) -> float:
    """
    Calculate the sum of shadow values along the given path.

    :param path: List of 2D geospatial coordinates representing the path.
    :param polygons: List of polygons representing the shaded areas.
    :return: The total shadow value along the path.
    """
    
    # Create a LineString from the path
    path_line = LineString(path)
    
    total_shadow_value = 0.0

    # Iterate over each polygon
    for poly in polygons:
        # Check if the path intersects with the polygon
        if path_line.intersects(poly):
            # Find the intersection
            intersection = path_line.intersection(poly)
            # If the intersection is a LineString or MultiLineString, add its length to the total shadow value
            if intersection.is_empty:
                continue
            elif intersection.geom_type == 'LineString':
                total_shadow_value += intersection.length
            elif intersection.geom_type == 'MultiLineString':
                for line in intersection:
                    total_shadow_value += line.length

    return total_shadow_value
