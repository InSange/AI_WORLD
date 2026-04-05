# WorldAI — 종족 스펙 (Race Specifications)

> 최종 수정: 2026-04-05 | 상태: Draft

---

## 스탯 정의

| 스탯 | 설명 | 범위 |
|------|------|------|
| `max_population` | 최대 인구 | 500 ~ 50000 |
| `growth_rate` | 틱당 인구 성장 배수 | 1.001 ~ 1.050 |
| `military_strength` | 전투 기본 능력 | 10 ~ 100 |
| `magic_affinity` | 마법 사용·저항력 | 0 ~ 100 |
| `technology_level` | 기술력 (무기, 건설 등) | 0 ~ 100 |
| `adaptability` | 다양한 환경 적응력 | 0 ~ 100 |
| `lifespan` | 평균 수명 (틱) | 25000 ~ 무한 |

---

## 카테고리 1 — 인간형 (Humanoids)

---

### 🧑 인간 (Human)

```yaml
id: human
name: 인간
name_en: Human
category: humanoid
tier: 1
description: >
  가장 보편적이며 다양한 환경에 적응하는 능력을 지닌 종족.
  마법이나 육체적 능력보다는 조직력과 기술로 대륙 패권을 노린다.

stats:
  max_population: 10000
  growth_rate: 1.005      # 보통 번식 (너무 빠르지 않게 조절)
  military_strength: 60
  magic_affinity: 30
  technology_level: 65    # 기술력 중상위권 (초반 급성장 방지)
  adaptability: 95        # 최고 적응력
  lifespan: 25920         # ~72년 (360틱/년)

special_traits:
  - id: adaptability_bonus
    name: "만능 적응"
    description: "모든 지형에서 패널티 없음. 다른 종족과 협력 시 시너지 +10%"
  - id: tech_research
    name: "기술 혁신"
    description: "기술 연구 속도 +15%, 매 150틱마다 소규모 기술 발전 이벤트 (초반 발전 완급 조절)"

behavior:
  aggression: 0.40
  expansion_drive: 0.60   # 영토 확장 욕구 중간 (초반 폭발 방지)
  alliance_tendency: 0.65
  trade_focus: 0.70

diplomacy_trait:
  trust_rate: 1.0
  grudge_rate: 0.9
  memory_duration: 200
  betrayal_penalty: 15

diplomacy_defaults:
  - target: elf
    affinity: 10          # 인간은 엘프를 동경하지만 상대방이 경계함
  - target: dwarf
    affinity: 40
  - target: halfling
    affinity: 50
  - target: orc
    affinity: -20
  - target: undead
    affinity: -50
```

---

### 🧝 엘프 (Elf)

```yaml
id: elf
name: 엘프
name_en: Elf
category: humanoid
tier: 2
description: >
  장수하며 마법과 자연에 친숙한 종족. 뾰족한 귀가 특징.
  수천 년을 사는 덕분에 깊은 지식을 쌓았지만, 변화를 두려워하는 경향이 있다.

stats:
  max_population: 3000    # 낮은 출생률
  growth_rate: 1.002      # 매우 느린 증가
  military_strength: 65   # 궁술, 민첩
  magic_affinity: 90      # 최고 마법 친화
  technology_level: 55
  adaptability: 50        # 숲 외 지형 불편
  lifespan: 1080000       # ~3000년

special_traits:
  - id: longevity_wisdom
    name: "장수의 지혜"
    description: "매 1000틱마다 고대 비전 지식 발견. 마법 연구 속도 +30%"
  - id: nature_bond
    name: "자연과의 유대"
    description: "숲 지형에서 방어력 +30%, 이동 불이익 없음. 벌목 시 친밀도 패널티"
  - id: isolationist
    name: "폐쇄적 고립주의"
    description: "외부 종족의 숲 진입 시 즉각 경보. 다른 종족이 먼저 접촉해도 외교 이벤트 발생 확률 -40%. 혼자 있을 때 마법 연구 효율 +20%"

behavior:
  aggression: 0.25        # 비공격적 (선제 공격은 거의 안 함)
  expansion_drive: 0.10   # 영토 확장 의지 매우 낮음 — 현재 영역 사수에만 집중
  alliance_tendency: 0.20 # 동맹 매우 꺼림. 공동의 적이 있어야 겨우 협력
  trade_focus: 0.30       # 교역도 최소한만
  isolationism: 0.90      # 폐쇄 성향 (높을수록 외부 접촉 회피)

diplomacy_trait:
  trust_rate: 0.50        # 신뢰 쌓기 매우 느림 (수백 년을 봐야 믿음)
  grudge_rate: 1.80       # 원한 쌓기 아주 빠름
  memory_duration: 1200   # 아주 오래 기억 (수천 년도 잊지 않음)
  betrayal_penalty: 60    # 배신 시 관계 회복 거의 불가

diplomacy_defaults:
  - target: human
    affinity: -20         # 인간을 경계함. 빠른 팽창과 자연 훼손을 위협으로 인식
  - target: fairy
    affinity: 70          # 같은 자연 존재
  - target: beastman
    affinity: 20          # 자연 공유하는 수인은 그나마 허용
  - target: orc
    affinity: -60
  - target: dragon
    affinity: 10          # 고대 존재에 대한 경외
  - target: undead
    affinity: -70
  - target: dwarf
    affinity: -5          # 드워프의 채굴로 자연 파괴 — 달갑지 않음
```

