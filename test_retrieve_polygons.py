import time

# Generate tests for the test function
start_location = (40.748817, -73.985428)  # New York (Latitude, Longitude)
end_location = (40.730610, -73.935242)    # New York (Latitude, Longitude)

start_time = time.time()
polygons = retrieve_route_polygons(start_location, end_location)
end_time = time.time()

execution_time = end_time - start_time

print(f"Execution time: {execution_time} seconds")
for poly in polygons:
    print(poly)