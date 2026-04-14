import pytest
from src.core.map import WorldMap

class MockFaction:
    def __init__(self, c_id: str, x: int, y: int, pop: int):
        self.id = c_id
        self.location_x = x
        self.location_y = y
        self.population = pop
        self.is_alive = True

def test_get_territory_delta():
    # 1. 초기 맵 (10x10)
    world_map = WorldMap(width=10, height=10)
    
    # 2. 초기 팩션 생성
    f1 = MockFaction("faction1", x=2, y=2, pop=100)
    f2 = MockFaction("faction2", x=8, y=8, pop=100)
    factions = [f1, f2]
    
    # 캐시 생성
    prev_territories = world_map.get_territory_data(factions) # type: ignore
    
    # 3. 팩션 변화 적용 (인구 변화)
    f1.population = 1000
    f2.population = 50
    changed_ids = {"faction1", "faction2"}
    
    # 4. delta 리턴
    updated_territories, delta = world_map.get_territory_delta(factions, changed_ids, prev_territories) # type: ignore
    
    # 5. 검증
    # length가 보존되어야 함
    assert len(updated_territories) == 100
    
    # delta 값이 비어있지 않아야 함
    assert len(delta) > 0
    
    # 모든 delta는 이전 캐시와 달라야 반영되는 점 검증
    for d in delta:
        idx = d["index"]
        new_owner = d["owner"]
        assert prev_territories[idx] != new_owner
        assert updated_territories[idx] == new_owner

def test_get_territory_delta_no_changes():
    world_map = WorldMap(width=10, height=10)
    f1 = MockFaction("faction1", x=2, y=2, pop=100)
    factions = [f1]
    
    prev_territories = world_map.get_territory_data(factions) # type: ignore
    
    # 변경 없음
    updated, delta = world_map.get_territory_delta(factions, set(), prev_territories) # type: ignore
    
    assert len(delta) == 0
    assert updated == prev_territories

def test_get_territory_delta_add_faction():
    world_map = WorldMap(width=10, height=10)
    f1 = MockFaction("faction1", x=2, y=2, pop=100)
    factions = [f1]
    
    prev_territories = world_map.get_territory_data(factions) # type: ignore
    
    # 새로운 팩션 추가
    f2 = MockFaction("faction2", x=8, y=8, pop=100)
    factions.append(f2)
    changed_ids = {"faction2"}
    
    updated, delta = world_map.get_territory_delta(factions, changed_ids, prev_territories) # type: ignore
    
    assert len(delta) > 0
    # 변경된 타일은 모두 f2_index인 1과 관련이 있어야 한다 (이전 -1 -> 1)
    for d in delta:
        assert d["owner"] == 1
