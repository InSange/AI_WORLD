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
    capitalPos: { x: number, y: number };
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
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center terrain-${terrain.toLowerCase()}`} style={{ width: '40px', height: '40px', flexShrink: 0 }}>
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
                  <Sword size={12} /> STATUS
                </div>
                <div className="text-sm font-bold" style={{ color: owner.status === 'Conflict' ? 'var(--accent)' : '#4ade80' }}>
                  {owner.status}
                </div>
              </div>
            </div>

            <div style={{ marginTop: '8px' }}>
              <div className="p-1 px-2 rounded font-black color-primary" style={{ display: 'inline-block', backgroundColor: 'rgba(99, 102, 241, 0.2)', fontSize: '9px', textTransform: 'uppercase' }}>
                Leader: {owner.leader || "Unknown"}
              </div>
            </div>
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
