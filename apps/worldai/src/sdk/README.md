# WorldAI Plugin SDK

WorldAI 코어 엔진은 외부 게임 클라이언트 환경(Unity, Python Bots, 등)과의 Seamless 연동을 위해 클라이언트 SDK를 제공합니다.

## Supported Languages
본 SDK는 별도의 의존성을 최소화하여 빌드 호환성을 높이는 아키텍처를 지향합니다.

### 1. C# SDK (Unity 호환)
`WorldAIClient.cs` 파일 하나만으로 완벽한 통신 기능을 수행할 수 있도록 `HttpClient`와 `ClientWebSocket`을 활용합니다.

#### 특징
- **비동기 큐(`ConcurrentQueue`)**: WebSocket으로 쏟아지는 시뮬레이션 지형 변경(`territory_delta`) 데이터를 백그라운드에서 안전하게 받고, 메인 스레드(Unity `Update`)에서 `ConsumeEvents()`로 일괄 소진하여 병목을 방지합니다.
- `async/await` 패턴 기반의 모던 C# 설계

#### 사용 예시 (Unity MonoBehaviour 대응)
```csharp
using UnityEngine;
using WorldAI.SDK;

public class WorldManager : MonoBehaviour
{
    private WorldAIClient _client;

    async void Start()
    {
        _client = new WorldAIClient("http://localhost:8000");
        
        // 현재 스냅샷 로드
        var worldData = await _client.GetWorldAsync();
        Debug.Log("World Loaded: " + worldData);

        // 실시간 변경 이벤트 스트리밍 연결
        await _client.ConnectEventsAsync();
    }

    void Update()
    {
        if (_client == null) return;
        
        // 프레임마다 축적된 메시지 전부 소비 후 UI 반영 (메인 스레드 안전)
        foreach (var msg in _client.ConsumeEvents())
        {
            Debug.Log("Event Received: " + msg);
            // 메세지 파싱 로직..
        }
    }

    void OnDestroy()
    {
        _client?.Dispose();
    }
}
```

### 2. Python SDK
`httpx`와 `websockets`를 활용한 풀 비동기 클라이언트입니다.

#### 사용 예시
```python
import asyncio
from src.sdk.python.worldai_client import WorldAIClient

async def event_handler(msg_dict):
    print(f"Server event: {msg_dict}")

async def main():
    client = WorldAIClient("http://localhost:8000")
    
    # 데이터 조회
    factions = await client.get_factions()
    print("Factions count:", len(factions))
    
    # 웹소켓 리스너 스레드 백그라운드 기동
    await client.connect_events(event_handler)
    
    # 시뮬레이터 틱 진행 명령
    await client.tick(hours=5)
    
    # 3초 대기 (이벤트 들어오길 확인용)
    await asyncio.sleep(3)
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```
