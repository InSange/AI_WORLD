# WorldAI — 파벌·군집 규모 시스템 (Faction & Settlement Scale)

> 최종 수정: 2026-04-05 | 상태: Draft

---

## 1. 설계 원칙

> 하나의 **종족(Race)** 안에 여러 **파벌(Faction)** 이 존재한다.
> 파벌은 위치한 지역, 규모, 지도자의 성향에 따라 독자적으로 행동한다.
> 같은 인간 종족이라도 "북벽 수비대"와 "중앙 평원 제국"은 서로 다른 파벌로 독립 행동한다.
> 파벌끼리는 협력하거나 전쟁할 수 있다 (동종 파벌 전쟁 포함).

---

## 2. 군집 규모 (Settlement Scale)

규모가 클수록 더 많은 자원, 더 강한 군사력, 더 높은 외교 영향력을 갖는다.

| 규모 ID | 이름 | 인구 기준 | 지도자 칭호 | 군사력 | 외교 가중치 |
|---------|------|-----------|------------|--------|------------|
| `outpost` | 전초기지/요새 | 50 이하 | 대장/지휘관 | 낮음 | 매우 낮음 |
| `village` | 마을 | 51 ~ 500 | 촌장 | 낮음 | 낮음 |
| `town` | 읍/소도시 | 501 ~ 2000 | 영주/시장 | 중간 | 중간 |
| `city` | 도시 | 2001 ~ 5000 | 영주/총독 | 높음 | 높음 |
| `kingdom` | 왕국 | 5001 ~ 15000 | 왕(王) | 강함 | 강함 |
| `empire` | 제국 | 15001 이상 | 황제(皇帝) | 최강 | 최강 |

### 인간 파벌 예시 (지역별)

```yaml
# 북부 설원 지역
- faction_id: northern_wall_guard
  race: human
  name: "북벽 수비대"
  region: northern_tundra
  scale: outpost
  leader_title: 대장
  leader_name: "에릭 아이언"
  population: 120
  specialty: 극한지 전투, 설원 감시

# 중앙 평원 지역
- faction_id: central_empire
  race: human
  name: "아스테리아 중앙 제국"
  region: central_plains
  scale: empire
  leader_title: 황제
  leader_name: "알렉산 3세"
  population: 25000
  specialty: 외교, 기술, 대군 운용

- faction_id: river_kingdom
  race: human
  name: "강변 왕국 리베르"
  region: river_coast
  scale: kingdom
  leader_title: 왕
  leader_name: "마르코 드레인"
  population: 8000
  specialty: 교역, 수군
```

---

## 3. 종족별 군집 규모 체계

### 🧑 인간 (Human)

| 규모 | 이름 | 지도자 | 특징 |
|------|------|--------|------|
| 전초기지 | 요새·주둔지 | 대장 | 군사 목적. 영구 정착 아님 |
| 마을 | 마을 | 촌장 | 농업, 자급자족 |
| 읍·소도시 | 읍 | 영주 | 교역 중심 |
| 도시 | 도시 | 영주/총독 | 정치·문화 중심 |
| 왕국 | 왕국 | 왕 | 복수 도시 통합 |
| 제국 | 제국 | 황제 | 복수 왕국 통합 |

### 🧝 엘프 (Elf)

| 규모 | 이름 | 지도자 | 특징 |
|------|------|--------|------|
| 전초기지 | 숲 감시소 | 수호자 | 국경 감시, 비공개 |
| 마을 | 숲 촌락 | 장로 | 은밀한 공동체 |
| 도시급 | 숲 도시 | 장로 평의회 | 1000년 이상 된 정착지 |
| 왕국급 | 고대 성역 | 대장로/숲의 왕 | 엘프 최고 군집. 외부 출입 거의 불가 |

> **엘프는 제국을 형성하지 않는다.** 영토 확장 의지가 없어 성역 수준이 최대.

### ⛏️ 드워프 (Dwarf)

