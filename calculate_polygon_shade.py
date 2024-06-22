import pandas as pd
import geopandas as gpd
import pybdshadow
import shapely
from typing import List

from retrieve_polygons import retrieve_route_polygons

def calculate_polygon_shade(buildings: gpd.GeoDataFrame, date: pd.Timestamp) -> List[shapely.geometry.Polygon]:
    """
    Calculate the shadow cast by buildings on the ground at a given time.

    Parameters
    ----------
    buildings : geopandas.GeoDataFrame
        A GeoDataFrame containing building footprints.
    date : pandas.Timestamp
        The date and time at which to calculate shadows.

    Returns
    -------
    shadows : list of shapely.geometry.Polygon
        A list of polygons representing the shadows cast by the buildings.
    """

    # Preprocess the building data
    buildings = pybdshadow.bd_preprocess(buildings)

    # Calculate the shadows
    shadow_gdf = pybdshadow.bdshadow_sunlight(buildings, date, roof=False, include_building=False)
    return shadow_gdf

    # Extract shadow polygons from the GeoDataFrame
    shadows = list(shadow_gdf.geometry)

    return shadows

def test():
    # Load building data
    #buildings = gpd.read_file("data/buildings.json")
    start_location = (40.748817, -73.985428)  # New York (Latitude, Longitude)
    end_location = (40.730610, -73.935242)    # New York (Latitude, Longitude)
    buildings = retrieve_route_polygons(start_location, end_location)
    buildings.to_file("data/buildings_dwnld.json")

    # Calculate shadows for a specific date
    shadows = calculate_polygon_shade(buildings, pd.Timestamp("2022-06-21 14:00:00"))
    # pybdshadow.show_bdshadow(buildings=buildings, shadows=shadows)
    
    # Visualize the polygons in matplotlib
    import matplotlib.pyplot as plt
    ax = gpd.GeoSeries(shadows).plot()
    ax.set_title("Shadows cast by buildings")
    ax.set_axis_off()
    plt.show()

if __name__ == "__main__":
    test()
