import pandas as pd
import geopandas as gpd
import pybdshadow
import shapely
from typing import List

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
    shadow_gdf = pybdshadow.bdshadow_sunlight(buildings, date, roof=True, include_building=False)

    # Extract shadow polygons from the GeoDataFrame
    shadows = list(shadow_gdf.geometry)

    return shadows

def test():
    # Load building data
    buildings = gpd.read_file("data/buildings.json")

    # Calculate shadows for a specific date
    shadows = calculate_polygon_shade(buildings, pd.Timestamp("2022-06-21 2:00:00"))
    
    # Visualize the polygons in matplotlib
    import matplotlib.pyplot as plt
    ax = gpd.GeoSeries(shadows).plot()
    ax.set_title("Shadows cast by buildings")
    ax.set_axis_off()
    plt.show()

if __name__ == "__main__":
    test()