import urllib.request
import json

BASE = "http://localhost:8000"


def get(path):
    with urllib.request.urlopen(BASE + path) as r:
        return json.loads(r.read())


def post(path, data=None):
    body = json.dumps(data or {}).encode()
    req = urllib.request.Request(
        BASE + path, data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def main():
    # 1. 상태 확인
    s = get("/simulation/status")
    print(f"[상태] Tick={s['tick']} Year={s['year']} 계절={s['season_display']} 종족={s['active_races']}")

    # 2. 10틱 실행
    r = post("/simulation/run?ticks=10")
    print(f"[10틱 실행] 현재 Tick={r['current_tick']} 주요이벤트={r['total_notable_events']}개")
    for e in r["notable_events"][:3]:
        print(f"  🔔 {e['title']}")

    # 3. 종족 순위
    races = get("/world/races?sort_by=population")
    print("[인구 순위 Top 3]")
    for i, race in enumerate(races[:3]):
        print(f"  {i+1}. {race['name']}: {race['population']:,}명 (기술:{race['technology_level']})")

    # 4. 파벌 목록
    factions = get("/factions")
    print(f"[파벌] 총 {factions['total']}개")
    for f in factions["factions"][:4]:
        print(f"  [{f['scale_display']}] {f['name']} pop={f['population']:,}")

    # 5. 외교 현황 (전쟁 상태만)
    diplomacy = get("/world/diplomacy?min_abs=60&level=WAR")
    print(f"[전쟁 관계] {diplomacy['total']}개")
    for rel in diplomacy["relations"][:3]:
        print(f"  {rel['from']} → {rel['to']}: {rel['value']}")

    # 6. 초월자 이벤트
    print("[초월자 이벤트]")
    t = post("/factions/central_empire/transcendent", {
        "faction_id": "central_empire",
        "transcendent_type": "dragonborn",
        "source": "북방 드래곤 처치 후 심장 흡수",
    })
    print(f"  {t['message']}")
    print(f"  레벨 상한: {t['detail']['level_cap']}")
    print(f"  추가 특성: {t['detail']['extra_traits']}")

    # 7. 리더보드
    lb = get("/world/leaderboard")
    print("[기술력 순위]")
    for e in lb["by_technology_level"][:3]:
        print(f"  {e['rank']}위. {e['name']}: {e['technology_level']}")


if __name__ == "__main__":
    main()
