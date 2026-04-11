export interface WSMessage {
  type: 'INIT' | 'UPDATE' | 'SUMMARY' | 'EVENT';
  tick?: number;
  year?: number;
  hour?: number;
  day_phase?: string;
  is_daytime?: boolean;
  season?: string;
  events?: any[];
  map?: any;
  populations?: Record<string, number>;
  message?: string;
}

export type MessageHandler = (data: WSMessage) => void;

class WebSocketClient {
  private socket: WebSocket | null = null;
  private handlers: MessageHandler[] = [];
  private reconnectInterval = 5000;
  private url = `ws://${window.location.hostname}:8000/ws`;

  constructor() {
    this.connect();
  }

  connect() {
    console.log("📡 Connecting to WorldAI Server...");
    this.socket = new WebSocket(this.url);

    this.socket.onopen = () => {
      console.log("✅ WebSocket Connected");
    };

    this.socket.onmessage = (event) => {
      const data: WSMessage = JSON.parse(event.data);
      this.handlers.forEach(h => h(data));
    };

    this.socket.onclose = () => {
      console.log("🔌 WebSocket Disconnected. Reconnecting...");
      setTimeout(() => this.connect(), this.reconnectInterval);
    };

    this.socket.onerror = (err) => {
      console.error("⚠️ WebSocket Error:", err);
      this.socket?.close();
    };
  }

  onMessage(handler: MessageHandler) {
    this.handlers.push(handler);
    return () => {
      this.handlers = this.handlers.filter(h => h !== handler);
    };
  }

  async triggerTick() {
    return fetch(`http://${window.location.hostname}:8000/simulation/tick`, {
      method: "POST"
    }).then(res => res.json());
  }

  async getMap() {
    return fetch(`http://${window.location.hostname}:8000/world/map`).then(res => res.json());
  }

  async resetSimulation() {
    return fetch(`http://${window.location.hostname}:8000/simulation/reset`, {
      method: "POST"
    }).then(res => res.json());
  }
}

export const api = new WebSocketClient();
