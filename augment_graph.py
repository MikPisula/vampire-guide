import shapely
import networkx as nx

def add_intersection_length(G: nx.MultiDiGraph, polys: shapely.MultiPolygon, attr: str) -> None:
    for u, v, k, data in list(G.edges(keys=True, data=True)):
        if "geometry" not in data:
            continue
        edge_geom = data["geometry"]

        if "length" not in data:
            continue
        length = data["length"]

        intersection = edge_geom.intersection(polys)
        G.edges[u, v, k][attr] = length - shapely.length(intersection)

def test():
    shadows = shapely.MultiPolygon([shapely.geometry.box(0, 0, 1, 1)])
    G = nx.MultiDiGraph()
    line = shapely.geometry.LineString([(0, -1), (0, 0), (1, 1), (0.5, 0.3), (2, 2), (0.2, 0.7)])
    G.add_edge(0, 1, geometry=line, length=line.length)
    add_intersection_length(G, shadows, 'sun_length')
    print(G.edges(data=True))


if __name__ == '__main__':
    test()
