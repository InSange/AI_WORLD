"""
WebSocket Connection Manager
=============================
여러 클라이언트의 WebSocket 연결을 관리하고 메시지를 브로드캐스트한다.
"""
from __future__ import annotations
from typing import Any
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        # 활성화된 연결 리스트
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """새 클라이언트 연결 수락"""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"📡 New WS Connection: {len(self.active_connections)} total")

    def disconnect(self, websocket: WebSocket):
        """클라이언트 연결 해제"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"🔌 WS Disconnected: {len(self.active_connections)} left")

    async def send_personal_message(self, message: Any, websocket: WebSocket):
        """특정 클라이언트에게 메시지 전송 (JSON)"""
        await websocket.send_json(message)

    async def broadcast(self, message: Any):
        """모든 연결된 클라이언트에게 메시지 브로드캐스트 (JSON)"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                # 연결이 끊겼으나 아직 리스트에 남아있는 경우 대비
                print(f"⚠️ WS Broadcast Error: {e}")
                continue


# 전역 매니저 인스턴스
manager = ConnectionManager()
