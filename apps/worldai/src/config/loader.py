"""
WorldAI Config Loader
======================
YAML 기반 종족·세계관 설정 파일을 자동 탐색·로드한다.
새 YAML 파일 추가만으로 코드 변경 없이 종족/세계관이 자동 인식된다.
"""
from __future__ import annotations

import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any

# configs/ 폴더 절대 경로
_ROOT = Path(__file__).parent.parent.parent  # apps/worldai/
CONFIGS_DIR = _ROOT / "configs"
RACES_DIR = CONFIGS_DIR / "races"
WORLDS_DIR = CONFIGS_DIR / "worlds"


# ──────────────────────────────────────────
# 데이터 모델
# ──────────────────────────────────────────

@dataclass
class DiplomacyDefault:
    target: str
    affinity: float


@dataclass
class SpecialTrait:
    id: str
    name: str
    description: str


@dataclass
class BehaviorProfile:
    aggression: float = 0.5
    expansion_drive: float = 0.5
    alliance_tendency: float = 0.5
    trade_focus: float = 0.5
    isolationism: float = 0.2


@dataclass
class DiplomacyTrait:
    trust_rate: float = 1.0
    grudge_rate: float = 1.0
    memory_duration: int = 300
    betrayal_penalty: float = 20.0


@dataclass
class RaceStats:
    max_population: int
    growth_rate: float
    military_strength: int
    magic_affinity: int
    technology_level: int
    adaptability: int
    lifespan: int


@dataclass
class RaceConfig:
    id: str
    name: str
    name_en: str
    category: str
    tier: int
    description: str
    stats: RaceStats
    special_traits: list[SpecialTrait] = field(default_factory=list)
    behavior: BehaviorProfile = field(default_factory=BehaviorProfile)
    diplomacy_trait: DiplomacyTrait = field(default_factory=DiplomacyTrait)
    diplomacy_defaults: list[DiplomacyDefault] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)  # 원본 YAML 전체 보관


@dataclass
class WorldConfig:
    id: str
    name: str
    description: str
    raw: dict[str, Any] = field(default_factory=dict)


# ──────────────────────────────────────────
# Race Loader
# ──────────────────────────────────────────

def _parse_race(data: dict[str, Any]) -> RaceConfig:
    """YAML dict → RaceConfig 파싱"""
    stats_data = data.get("stats", {})
    stats = RaceStats(
        max_population=stats_data.get("max_population", 1000),
        growth_rate=stats_data.get("growth_rate", 1.005),
        military_strength=stats_data.get("military_strength", 50),
        magic_affinity=stats_data.get("magic_affinity", 30),
        technology_level=stats_data.get("technology_level", 40),
        adaptability=stats_data.get("adaptability", 60),
        lifespan=stats_data.get("lifespan", 25920),
    )

    traits = [
        SpecialTrait(
            id=t.get("id", ""),
            name=t.get("name", ""),
            description=str(t.get("description", "")),
        )
        for t in data.get("special_traits", [])
    ]

    behavior_data = data.get("behavior", {})
    behavior = BehaviorProfile(
        aggression=behavior_data.get("aggression", 0.5),
        expansion_drive=behavior_data.get("expansion_drive", 0.5),
        alliance_tendency=behavior_data.get("alliance_tendency", 0.5),
        trade_focus=behavior_data.get("trade_focus", 0.5),
        isolationism=behavior_data.get("isolationism", 0.2),
    )

    dt_data = data.get("diplomacy_trait", {})
    diplomacy_trait = DiplomacyTrait(
        trust_rate=dt_data.get("trust_rate", 1.0),
        grudge_rate=dt_data.get("grudge_rate", 1.0),
        memory_duration=dt_data.get("memory_duration", 300),
        betrayal_penalty=dt_data.get("betrayal_penalty", 20.0),
    )

    diplomacy_defaults = [
        DiplomacyDefault(
            target=d.get("target", ""),
            affinity=float(d.get("affinity", 0)),
        )
        for d in data.get("diplomacy_defaults", [])
    ]

    return RaceConfig(
        id=data["id"],
        name=data.get("name", data["id"]),
        name_en=data.get("name_en", data["id"]),
        category=data.get("category", "unknown"),
        tier=data.get("tier", 1),
        description=str(data.get("description", "")),
        stats=stats,
        special_traits=traits,
        behavior=behavior,
        diplomacy_trait=diplomacy_trait,
        diplomacy_defaults=diplomacy_defaults,
        raw=data,
    )


def load_race(yaml_path: Path) -> RaceConfig:
    """단일 종족 YAML 파일 로드"""
    with open(yaml_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return _parse_race(data)


def load_all_races(races_dir: Path | None = None) -> dict[str, RaceConfig]:
    """
    races/ 하위 모든 YAML 파일을 자동 탐색·로드한다.
    새 YAML 파일 추가만으로 자동 인식됨.

    Returns:
        dict[race_id → RaceConfig]
    """
    if races_dir is None:
        races_dir = RACES_DIR

    races: dict[str, RaceConfig] = {}
    yaml_files = sorted(races_dir.rglob("*.yaml"))

    for yaml_path in yaml_files:
        try:
            race = load_race(yaml_path)
            races[race.id] = race
            print(f"  ✅ 로드: {race.id} ({race.name}) — {yaml_path.parent.name}/{yaml_path.name}")
        except Exception as e:
            print(f"  ❌ 오류: {yaml_path} — {e}")

    return races


# ──────────────────────────────────────────
# World Loader
# ──────────────────────────────────────────

def load_world(world_id: str = "asteria") -> WorldConfig:
    """
    세계관 YAML 파일 로드.
    기본값: configs/worlds/default_world.yaml
    """
    yaml_path = WORLDS_DIR / f"{world_id}.yaml"
    if not yaml_path.exists():
        # default_world.yaml 폴백
        yaml_path = WORLDS_DIR / "default_world.yaml"

    with open(yaml_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return WorldConfig(
        id=data.get("id", world_id),
        name=data.get("name", world_id),
        description=str(data.get("description", "")),
        raw=data,
    )


# ──────────────────────────────────────────
# 직접 실행 시 검증
# ──────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("WorldAI Config Loader — 종족 로드 테스트")
    print("=" * 50)

    races = load_all_races()
    print(f"\n총 {len(races)}개 종족 로드 완료\n")

    for race_id, race in races.items():
        print(f"  [{race.tier}티어] {race.name} ({race.name_en})")
        print(f"    카테고리: {race.category}")
        print(f"    인구 성장률: {race.stats.growth_rate} | 전투력: {race.stats.military_strength}")
        print(f"    특수 능력: {[t.id for t in race.special_traits]}")
        print()

    print("=" * 50)
    print("WorldAI Config Loader — 세계관 로드 테스트")
    print("=" * 50)
    world = load_world()
    print(f"  세계관: {world.name}")
    print(f"  설명: {world.description}")
    print(f"  시작 종족 수: {len(world.raw.get('starting_races', []))}")
