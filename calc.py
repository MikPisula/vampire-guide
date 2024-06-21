import numpy as np

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