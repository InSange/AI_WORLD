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
  const [mapWidth, setMapWidth] = useState<number>(100);
  const [mapHeight, setMapHeight] = useState<number>(100);
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
      if (data.width) setMapWidth(data.width);
      if (data.height) setMapHeight(data.height);
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
        if (msg.map?.width) setMapWidth(msg.map.width);
        if (msg.map?.height) setMapHeight(msg.map.height);
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

  const handleTileClick = (x: number, y: number, terrainType: number) => {
    if (!territories) return;
    
    const idx = y * mapWidth + x;
    const ownerIdx = territories[idx];
    
    // 현재 맵의 가로 크기 (100x100 기반) 삭제 이후 인덱싱 부분
    const terrainNames = ["Ocean", "Plains", "Forest", "Mountain", "Snow", "Desert", "Wasteland", "Lake/River"];
    const terrainName = terrainType !== -1 && terrainType < terrainNames.length ? terrainNames[terrainType] : "Unknown";
    
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
        leaderTitle: f.leader?.title,
        capitalPos: { x: f.location.x, y: f.location.y },
        military: f.military_strength,
        specialties: f.specialty,
        recentEvents: logs.filter(l => l.affected?.includes(f.race) || l.affected?.includes(f.id)).slice(0, 3)
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
      const res = await fetch(`http://${window.location.hostname}:8000/factions`);
      const data = await res.json();
      setFactions(data.factions);
    } catch (err) {
      console.error(err);
    } finally {
      setTimeout(() => setIsTicking(false), 300);
    }
  };

  const handleReset = async () => {
    if (!window.confirm("진행 중인 틱과 이벤트를 모두 잃고 월드를 다시 생성하시겠습니까?")) return;
    setIsTicking(true);
    try {
      await api.resetSimulation();
      
      // 맵 및 파벌 즉시 재로드
      const [factionsRes, mapDataRes] = await Promise.all([
        fetch(`http://${window.location.hostname}:8000/factions`),
        api.getMap()
      ]);
      const factionsData = await factionsRes.json();
      setFactions(factionsData.factions);
      
      if (mapDataRes.width) setMapWidth(mapDataRes.width);
      if (mapDataRes.height) setMapHeight(mapDataRes.height);
      if (mapDataRes.data) setMapData(mapDataRes.data);
      if (mapDataRes.territories) setTerritories(mapDataRes.territories);
      
      setStatus(null); // 로컬 상태 초기화
      setLogs([]);
      setHoverInfo(null);
    } catch (err) {
      console.error(err);
    } finally {
      setIsTicking(false);
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
            onClick={handleReset}
            disabled={isTicking}
            className="btn-danger rounded-xl px-4 py-3 font-bold flex items-center bg-red-600/80 hover:bg-red-500/80 transition"
            title="Reset simulation and regenerate map"
          >
            <RefreshCcw size={18} />
          </button>
          
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
            onClick={handleTileClick} 
            mapData={mapData}
            territories={territories} 
            factions={factions}
            hoverInfo={hoverInfo}
            width={mapWidth}
            height={mapHeight}
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
                logs.map((log, i) => {
                  const hasFactions = log.affected_factions && log.affected_factions.length > 0;
                  return (
                  <div 
                    key={i} 
                    className={`p-3 rounded-lg bg-white-5 border-w-5 animate-fade-in ${hasFactions ? 'cursor-pointer hover:bg-white-10 transition' : ''}`}
                    onClick={() => {
                      if (!hasFactions) return;
                      const fid = log.affected_factions[0]; // 주요 당사자 1
                      const faction = factions.find(f => f.id === fid);
                      if (faction) {
                        // API 지형을 모르니 단순히 정보창만 띄우도록
                        handleTileClick(faction.location.x, faction.location.y, -1);
                      }
                    }}
                  >
                    <div className="flex justify-between text-xs font-bold color-primary mb-1">
                      <span style={{ fontSize: '10px', textTransform: 'uppercase' }}>{log.type || log.event_type}</span>
                      <span className="color-darker">Tick {log.tick}</span>
                    </div>
                    <div className="font-bold text-sm mb-1">{log.title}</div>
                    <p className="text-xs color-muted" style={{ lineHeight: '1.5' }}>{log.description}</p>
                    {hasFactions && (
                      <div className="mt-2 text-[10px] text-primary bg-primary/10 rounded px-2 py-1 inline-block">
                        🔍 클릭하여 당사자({factions.find(f => f.id === log.affected_factions[0])?.name}) 정보 보기
                      </div>
                    )}
                  </div>
                )})
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
