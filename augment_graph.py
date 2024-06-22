import shapely
import networkx as nx
import functools
import math

from collections.abc import Callable

def intersection_len_fun(G: nx.MultiDiGraph, polys: shapely.MultiPolygon, alpha: float = 5, beta: float = 5) -> Callable[[int, int, dict], float]:
    @functools.cache
    def intersection_len_inner(u: int, v: int, edge_geom: shapely.LineString | None, len: float | None) -> float:
        if edge_geom is None:
            edge_geom = shapely.LineString([(G.nodes[u]['x'], G.nodes[u]['y']), (G.nodes[v]['x'], G.nodes[v]['y'])])
        if len is None:
            len = edge_geom.length

        intersection = edge_geom.intersection(polys)
        return len  + alpha * math.exp((len - intersection.length) / beta)
    
    def intersection_len(u: int, v: int, data: dict) -> float:
        edge_geom = data.get("geometry", None)
        length = data.get("length", None)
        return intersection_len_inner(u, v, edge_geom, length)

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
