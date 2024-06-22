import osmnx as ox
import folium
import haversine as hs # geocords to meters 
import mpire
import multiprocessing as mp

start_location = (40.748817, -73.985428)  # Example: New York (Latitude, Longitude)
end_location = (40.730610, -73.935242)    # Example: New York (Latitude, Longitude)

margin = 0.1

search_radius = 1000 * (margin + 1) * hs.haversine(start_location, end_location) / 2
print(search_radius)

# Download the street network for the area
G = ox.graph_from_point(start_location, dist=5000, network_type='walk')

# Get the nearest nodes to the start and end points
orig_node = ox.distance.nearest_nodes(G, start_location[1], start_location[0])
dest_node = ox.distance.nearest_nodes(G, end_location[1], end_location[0])

# Calculate the shortest path
shortest_path = ox.shortest_path(G, orig_node, dest_node, weight='length')

print("Found shortest path!")

midpoint = ((start_location[0] + end_location[0]) / 2, (start_location[1] + end_location[1]) / 2)
m = folium.Map(location=midpoint, zoom_start=13, tiles="OpenStreetMap")

# Plot the route on the map
route_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in shortest_path]
folium.PolyLine(route_coords, color='blue', weight=5, opacity=0.7).add_to(m)

# Add start and end markers
folium.Marker(location=start_location, popup='Start', icon=folium.Icon(color='green')).add_to(m)
folium.Marker(location=end_location, popup='End', icon=folium.Icon(color='red')).add_to(m)

def handle_node(poly_q: mp.SimpleQueue, node_y: float, node_x: float) -> None:
    buildings = ox.features_from_point((node_y, node_x), {"building": True}, 50)

    for geometry in buildings['geometry']:
        if not hasattr(geometry, 'exterior'):
            continue
        inverted_coords = tuple((y, x) for x, y in geometry.exterior.coords)
        poly_q.put(inverted_coords)

class StopProcessing:
    pass

def add_polygons_to_map(poly_q: mp.SimpleQueue) -> None:
    while True:
        inverted_coords = poly_q.get()
        if isinstance(inverted_coords, StopProcessing):
            break
        folium.Polygon(inverted_coords).add_to(m)


with mpire.WorkerPool(pass_worker_id=False) as pool:
    poly_q = mp.SimpleQueue()
    pool.set_shared_objects(poly_q)
    polys_process = mp.Process(target=add_polygons_to_map, args=(poly_q,))
    polys_process.start()
    pool.map_unordered(handle_node, route_coords, progress_bar=True)
    poly_q.put(StopProcessing())
    poly_q.close()
    polys_process.join()
    
# Save the map to an HTML file
m.save('shortest_path_map.html')
