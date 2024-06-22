import osmnx as ox
from datetime import datetime, timedelta
import pathlib
import networkx as nx
from typing import Dict
import igraph

import geopandas as gpd

from tqdm import tqdm

from quadtree_buildings import PolygonQuery
from calculate_polygon_shade import calculate_polygon_shade

from shapely.geometry import Polygon, LineString

def generate_times() -> list[str]:
    """
        Returns ["1 09:00", "1 10:00", ..., "12 18:00", "12 19:00"]
    """

    # Define start and end times
    start_time = datetime.strptime('09:00', '%H:%M')
    end_time = datetime.strptime('19:00', '%H:%M')

    # Generate list of time strings for 10 hours (from 9:00 to 19:00)
    time_stages = [(start_time + timedelta(hours=h)).strftime('%H:%M') for h in range(10)]

    # Define months
    months = list(range(1, 13))

    # Generate list of time stages for each month
    time_stages_per_month = [f"{month} {time}" for month in months for time in time_stages]
    
    return time_stages_per_month

TIMES = generate_times()

class PrecomputedPathfinder:
    """
    Class for precomputing and storing pathfinding data for a given city.

    Contains an ig.graph for each time of day and month of the year (9:00 - 19:00).

    We differentiate between primary graph and a list of igraphs.
    - The primary graph is the graph that is downloaded from OSM and saved as a graphml file.
    - The list of igraphs is a dictionary of igraphs for each time of day and month of the year.

    NOTE: Loading the Primary Graph of Gdansk takes around 25s.
    
    """
    
    def __init__(self, city_name, verbose = True):
        self.verbose = verbose
        self.city_name = city_name

        print("Loading Polygon Query module...")
        csv_name = f'data/buildings_{city_name}_clean.csv'
        self.qtb = PolygonQuery(csv_name)
        print("Polygon Query module loaded.")

        self.graphs = self._create_graph(city_name)
        self.was_loaded = False


    def _create_graph(self, city_name):
        """
            Downloads or loads the graph for the given city.

            If it is downloaded, it is modified to create a dictionary of igraphs 
            for each time of day and month of the year.
        """
        
        graph_path = f"data/{city_name}.graphml"
        modified_graph_path = f"data/{city_name}_modified/"
        # TEMP_graph_path = f"data/{city_name}_TEMP.graphml"
        start_time = datetime.now()
        if not pathlib.Path(modified_graph_path).exists():

            graph = None
            if pathlib.Path(graph_path).exists():
                print("Primary graph already exists, loading...")
                graph = ox.load_graphml(filepath=graph_path)
                print("Primary graph loaded.")
            else:
                print("Downloading primary graph...")
                graph = ox.graph_from_place(city_name, network_type='walk')
                print("Primary graph downloaded.")

            # # TEMPORARY!!! 
            # ox.save_graphml(graph, filepath=TEMP_graph_path)

            # Change the graph to a dictionary of igraphs for each time of day and month of the year
            graphs = self._modify_graph(graph)

            for time, graph in tqdm(graphs.items()):
                graph.save(f"{modified_graph_path}{time}.graphml")
                print(f"Graph for {time} saved.")

        else:
            
            for time in tqdm(TIMES):
                print(f"Loading graph for {time}...")

                specific_time_graph_path = f"{modified_graph_path}{time}.graphml" 

                graph = ox.load_graphml(filepath=specific_time_graph_path)

                print(f"Graph for {time} loaded.")

            graph = ox.load_graphml(filepath=modified_graph_path)
            self.was_loaded = True
            end_time = datetime.now()
            print("Dict of graphs loaded in:", end_time - start_time, "s")

        end_time = datetime.now()
        print("Graph loaded/downloaded in", end_time - start_time, "s")
        return graph

    def _modify_graph(self, graph: nx.MultiDiGraph) -> Dict[str, igraph.Graph]:
        """
            Modifies the graph to create a dictionary of igraphs 
            for each time of day and month of the year.
        """

        graphs = {}
        for time in tqdm(TIMES):
            edges = [
                (u, v, self._calculate_edge(graph.nodes[u], graph.nodes[v], time))
                for u, v, k, data in graph.edges(data=True, keys=True)
            ]
            graphs[time] = igraph.Graph.TupleList(edges=edges, directed=False)
        return graphs

    def _calculate_edge(self, start, end, time) -> float:
        """
        Calculates the value of the edge for a given time.

        For now it is only the proportion of the edge that is in the shade.

        """

        x1, y1 = start['x'], start['y']
        x2, y2 = end['x'], end['y']

        proportion_in_shade = 0

        potential_polygons = self.qtb.query(x1, y1, x2, y2)
        if potential_polygons == []:
            proportion_in_shade = 0
        else: 
            print(len(potential_polygons))
            potential_polygons_geometries = gpd.GeoSeries(potential_polygons)
            potential_polygons_gdf        = gpd.GeoDataFrame(
                                                geometry=potential_polygons_geometries, 
                                                # crs='EPSG:4326'
                                                )
            potential_polygons_gdf        = potential_polygons_gdf.set_geometry('geometry')

            list_of_shades = calculate_polygon_shade(potential_polygons_gdf, time)

            for shade in list_of_shades:
                line = LineString([(x1, y1), (x2, y2)])
                intersection: float = shade.intersection(line).length
                proportion_in_shade += intersection / line.length

        return proportion_in_shade

    def find_path(self, start, end):
        """
        Finds the path between two points using the precomputed data.
        """

        # TODO

        return None


def test():
    city_name = "gdansk"
    pathfinder = PrecomputedPathfinder(city_name)

    # Example start and end points
    start = "Brama Wyżynna, Wały Jagiellońskie 2A, 80-887 Gdańsk"
    end = "Museum of the Second World War, plac Władysława Bartoszewskiego 1, 80-862 Gdańsk"

    # Find path
    path = pathfinder.find_path(start, end)
    print("Path found:", path)

# Example usage for Gdansk
if __name__ == '__main__':
    test()
