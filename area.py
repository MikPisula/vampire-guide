from calculate_polygon_shade import calculate_polygon_shade
import osmnx as ox
import pandas as pd
import geopandas as gpd
import shapely
from dataclasses import dataclass
import hashlib
import networkx as nx
import json
from typing import Any
from pydantic import BaseModel

from pathlib import Path

CACHE_PATH = Path(".cache")

class Polygon(BaseModel):
    coords: list[tuple[float, float]]
    fill_color: str
    fill_opacity: float

@dataclass
class Area:
    id: str
    start: tuple[float, float]
    end: tuple[float, float]
    buildings: gpd.GeoDataFrame
    routing_network: nx.MultiDiGraph

    def get_buildings(self) -> list[Polygon]:
        return to_polys(self.buildings['geometry'])
    
    @classmethod
    def from_json(cls, data: dict[str, Any], buildings: gpd.GeoDataFrame, routing_network: nx.MultiDiGraph) -> 'Area':
        return cls(data['id'], data['start'], data['end'], buildings, routing_network)

class AreaManager:
    def __init__(self) -> None:
        self.areas: dict[str, Area] = {}

    @staticmethod
    def id(start: tuple[float, float], end=tuple[float, float]) -> str:
        return hashlib.sha3_256(f"{start=}{end=}".encode(encoding="utf-8")).hexdigest()

    def new(self, start: tuple[float, float], end: tuple[float, float]) -> Area:
        id = self.id(start, end)
        if id not in self.areas:
            self.areas[id] = prepare_area(id, start, end)
        return self.areas[id]
    
    def get(self, id: str) -> Area:
        if id not in self.areas:
            self.areas[id] = load_area(id)
        return self.areas[id]

@dataclass
class ShadowArea:
    id: str
    area_id: str
    time: pd.Timestamp
    shadows: gpd.GeoDataFrame

    def __post_init__(self) -> None:
        self.shadows_mp: shapely.MultiPolygon = shapely.union_all(self.shadows['geometry'])

    def get_shadows(self) -> list[Polygon]:
        return to_polys(self.shadows_mp.geoms)
    
    @classmethod
    def from_json(cls, data: dict[str, Any], shadows: gpd.GeoDataFrame) -> 'ShadowArea':
        return cls(data['id'], data['area_id'], pd.Timestamp.fromisoformat(data['time']), shadows)

class ShadowAreaManager:
    def __init__(self) -> None:
        self.shadows: dict[str, ShadowArea] = {}

    @staticmethod
    def id(area_id: str, datetime: pd.Timestamp) -> str:
        return hashlib.sha3_256(f"{area_id=}{datetime=}".encode(encoding="utf-8")).hexdigest()
    
    def new(self, area: Area, datetime: pd.Timestamp) -> ShadowArea:
        id = self.id(area.id, datetime)
        if id not in self.shadows:
            self.shadows[id] = prepare_shadow_area(id, area, datetime)
        return self.shadows[id]
    
    def get(self, id: str) -> ShadowArea:
        if id not in self.shadows:
            self.shadows[id] = load_shadow_area(id)
        return self.shadows[id]


def to_polys(geometry: pd.Series) -> list[Polygon]:
    result = []
    for poly in geometry:
        if not hasattr(poly, 'exterior'):
            continue
        if len(poly.exterior.coords) <= 3:
            continue
    
        inverted_coords = tuple((y, x) for x, y in poly.exterior.coords)
        result.append(Polygon(coords=inverted_coords, fill_color="#bbb", fill_opacity=1))
    return result

def load_area(id: str) -> Area:
    cache_prefix = CACHE_PATH / id[0] / id

    area_meta = json.load(cache_prefix.with_name(f"area_meta_{cache_prefix.name}.json").open())
    buildings = gpd.read_file(cache_prefix.with_name(f"buildings_{cache_prefix.name}.json"))
    routing_network = ox.load_graphml(cache_prefix.with_name(cache_prefix.name + "_network.graphml"), edge_dtypes={'sun_length': float})
    return Area.from_json(area_meta, buildings, routing_network)

def load_shadow_area(id: str) -> ShadowArea:
    cache_prefix = CACHE_PATH / id[0] / id

    shadow_meta = json.load(cache_prefix.with_name(f"shadow_meta_{cache_prefix.name}.json").open())
    shadows = gpd.read_file(cache_prefix.with_name(f"shadows_{cache_prefix.name}.json"))
    return ShadowArea.from_json(shadow_meta, shadows)

def prepare_area(id: str, start: tuple[float, float], end=tuple[float, float]) -> gpd.GeoDataFrame:
    cache_prefix = CACHE_PATH / id[0] / id
    cache_prefix.parent.mkdir(parents=True, exist_ok=True)

    area_path = cache_prefix.with_name(f"area_meta_{cache_prefix.name}.json")
    if area_path.exists():
        area_meta = json.loads(area_path.read_text())
        assert area_meta['start'] == start
        assert area_meta['end'] == end
    else:
        area_meta = {"id": id, "start": start, "end": end}
        json.dump(area_meta, area_path.open("w"))

    buildings_path = cache_prefix.with_name(f"buildings_{cache_prefix.name}.json")
    buildings: gpd.GeoDataFrame
    if buildings_path.exists():
        buildings = gpd.read_file(buildings_path)
    else:
        buildings = ox.features_from_bbox(bbox=(start[0], end[0], start[1], end[1]),
                                                            tags={"building": True})
        buildings = buildings[['geometry', 'height']]
        buildings['height'] = buildings['height'].astype(float)
        buildings['height'] = buildings['height'].fillna(5.0)
        buildings_path.write_text(buildings.to_json())

    routing_network = cache_prefix.with_name(cache_prefix.name + "_network.graphml")
    if routing_network.exists():
        G = ox.load_graphml(routing_network, edge_dtypes={'sun_length': float})
    else:
        G = ox.graph_from_bbox(bbox=(start[0], end[0], start[1], end[1]), network_type='walk')
        ox.save_graphml(G, routing_network)

    return Area(id, start, end, buildings, routing_network)

def prepare_shadow_area(id: str, area: Area, time: pd.Timestamp) -> ShadowArea:
    cache_prefix = CACHE_PATH / id[0] / id
    cache_prefix.parent.mkdir(parents=True, exist_ok=True)

    shadow_path = cache_prefix.with_name(f"shadow_meta_{cache_prefix.name}.json")
    if shadow_path.exists():
        shadow_meta = json.loads(shadow_path.read_text())
        assert shadow_meta['area_id'] == area.id
        assert pd.Timestamp.fromisoformat(shadow_meta['time']) == time
    else:
        shadow_meta = {"id": id, "area_id": area.id, "time": time.isoformat()}
        json.dump(shadow_meta, shadow_path.open("w"))

    shadows_path = cache_prefix.with_name(f"shadows_{cache_prefix.name}.json")
    shadows: gpd.GeoDataFrame
    if shadows_path.exists():
        shadows = gpd.read_file(shadows_path)
    else:
        shadows = calculate_polygon_shade(area.buildings, time)
        shadows_path.write_text(shadows.to_json())

    return ShadowArea(id, area.id, time, shadows)