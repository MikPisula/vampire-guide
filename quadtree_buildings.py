import csv
import tempfile

import numpy as np
from scipy.spatial import KDTree

from shapely.geometry import box, Polygon
from shapely import wkt

import geopandas as gpd
import time

class PolygonQuery:
    def __init__(self, csv_file):
        self.polygons: list[Polygon] = []
        self.midpoints = []
        self.load_polygons(csv_file)
        self.kdtree = KDTree(self.midpoints)

    def load_polygons(self, csv_file):
        with open(csv_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            polygon_column = None
            # Skip the header, remember the Polygon column
            for i, row in enumerate(reader):
                if i == 0:
                    polygon_column = row.index('geometry')
                    continue
                polygon_str = row[polygon_column]
                polygon = wkt.loads(polygon_str)

                self.polygons.append(polygon)
                self.midpoints.append(polygon.centroid.coords[0])

    def query(self, minx, miny, maxx, maxy, 
              search_margin=0.1) -> list[Polygon]:

        query_box = box(minx * (1 + search_margin), 
                        miny * (1 + search_margin), 
                        maxx * (1 + search_margin), 
                        maxy * (1 + search_margin))
        
        midpoints_in_box = self.kdtree.query_ball_point([(minx + maxx) / 2, (miny + maxy) / 2], 
                                                        max(maxx - minx, maxy - miny) / 2)
        result_polygons = [self.polygons[i] for i in midpoints_in_box if query_box.intersects(self.polygons[i])]
        return result_polygons

def test(ntests = 100, test_on_gdansk = True):

    exec_times = []

    import tqdm

    with tempfile.NamedTemporaryFile(delete=False, mode='w', newline='') as temp_csv:

            buildings = None
            buildings_name = None
            if test_on_gdansk:
                # Gdansk is already in .csv format
                # buildings = gpd.read_file('data/buildings_gdansk.csv')
                buildings_name = 'data/buildings_gdansk.csv'
            else: 
                # Load buildings data and write to the temporary .csv file
                buildings = gpd.read_file('data/buildings_suzhou.json')
                buildings.to_csv(temp_csv.name)
                buildings_name = temp_csv.name

            # Load the polygons from the .csv file
            polygon_query = PolygonQuery(buildings_name)

            for i in tqdm.tqdm(range(ntests)):
                # Create a temporary .csv file

                # Find a random rectangle to query based on polygons
                two_random_polygons = np.random.choice(polygon_query.polygons, 2)

                minx = min([p.bounds[0] for p in two_random_polygons])
                miny = min([p.bounds[1] for p in two_random_polygons])
                maxx = max([p.bounds[2] for p in two_random_polygons])
                maxy = max([p.bounds[3] for p in two_random_polygons])

                # Query the polygons
                start_time = time.time()
                result = polygon_query.query(minx, miny, maxx, maxy)
                end_time = time.time()
                execution_time = end_time - start_time
                # print("Execution time:", execution_time, "seconds")

                exec_times.append(execution_time)

                if i == ntests - 1:
                    # Visualize the found polygons in red, the original polygons in blue
                    import matplotlib.pyplot as plt
                    ax = gpd.GeoSeries(polygon_query.polygons).plot(color='blue')
                    gpd.GeoSeries(result).plot(ax=ax, color='red')
                    ax.set_title(f'Query result, last test. Avg time: {sum(exec_times) / ntests:.5f} seconds')
                    ax.set_axis_off()
                    
                    # Add start and end coordinates to the plot
                    ax.annotate(f"Start: ({minx}, {miny})", xy=(minx, miny), xytext=(minx, miny-0.1), color='black')
                    ax.annotate(f"End: ({maxx}, {maxy})", xy=(maxx, maxy), xytext=(maxx, maxy+0.1), color='black')
                    
                    plt.show()

if __name__ == "__main__":
    test()