---

### ⛏️ 드워프 (Dwarf)

```yaml
id: dwarf
name: 드워프
name_en: Dwarf
category: humanoid
tier: 1
description: >
  키가 작고 튼튼하며 광업과 대장기술에 능한 종족.
  지하 왕국을 건설하고, 최고 품질의 무기와 갑옷을 제작한다.

stats:
  max_population: 5000
  growth_rate: 1.004
  military_strength: 75   # 강력한 근접전
  magic_affinity: 15      # 마법 거의 사용 안 함
  technology_level: 90    # 기술력 최고
  adaptability: 40        # 산악 특화, 다른 지형 불편
  lifespan: 144000        # ~400년

special_traits:
  - id: master_craftsman
    name: "마스터 장인"
    description: "무기/갑옷 품질 +40%. 제작한 아이템 거래 시 추가 소득"
  - id: underground_king
    name: "지하의 왕"
    description: "산악·지하 지형에서 이동 및 전투 패널티 없음. 광맥 발견 확률 +50%"

behavior:
  aggression: 0.50
  expansion_drive: 0.30   # 지하 위주 확장
  alliance_tendency: 0.55
  trade_focus: 0.80       # 교역 매우 중요

diplomacy_trait:
  trust_rate: 0.80
  grudge_rate: 1.20
  memory_duration: 500    # 드워프는 원한을 오래 기억
  betrayal_penalty: 35

diplomacy_defaults:
  - target: human
    affinity: 40
  - target: orc
    affinity: -50
  - target: goblin
    affinity: -40
  - target: golem
    affinity: 30          # 기계 종족에 친화적
```

---

### 🪖 오크/고블린/트롤 (Orc / Goblin / Troll)

```yaml
id: orc
name: 오크 (Orc 계열)
name_en: Orc
category: humanoid
tier: 1
description: >
  강력한 육체나 빠른 번식력을 지닌, 엘프와 대조되는 종족.
  서브 종족: 오크(전투 특화), 고블린(수 특화), 트롤(재생 특화)

stats:
  max_population: 8000
  growth_rate: 1.012      # 빠른 번식
  military_strength: 80   # 최강 근접전
  magic_affinity: 10
  technology_level: 25    # 낮은 기술
  adaptability: 60
  lifespan: 18000         # ~50년 (수명 짧음)

special_traits:
  - id: berserker_rage
    name: "광전사의 분노"
    description: "전투 시 HP 30% 이하에서 공격력 +50%. 패배 시 오히려 반격 강화"
  - id: horde_tactics
    name: "군집 전술"
    description: "같은 군집 내 유닛 수가 많을수록 전투력 보정 (최대 +30%)"

behavior:
  aggression: 0.80        # 매우 공격적
  expansion_drive: 0.70
  alliance_tendency: 0.25 # 동맹 잘 안 맺음
  trade_focus: 0.20

diplomacy_trait:
  trust_rate: 1.20        # 힘을 보여주면 빨리 인정
  grudge_rate: 0.80       # 원한은 상대적으로 짧음
  memory_duration: 150
  betrayal_penalty: 20

diplomacy_defaults:
  - target: elf
    affinity: -60
  - target: dwarf
    affinity: -50
  - target: human
    affinity: -20
  - target: goblin
    affinity: 40          # 같은 계열
  - target: troll
    affinity: 30
```

