from augment_graph import add_intersection_length
from calculate_polygon_shade import calculate_polygon_shade
import osmnx as ox
import pandas as pd
import geopandas as gpd
import folium
import shapely

from pathlib import Path

def test():
    start_location = (40.748817, -73.985428)  # New York (Latitude, Longitude)
    end_location = (40.730610, -73.935242)    # New York (Latitude, Longitude)
    
    midpoint = ((start_location[0] + end_location[0]) / 2, (start_location[1] + end_location[1]) / 2)
    m = folium.Map(location=midpoint, zoom_start=13, tiles="OpenStreetMap")

    buildings_path = Path("data/buildings_dwnld.json")
    if buildings_path.exists():
        buildings = gpd.read_file(buildings_path)
    else:
        buildings: gpd.GeoDataFrame = ox.features_from_bbox(bbox=(start_location[0], end_location[0], start_location[1], end_location[1]), tags={"building": True})
        buildings['height'] = buildings['height'].astype(float)
        buildings['height'] = buildings['height'].fillna(5.0)
        buildings_path.write_text(buildings[['geometry', 'height']].to_json())

    shadows_path = Path("data/shadows.json")
    if shadows_path.exists():
        shadows = gpd.read_file(shadows_path)
        shadows = shapely.MultiPolygon()
    else:
        shadows: shapely.MultiPolygon = shapely.union_all(calculate_polygon_shade(buildings, pd.Timestamp("2022-06-21 14:00:00"))['geometry'])
        print(shadows)
        shadows_path.write_text(gpd.GeoSeries([shadows]).to_json())


    network_path = Path("data/network.graphml")
    if network_path.exists():
        G = ox.load_graphml(network_path, edge_dtypes={'sun_length': float})
    else:
        G = ox.graph_from_bbox(bbox=(start_location[0], end_location[0], start_location[1], end_location[1]), network_type='walk')
        add_intersection_length(G, shadows, 'sun_length')
        ox.save_graphml(G, network_path)
        
    folium.Rectangle(((start_location[0], start_location[1]), (end_location[0], end_location[1])), color='green').add_to(m)
        
    for edge in G.edges:
        folium.PolyLine(((G.nodes[edge[0]]['y'], G.nodes[edge[0]]['x']), (G.nodes[edge[1]]['y'], G.nodes[edge[1]]['x'])), color='red').add_to(m)
        
    # Get the nearest nodes to the start and end points
    orig_node = ox.distance.nearest_nodes(G, start_location[1], start_location[0])
    dest_node = ox.distance.nearest_nodes(G, end_location[1], end_location[0])

    # Calculate the shortest path
    shortest_path = ox.shortest_path(G, orig_node, dest_node, weight='sun_length')
    normal_path = ox.shortest_path(G, orig_node, dest_node, weight='length')

    print("Found shortest path!")
    

    for geometry in buildings['geometry']:
        if not hasattr(geometry, 'exterior'):
            continue
        if len(geometry.exterior.coords) <= 3:
            continue
        
        inverted_coords = tuple((y, x) for x, y in geometry.exterior.coords)
        folium.Polygon(inverted_coords, fill_color="#bbb", weight=0, fill_opacity=1).add_to(m)

    for polygon in list(shadows.geoms):
        try:
            inverted_coords = tuple((y, x) for x, y in polygon.exterior.coords)
            folium.Polygon(inverted_coords, fill_color='black', fill_opacity=0.5, weight=0).add_to(m)
                
        except Exception as e:
            print(e)

    # Plot the route on the map
    route_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in shortest_path]
    folium.PolyLine(route_coords, color='blue', weight=5, opacity=0.7).add_to(m)

    route_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in normal_path]
    folium.PolyLine(route_coords, color='green', weight=5, opacity=0.7).add_to(m)

    # Add start and end markers
    folium.Marker(location=start_location, popup='Start', icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(location=end_location, popup='End', icon=folium.Icon(color='red')).add_to(m)

    m.save("asd.html")



if __name__ == '__main__':
    test()