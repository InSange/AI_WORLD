from __future__ import annotations
import random
import opensimplex  # type: ignore[import-untyped]
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Any, TYPE_CHECKING
if TYPE_CHECKING:
    from .faction_manager import Faction

class TileType(str, Enum):
    WATER = "water"         # 0: 파란색 (West/South Hub)
    PLAINS = "plains"       # 1: 연두색 (Center Hub)
    FOREST = "forest"       # 2: 짙은 초록색 (East/Center)
    MOUNTAIN = "mountain"   # 3: 어두운 회색 (North/East)
    SNOW = "snow"           # 4: 흰색 (North Hub)
    DESERT = "desert"       # 5: 황토색
    WASTELAND = "wasteland" # 6: 갈색
    LAKE = "lake"           # 7: 강/호수

    def display(self) -> str:
        labels = {
            "snow": "설원", "plains": "평원",
            "forest": "숲", "mountain": "산맥", "water": "바다",
            "desert": "사막", "wasteland": "황무지",
            "lake": "호수/강"
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
    def __init__(self, width: int = 200, height: int = 200, unexplored_borders: Optional[dict[str, bool]] = None):
        self.width = width
        self.height = height
        self.unexplored_borders = unexplored_borders or {"north": True, "south": False, "east": False, "west": False}
        self.tiles: list[list[MapTile]] = []
        self.seed = random.randint(0, 1000000)
        opensimplex.seed(self.seed)
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
        """opensimplex 기반 자연 대륙 (Biome Matrix) 엔진"""
        nx, ny = x / self.width, y / self.height
        
        # 1. 미개척지가 아닌 가장자리(경계)를 물리적 바다로 강제 깎아내림 (3면 바다 등)
        edge_thick = 0.02
        # 경계선이 칼로 자른듯하지 않도록 노이즈 오프셋 추가
        border_noise = opensimplex.noise2(x * 0.1, y * 0.1) * 0.015
        
        if not self.unexplored_borders.get("west", False) and nx < edge_thick + border_noise:
            return TileType.WATER
        if not self.unexplored_borders.get("east", False) and nx > 1.0 - edge_thick + border_noise:
            return TileType.WATER
        if not self.unexplored_borders.get("north", False) and ny < edge_thick + border_noise:
            return TileType.WATER
        if not self.unexplored_borders.get("south", False) and ny > 1.0 - edge_thick + border_noise:
            return TileType.WATER

        # 맵 규모(200x200)에 맞춘 주파수 세팅
        scale_t = 0.03
        scale_e = 0.04
        scale_m = 0.04
        
        # 2. 온도 (Temperature: 0.0 ~ 1.0)
        # 북쪽은 춥고 남쪽은 덥게 베이스 설정 후 노이즈를 크게 적용해 랜덤 스팟 생성
        base_temp = ny
        n_temp = opensimplex.noise2(x * scale_t, y * scale_t)
        temp = max(0.0, min(1.0, base_temp + n_temp * 0.35))
        
        # 3. 습도 (Moisture: 노이즈 자체, 0.0 ~ 1.0)
        # 숲, 평원, 사막을 가르는 기준점
        n_moisture = opensimplex.noise2(x * scale_m + 500, y * scale_m - 500)
        moisture = (n_moisture + 1.0) / 2.0
        
        # 4. 고도 (Elevation)
        # 중앙이 높고 가장자리가 낮아지는 형태 (반도 베이스)
        dist_x_from_center = abs(nx - 0.5) * 2.0
        dist_y_south_penalty = max(0.0, (ny - 0.80) * 5.0) if not self.unexplored_borders.get("south", False) else 0.0
        base_elev = 1.0 - (dist_x_from_center ** 1.8) - dist_y_south_penalty
        
        # 북쪽 미개척지는 고육지 부스트
        if self.unexplored_borders.get("north", True) and ny < 0.2:
            base_elev += (0.2 - ny) * 5.0
            
        # 고도 노이즈의 영향력을 크게(+0.5) 주어 대륙 곳곳에 간헐적인 산맥이 형성되도록 유도
        n_elev = opensimplex.noise2(x * scale_e + 1000, y * scale_e + 1000)
        elevation = base_elev + n_elev * 0.5
        
        # 5. 해안선 판정 (Water)
        if elevation < 0.15:
            return TileType.WATER
            
        # 6. 강/호수 (Lake) - 아주 깊숙한 내륙 특정 포인트
        lake_n = opensimplex.noise2(x * 0.08 + 2000, y * 0.08 + 2000)
        if lake_n > 0.8 and elevation < 0.8 and temp > 0.1:
            return TileType.LAKE
            
        # 7. 산맥 (Mountain) 판정
        # 기온과 관계 없이 고도가 1.25 이상이면 무조건 산맥! (어느 지방이든 발생 가능)
        # 단, 맵의 정중앙 평원(0.3~0.7) 부분은 평야가 돋보이게 산맥 등장 기준치를 높임
        mountain_threshold = 1.35 if (0.3 < nx < 0.7 and 0.3 < ny < 0.7) else 1.25
        if elevation > mountain_threshold:
            return TileType.MOUNTAIN
            
        # 8. 바이옴 분배 (온도 x 습도 기반 유기적 렌더링)
        if temp < 0.25:
            # 북부 전체를 설원(Snow)으로 통일 (온도/툰드라 세부 시스템은 나중에 도입)
            return TileType.SNOW
            
        elif temp > 0.65:
            # 더운 기후 (사막과 황무지 위주)
            # 알록달록함을 줄이기 위해 열대 지형(Tropical)을 삭제!
            # 아주 건조하면 사막, 약간 건조하면 황무지, 습도가 높으면 오히려 주변과 어울리는 '평원(Plains)'으로 처리.
            if moisture < 0.45:
                return TileType.DESERT
            elif moisture < 0.70:
                return TileType.WASTELAND
            else:
                return TileType.PLAINS
            
        else:
            # 온대 기후 (중앙 대평원 베이스)
            # 사용자의 피드백 1: 동/서 쪽에 울창한 숲 비중 버프
            # 사용자의 피드백 2: 칼로 자른듯한 일직선(x > 0.7)을 없애기 위해 습도에 완만한 그라데이션 가중치 부여
            m_boost = 0.0
            if nx > 0.6:
                m_boost = (nx - 0.6) * 0.6  # 동쪽으로 갈수록 천천히 습해짐 (최대 +0.24)
            if nx < 0.4:
                m_boost = (0.4 - nx) * 0.6  # 서쪽으로 갈수록 천천히 습해짐 (최대 +0.24)
            
            final_moisture = moisture + m_boost
            
            if final_moisture > 0.55:
                return TileType.FOREST
            else:
                return TileType.PLAINS

    def get_tile(self, x: int, y: int) -> Optional[MapTile]:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None

    def find_suitable_location(self, preferred_biomes: list[str], occupied_spots: Optional[list[tuple[int, int]]] = None, min_dist: float = 10.0) -> tuple[int, int]:
        """
        선호하는 군계(Biome) 목록 중 하나에 해당하는 타일을 무작위로 찾아 반환한다.
        찾지 못하면 점진적으로 아무 육지나 반환하며, 기존 스폰들과 겹치지 않도록 min_dist 거리를 유지하려 시도.
        """
        import random
        occupied = occupied_spots or []
        
        # 1. 선호 군계를 만족하는 후보군 수집
        candidates = []
        fallback_candidates = [] # 바다/호수가 아닌 모든 육지
        
        for y in range(self.height):
            for x in range(self.width):
                t = self.get_tile(x, y)
                if not t:
                    continue
                # बा다/호수는 수중 종족 지정이 없으면 기본 스폰 금지
                is_water = t.tile_type.value in ("water", "lake")
                if is_water and t.tile_type.value not in preferred_biomes:
                    continue
                    
                fallback_candidates.append((x, y))
                
                if t.tile_type.value in preferred_biomes:
                    candidates.append((x, y))
                    
        def get_best_spot(spots):
            if not spots:
                return None
            # 랜덤 셔플 후 거리체크
            random.shuffle(spots)
            for sx, sy in spots:
                # 다른 occupied와의 거리가 통과하는지 확인
                too_close = False
                for ox, oy in occupied:
                    dist = ((sx - ox)**2 + (sy - oy)**2)**0.5
                    if dist < min_dist:
                        too_close = True
                        break
                if not too_close:
                    return (sx, sy)
            # 조건부 통과 못하면 그냥 아무거나 첫번째 리턴 (공간 부족)
            return spots[0]
            
        best = get_best_spot(candidates)
        if best:
            return best
        
        # 2. 선호 군계를 못 찾으면 차선책(아무 육지)에서 거리가 있는 곳
        best_fallback = get_best_spot(fallback_candidates)
        if best_fallback:
            return best_fallback
        
        # 3. 정 안되면 그냥 정중앙 부근 리턴
        return (self.width // 2, self.height // 2)

    def set_occupancy(self, x: int, y: int, faction_id: str) -> None:
        tile = self.get_tile(x, y)
        if tile:
            tile.faction_id = faction_id

    def to_summary_dict(self, factions: Optional[list["Faction"]] = None) -> dict[str, Any]:
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
        영향력 기반 영토 지도를 생성한다. (전체 재계산 — 초기 로드 또는 강제 리프레시용)
        - 영향력 = pop^0.4 * 10 / (dist² + 1)
        - 반환값: Faction 리스트에서의 인덱스 (소유주 없으면 -1)
        틱당 호출은 get_territory_delta() 를 사용할 것.
        """
        territories = [-1] * (self.width * self.height)
        if not factions:
            return territories

        faction_infos = [
            (i, f.location_x, f.location_y, f.population)
            for i, f in enumerate(factions) if f.is_alive
        ]

        for y in range(self.height):
            for x in range(self.width):
                max_influence = 0.0
                owner_idx = -1
                for idx, fx, fy, pop in faction_infos:
                    dist_sq = (x - fx)**2 + (y - fy)**2
                    influence = 999999.0 if dist_sq == 0 else ((pop ** 0.4) * 10.0) / (dist_sq + 1.0)
                    if influence > max_influence:
                        max_influence = influence
                        owner_idx = idx
                if max_influence > 0.5:
                    territories[y * self.width + x] = owner_idx

        return territories

    def get_territory_delta(
        self,
        factions: list["Faction"],
        changed_faction_ids: set[str],
        prev_territories: list[int],
    ) -> tuple[list[int], list[dict]]:
        """
        [Dirty Region] 변경된 파벌 주변 타일만 재계산한다.

        전체 40,000타일을 순회하는 대신, 인구 변화가 발생한 파벌의
        영향 반경(r = pop^0.4 * 10^0.5 ≈ 영향력이 0.5 문턱 이하가 되는 거리)
        내부 타일만 dirty 마킹하여 재계산함.

        Args:
            factions: 전체 파벌 리스트
            changed_faction_ids: 이번 틱에 인구·위치 변화가 있었던 파벌 ID 집합
            prev_territories: 직전 틱 territories 배열 (캐시)

        Returns:
            (updated_territories, delta)
            - updated_territories: 갱신된 전체 territories 배열 (캐시 교체용)
            - delta: [{"index": int, "owner": int}, ...] — 변경된 타일만
        """
        if not changed_faction_ids or not prev_territories:
            return prev_territories, []

        faction_infos = [
            (i, f.location_x, f.location_y, f.population)
            for i, f in enumerate(factions) if f.is_alive
        ]
        faction_id_to_idx = {f.id: i for i, f in enumerate(factions)}

        # dirty 타일 좌표 수집 — 변경된 파벌의 영향 반경 bounding box만
        dirty_coords: set[tuple[int, int]] = set()
        for fid in changed_faction_ids:
            idx = faction_id_to_idx.get(fid)
            if idx is None:
                continue
            f = factions[idx]
            if not f.is_alive:
                continue
            radius = max(10, int((f.population ** 0.4) * (10.0 ** 0.5)) + 2)
            x0 = max(0, f.location_x - radius)
            x1 = min(self.width - 1, f.location_x + radius)
            y0 = max(0, f.location_y - radius)
            y1 = min(self.height - 1, f.location_y + radius)
            for dy in range(y0, y1 + 1):
                for dx in range(x0, x1 + 1):
                    dirty_coords.add((dx, dy))

        # dirty 타일만 영향력 재계산
        updated = list(prev_territories)
        delta: list[dict] = []

        for (x, y) in dirty_coords:
            max_influence = 0.0
            owner_idx = -1
            for i, fx, fy, pop in faction_infos:
                dist_sq = (x - fx)**2 + (y - fy)**2
                influence = 999999.0 if dist_sq == 0 else ((pop ** 0.4) * 10.0) / (dist_sq + 1.0)
                if influence > max_influence:
                    max_influence = influence
                    owner_idx = i
            new_owner = owner_idx if max_influence > 0.5 else -1
            tile_idx = y * self.width + x
            if updated[tile_idx] != new_owner:
                updated[tile_idx] = new_owner
                delta.append({"index": tile_idx, "owner": new_owner})

        return updated, delta
