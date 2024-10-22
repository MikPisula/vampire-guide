import osmnx as ox
import folium
import haversine as hs
import shapely
import pandas as pd
import geopandas as gpd

from typing import List

def retrieve_route_polygons(start_location: tuple[float, float], 
                            end_location: tuple[float, float], 
                            search_margin=0.1, 
                            polygon_buffer_dist=50) -> gpd.GeoDataFrame:
    """
        Retrieve building polygons along the route between two locations.

        :param start_location: The starting location (latitude, longitude).
        :param end_location: The ending location (latitude, longitude).
        :param search_margin: The margin to add to the search radius.
        :param polygon_buffer_dist: The buffer distance for building polygons.

        :return: A list of building polygons along the route.

    """

    search_radius = 1000 * (search_margin + 1) * hs.haversine(start_location, end_location) / 2

    # Download the street network for the area
    G = ox.graph_from_point(start_location, dist=search_radius, network_type='walk')

    # Get the nearest nodes to the start and end points
    orig_node = ox.distance.nearest_nodes(G, start_location[1], start_location[0])
    dest_node = ox.distance.nearest_nodes(G, end_location[1], end_location[0])

    # Calculate the shortest path
    shortest_path = ox.shortest_path(G, orig_node, dest_node, weight='length')

    # Extract route coordinates
    route_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in shortest_path]

    # Extract building polygons along the route
    allbldgs: List[gpd.GeoDataFrame] | gpd.GeoDataFrame = []
    for node in route_coords:
        allbldgs.append(ox.features_from_point(node, {"building": True}, polygon_buffer_dist))
    allbldgs = pd.concat(allbldgs)
    allbldgs['height'] = allbldgs['height'].astype(float)
    return allbldgs.loc[:, ["geometry", "height"]]

def test():

    # Example usage:
    start_location = (40.748817, -73.985428)  # New York (Latitude, Longitude)
    end_location = (40.730610, -73.935242)    # New York (Latitude, Longitude)
    
    polygons = retrieve_route_polygons(start_location, end_location)
    for poly in polygons:
        print(poly)

if __name__ == "__main__":
    test()
