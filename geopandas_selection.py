import osmnx as ox
import folium

m = folium.Map(zoom_start=13, tiles="OpenStreetMap")

buildings = ox.features_from_place("Gdańsk, Poland", { "building": True })

import time

start = time.time()
wtf = buildings.cx[:, :54.3]['geometry']
end = time.time()

print(f"Execution time: {end - start:.3f} seconds")

for geometry in wtf:
    try:
        coords = tuple(geometry.exterior.coords)
        inverted_coords = tuple((y, x) for x, y in coords)
        
        folium.Polygon(inverted_coords).add_to(m)
        
    except Exception as e:
        print(e)

m.save('shortest_path_map.html')