---

### 🍃 하플링/호빗 (Halfling)

```yaml
id: halfling
name: 하플링
name_en: Halfling
category: humanoid
tier: 1
description: >
  드워프보다 작고 조용한 생활을 좋아하는 종족.
  전투를 꺼리지만, 은신과 기민함에서 타의 추종을 불허한다.

stats:
  max_population: 4000
  growth_rate: 1.006
  military_strength: 30   # 낮은 전투력
  magic_affinity: 20
  technology_level: 45
  adaptability: 75
  lifespan: 64800         # ~180년

special_traits:
  - id: stealth_master
    name: "은신의 달인"
    description: "평원·숲 지형에서 적에게 발견되지 않음. 정보 수집 능력 +50%"
  - id: lucky_feet
    name: "행운의 발"
    description: "부정적 이벤트 발생 확률 -20%. 교역 협상 성공률 +15%"

behavior:
  aggression: 0.10        # 매우 평화적
  expansion_drive: 0.15
  alliance_tendency: 0.80 # 동맹 선호
  trade_focus: 0.75

diplomacy_defaults:
  - target: human
    affinity: 50
  - target: elf
    affinity: 45
  - target: dwarf
    affinity: 40
  - target: orc
    affinity: -30
```

---

## 카테고리 2 — 수인/비인간 (Beastmen & Non-Humans)

---

### 🐺 수인 (Beastman)

```yaml
id: beastman
name: 수인 (견족/묘족 등)
name_en: Beastman
category: beastmen
tier: 1
description: >
  동물과 인간의 특징을 혼합한 종족. 견족(늑대), 묘족(고양이) 등 다양한 하위 부족이 있다.
  부족 단위로 이동하며 각자의 본능을 따른다.

stats:
  max_population: 6000
  growth_rate: 1.009
  military_strength: 70
  magic_affinity: 25
  technology_level: 35
  adaptability: 80       # 야생 환경 적응 탁월
  lifespan: 25920        # 인간과 비슷

special_traits:
  - id: pack_hunting
    name: "무리 사냥"
    description: "3기 이상 군집 시 전투력 +25%. 기습 공격 성공률 2배"
  - id: wild_instinct
    name: "야생의 본능"
    description: "적의 이동 방향 사전 감지 (정찰 역할). 함정 탐지 +40%"

behavior:
  aggression: 0.55
  expansion_drive: 0.50
  alliance_tendency: 0.40
  trade_focus: 0.30

diplomacy_defaults:
  - target: human
    affinity: 10
  - target: elf
    affinity: 20          # 자연 공유
  - target: fairy
    affinity: 15
```

---

### 🐴 반인반수 (Half-Beast: 켄타우로스·하피·라미아)

```yaml
id: half_beast
name: 반인반수
name_en: Half-Beast
category: beastmen
tier: 2
description: >
  켄타우로스(상반신 인간, 하반신 말), 하피(인간+새), 라미아(인간+뱀) 등
  신화적 기반을 둔 종족. 희귀하고 강력하다.

stats:
  max_population: 1500   # 희귀
  growth_rate: 1.003
  military_strength: 75
  magic_affinity: 40
  technology_level: 30
  adaptability: 65
  lifespan: 108000       # ~300년

special_traits:
  - id: mythic_form
    name: "신화의 형태"
    description: "적에게 공포 효과 적용 시 전투 시작 전 사기 -20% 부여"
  - id: terrain_mastery
    name: "지형 정복"
    description: "켄타우로스=평원 특화, 하피=산악 비행, 라미아=수중·사막 이동"
```

---

### 🧚 페어리/요정 (Fairy)

