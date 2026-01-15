import React from 'react';

interface HexagramDisplayProps {
  hexagramSymbol: string[];
  className?: string;
}

/**
 * 卦象展示组件
 * 优化后的卦象图标展示，使用视觉化的线条而非文本符号
 */
const HexagramDisplay: React.FC<HexagramDisplayProps> = ({ hexagramSymbol, className = '' }) => {
  // 将文本符号转换为二进制数组（从下往上）
  const lines = hexagramSymbol.map(symbol => {
    // "▅▅▅▅▅" 是阳爻 (1), "▅▅  ▅▅" 是阴爻 (0)
    return symbol.includes('  ') ? 0 : 1;
  }).reverse(); // 反转，从下往上显示

  return (
    <div className={`flex flex-col-reverse gap-1.5 bg-black/80 p-3 border-2 border-green-600/50 rounded relative overflow-hidden ${className}`}
         style={{ 
           boxShadow: '0 0 15px rgba(34, 197, 94, 0.3), inset 0 0 10px rgba(0, 0, 0, 0.5)',
           minWidth: '80px'
         }}>
      {/* 背景光效 */}
      <div className="absolute inset-0 bg-gradient-to-b from-green-900/20 via-transparent to-green-900/20 pointer-events-none"></div>
      <div className="absolute inset-0 bg-green-500/5 animate-pulse pointer-events-none"></div>
      
      {/* 六爻显示 */}
      {lines.map((line, idx) => (
        <div 
          key={idx} 
          className="relative h-2.5 flex items-center justify-center transition-all duration-300"
          style={{
            opacity: 0.9 + (idx * 0.02),
            transform: `translateX(${Math.sin(idx) * 0.5}px)`
          }}
        >
          {line === 1 ? (
            // 阳爻 - 实线
            <div 
              className="w-full h-full bg-green-500 rounded-sm relative overflow-hidden"
              style={{
                boxShadow: '0 0 8px rgba(34, 197, 94, 0.6), inset 0 0 4px rgba(34, 197, 94, 0.3)'
              }}
            >
              <div 
                className="absolute inset-0 bg-gradient-to-r from-transparent via-green-400/50 to-transparent"
                style={{
                  animation: 'shimmer 2s ease-in-out infinite',
                  animationDelay: `${idx * 0.2}s`
                }}
              ></div>
            </div>
          ) : (
            // 阴爻 - 断线（两段）
            <div className="w-full h-full flex justify-between items-center gap-1.5">
              <div 
                className="h-full bg-green-500 rounded-sm relative overflow-hidden"
                style={{
                  boxShadow: '0 0 8px rgba(34, 197, 94, 0.6), inset 0 0 4px rgba(34, 197, 94, 0.3)',
                  width: '45%'
                }}
              >
                <div 
                  className="absolute inset-0 bg-gradient-to-r from-transparent via-green-400/50 to-transparent"
                  style={{
                    animation: 'shimmer 2s ease-in-out infinite',
                    animationDelay: `${idx * 0.2}s`
                  }}
                ></div>
              </div>
              <div 
                className="h-full bg-green-500 rounded-sm relative overflow-hidden"
                style={{
                  boxShadow: '0 0 8px rgba(34, 197, 94, 0.6), inset 0 0 4px rgba(34, 197, 94, 0.3)',
                  width: '45%'
                }}
              >
                <div 
                  className="absolute inset-0 bg-gradient-to-r from-transparent via-green-400/50 to-transparent"
                  style={{
                    animation: 'shimmer 2s ease-in-out infinite',
                    animationDelay: `${idx * 0.2 + 0.1}s`
                  }}
                ></div>
              </div>
            </div>
          )}
        </div>
      ))}
      
      {/* 扫描线效果 */}
      <div 
        className="absolute inset-0 pointer-events-none opacity-30"
        style={{
          background: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(34, 197, 94, 0.1) 2px, rgba(34, 197, 94, 0.1) 4px)',
          animation: 'scan 3s linear infinite'
        }}
      ></div>
    </div>
  );
};

export default HexagramDisplay;
