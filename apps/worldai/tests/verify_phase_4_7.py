import sys
from pathlib import Path

# Add project root to path
_ROOT = Path(__file__).parent.parent  # apps/worldai
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.core.world import World
from src.core.faction_manager import FactionManager
from src.core.map import TileType

def test_map_generation():
    print("--- Testing Map Generation ---")
    world = World.from_config("asteria")
    world_map = world.map
    print(f"Map Size: {world_map.width}x{world_map.height}")
    
    # Check biomes at different latitudes
    north_tile = world_map.get_tile(50, 5)
    central_tile = world_map.get_tile(50, 40)
    south_tile = world_map.get_tile(50, 75)
    
    print(f"North (50, 5) type: {north_tile.tile_type.display()}")
    print(f"Central (50, 40) type: {central_tile.tile_type.display()}")
    print(f"South (50, 75) type: {south_tile.tile_type.display()}")
    
    summary = world_map.to_summary_dict()
    print(f"Summary data length: {len(summary['data'])}")
    assert len(summary['data']) == 100 * 80
    print("✅ Map Generation OK")

def test_population_segments():
    print("\n--- Testing Population Segments ---")
    fm = FactionManager()
    f = fm.create_faction(
        "test_f", "Test Faction", "human", "central", 
        population=1000, location=(50, 40)
    )
    
    print(f"Faction Population: {f.population}")
    print(f"Segments Count: {len(f.population_segments)}")
    for s in f.population_segments:
        print(f"  - {s.pop_type.display()}: {int(s.count)}")
        
    assert f.population == 1000
    print("✅ Population Segments OK")

def test_migration():
    print("\n--- Testing Migration ---")
    world = World.from_config("asteria")
    fm = FactionManager()
    
    # Create two nearby factions
    f1 = fm.create_faction("f1", "City A", "human", "central", 1000, location=(50, 40))
    f2 = fm.create_faction("f2", "Village B", "human", "central", 100, location=(52, 42))
    
    initial_f1 = f1.population
    initial_f2 = f2.population
    
    # Run a tick
    fm.tick(lambda r: 1.0, 1.0, 1, world_map=world.map)
    
    print(f"F1 population: {initial_f1} -> {f1.population}")
    print(f"F2 population: {initial_f2} -> {f2.population}")
    
    # Total population should be preserved (migration only)
    assert abs((f1.population + f2.population) - (initial_f1 + initial_f2)) < 0.1
    print("✅ Migration OK")

if __name__ == "__main__":
    try:
        test_map_generation()
        test_population_segments()
        test_migration()
        print("\n🎉 All Verification Tests Passed!")
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
