import numpy as np
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import split
from typing import List

def calc_shadow_sum_along_path(path: List[tuple[float, float]], polygons: List[Polygon]) -> float:
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
