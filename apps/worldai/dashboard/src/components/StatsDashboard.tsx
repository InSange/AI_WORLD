import React from 'react';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';

const data = [
  { name: 'Tick 1', pop: 4000, mil: 2400 },
  { name: 'Tick 2', pop: 4200, mil: 2500 },
  { name: 'Tick 3', pop: 4350, mil: 2300 },
  { name: 'Tick 4', pop: 4400, mil: 2600 },
  { name: 'Tick 5', pop: 4600, mil: 2800 },
];

export const StatsDashboard: React.FC = () => {
  return (
    <div className="card glass p-6 h-[250px]">
      <h3 className="text-sm font-bold mb-4 flex justify-between items-center">
        Population & Military Growth
        <span className="text-[10px] text-primary bg-primary/10 px-2 py-0.5 rounded">Real-time</span>
      </h3>
      <div className="h-[180px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="colorPop" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
            <XAxis dataKey="name" hide />
            <YAxis hide />
            <Tooltip 
              contentStyle={{ background: '#1a1a1c', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
              itemStyle={{ fontSize: '12px' }}
            />
            <Area 
              type="monotone" 
              dataKey="pop" 
              stroke="#6366f1" 
              fillOpacity={1} 
              fill="url(#colorPop)" 
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
