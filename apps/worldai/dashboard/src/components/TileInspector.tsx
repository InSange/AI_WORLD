import React from 'react';
import { 
  MapPin, 
  Users, 
  Sword, 
  TrendingUp, 
  Shield, 
  Crown,
  Info
} from 'lucide-react';

interface TileInfo {
  x: number;
  y: number;
  terrain: string;
  owner?: {
    name: string;
    race: string;
    population: number;
    scale: string;
    status: string;
    leader?: string;
    leaderTitle?: string;
    capitalPos: { x: number, y: number };
    military?: number;
    specialties?: string[];
    recentEvents?: any[];
  };
}

interface TileInspectorProps {
  info: TileInfo | null;
}

export const TileInspector: React.FC<TileInspectorProps> = ({ info }) => {
  if (!info) {
    return (
      <div className="card glass p-8 flex flex-col items-center justify-center color-darker border-dash border-w-5 h-full" style={{ minHeight: '300px' }}>
        <MapPin size={48} className="mb-4" style={{ opacity: 0.2 }} />
        <p className="text-sm font-bold text-center">
          Hover over the map to inspect<br />territory details
        </p>
      </div>
    );
  }

  const { x, y, terrain, owner } = info;

  return (
    <div className="card glass p-6 flex flex-col gap-6 animate-fade-in h-full overflow-y-auto">
      {/* Header: Coordinates & Terrain */}
      <div className="flex justify-between items-start">
        <div>
          <div className="text-xs font-bold color-primary mb-1" style={{ textTransform: 'uppercase', letterSpacing: '0.1em' }}>Regional Intel</div>
          <h2 className="text-2xl font-black uppercase" style={{ letterSpacing: '-0.02em', lineHeight: '1' }}>
            Tile #{y * 100 + x}
          </h2>
        </div>
        <div className="bg-white-5 border-w-5 p-1 px-3 rounded-xl text-xs font-bold color-muted">
          X: {x} Y: {y}
        </div>
      </div>

      {/* Terrain Badge */}
      <div className="flex items-center gap-3 p-3 bg-white-5 rounded-xl border-w-5">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center terrain-${(terrain || 'plains').toLowerCase()}`} style={{ width: '40px', height: '40px', flexShrink: 0 }}>
          <Info size={20} style={{ color: 'white' }} />
        </div>
        <div>
          <div className="text-xs font-bold color-darker" style={{ textTransform: 'uppercase', fontSize: '10px' }}>Terrain Type</div>
          <div className="font-bold text-sm">{terrain}</div>
        </div>
      </div>

      {/* Territory Info */}
      <div className="flex flex-col gap-4">
        <h3 className="text-xs uppercase font-bold color-muted flex items-center gap-2">
          <Shield size={14} className="color-primary" /> Territory Ownership
        </h3>
        
        {owner ? (
          <div className="flex flex-col gap-4 p-4 bg-primary-5 border-w-5 rounded-2xl relative overflow-hidden" style={{ borderColor: 'rgba(99, 102, 241, 0.2)' }}>
            <div style={{ position: 'absolute', top: 0, right: 0, padding: '16px', opacity: 0.05 }}>
              <Crown size={64} />
            </div>
            
            <div style={{ position: 'relative' }}>
              <div className="text-xs font-bold color-primary mb-2" style={{ textTransform: 'uppercase', fontSize: '10px', textDecoration: 'underline', textDecorationColor: 'rgba(99, 102, 241, 0.3)', textUnderlineOffset: '4px' }}>
                Under Authority Of
              </div>
              <div className="text-xl font-bold mb-1">{owner.name}</div>
              <div className="flex justify-between items-center">
                <div className="text-xs font-bold color-muted flex items-center gap-1">
                  <span style={{ textTransform: 'capitalize' }}>{owner.race}</span> {owner.scale}
                </div>
                <div className="text-[10px] font-black color-primary bg-primary-5 p-1 px-2 rounded flex items-center gap-1 border-w-5">
                   <MapPin size={10} /> CAPITAL: {owner.capitalPos.x}, {owner.capitalPos.y}
                </div>
              </div>
            </div>

            <div className="layout-grid gap-3" style={{ gridTemplateColumns: '1fr 1fr', marginTop: '8px' }}>
              <div className="bg-black-20 p-3 rounded-xl border-w-5">
                <div className="flex items-center gap-2 color-muted font-bold mb-1" style={{ fontSize: '10px' }}>
                  <Users size={12} /> POPULATION
                </div>
                <div className="text-lg font-bold">{owner.population.toLocaleString()}</div>
              </div>
              <div className="bg-black-20 p-3 rounded-xl border-w-5">
                <div className="flex items-center gap-2 color-muted font-bold mb-1" style={{ fontSize: '10px' }}>
                  <Sword size={12} /> MILITARY
                </div>
                <div className="text-sm font-bold text-red-400">
                  {Math.round(owner.military || 0).toLocaleString()}
                </div>
              </div>
            </div>

            {owner.specialties && owner.specialties.length > 0 && (
              <div className="flex gap-2 mt-2 flex-wrap">
                 {owner.specialties.map(spec => (
                    <span key={spec} className="px-2 py-1 bg-white-10 rounded text-[10px] uppercase font-bold text-text-muted">
                        {spec.replace('_', ' ')}
                    </span>
                 ))}
              </div>
            )}

            <div style={{ marginTop: '8px', padding: '8px', backgroundColor: 'rgba(0,0,0,0.2)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
              <div className="text-[10px] color-muted font-bold uppercase mb-1">Ruler / Leader</div>
              <div className="font-bold text-sm color-primary flex items-center gap-2">
                 <Crown size={14} className="text-yellow-500" />
                 {owner.leader ? `${owner.leaderTitle || ''} ${owner.leader}` : "No Ruling Leader"}
              </div>
            </div>

            {/* Recent Events */}
            {owner.recentEvents && owner.recentEvents.length > 0 && (
              <div style={{ marginTop: '8px' }}>
                <div className="text-[10px] color-muted font-bold uppercase mb-2">Recent Activities</div>
                <div className="flex flex-col gap-2">
                  {owner.recentEvents.map((evt: any, i: number) => (
                    <div key={i} className="bg-black-20 p-2 rounded-lg border-w-5">
                      <div className="text-[10px] uppercase font-bold text-yellow-400 mb-1">{evt.type || evt.event_type} (Tick {evt.tick})</div>
                      <div className="text-xs font-bold">{evt.title}</div>
                      <div className="text-[10px] color-muted mt-1 leading-tight">{evt.description}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="p-8 text-center bg-white-5 border-dash border-w-5 rounded-2xl">
            <p className="text-xs color-darker font-bold">Unclaimed Neutral Territory</p>
          </div>
        )}
      </div>

      {/* Strategic Value */}
      <div style={{ marginTop: 'auto' }}>
        <h3 className="text-xs uppercase font-bold color-muted flex items-center gap-2 mb-3">
          <TrendingUp size={14} className="color-primary" /> Strategic Intelligence
        </h3>
        <p className="text-xs color-muted italic" style={{ fontSize: '11px', lineHeight: '1.5' }}>
          {owner 
             ? `Strategic foothold for the ${owner.name}. This area provides significant military and economic leverage over neighboring districts.`
             : "Wild and untamed lands. High potential for monster activity or resource harvesting, but lacks established protection."}
        </p>
      </div>

      <style>{`
        .terrain-water { background-color: var(--tile-water); }
        .terrain-plains { background-color: var(--tile-plains); }
        .terrain-forest { background-color: var(--tile-forest); }
        .terrain-mountain { background-color: var(--tile-mountain); }
        .terrain-snow { background-color: var(--tile-snow); }
        .terrain-tundra { background-color: var(--tile-tundra); }
        .terrain-desert { background-color: var(--tile-desert); }
        .terrain-wasteland { background-color: var(--tile-wasteland); }
        .terrain-tropical { background-color: var(--tile-tropical); }
      `}</style>
    </div>
  );
};
