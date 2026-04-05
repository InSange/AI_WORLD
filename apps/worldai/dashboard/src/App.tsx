import React, { useEffect, useState } from 'react';
import { api } from './api';
import type { WSMessage } from './api';
import { MapCanvas } from './components/MapCanvas';
import { StatsDashboard } from './components/StatsDashboard';
import { TileInspector } from './components/TileInspector';
import { 
  Globe, 
  Terminal, 
  Play, 
  RefreshCcw,
  BarChart3,
  Waves
} from 'lucide-react';

const App: React.FC = () => {
  const [status, setStatus] = useState<WSMessage | null>(null);
  const [factions, setFactions] = useState<any[]>([]);
  const [mapData, setMapData] = useState<number[] | null>(null);
  const [territories, setTerritories] = useState<number[] | null>(null);
  const [hoverInfo, setHoverInfo] = useState<any | null>(null);
  const [logs, setLogs] = useState<any[]>([]);
  const [isTicking, setIsTicking] = useState(false);

  useEffect(() => {
    // 1. 초기 파벌 정보 로드
    fetch(`http://${window.location.hostname}:8000/factions`)
      .then(res => res.json())
      .then(data => setFactions(data.factions));

    // 2. 초기 맵 데이터 로드 (영토 정보 포함)
    api.getMap().then(data => {
      if (data.data) setMapData(data.data);
      if (data.territories) setTerritories(data.territories);
    });

    // 3. WebSocket 실시간 연동
    const unsub = api.onMessage((msg: any) => {
      if (msg.type === 'INIT' || msg.type === 'UPDATE' || msg.type === 'SUMMARY') {
        setStatus(prev => ({ ...prev, ...msg }));
        if (msg.events) {
          setLogs(prev => [...msg.events!, ...prev].slice(0, 50));
        }
        if (msg.map?.data) {
          setMapData(msg.map.data);
        }
        if (msg.map?.territories) {
          setTerritories(msg.map.territories);
        }
      }
    });

    return unsub;
  }, []);

  const handleTileHover = (x: number, y: number, terrainType: number) => {
    if (!territories) return;
    const idx = y * 100 + x;
    const ownerIdx = territories[idx];
    
    // 지형 이름 매핑
    const terrainNames = ["Water", "Plains", "Forest", "Mountain", "Snow", "Tundra", "Desert", "Wasteland", "Tropical"];
    const terrainName = terrainType !== -1 ? terrainNames[terrainType] : "Unknown";
    
    let ownerInfo = undefined;
    if (ownerIdx !== -1 && factions[ownerIdx]) {
      const f = factions[ownerIdx];
      ownerInfo = {
        name: f.name,
        race: f.race,
        population: f.population,
        scale: f.scale_display,
        status: "Peaceful", // 추후 확장
        leader: f.leader?.name,
        capitalPos: { x: f.location.x, y: f.location.y }
      };
    }

    setHoverInfo({
      x, y,
      terrain: terrainName,
      owner: ownerInfo
    });
  };

  const handleTick = async () => {
    setIsTicking(true);
    try {
      await api.triggerTick();
      // 틱 이후 파벌 인구 등 정보 갱신을 위해 재로드
      const res = await fetch(`http://${window.location.hostname}:8000/factions`);
      const data = await res.json();
      setFactions(data.factions);
    } catch (err) {
      console.error(err);
    } finally {
      setTimeout(() => setIsTicking(false), 300);
    }
  };

  return (
    <div className="min-h-screen p-6 flex flex-col gap-6" style={{ height: '100vh' }}>
      {/* Header */}
      <header className="flex justify-between items-center glass p-6 rounded-2xl animate-fade-in">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-primary/20 rounded-xl">
            <Globe className="text-primary" size={28} />
          </div>
          <div>
            <h1 className="text-2xl font-bold">WorldAI Simulation</h1>
            <p className="text-text-muted text-sm font-medium">Real-time Fantasy World Monitoring</p>
          </div>
        </div>
        
        <div className="flex items-center gap-6 text-sm">
          <StatBox label="Current Tick" value={status?.tick ?? 0} icon={<RefreshCcw size={14} />} />
          <StatBox label="Time" value={`${status?.hour ?? 0}:00`} icon={<RefreshCcw size={14} />} />
          <StatBox label="Year" value={status?.year ?? 1} icon={<BarChart3 size={14} />} />
          <StatBox label="Season" value={status?.season ?? "Spring"} icon={<Waves size={14} />} />
          
          <button 
            onClick={handleTick}
            disabled={isTicking}
            className={`btn-primary rounded-xl px-6 py-3 font-bold ${isTicking ? 'glow' : ''}`}
            style={{ minWidth: '140px' }}
          >
            <Play size={18} fill="currentColor" style={{ marginRight: '8px' }} />
            <span>Next Tick</span>
          </button>
        </div>
      </header>

      {/* Main Grid */}
      <main className="layout-grid flex-1 overflow-hidden" style={{ minHeight: 0 }}>
        
        {/* Left: Map */}
        <section className="col-8 flex flex-col gap-6 animate-fade-in overflow-y-auto" style={{ animationDelay: '0.1s' }}>
          <MapCanvas 
            onHover={handleTileHover} 
            mapData={mapData}
            territories={territories} 
            factions={factions}
            hoverInfo={hoverInfo}
          />
          
          <div className="grid grid-cols-2 gap-6">
            <StatsDashboard />
            <div className="card glass p-6 flex flex-col gap-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-text-muted text-xs uppercase font-bold tracking-wider">
                  <BarChart3 size={14} /> Faction Influence
                </div>
                <span className="text-[10px] text-primary">Top 3</span>
              </div>
              <div className="space-y-4">
                <div className="space-y-1">
                  <div className="flex justify-between text-xs"><span className="font-bold">Central Empire</span> <span className="text-text-muted">45%</span></div>
                  <div className="h-1.5 bg-white/5 rounded-full overflow-hidden"><div className="h-full bg-primary w-[45%]"></div></div>
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between text-xs"><span className="font-bold">Ancient Forest</span> <span className="text-text-muted">22%</span></div>
                  <div className="h-1.5 bg-white/5 rounded-full overflow-hidden"><div className="h-full bg-accent w-[22%]"></div></div>
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between text-xs"><span className="font-bold">Ironpeak</span> <span className="text-text-muted">18%</span></div>
                  <div className="h-1.5 bg-white/5 rounded-full overflow-hidden"><div className="h-full bg-yellow-500 w-[18%]"></div></div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Right: Logs & Inspector */}
        <section className="col-4 flex flex-col gap-6 animate-fade-in h-full overflow-hidden" style={{ animationDelay: '0.2s' }}>
          <div className="h-1/2">
             <TileInspector info={hoverInfo} />
          </div>
          
          <div className="card glass p-6 flex flex-col h-half overflow-hidden">
            <div className="flex items-center gap-2 mb-4">
              <Terminal size={18} className="text-primary" />
              <h2 className="text-lg font-bold">Simulation Event Feed</h2>
            </div>
            
            <div className="flex-1 overflow-y-auto gap-3 flex flex-col" style={{ paddingRight: '8px' }}>
              {logs.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center color-darker italic">
                  Waiting for events...
                </div>
              ) : (
                logs.map((log, i) => (
                  <div key={i} className="p-3 rounded-lg bg-white-5 border-w-5 animate-fade-in">
                    <div className="flex justify-between text-xs font-bold color-primary mb-1">
                      <span style={{ fontSize: '10px', textTransform: 'uppercase' }}>{log.event_type}</span>
                      <span className="color-darker">Tick {log.tick}</span>
                    </div>
                    <div className="font-bold text-sm mb-1">{log.title}</div>
                    <p className="text-xs color-muted" style={{ lineHeight: '1.5' }}>{log.description}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        </section>
      </main>

      <style>{`
        .glow {
          box-shadow: 0 0 20px var(--primary-glow);
        }
      `}</style>
    </div>
  );
};

const StatBox = ({ label, value, icon }: { label: string, value: string | number, icon: React.ReactNode }) => (
  <div className="flex flex-col items-end">
    <span className="text-[10px] uppercase font-bold text-text-darker flex items-center gap-1">
      {icon} {label}
    </span>
    <span className="text-lg font-bold text-text-main leading-none mt-1">{value}</span>
  </div>
);

export default App;
