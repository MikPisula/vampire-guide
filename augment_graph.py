import shapely
import networkx as nx
import functools
import math
import haversine
import itertools

from collections.abc import Callable

def greate_circle_length(line_strings: shapely.MultiLineString) -> float:
    def single_line_str(line_string: shapely.LineString) -> float:
        return sum(haversine.haversine(p1, p2, unit=haversine.Unit.METERS)
                   for p1, p2 in itertools.pairwise(line_string.coords))

    if not hasattr(line_strings, 'geoms'):
        return single_line_str(line_strings)
    
    return sum(single_line_str(line_string) for line_string in line_strings.geoms)

def intersection_len_fun(G: nx.MultiDiGraph, polys: shapely.MultiPolygon, alpha: float = 2, beta: float = 10) -> Callable[[int, int, dict], float]:
    @functools.cache
    def intersection_len_inner(u: int, v: int, edge_geom: shapely.LineString | None, len: float | None) -> float:
        if edge_geom is None:
            edge_geom = shapely.LineString([(G.nodes[u]['x'], G.nodes[u]['y']), (G.nodes[v]['x'], G.nodes[v]['y'])])
        if len is None:
            return float('inf')

        intersection = edge_geom.intersection(polys)
        int_len = greate_circle_length(intersection)
        if int_len < 1e-4:
            int_len = 0
        val = len  + alpha * math.exp((len - int_len) / beta)
        return val
    
    def intersection_len(u: int, v: int, data: dict) -> float:
        res = float('inf')
        for val in data.values():
            edge_geom = val.get("geometry", None)
            length = val.get("length", None)
            res = min(res, intersection_len_inner(u, v, edge_geom, length))
        return res

    return intersection_len

def test():
    shadows = shapely.MultiPolygon([shapely.geometry.box(0, 0, 1, 1)])
    G = nx.MultiDiGraph()
    line = shapely.geometry.LineString([(0, -1), (0, 0), (1, 1), (0.5, 0.3), (2, 2), (0.2, 0.7)])
    G.add_edge(0, 1, geometry=line, length=line.length)
    add_intersection_length(G, shadows, 'sun_length')
    print(G.edges(data=True))


if __name__ == '__main__':
    test()
