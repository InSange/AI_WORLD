from __future__ import annotations
import random
import math
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Any

class TileType(str, Enum):
    SNOW = "snow"           # 설원 (North Extreme)
    TUNDRA = "tundra"       # 툰드라 (North Transition)
    PLAINS = "plains"       # 평원 (Central)
    FOREST = "forest"       # 숲 (Central)
    MOUNTAIN = "mountain"   # 산맥 (Random scattered)
    WATER = "water"         # 강/호수/해안
    DESERT = "desert"       # 사막 (South Extreme)
    WASTELAND = "wasteland" # 황무지 (South Transition)
    TROPICAL = "tropical"   # 열대 우림 (South Extreme)

    def display(self) -> str:
        labels = {
            "snow": "설원", "tundra": "툰드라", "plains": "평원",
            "forest": "숲", "mountain": "산맥", "water": "물",
            "desert": "사막", "wasteland": "황무지", "tropical": "열대"
        }
        return labels.get(self.value, self.value)

@dataclass
class MapTile:
    x: int
    y: int
    tile_type: TileType
    faction_id: Optional[str] = None
    population_density: float = 0.0  # 해당 타일의 인구 밀집도 표시용

class WorldMap:
    def __init__(self, width: int = 100, height: int = 80):
        self.width = width
        self.height = height
        self.tiles: list[list[MapTile]] = []
        self.generate_terrain()

    def generate_terrain(self) -> None:
        """위도(Y)에 따른 점진적 지형 생성"""
        self.tiles = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                tile_type = self._determine_tile_type(x, y)
                row.append(MapTile(x=x, y=y, tile_type=tile_type))
            self.tiles.append(row)

    def _determine_tile_type(self, x: int, y: int) -> TileType:
        """위도 기반 지형 결정 로직"""
        # 0 ~ 80 사이의 상대적 위치 (0: 북쪽 끝, 1: 남쪽 끝)
        lat = y / self.height
        rand = random.random()

        # 1. 산맥 및 물은 확률적으로 전체에 분포 (단, 중앙 평원에 강이 더 많음)
        if random.random() < 0.05: return TileType.MOUNTAIN
        if random.random() < 0.03: return TileType.WATER

        # 2. 권역별 지형 (위도 기반)
        
        # 북부 (0% ~ 25%) - 설원/툰드라
        if lat < 0.25:
            # 북쪽 끝일수록 설원 확률 높음
            snow_prob = 1.0 - (lat / 0.25)  # 0->1.0, 0.25->0.0
            if rand < snow_prob * 0.8: return TileType.SNOW
            if rand < 0.7: return TileType.TUNDRA
            return TileType.PLAINS  # 남하하면서 평원 섞임

        # 중앙 (25% ~ 65%) - 평원/숲
        elif lat < 0.65:
            # 숲/평원 혼합
            if rand < 0.4: return TileType.FOREST
            if rand < 0.1: return TileType.WATER # 강/호수
            # 북쪽 접경 (툰드라 섞임)
            if lat < 0.35 and rand > 0.8: return TileType.TUNDRA
            # 남쪽 접경 (황무지 섞임)
            if lat > 0.55 and rand > 0.8: return TileType.WASTELAND
            return TileType.PLAINS

        # 남부 (65% ~ 100%) - 사막/황무지/열대
        else:
            # 남쪽 끝일수록 사막/열대 확률 높음
            south_lat = (lat - 0.65) / 0.35 # 0.65->0.0, 1.0->1.0
            if rand < south_lat * 0.4: return TileType.DESERT
            if rand < south_lat * 0.3: return TileType.TROPICAL
            if rand < 0.6: return TileType.WASTELAND
            return TileType.PLAINS # 북상하면서 평원 섞임

    def get_tile(self, x: int, y: int) -> Optional[MapTile]:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None

    def set_occupancy(self, x: int, y: int, faction_id: str) -> None:
        tile = self.get_tile(x, y)
        if tile:
            tile.faction_id = faction_id

    def to_summary_dict(self, factions: list["Faction"] = None) -> dict[str, Any]:
        """대시보드 전송용 압축 데이터 (지형 인덱스 + 영토 인덱스)"""
        type_to_idx = {t.value: i for i, t in enumerate(TileType)}
        flattened_tiles = []
        for row in self.tiles:
            for tile in row:
                flattened_tiles.append(type_to_idx[tile.tile_type.value])
        
        result = {
            "width": self.width,
            "height": self.height,
            "data": flattened_tiles,
            "territories": []
        }

        if factions:
            result["territories"] = self.get_territory_data(factions)

        return result

    def get_territory_data(self, factions: list["Faction"]) -> list[int]:
        """
        영향력 기반 영토 지도를 생성한다.
        - 영향력 = Faction.population / (Distance^2 + 1)
        - 반환값: Faction 리스트에서의 인덱스 (소유주 없으면 -1)
        """
        territories = [-1] * (self.width * self.height)
        if not factions:
            return territories

        # 최적화: 유효한 파별 정보 미리 추출
        faction_infos = [
            (i, f.location_x, f.location_y, f.population)
            for i, f in enumerate(factions) if f.is_alive
        ]

        for y in range(self.height):
            for x in range(self.width):
                max_influence = 0.0
                owner_idx = -1
                
                for idx, fx, fy, pop in faction_infos:
                    # 유클리드 거리 제곱
                    dist_sq = (x - fx)**2 + (y - fy)**2
                    influence = pop / (dist_sq + 1.0)
                    
                    if influence > max_influence:
                        max_influence = influence
                        owner_idx = idx
                
                # 최소 영향력 문턱값 (예: 인구 대비 일정 수준 이상의 영향력이 있어야 영토로 인정)
                if max_influence > 0.5:
                    territories[y * self.width + x] = owner_idx

        return territories
