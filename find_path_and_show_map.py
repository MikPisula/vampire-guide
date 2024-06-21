import osmnx as ox
import folium

start_location = (40.748817, -73.985428)  # Example: New York (Latitude, Longitude)
end_location = (40.730610, -73.935242)    # Example: New York (Latitude, Longitude)

# Download the street network for the area
G = ox.graph_from_point(start_location, dist=5000, network_type='walk')

# Get the nearest nodes to the start and end points
orig_node = ox.distance.nearest_nodes(G, start_location[1], start_location[0])
dest_node = ox.distance.nearest_nodes(G, end_location[1], end_location[0])

# Calculate the shortest path
shortest_path = ox.shortest_path(G, orig_node, dest_node, weight='length')

midpoint = ((start_location[0] + end_location[0]) / 2, (start_location[1] + end_location[1]) / 2)
m = folium.Map(location=midpoint, zoom_start=13, tiles="OpenStreetMap")

# Plot the route on the map
route_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in shortest_path]
folium.PolyLine(route_coords, color='blue', weight=5, opacity=0.7).add_to(m)

# Add start and end markers
folium.Marker(location=start_location, popup='Start', icon=folium.Icon(color='green')).add_to(m)
folium.Marker(location=end_location, popup='End', icon=folium.Icon(color='red')).add_to(m)

for node in route_coords:
    buildings = ox.features_from_point(node, {"building": True}, 50)

    for geometry in buildings['geometry']:
        try:
            coords = tuple(geometry.exterior.coords)
            inverted_coords = tuple((y, x) for x, y in coords)
            
            folium.Polygon(inverted_coords).add_to(m)
        except Exception as e:
            print(e)
    
# Save the map to an HTML file
m.save('shortest_path_map.html')
