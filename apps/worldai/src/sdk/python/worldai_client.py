import asyncio
import httpx
import websockets
import json
from typing import Callable, Optional, Dict, Any, Awaitable

class WorldAIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.ws_url = self.base_url.replace("http://", "ws://").replace("https://", "wss://")
        self.client = httpx.AsyncClient(base_url=self.base_url)
        self._ws_connection: Optional[Any] = None
        self._ws_task: Optional[asyncio.Task] = None

    async def get_world(self) -> Dict[str, Any]:
        """현재 세계 상태 기본 정보를 가져옵니다."""
        response = await self.client.get("/world")
        response.raise_for_status()
        return response.json()

    async def get_factions(self) -> list:
        """전체 파벌 정보를 가져옵니다."""
        response = await self.client.get("/factions")
        response.raise_for_status()
        return response.json()

    async def get_leaderboard(self) -> Dict[str, Any]:
        """군사력, 영향력 등 파벌 리더보드를 반환합니다."""
        response = await self.client.get("/leaderboard")
        response.raise_for_status()
        return response.json()

    async def tick(self, hours: int = 1) -> Dict[str, Any]:
        """지정된 시간(시간 단위)만큼 시뮬레이션을 진행시킵니다."""
        response = await self.client.post("/simulation/tick", params={"hours": hours})
        response.raise_for_status()
        return response.json()

    async def run_simulation(self, hours: int, active: bool = True) -> Dict[str, Any]:
        """지정된 시간만큼 백그라운드 처리를 실행하거나 중지합니다."""
        response = await self.client.post("/simulation/run", json={"hours": hours, "active": active})
        response.raise_for_status()
        return response.json()

    async def connect_events(self, on_message: Callable[[Dict[str, Any]], Awaitable[None]]):
        """WebSocket에 연결하여 실시간 이벤트(영토 변경, 이벤트 로그 등) 수신을 비동기로 시작합니다."""
        if self._ws_task is not None and not self._ws_task.done():
            return  # Already connected

        async def _listen():
            try:
                async with websockets.connect(f"{self.ws_url}/ws") as websocket:
                    self._ws_connection = websocket
                    async for message in websocket:
                        data = json.loads(message)
                        # Call the user-provided callback
                        await on_message(data)
            except Exception as e:
                print(f"[WorldAIClient] WebSocket connection closed or error: {e}")
            finally:
                self._ws_connection = None

        self._ws_task = asyncio.create_task(_listen())

    async def close(self):
        """클라이언트 및 소켓 연결을 종료합니다."""
        if self._ws_connection is not None:
            await self._ws_connection.close()
        if self._ws_task is not None:
            self._ws_task.cancel()
        await self.client.aclose()