| 규모 | 이름 | 지도자 | 특징 |
|------|------|--------|------|
| 전초기지 | 광산 캠프 | 감독관 | 임시, 광맥 고갈 시 이동 |
| 마을급 | 터전 (Hold) | 터전주 | 지하 정착지 |
| 도시급 | 요새도시 | 영지주 | 방어에 특화된 지하 도시 |
| 왕국급 | 지하왕국 | 왕 (드왈린) | 드워프 최대 군집. 지하 네트워크 연결 |

### 🪖 오크 (Orc)

| 규모 | 이름 | 지도자 | 특징 |
|------|------|--------|------|
| 마을급 | 소부족 | 부족장 | 20~100명 전투 집단 |
| 읍급 | 부족 | 추장 | 복수 소부족 통합 |
| 도시급 | 대부족 연합 | 전쟁추장 | 전투 시 폭발적 강함 |
| 왕국급 | 대왕국 (하급) | 오크로드 | 드물게 발생. 강력한 카리스마 필요 |

> **오크는 제국을 형성하기 어렵다.** 우두머리가 죽으면 분열 확률 80%.

### 🐉 드래곤 (Dragon)

| 규모 | 이름 | 지도자 | 특징 |
|------|------|--------|------|
| 개인 서식지 | 둥지 (Lair) | 단독 드래곤 | 자신의 영역 사수 |
| 소군집 | 드래곤 군락 | 연장자 드래곤 | 2~5마리, 극히 드묾 |
| 대군집 | 용족 왕국 | 용왕 | 용왕이 나타날 때만 형성 |

### 💀 언데드 (Undead)

| 규모 | 이름 | 지도자 | 특징 |
|------|------|--------|------|
| 소규모 | 좀비 무리 | 없음 (본능) | 통제되지 않은 언데드 |
| 마을급 | 유령 촌락 | 뱀파이어 영주 | 살아있는 희생양 관리 |
| 왕국급 | 언데드 영지 | 리치 군주 | 마법으로 통제 |
| 제국급 | 죽음의 왕국 | 죽음의 황제 | 드물게 발생. 전 대륙 위협 |

---

## 4. 파벌 YAML 스키마

```yaml
# apps/worldai/configs/factions/northern_tundra/iron_claw_tribe.yaml
faction_id: iron_claw_tribe
race: beastman
sub_type: wolf_tribe       # 견족
name: "철발톱 부족"
region: northern_tundra
location:                  # 맵 좌표 (타일 기반)
  x: 30
  y: 8
scale: village             # village / town / city / kingdom / empire
  
leader:
  name: "그레이팡 카르"
  title: 촌장
  combat_grade: 전사        # 개인 전투 등급 (rank_level_system.md 참조)
  level: 42

population: 280
military_strength: 65
specialty: [cold_resistance, pack_hunting]
territory_tiles: 8

relations:                 # 파벌 간 외교 (종족 기본값에서 파생)
  - target_faction: northern_wall_guard  # 인간 요새
    affinity: -15          # 긴장 (기본 인간-수인 0에서 파생)
  - target_faction: peak_dragon_grimm    # 드래곤 서식지
    affinity: -30          # 위협 관계
```

---

## 5. 파벌 이름 생성 규칙

파벌 이름은 **지역 + 종족 특성 + 규모** 조합으로 자동 생성 가능하다.

```python
# 이름 생성 예시 (Phase 3.5 구현 예정)
def generate_faction_name(race: str, region: str, scale: str) -> str:
    prefixes = {
        "northern_tundra": ["북방", "설원", "철벽", "빙하"],
        "central_plains":  ["중앙", "황금", "태양", "광야"],
        "eastern_mountain": ["동부", "철산", "암벽", "지하"],
        "western_forest":   ["서부", "고대", "달빛", "안개"],
        "southern_wasteland": ["남부", "사막", "재의", "저승"],
    }
    suffixes = {
        "empire":  ["제국", "대제국", "황제국"],
        "kingdom": ["왕국", "왕조", "왕가"],
        "city":    ["도시", "공국", "영지"],
        "town":    ["읍", "소공국", "영토"],
        "village": ["마을", "촌락", "공동체"],
        "outpost": ["요새", "수비대", "전초기지"],
    }
    prefix = random.choice(prefixes.get(region, ["미지의"]))
    suffix = random.choice(suffixes.get(scale, ["집단"]))
    return f"{prefix} {suffix}"
```
