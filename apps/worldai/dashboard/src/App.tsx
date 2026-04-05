import React, { useEffect, useState } from 'react';
import { api } from './api';
import type { WSMessage } from './api';
import { MapCanvas } from './components/MapCanvas';
import { StatsDashboard } from './components/StatsDashboard';
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
  const [logs, setLogs] = useState<any[]>([]);
  const [isTicking, setIsTicking] = useState(false);

  useEffect(() => {
    const unsub = api.onMessage((msg) => {
      if (msg.type === 'INIT' || msg.type === 'UPDATE' || msg.type === 'SUMMARY') {
        setStatus(prev => ({ ...prev, ...msg }));
        if (msg.events) {
          setLogs(prev => [...msg.events!, ...prev].slice(0, 50));
        }
      }
    });

    return unsub;
  }, []);

  const handleTick = async () => {
    setIsTicking(true);
    try {
      await api.triggerTick();
    } catch (err) {
      console.error(err);
    } finally {
      setTimeout(() => setIsTicking(false), 300);
    }
  };

  return (
    <div className="min-h-screen p-6 flex flex-col gap-6">
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
          <StatBox label="Year" value={status?.year ?? 1} icon={<BarChart3 size={14} />} />
          <StatBox label="Season" value={status?.season ?? "Spring"} icon={<Waves size={14} />} />
          
          <button 
            onClick={handleTick}
            disabled={isTicking}
            className={`flex items-center gap-2 px-6 py-3 rounded-xl bg-primary text-white font-bold transition-all hover:scale-105 active:scale-95 disabled:opacity-50 ${isTicking ? 'glow' : ''}`}
          >
            <Play size={18} fill="currentColor" />
            <span>Next Tick</span>
          </button>
        </div>
      </header>

      {/* Main Grid */}
      <main className="grid grid-cols-12 gap-6 flex-1">
        
        {/* Left: Map */}
        <section className="col-span-8 flex flex-col gap-6 animate-fade-in" style={{ animationDelay: '0.1s' }}>
          <MapCanvas />
          
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

        {/* Right: Logs */}
        <section className="col-span-4 flex flex-col gap-6 animate-fade-in" style={{ animationDelay: '0.2s' }}>
          <div className="card glass p-6 flex flex-col flex-1 h-[600px]">
            <div className="flex items-center gap-2 mb-4">
              <Terminal size={18} className="text-primary" />
              <h2 className="text-lg font-bold">Simulation Event Feed</h2>
            </div>
            
            <div className="flex-1 overflow-y-auto pr-2 space-y-3">
              {logs.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-text-darker italic">
                  Waiting for events...
                </div>
              ) : (
                logs.map((log, i) => (
                  <div key={i} className="p-3 rounded-lg bg-white/5 border border-white/5 hover:bg-white/10 transition-colors animate-fade-in">
                    <div className="flex justify-between text-[10px] uppercase font-bold text-primary mb-1">
                      <span>{log.event_type}</span>
                      <span className="text-text-darker">Tick {log.tick}</span>
                    </div>
                    <div className="font-bold text-sm mb-1">{log.title}</div>
                    <p className="text-xs text-text-muted leading-relaxed">{log.description}</p>
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
