import React, { useEffect, useRef, useState } from 'react';
import { api } from '../api';

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

export const MapCanvas: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [mapData, setMapData] = useState<number[] | null>(null);
  const [hoverTile, setHoverTile] = useState<{x: number, y: number} | null>(null);

  useEffect(() => {
    // 초기 맵 데이터 로드
    api.getMap().then(data => {
      setMapData(data.data);
    });
  }, []);

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

    // 그리기
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const typeIndex = mapData[y * width + x];
        ctx.fillStyle = TILE_COLORS[typeIndex] || '#000';
        ctx.fillRect(x * tileSize, y * tileSize, tileSize, tileSize);
        
        // 아주 미세한 그리드 라인
        ctx.strokeStyle = 'rgba(255,255,255,0.03)';
        ctx.strokeRect(x * tileSize, y * tileSize, tileSize, tileSize);
      }
    }
  }, [mapData]);

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const x = Math.floor((e.clientX - rect.left) / 8);
    const y = Math.floor((e.clientY - rect.top) / 8);
    if (x >= 0 && x < 100 && y >= 0 && y < 80) {
      setHoverTile({ x, y });
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
      <div className="relative border border-white/5 rounded-lg overflow-hidden bg-black">
        <canvas 
          ref={canvasRef} 
          onMouseMove={handleMouseMove}
          onMouseLeave={() => setHoverTile(null)}
          className="cursor-crosshair shadow-2xl"
        />
      </div>
      <div className="mt-4 flex gap-4 text-xs font-medium text-text-muted">
        <div className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-[#22c55e]"></span> Plains</div>
        <div className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-[#166534]"></span> Forest</div>
        <div className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-[#0ea5e9]"></span> Water</div>
        <div className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-[#e2e8f0]"></span> Snow</div>
        <div className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-[#eab308]"></span> Desert</div>
      </div>
    </div>
  );
};