```yaml
id: fairy
name: 페어리 / 요정
name_en: Fairy
category: beastmen
tier: 2
description: >
  작은 몸집과 마법 능력을 지닌 정령 같은 존재.
  직접적인 전투보다 지원과 방해에 특화되어 있다.

stats:
  max_population: 2000
  growth_rate: 1.004
  military_strength: 15   # 매우 낮은 전투력
  magic_affinity: 85
  technology_level: 10
  adaptability: 90        # 어디서나 생존
  lifespan: 360000        # ~1000년

special_traits:
  - id: pixie_dust
    name: "요정 가루"
    description: "아군 종족에 버프 제공 (성장률 +5%, 행운 +10%). 지원 전문"
  - id: mind_trick
    name: "마음의 장난"
    description: "적 종족 외교 판단력 교란. 임박한 전쟁 확률 -20%"

diplomacy_defaults:
  - target: elf
    affinity: 70
  - target: nature_spirit
    affinity: 60
  - target: undead
    affinity: -80
  - target: demon
    affinity: -70
```

---

## 카테고리 3 — 고위/신화 종족 (Mythic Races)

---

### 🐉 드래곤 (Dragon)

```yaml
id: dragon
name: 드래곤
name_en: Dragon
category: mythic
tier: 3
description: >
  판타지 세계의 정점에 서 있는 강력한 파충류형 생물.
  개체 수는 적지만 압도적인 개체 전투력과 마법 능력을 보유한다.

stats:
  max_population: 200     # 극소수
  growth_rate: 1.0005     # 매우 느린 번식
  military_strength: 100  # 최강
  magic_affinity: 95
  technology_level: 40    # 기술보다 본능
  adaptability: 85
  lifespan: 3600000       # ~10000년

special_traits:
  - id: apex_predator
    name: "대륙의 정점"
    description: "어떤 종족도 드래곤 단독 개체를 무시할 수 없음. 존재만으로 주변 종족 사기 -15%"
  - id: dragon_flame
    name: "드래곤 불꽃"
    description: "전투 시 광역 화염 공격. 방어 무시. 도시/건물 파괴 가능"
  - id: ancient_memory
    name: "고대의 기억"
    description: "세계에 대한 지식 보유. 고대 유적 위치 파악. 교섭 시 정보 제공 가능"

behavior:
  aggression: 0.40        # 일반적으로 공격적이지 않음. 영역 침범 시 즉각 반응
  expansion_drive: 0.20   # 영역 유지 중심
  alliance_tendency: 0.15 # 동맹 거의 안 맺음
  trade_focus: 0.10

diplomacy_defaults:
  - target: human
    affinity: -10         # 약소 종족 무시
  - target: elf
    affinity: 15
  - target: undead
    affinity: -40
  - target: angel
    affinity: -20
```

---

### 💀 언데드 (Undead)

```yaml
id: undead
name: 언데드 (뱀파이어·리치·좀비)
name_en: Undead
category: mythic
tier: 2
description: >
  죽음에서 깨어난 존재들. 뱀파이어(지성형), 리치(마법형), 좀비(군집형)로 구성.
  생명 에너지를 흡수하고 죽은 자를 병사로 만들 수 있다.

stats:
  max_population: 4000
  growth_rate: 1.0        # 자연 증식 없음, 다른 종족 죽음으로 증가
  military_strength: 70
  magic_affinity: 75
  technology_level: 20
  adaptability: 70
  lifespan: 9999999       # 사실상 불멸

special_traits:
  - id: death_harvest
    name: "죽음의 수확"
    description: "전투에서 적 유닛 사망 시 25% 확률로 아군으로 부활. 인구 특수 증가 메커니즘"
  - id: plague_aura
    name: "역병의 기운"
    description: "주변 지역에 역병 서서히 전파. 인접 종족 성장률 -10%"
  - id: undying
    name: "불사"
    description: "생명 관련 이벤트(기근, 역병) 면역"

behavior:
  aggression: 0.70
  expansion_drive: 0.60
  alliance_tendency: 0.15

diplomacy_defaults:
  - target: angel
    affinity: -100        # 천사와 절대적 적대
  - target: human
    affinity: -50         # 인간은 먹잇감
  - target: demon
    affinity: 20          # 어둠 계열 연대
  - target: dragon
    affinity: -40
```

