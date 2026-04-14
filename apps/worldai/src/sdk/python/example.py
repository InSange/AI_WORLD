import asyncio
import sys
import os

# src 폴더를 sys.path에 추가하여 패키지를 인식하도록 함
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.sdk.python.worldai_client import WorldAIClient

async def event_handler(msg_dict):
    print(f"\n[WebSocket Event] {msg_dict.get('type')}: {str(msg_dict)[:200]}...")

async def main():
    print("--- WorldAI Python SDK Local Test ---")
    client = WorldAIClient("http://localhost:8000")
    
    try:
        factions = await client.get_factions()
        print(f"✅ Connected! Factions found: {len(factions)}")
        
        print("🌐 Connecting WebSocket...")
        await client.connect_events(event_handler)
        print("✅ WebSocket connected! Listening in background.")
        
        print("⏳ Tick 시뮬레이션 명령 발송 (10 hours)...")
        tick_resp = await client.tick(hours=10)
        print(f"✅ Tick Complete: {tick_resp}")
        
        print("대기 중... 이벤트가 WebSocket으로 수신되는지 확인 (5초 후 종료)")
        await asyncio.sleep(5)
    except Exception as e:
        print(f"❌ Error during test: {e}\n(Is the WorldAI server running on port 8000?)")
    finally:
        print("🔌 Closing connections...")
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
