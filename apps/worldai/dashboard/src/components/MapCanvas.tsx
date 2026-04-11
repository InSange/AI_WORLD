import React, { useEffect, useRef, useState } from 'react';

const TILE_COLORS: Record<number, string> = {
  0: '#0ea5e9', // OCEAN
  1: '#22c55e', // PLAINS
  2: '#166534', // FOREST
  3: '#475569', // MOUNTAIN
  4: '#e2e8f0', // SNOW
  5: '#eab308', // DESERT
  6: '#78350f', // WASTELAND
  7: '#38bdf8', // LAKE
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
  onClick: (x: number, y: number, terrainType: number) => void;
  mapData: number[] | null;
  territories: number[] | null;
  factions: any[];
  hoverInfo: any | null;
  width: number;
  height: number;
}

export const MapCanvas: React.FC<MapCanvasProps> = ({ onClick, mapData, territories, factions, hoverInfo, width, height }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [hoverTile, setHoverTile] = useState<{x: number, y: number} | null>(null);
  const [zoom, setZoom] = useState<number>(1.0);
  const [pan, setPan] = useState<{x: number, y: number}>({x: 0, y: 0});
  const [isDragging, setIsDragging] = useState(false);
  const [dragStartPos, setDragStartPos] = useState<{x: number, y: number} | null>(null);

  // 내부 데이터 로딩 로직 제거 (App.tsx에서 중앙 관리)

  useEffect(() => {
    if (!mapData || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const tileSize = width >= 150 ? 5 : 7; // 150x150의 경우 5로 맞춰 캔버스 크기(750)를 보기 좋게 함

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

    // 3. 파벌 거점(도시) 표시 - 종족별 아이콘
    factions.forEach((f) => {
        if (!f.location) return; // API에서 죽은 파벌은 안주므로 is_alive 검사 제거
        const x = f.location.x;
        const y = f.location.y;
        const color = FACTION_COLORS[f.race.toLowerCase()] || FACTION_COLORS.default;

        drawFactionIcon(ctx, x * tileSize, y * tileSize, tileSize, f.race.toLowerCase(), color);
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

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (isDragging) {
       setPan(prev => ({ x: prev.x + e.movementX, y: prev.y + e.movementY }));
       return;
    }
  
    if (!canvasRef.current) return;
    const rect = canvasRef.current.getBoundingClientRect();
    
    // 동적 그리드 정규화
    const x = Math.floor(((e.clientX - rect.left) / rect.width) * width);
    const y = Math.floor(((e.clientY - rect.top) / rect.height) * height);
    
    if (x >= 0 && x < width && y >= 0 && y < height) {
      setHoverTile({ x, y });
    } else {
      setHoverTile(null);
    }
  };

  const handlePointerDown = (e: React.MouseEvent<HTMLDivElement>) => {
    setIsDragging(true);
    setDragStartPos({ x: e.clientX, y: e.clientY });
  };

  const handlePointerUp = (e: React.MouseEvent<HTMLDivElement>) => {
    setIsDragging(false);
    if (!dragStartPos) return;

    // 단순 클릭 여부 판별 (드래그 거리가 5px 이하)
    const dist = Math.abs(e.clientX - dragStartPos.x) + Math.abs(e.clientY - dragStartPos.y);
    if (dist < 5 && canvasRef.current) {
        const rect = canvasRef.current.getBoundingClientRect();
        const x = Math.floor(((e.clientX - rect.left) / rect.width) * width);
        const y = Math.floor(((e.clientY - rect.top) / rect.height) * height);
        
        if (x >= 0 && x < width && y >= 0 && y < height) {
            const terrainType = mapData ? mapData[y * width + x] : -1;
            onClick(x, y, terrainType);
        }
    }
    setDragStartPos(null);
  };

  const handleWheel = (e: React.WheelEvent<HTMLDivElement>) => {
    e.preventDefault();
    setZoom(prev => Math.max(0.5, Math.min(5, prev - e.deltaY * 0.001)));
  };

  return (
    <div className="card glass p-4 flex flex-col items-center">
      <div className="flex justify-between w-full mb-3 px-2 items-center">
        <h3 className="text-lg font-bold">World Map ({width}x{height})</h3>
        {hoverTile && (
          <span className="text-text-muted text-sm uppercase">
            Coord: {hoverTile.x}, {hoverTile.y}
          </span>
        )}
      </div>
      <div 
        className="relative border-w-5 rounded-lg overflow-hidden bg-black-20 w-full flex justify-center items-center" 
        style={{ minHeight: "400px" }}
        onWheel={handleWheel}
      >
        <div 
          style={{ 
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`, 
            transformOrigin: "center center", 
            transition: isDragging ? "none" : "transform 0.1s ease-out",
            cursor: isDragging ? "grabbing" : "crosshair"
          }}
          onMouseDown={handlePointerDown}
          onMouseUp={handlePointerUp}
          onMouseLeave={() => { setIsDragging(false); setHoverTile(null); }}
          onMouseMove={handleMouseMove}
        >
            <canvas 
              ref={canvasRef} 
              style={{ display: 'block' }}
            />
        </div>
      </div>
      <div className="mt-4 w-full flex flex-col gap-4">
        <div className="flex gap-4 text-xs font-bold color-muted flex-wrap justify-center border-w-5 p-3 rounded-xl bg-white-5">
           <span className="color-darker uppercase mr-2" style={{ borderRight: '1px solid var(--border)', paddingRight: '12px' }}>Terrain</span>
           <LegendItem color="#0ea5e9" label="Ocean" />
           <LegendItem color="#38bdf8" label="Lake" />
           <LegendItem color="#22c55e" label="Plains" />
           <LegendItem color="#166534" label="Forest" />
           <LegendItem color="#475569" label="Mountain" />
           <LegendItem color="#e2e8f0" label="Snow" />
           <LegendItem color="#eab308" label="Desert" />
           <LegendItem color="#78350f" label="Wasteland" />
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

const drawFactionIcon = (ctx: CanvasRenderingContext2D, x: number, y: number, size: number, race: string, color: string) => {
    const emojis: Record<string, string> = {
        human: '🏰',
        elf: '🌿',
        orc: '👹',
        dwarf: '⛏️',
        undead: '💀',
        fairy: '🧚',
        dragon: '🐉',
        beastman: '🐺',
        golem: '🪨',
        elemental: '✨',
        demon: '👿'
    };
    
    // 투명도 복구 및 텍스트 색상 세팅 (앞서 투명도 0.15였음)
    ctx.fillStyle = 'rgba(255, 255, 255, 1)';
    ctx.globalAlpha = 1.0;
    
    // 외곽선 글로우(백라이트) 지정
    ctx.shadowBlur = 10;
    ctx.shadowColor = color;
    
    const emoji = emojis[race] || '🚩';
    const fontSize = Math.max(16, size * 2.5); // 이모지가 잘 보이도록 최소 16px 보장
    
    ctx.font = `${fontSize}px "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    
    const cx = x + size / 2;
    const cy = y + size / 2;
    
    ctx.fillText(emoji, cx, cy);
    
    // 그림자 초기화
    ctx.shadowBlur = 0;
};

const LegendItem = ({ color, label, isDiamond }: { color: string, label: string, isDiamond?: boolean }) => (
  <div className="flex items-center gap-1">
    {isDiamond ? (
      <span className="w-2.5 h-2.5" style={{ backgroundColor: color, transform: 'rotate(45deg)', display: 'inline-block', border: '1px solid white' }}></span>
    ) : (
      <span className="w-3 h-3 rounded-full" style={{ backgroundColor: color }}></span>
    )}
    {label}
  </div>
);
