import sys
sys.path.insert(0, 'apps/worldai')
from src.core.models import DayPhase, PopulationType, PopulationSegment, TimeConfig, SettlementScale

# TimeConfig 테스트
tc = TimeConfig()
print(f"[TimeConfig] {tc}")
print(f"  ticks_per_day={tc.ticks_per_day}, season={tc.ticks_per_season}, year={tc.ticks_per_year}")

# DayPhase 테스트
for h in [2, 5, 12, 18, 22]:
    phase = DayPhase.from_hour(h)
    print(f"  {h:02d}:00 -> {phase.display()}")

# PopulationSegment 분배 테스트
segs = PopulationSegment.distribute(10000, SettlementScale.EMPIRE)
print("[인구 분배] 제국 10000명:")
for s in segs:
    print(f"  {s.pop_type.display():6}: {int(s.count):,}명 (이동={s.can_travel})")

# World 시간 시스템 테스트
from src.core.world import World, get_race_phase_modifier
world = World.from_config("asteria")
world.tick = 17  # 17:00 황혼
print(f"[World] Tick={world.tick}, 시각={world.hour_of_day}시, Phase={world.day_phase.display()}, 낮={world.is_daytime}")
mod = get_race_phase_modifier("undead", world.day_phase)
print(f"  언데드 활성도: {mod}")

world.tick = 2   # 02:00 깊은 밤
print(f"[World] Tick={world.tick}, 시각={world.hour_of_day}시, Phase={world.day_phase.display()}")
un = get_race_phase_modifier("undead", world.day_phase)
hu = get_race_phase_modifier("human", world.day_phase)
print(f"  언데드 활성도: {un} (최강)")
print(f"  인간 활성도:   {hu} (최약)")