---

### 👼 천사/악마 (Angel / Demon)

```yaml
id: angel_demon
name: 천사 / 악마
name_en: Angel / Demon
category: mythic
tier: 3
description: >
  천상계(천사)나 마계(악마)에서 온 초월적 존재.
  두 세력은 세계 각지에서 끊임없이 충돌하며, 필멸 종족을 대리전에 이용한다.

stats:
  max_population: 300
  growth_rate: 1.001
  military_strength: 95
  magic_affinity: 100     # 마법 능력 최고
  technology_level: 5     # 마법에만 의존
  adaptability: 95
  lifespan: 9999999

special_traits:
  - id: divine_intervention
    name: "신성 개입 / 마계 유혹"
    description: "동맹 종족에게 강력한 축복/저주 부여. 전쟁 중 기적적 역전 가능"
  - id: celestial_war
    name: "천상의 전쟁"
    description: "천사와 악마 친밀도는 항상 -100. 필멸 종족에 각자 영향력 행사"
```

---

## 카테고리 4 — 기타 (Others)

---

### 🔥 정령 (Elemental)

```yaml
id: elemental
name: 정령 (4원소)
name_en: Elemental Spirit
category: others
tier: 2
description: >
  불, 물, 땅, 바람의 원소를 다루는 존재.
  특정 자연 환경에 귀속되어 다른 지형에서는 힘을 잃는다.

stats:
  max_population: 1000
  growth_rate: 1.002
  military_strength: 65
  magic_affinity: 100
  technology_level: 0     # 기술 개념 없음
  adaptability: 30        # 자신의 원소 지형에서만 강함
  lifespan: 9999999       # 원소 소멸 시 재탄생

sub_types:
  - fire:   terrain=volcano/desert, bonus=공격력 +30%
  - water:  terrain=ocean/river, bonus=재생력 +30%
  - earth:  terrain=mountain/forest, bonus=방어력 +40%
  - wind:   terrain=plains/sky, bonus=이동력 +50%

diplomacy_defaults:
  - target: fairy
    affinity: 50
  - target: elf
    affinity: 30
  - target: golem
    affinity: -20          # 정령 vs 인공 생명체 긴장
  - target: undead
    affinity: -60
```

---

### ⚙️ 골렘/기계 종족 (Golem)

```yaml
id: golem
name: 골렘 / 기계 종족
name_en: Golem / Construct
category: others
tier: 2
description: >
  마법이나 기술로 만들어진 인공 생명체.
  창조자 종족의 목적에 따라 행동하지만, 오랜 시간이 지나 자아를 가지기도 한다.

stats:
  max_population: 800     # 제작에 자원 필요
  growth_rate: 1.0        # 자연 번식 없음, 제작으로만 증가
  military_strength: 85   # 강력한 구조적 힘
  magic_affinity: 30
  technology_level: 60    # 고도 기술 산물
  adaptability: 50
  lifespan: 9999999       # 유지보수만 되면 영구

special_traits:
  - id: no_needs
    name: "무욕"
    description: "식량, 기근, 역병 이벤트 면역. 자원 소비 없음"
  - id: upgrade_system
    name: "업그레이드 가능"
    description: "기술 연구 완료 시 기존 개체에 성능 향상 적용 가능"

diplomacy_defaults:
  - target: dwarf
    affinity: 30
  - target: human
    affinity: 20
  - target: elemental
    affinity: -20          # 자연 vs 인공 긴장
  - target: fairy
    affinity: -10
```

---

## 종족 티어 요약

| 티어 | 특징 | 해당 종족 |
|------|------|---------|
| **Tier 1** | 흔한 종족, 빠른 성장, 균형 | 인간, 드워프, 오크, 하플링 |
| **Tier 2** | 특수 능력 보유, 제한적 성장 | 엘프, 수인, 반인반수, 페어리, 언데드, 정령, 골렘 |
| **Tier 3** | 희귀, 압도적 능력, 극소 인구 | 드래곤, 천사/악마 |
