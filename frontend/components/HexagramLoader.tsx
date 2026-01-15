import React from 'react';

interface HexagramLoaderProps {
  lines: number[]; // 0 or 1
}

const HexagramLoader: React.FC<HexagramLoaderProps> = ({ lines }) => {
  return (
    <div className="flex flex-col-reverse gap-3 my-6 w-40 mx-auto p-6 bg-black/60 border-2 border-green-900 rounded-sm relative overflow-hidden">
       {/* 绿色微光 */}
       <div className="absolute inset-0 bg-green-900/10 animate-pulse pointer-events-none"></div>

      {[...Array(6)].map((_, i) => (
        <div key={i} className={`h-3 transition-all duration-300 flex justify-between relative ${i < lines.length ? 'opacity-100 scale-100' : 'opacity-10 scale-95'}`}>
          {/* 模拟全息能量条 */}
          {i < lines.length ? (
            lines[i] === 1 ? (
              <div 
                className="w-full bg-green-500 h-full animate-fade-in"
                style={{ boxShadow: '0 0 10px #22c55e' }}
              ></div> // 阳爻
            ) : (
              <>
               <div className="bg-green-500 h-full" style={{ width: '45%', boxShadow: '0 0 10px #22c55e' }}></div>
               <div className="bg-green-500 h-full" style={{ width: '45%', boxShadow: '0 0 10px #22c55e' }}></div> 
              </> // 阴爻
            )
          ) : (
            <div className="w-full bg-gray-800 h-full border border-green-900/30"></div>
          )}
        </div>
      ))}
    </div>
  );
};

export default HexagramLoader;