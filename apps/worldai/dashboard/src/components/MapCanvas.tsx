import React, { useEffect, useRef, useState } from 'react';

const TILE_COLORS: Record<number, string> = {
  0: '#0ea5e9', // WATER
  1: '#22c55e', // PLAINS
  2: '#166534', // FOREST
  3: '#475569', // MOUNTAIN
  4: '#e2e8f0', // SNOW
  5: '#94a3b8', // TUNDRA
  6: '#eab308', // DESERT
  7: '#78350f', // WASTELAND
  8: '#059669', // TROPICAL
};

const FACTION_COLORS: Record<string, string> = {
    'human': '#3b82f6',
    'elf': '#10b981',
    'orc': '#ef4444',
    'dwarf': '#f59e0b',
    'undead': '#8b5cf6',
    'fairy': '#ec4899',
    'dragon': '#f43f5e',
    'beastman': '#14b8a6',
    'golem': '#64748b',
    'elemental': '#06b6d4',
    'default': '#ffffff'
};

interface MapCanvasProps {
  onHover: (x: number, y: number, terrainType: number) => void;
  mapData: number[] | null;
  territories: number[] | null;
  factions: any[];
  hoverInfo: any | null;
}

export const MapCanvas: React.FC<MapCanvasProps> = ({ onHover, mapData, territories, factions, hoverInfo }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [hoverTile, setHoverTile] = useState<{x: number, y: number} | null>(null);

  // 내부 데이터 로딩 로직 제거 (App.tsx에서 중앙 관리)

  useEffect(() => {
    if (!mapData || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = 100;
    const height = 80;
    const tileSize = 8;

    canvas.width = width * tileSize;
    canvas.height = height * tileSize;

    // 1. 지형 배경 그리기
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const idx = y * width + x;
        const typeIndex = mapData[idx];
        ctx.fillStyle = TILE_COLORS[typeIndex] || '#000';
        ctx.fillRect(x * tileSize, y * tileSize, tileSize, tileSize);
        
        ctx.strokeStyle = 'rgba(255,255,255,0.03)';
        ctx.strokeRect(x * tileSize, y * tileSize, tileSize, tileSize);
      }
    }

    // 2. 영토 소유자 표시
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const idx = y * width + x;
        if (territories && territories[idx] !== -1) {
            ctx.fillStyle = 'rgba(255,255,255,0.15)';
            ctx.fillRect(x * tileSize + 3, y * tileSize + 3, 2, 2);
        }
      }
    }

    // 3. 파벌 거점(도시) 표시
    factions.forEach((f) => {
        if (!f.is_alive || !f.location) return;
        const x = f.location.x;
        const y = f.location.y;
        const color = FACTION_COLORS[f.race.toLowerCase()] || FACTION_COLORS.default;

        // 마커 배경 (빛나는 다이아몬드)
        ctx.fillStyle = color;
        ctx.shadowBlur = 10;
        ctx.shadowColor = color;
        
        ctx.beginPath();
        ctx.moveTo(x * tileSize + tileSize/2, y * tileSize); // 위
        ctx.lineTo(x * tileSize + tileSize, y * tileSize + tileSize/2); // 우
        ctx.lineTo(x * tileSize + tileSize/2, y * tileSize + tileSize); // 아래
        ctx.lineTo(x * tileSize, y * tileSize + tileSize/2); // 좌
        ctx.closePath();
        ctx.fill();
        
        ctx.shadowBlur = 0; // 그림자 초기화

        // 테두리
        ctx.strokeStyle = 'white';
        ctx.lineWidth = 1;
        ctx.stroke();
    });

    // 4. 하이라이트 연동 (호버한 타일의 주인이 있으면 거점 강조)
    if (hoverInfo?.owner?.capitalPos) {
        const startX = hoverInfo.x * tileSize + tileSize/2;
        const startY = hoverInfo.y * tileSize + tileSize/2;
        const endX = hoverInfo.owner.capitalPos.x * tileSize + tileSize/2;
        const endY = hoverInfo.owner.capitalPos.y * tileSize + tileSize/2;

        // 1. 연결선 (Dashed Line)
        ctx.setLineDash([4, 4]);
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(startX, startY);
        ctx.lineTo(endX, endY);
        ctx.stroke();
        ctx.setLineDash([]); // 대시 초기화

        // 2. 거점 타겟팅 서클
        ctx.strokeStyle = FACTION_COLORS[hoverInfo.owner.race] || '#fff';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(endX, endY, tileSize * 2, 0, Math.PI * 2);
        ctx.stroke();

        ctx.fillStyle = 'rgba(255,255,255,0.2)';
        ctx.fill();
    }
  }, [mapData, territories, factions, hoverInfo]);

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current) return;
    const rect = canvasRef.current.getBoundingClientRect();
    
    // 캔버스 크기에 상관없이 100x80 그리드로 정규화하여 계산
    const x = Math.floor(((e.clientX - rect.left) / rect.width) * 100);
    const y = Math.floor(((e.clientY - rect.top) / rect.height) * 80);
    
    if (x >= 0 && x < 100 && y >= 0 && y < 80) {
      setHoverTile({ x, y });
      const terrainType = mapData ? mapData[y * 100 + x] : -1;
      onHover(x, y, terrainType);
    }
  };

  return (
    <div className="card glass p-4 flex flex-col items-center">
      <div className="flex justify-between w-full mb-3 px-2">
        <h3 className="text-lg font-bold">World Map (100x80)</h3>
        {hoverTile && (
          <span className="text-text-muted text-sm uppercase">
            Coord: {hoverTile.x}, {hoverTile.y}
          </span>
        )}
      </div>
      <div className="relative border-w-5 rounded-lg overflow-hidden bg-black-20 w-full flex justify-center">
        <canvas 
          ref={canvasRef} 
          onMouseMove={handleMouseMove}
          onMouseLeave={() => setHoverTile(null)}
          className="cursor-crosshair shadow-2xl"
          style={{ display: 'block' }}
        />
      </div>
      <div className="mt-4 w-full flex flex-col gap-4">
        <div className="flex gap-4 text-xs font-bold color-muted flex-wrap justify-center border-w-5 p-3 rounded-xl bg-white-5">
           <span className="color-darker uppercase mr-2" style={{ borderRight: '1px solid var(--border)', paddingRight: '12px' }}>Terrain</span>
           <LegendItem color="#0ea5e9" label="Water" />
           <LegendItem color="#22c55e" label="Plains" />
           <LegendItem color="#166534" label="Forest" />
           <LegendItem color="#475569" label="Mountain" />
           <LegendItem color="#e2e8f0" label="Snow" />
           <LegendItem color="#94a3b8" label="Tundra" />
           <LegendItem color="#eab308" label="Desert" />
           <LegendItem color="#78350f" label="Wasteland" />
           <LegendItem color="#059669" label="Tropical" />
        </div>

        <div className="flex gap-4 text-xs font-bold color-muted flex-wrap justify-center border-w-5 p-3 rounded-xl bg-white-5">
           <span className="color-darker uppercase mr-2" style={{ borderRight: '1px solid var(--border)', paddingRight: '12px' }}>Factions</span>
           {Object.entries(FACTION_COLORS).filter(([k]) => k !== 'default').map(([race, color]) => (
             <LegendItem key={race} color={color} label={race.toUpperCase()} isDiamond />
           ))}
        </div>
      </div>
    </div>
  );
};

const LegendItem = ({ color, label, isDiamond }: { color: string, label: string, isDiamond?: boolean }) => (
  <div className="flex items-center gap-1">
    {isDiamond ? (
      <span className="w-2.5 h-2.5" style={{ backgroundColor: color, transform: 'rotate(45deg)', display: 'inline-block' }}></span>
    ) : (
      <span className="w-3 h-3 rounded-full" style={{ backgroundColor: color }}></span>
    )}
    {label}
  </div>
);
