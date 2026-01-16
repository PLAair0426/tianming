import React, { useState, useEffect, useRef } from 'react';
import { getDivination, generateSingleLine } from './services/apiService';

// --- SVG 图标组件 (霓虹道士版) ---
const IconWrapper = ({ children, className = '', style = {} }) => (
  <svg 
    xmlns="http://www.w3.org/2000/svg" 
    width="24" 
    height="24" 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="currentColor" 
    strokeWidth="2" 
    strokeLinecap="round" 
    strokeLinejoin="round" 
    className={className}
    style={style}
  >
    {children}
  </svg>
);

// 经典太极图标（动态旋转版）
const Bagua = ({ className = '', style = {} }: { className?: string; style?: any }) => {
  return (
    <svg 
      xmlns="http://www.w3.org/2000/svg" 
      width="24" 
      height="24" 
      viewBox="0 0 24 24" 
      fill="none" 
      stroke="currentColor" 
      strokeWidth="2" 
      strokeLinecap="round" 
      strokeLinejoin="round" 
      className={`${className} animate-spin-slow`}
      style={style}
    >
      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
      <path d="M12 2a5 5 0 0 1 0 10 5 5 0 0 0 0 10" stroke="currentColor" strokeWidth="2" />
      <circle cx="12" cy="7" r="1.5" fill="currentColor" stroke="none" />
      <circle cx="12" cy="17" r="1.5" fill="currentColor" stroke="none" />
    </svg>
  );
};

const Skull = ({ className = '', style = {} }) => (
  <IconWrapper className={className} style={style}>
    <circle cx="9" cy="12" r="1" />
    <circle cx="15" cy="12" r="1" />
    <path d="M8 20v2h8v-2" />
    <path d="m12.5 17-.5-1-.5 1h1z" />
    <path d="M16 20a2 2 0 0 0 1.56-3.25 8 8 0 1 0-11.12 0A2 2 0 0 0 8 20" />
  </IconWrapper>
);

const Scroll = ({ className = '', style = {} }) => (
  <IconWrapper className={className} style={style}>
    <path d="M8 2h8a4 4 0 0 1 4 4v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a4 4 0 0 1 4-4Z" />
    <path d="M8 2v4a2 2 0 0 1-2 2" />
  </IconWrapper>
);

const RefreshCcw = ({ className = '', style = {} }) => (
  <IconWrapper className={className} style={style}>
    <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
    <path d="M3 3v5h5" />
    <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16" />
    <path d="M16 16h5v5" />
  </IconWrapper>
);

const Coffee = ({ className = '', style = {} }) => (
  <IconWrapper className={className} style={style}>
    <path d="M17 8h1a4 4 0 1 1 0 8h-1" />
    <path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z" />
    <line x1="6" x2="6" y1="2" y2="4" />
    <line x1="10" x2="10" y1="2" y2="4" />
    <line x1="14" x2="14" y1="2" y2="4" />
  </IconWrapper>
);

const Zap = ({ className = '', style = {} }) => (
  <IconWrapper className={className} style={style}>
    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
  </IconWrapper>
);

const Wifi = ({ className = '', style = {} }) => (
  <IconWrapper className={className} style={style}>
    <path d="M5 12.859a10 10 0 0 1 14 0" />
    <path d="M8.5 16.429a5 5 0 0 1 7 0" />
    <path d="M12 20h.01" />
    <path d="M2 8.82a15 15 0 0 1 20 0" />
  </IconWrapper>
);

const Battery = ({ className = '', style = {} }) => (
  <IconWrapper className={className} style={style}>
    <rect width="16" height="10" x="2" y="7" rx="2" ry="2" />
    <line x1="22" x2="22" y1="11" y2="13" />
  </IconWrapper>
);

const MousePointerClick = ({ className = '', style = {} }) => (
    <IconWrapper className={className} style={style}>
        <path d="M14 4.1 12 6" />
        <path d="m5.1 8-2.9-.8" />
        <path d="m6 12-1.9 2" />
        <path d="M7.2 2.2 8 5.1" />
        <path d="M9.037 9.69a.498.498 0 0 1 .653-.653l11 4.5a.5.5 0 0 1-.074.949l-4.349 1.041a1 1 0 0 0-.74.739l-1.04 4.35a.5.5 0 0 1-.95.074z" />
    </IconWrapper>
);

// 所有卦象和推理数据都由后端生成，不使用预设数据

// --- 技师状态 ---
const TECH_STATUS = [
    { status: "丹炉预热中", color: "#fbbf24", bg: "rgba(251, 191, 36, 0.1)", border: "#d97706" },
    { status: "量子纠缠中", color: "#22d3ee", bg: "rgba(34, 211, 238, 0.1)", border: "#0891b2" },
    { status: "元神出窍", color: "#e879f9", bg: "rgba(232, 121, 249, 0.1)", border: "#c026d3" },
    { status: "系统维护", color: "#9ca3af", bg: "rgba(156, 163, 175, 0.1)", border: "#4b5563" },
    { status: "功德挖矿中", color: "#34d399", bg: "rgba(52, 211, 153, 0.1)", border: "#059669" },
];

// --- 加载骚话 ---
const LOADING_MESSAGES = [
  "正在连接【33重天】量子服务器...",
  "正在校验时空哈希值...",
  "技师正在穿戴外骨骼机甲...",
  "正在从天道数据库下载补丁...",
  "检测到因果律波动，正在稳压...",
  "正在加载【天眼通 Pro Max】插件...",
  "正在计算你的命运比特币汇率...",
];

// --- RPG 打字机组件 ---
const Typewriter = ({ text, speed, onComplete = null, className = '' }) => {
  const [displayedText, setDisplayedText] = useState('');
  const indexRef = useRef(0);

  useEffect(() => {
    setDisplayedText('');
    indexRef.current = 0;
    if (!text) return;

    const timer = setInterval(() => {
      if (indexRef.current < text.length) {
        const char = text.charAt(indexRef.current);
        setDisplayedText((prev) => prev + char);
        indexRef.current++;
      } else {
        clearInterval(timer);
        if (onComplete) onComplete();
      }
    }, speed);

    return () => clearInterval(timer);
  }, [text, speed]);

  return (
    <div className={`whitespace-pre-wrap ${className}`}>
      {displayedText}
      <span 
        className="animate-pulse inline-block w-2 h-4 align-middle"
        style={{ backgroundColor: '#22d3ee', boxShadow: '0 0 8px #22d3ee' }}
      ></span>
    </div>
  );
};

// --- [核心] 阴阳爻绘制组件 ---
const HexagramLine = ({ isYang, color = '#fbbf24', animate = false, hexValue = null }) => {
    // 霓虹光效样式
    const glowStyle = {
        backgroundColor: color,
        boxShadow: `0 0 12px ${color}, inset 0 0 6px rgba(255,255,255,0.6)`,
        opacity: animate ? 0.8 : 1,
        transition: 'all 0.3s ease'
    };
    
    // 判断是否为动爻（老阴=6 或 老阳=9）
    const isMoving = hexValue === 6 || hexValue === 9;

    if (isYang) {
        // 阳爻：一根实线
        return (
            <div 
                className={`w-full h-full rounded-sm relative ${animate ? 'animate-pulse' : ''}`}
                style={glowStyle}
            >
            </div>
        );
    } else {
        // 阴爻：两根短线，中间断开
        return (
            <div className="w-full h-full flex justify-between items-center relative">
                <div 
                    className={`h-full rounded-sm ${animate ? 'animate-pulse' : ''}`}
                    style={{ ...glowStyle, width: '42%' }}
                ></div>
                <div 
                    className={`h-full rounded-sm ${animate ? 'animate-pulse' : ''}`}
                    style={{ ...glowStyle, width: '42%' }}
                ></div>
            </div>
        );
    }
};

// --- 六爻生成动画/展示组件 ---
const HexagramLoader = ({ lines, hexagramValues = null, isStatic = false }) => {
  // 根据爻的原始数值（6,7,8,9）生成名称
  // 6 = 老阴, 7 = 少阳, 8 = 少阴, 9 = 老阳
  const getLineName = (value: number | null) => {
    if (value === null) return '';
    
    switch (value) {
      case 6:
        return '老阴';
      case 7:
        return '少阳';
      case 8:
        return '少阴';
      case 9:
        return '老阳';
      default:
        return '';
    }
  };
  
  return (
    <div 
        className="flex flex-col-reverse gap-2 my-6 p-4 bg-black border-2 rounded-lg relative overflow-hidden transition-all duration-500"
        style={{ 
            width: isStatic ? '160px' : '220px', 
            margin: isStatic ? '0' : '24px auto',
            borderColor: isStatic ? 'rgba(251, 191, 36, 0.5)' : '#06b6d4',
            background: 'rgba(0,0,0,0.7)',
            boxShadow: isStatic ? '0 0 15px rgba(251, 191, 36, 0.2)' : '0 0 20px rgba(6, 182, 212, 0.2)'
        }}
    >
       {/* 背景光效 */}
       <div 
            className="absolute inset-0 animate-pulse pointer-events-none" 
            style={{ 
                backgroundColor: isStatic ? 'rgba(251, 191, 36, 0.05)' : 'rgba(34, 211, 238, 0.1)' 
            }}
       ></div>
       
       {/* 装饰线 */}
       <div className="absolute top-0 left-0 w-full" style={{ height: '1px', backgroundColor: isStatic ? 'rgba(251, 191, 36, 0.3)' : 'rgba(6, 182, 212, 0.5)' }}></div>
       <div className="absolute bottom-0 right-0 w-full" style={{ height: '1px', backgroundColor: isStatic ? 'rgba(251, 191, 36, 0.3)' : 'rgba(6, 182, 212, 0.5)' }}></div>

      {/* 渲染六爻：总共显示6个位置，已生成的显示亮色，未生成的显示暗色底座 */}
      {[...Array(6)].map((_, i) => {
          const isActive = i < lines.length;
          const lineValue = isActive ? lines[i] : null; // 1 or 0
          // 获取原始数值（6,7,8,9），如果没有则根据阴阳推断（7=少阳, 8=少阴）
          const hexValue = hexagramValues && i < hexagramValues.length 
            ? hexagramValues[i] 
            : (lineValue === 1 ? 7 : (lineValue === 0 ? 8 : null));
          const lineName = getLineName(hexValue);
          
          return (
            <div 
                key={i} 
                className="flex items-center gap-2 relative transition-all duration-300"
                style={{ 
                    opacity: isActive ? 1 : 0.2,
                    transform: isActive ? 'scale(1)' : 'scale(0.95)'
                }}
            >
              {/* 爻的名称标签 - 放在左边 */}
              <div 
                className="text-xs font-tech flex-shrink-0"
                style={{ 
                  width: '40px',
                  color: isStatic ? 'rgba(251, 191, 36, 0.9)' : 'rgba(34, 211, 238, 0.9)',
                  fontSize: '11px',
                  textAlign: 'left',
                  fontFamily: 'monospace'
                }}
              >
                {lineName}
              </div>
              
              {/* 爻的线条 */}
              <div 
                className="flex-1 relative"
                style={{ 
                  height: isStatic ? '6px' : '10px'
                }}
              >
                {isActive ? (
                    // 显示已生成的爻 (加载时青色，结果时金色)
                    <HexagramLine 
                      isYang={lineValue === 1} 
                      color={isStatic ? '#fbbf24' : '#22d3ee'} 
                      animate={!isStatic}
                      hexValue={hexValue}
                    />
                ) : (
                    // 空位显示底座
                    <div className="w-full h-full border rounded-sm" style={{ borderColor: 'rgba(34, 211, 238, 0.3)', backgroundColor: 'transparent' }}></div>
                )}
              </div>
            </div>
          );
      })}
    </div>
  );
};

// --- 赛博矩阵雨背景 (青色版) ---
const MatrixBackground = () => {
    const canvasRef = useRef(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        let width = canvas.width = window.innerWidth;
        let height = canvas.height = window.innerHeight;
        
        // 字符集：八卦 + 科技
        const chars = '☰☱☲☳☴☵☶☷01DATA'.split('');
        const fontSize = 14;
        const columns = width / fontSize;
        const drops = [];

        for(let x = 0; x < columns; x++) {
            drops[x] = 1;
        }

        const draw = () => {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
            ctx.fillRect(0, 0, width, height);

            ctx.font = fontSize + 'px "Orbitron", monospace';

            for(let i = 0; i < drops.length; i++) {
                const text = chars[Math.floor(Math.random() * chars.length)];
                // 随机颜色：主青色，偶尔白色高亮
                ctx.fillStyle = Math.random() > 0.95 ? '#ffffff' : '#06b6d4'; 
                ctx.fillText(text, i * fontSize, drops[i] * fontSize);

                if(drops[i] * fontSize > height && Math.random() > 0.975) {
                    drops[i] = 0;
                }
                drops[i]++;
            }
        };

        const interval = setInterval(draw, 33);
        const handleResize = () => {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
        };
        window.addEventListener('resize', handleResize);
        return () => {
            clearInterval(interval);
            window.removeEventListener('resize', handleResize);
        };
    }, []);

    return <canvas ref={canvasRef} className="fixed inset-0 pointer-events-none opacity-20 z-0" />;
};

export default function App() {
  const [step, setStep] = useState('input');
  const [question, setQuestion] = useState('');
  const [loadingMsg, setLoadingMsg] = useState(LOADING_MESSAGES[0]);
  const [finalResult, setFinalResult] = useState(null);
  const [stage, setStage] = useState('reasoning');
  const [hexLines, setHexLines] = useState([]);  // 存储从后端获取的爻的二进制值 [0,1]
  const [hexValues, setHexValues] = useState([]);  // 存储从后端获取的爻的原始数值 [6,7,8,9]
  const [currentTechStatus, setCurrentTechStatus] = useState(TECH_STATUS[0]);
  const [technicianId, setTechnicianId] = useState(() => Math.floor(Math.random() * 100) + 1);
  const [showCoffeeModal, setShowCoffeeModal] = useState(false);  // 控制咖啡提示框显示
  const [showPaymentModal, setShowPaymentModal] = useState(false);  // 控制付费二维码显示
  const [isPaymentThank, setIsPaymentThank] = useState(false);  // 是否是付费后的感谢提示框
  const [vitality, setVitality] = useState({ current: 100, max: 100, percentage: 100, can_use: true });  // 元气状态

  useEffect(() => {
      setCurrentTechStatus(TECH_STATUS[Math.floor(Math.random() * TECH_STATUS.length)]);
  }, []);

  // 定期更新元气状态
  useEffect(() => {
      const updateVitality = async () => {
          try {
              const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
              const response = await fetch(`${apiUrl}/api/divination/karma-status`, {
                  method: 'GET',
                  credentials: 'omit',
              });
              if (response.ok) {
                  const data = await response.json();
                  setVitality({
                      current: data.current_vitality || 100,
                      max: data.max_vitality || 100,
                      percentage: data.percentage || 100,
                      can_use: data.can_use !== false
                  });
              }
          } catch (error) {
              console.error('获取元气状态失败:', error);
          }
      };
      
      // 立即更新一次
      updateVitality();
      
      // 每30秒更新一次
      const interval = setInterval(updateVitality, 30000);
      
      return () => clearInterval(interval);
  }, []);

  const handleStartDivination = (customQ = null) => {
    const q = customQ || question;
    if (!q.trim()) return;
    setQuestion(q);
    setStep('divination');
    setHexLines([]);
    setHexValues([]);  // 重置爻的原始数值
  };

  const handleCastLine = async () => {
      // 所有卦象数据都由后端processor生成
      // 每次点击都从后端获取一个爻的数值
      
      console.log('handleCastLine 被调用，当前 hexLines.length:', hexLines.length);
      
      // 防止重复点击或超过6个爻
      if (hexLines.length >= 6) {
          console.log('已达到6个爻，停止生成');
          return;
      }
      
      try {
          console.log('开始调用 generateSingleLine...');
          const lineData = await generateSingleLine();
          console.log('generateSingleLine 返回:', lineData);
          
          const newBinary = lineData.binary;  // 0 或 1
          const newValue = lineData.value;    // 6, 7, 8, 或 9
          
          // 确保数据有效性
          if (newBinary === undefined || newValue === undefined) {
              throw new Error('后端返回的数据格式不正确');
          }
          
          const newLines = [...hexLines, newBinary];
          const newValues = [...hexValues, newValue];
          
          console.log('更新状态: newLines =', newLines, 'newValues =', newValues);
          
          // 确保不超过6个爻
          if (newLines.length > 6) {
              console.warn('爻的数量超过6个，已截断');
              return;
          }
          
          setHexLines(newLines);
          setHexValues(newValues);

      if (newLines.length >= 6) {
              // 确保状态更新完成后再调用分析
              // 直接传递最新的值，避免React状态更新延迟问题
          setTimeout(() => {
              setStep('loading');
                  startAnalysis(newValues, newLines);
          }, 500);
          }
      } catch (error) {
          console.error('生成爻失败:', error);
          // 如果后端调用失败，显示详细的错误信息
          let errorMessage = '未知错误';
          if (error instanceof Error) {
              errorMessage = error.message;
          } else if (typeof error === 'string') {
              errorMessage = error;
          } else if (error && typeof error === 'object') {
              // 处理对象类型的错误
              try {
                  errorMessage = JSON.stringify(error);
              } catch {
                  errorMessage = String(error);
              }
          }
          
          const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
          
          // 显示错误提示
          alert(
            `生成爻失败：${errorMessage}\n\n` +
            `请检查：\n` +
            `1. 后端服务是否已启动（${apiUrl}）\n` +
            `2. 后端API是否正常运行\n` +
            `3. 网络连接是否正常\n\n` +
            `启动后端服务：\n` +
            `cd backend\n` +
            `python start_server.py\n\n` +
            `详细错误信息请查看浏览器控制台（F12）`
          );
      }
  };

  const startAnalysis = async (providedHexValues = null, providedHexLines = null) => {
    // 开始轮播加载消息
    const msgInterval = setInterval(() => {
        setLoadingMsg(LOADING_MESSAGES[Math.floor(Math.random() * LOADING_MESSAGES.length)]);
    }, 800);

    try {
      // 优先使用传入的参数，如果没有则使用状态中的值
      // 这样可以避免React状态更新延迟的问题
      const currentHexValues = providedHexValues || (hexValues.length === 6 ? hexValues : null);
      const currentHexLines = providedHexLines || (hexLines.length === 6 ? hexLines : []);
      
      if (!currentHexValues || currentHexValues.length !== 6) {
        throw new Error('爻数据不完整，请重新生成。请确保已生成6个爻。');
      }
      
      if (!currentHexLines || currentHexLines.length !== 6) {
        throw new Error('爻数据不完整，请重新生成。请确保已生成6个爻。');
      }
      
      const result = await getDivination(question, currentHexValues);
      
        clearInterval(msgInterval);
      
      // 始终使用用户点击生成的爻数据，确保显示一致
      // 用户生成的 hexLines 和 hexValues 是唯一真实数据源
      const lines = currentHexLines;  // 直接使用用户生成的二进制数组
      const originalHexValues = currentHexValues;  // 直接使用用户生成的原始数值
      
      // 变卦：使用后端返回的 changed_binary，因为变卦是根据本卦计算的
      const changedLines = result.changedBinary && result.changedBinary.length > 0
        ? result.changedBinary
        : result.changedHexagramSymbol.map(symbol => 
            symbol.includes('  ') ? 0 : 1
          );
      
      setFinalResult({
        hexagram: result.hexagram,
        lines: lines,  // 使用用户点击生成的爻
        changedHexagram: result.changedHexagram,
        changedLines: changedLines,
        originalHexagram: originalHexValues,  // 使用用户点击生成的原始数值
        changedHexagramValues: result.changedHexagramValues || [],
        originalNature: result.originalNature,
        changedNature: result.changedNature,
        originalInfo: result.originalInfo,
        changedInfo: result.changedInfo,
        reasoning: result.reasoning,
        content: result.content
      });
      
        setStep('result');
        setStage('reasoning');
    } catch (error) {
        clearInterval(msgInterval);
      console.error('占卜失败:', error);
      
      // 错误处理：显示错误信息，不使用模拟数据
      // 所有卦象数据必须由后端生成，确保数据一致性
      const errorMessage = error instanceof Error 
        ? error.message 
        : '未知错误';
      const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      
      // 检查是否是元气不足的错误
      if (errorMessage.includes('元气不足')) {
        alert(errorMessage);
        // 元气不足时，不显示错误结果，保持在loading状态或返回divination状态
        setStep('divination');
        return;
      }
      
      // 检查是否是限流错误（请求过于频繁）
      if (errorMessage.includes('请求过于频繁')) {
        // 限流错误是正常的业务逻辑，不需要显示系统错误界面
        alert(errorMessage);
        setStep('divination');
        return;
      }
      
      setFinalResult({
        hexagram: 'System_Error',
        lines: hexLines.length === 6 ? hexLines : [],
        changedHexagram: 'System_Error',
        changedLines: [],
        originalHexagram: hexValues.length === 6 ? hexValues : [],
        changedHexagramValues: [],
        changedBinary: [],
        originalNature: '未知',
        changedNature: '未知',
        originalInfo: null,
        changedInfo: null,
        reasoning: '【技师日志】后端服务连接失败，无法生成卦象数据。',
        content: `系统连接失败：${errorMessage}。\n\n所有卦象数据必须由后端生成，请确保后端服务正常运行（默认地址：${apiUrl}）。\n\n请检查：\n1. 后端服务是否已启动\n2. 网络连接是否正常\n3. API地址配置是否正确\n\n启动后端服务：\ncd backend\npython start_server.py`
      });
      setStep('result');
      setStage('reasoning');
    }
  };

  useEffect(() => {
    let interval;
    if (step === 'loading') {
      interval = setInterval(() => {
        setLoadingMsg(LOADING_MESSAGES[Math.floor(Math.random() * LOADING_MESSAGES.length)]);
      }, 800);
    }
    return () => clearInterval(interval);
  }, [step]);

  const handleReset = () => {
    setQuestion('');
    setStep('input');
    setFinalResult(null);
    setHexLines([]);
    setHexValues([]);  // 重置爻的原始数值
    setCurrentTechStatus(TECH_STATUS[Math.floor(Math.random() * TECH_STATUS.length)]);
    setTechnicianId(Math.floor(Math.random() * 100) + 1); // 重置时生成新的技师ID
  };

  // 提取关键分析信息：卦的组成、卦题等基本分析
  const extractKeyAnalysis = (result) => {
    if (!result) return '';
    
    const keyInfo = [];
    
    // 1. 本卦信息
    if (result.hexagram) {
      keyInfo.push(`本卦：${result.hexagram}`);
    }
    
    // 2. 变卦信息
    if (result.changedHexagram && result.changedHexagram !== result.hexagram) {
      keyInfo.push(`变卦：${result.changedHexagram}`);
    }
    
    // 3. 卦的组成（nature）+ 卦的符号（包括本卦和变卦）
    // nature到八卦名称的映射
    const natureToTrigram = {
      '天': '乾',
      '地': '坤',
      '雷': '震',
      '风': '巽',
      '水': '坎',
      '火': '离',
      '山': '艮',
      '泽': '兑'
    };
    
    // 八卦符号映射
    const trigramSymbols = {
      '乾': '☰',
      '坤': '☷',
      '震': '☳',
      '巽': '☴',
      '坎': '☵',
      '离': '☲',
      '艮': '☶',
      '兑': '☱'
    };
    
    // 解析本卦的组成
    const parseComposition = (nature) => {
      if (!nature) return null;
      
      const natureParts = nature.split('\n').map(s => s.trim()).filter(s => s);
      if (natureParts.length >= 2) {
        const upperNature = natureParts[0];
        const lowerNature = natureParts[1];
        
        const upperTrigram = natureToTrigram[upperNature];
        const lowerTrigram = natureToTrigram[lowerNature];
        
        const symbols = [];
        if (upperTrigram && trigramSymbols[upperTrigram]) {
          symbols.push(trigramSymbols[upperTrigram]);
        }
        if (lowerTrigram && trigramSymbols[lowerTrigram]) {
          symbols.push(trigramSymbols[lowerTrigram]);
        }
        
        return {
          text: `上${upperNature}下${lowerNature}`,
          symbols: symbols
        };
      }
      return null;
    };
    
    // 本卦组成
    if (result.originalNature) {
      const originalComp = parseComposition(result.originalNature);
      if (originalComp) {
        if (originalComp.symbols.length > 0) {
          keyInfo.push(`本卦：${originalComp.text}（${originalComp.symbols.join(' ')}）`);
        } else {
          keyInfo.push(`本卦：${originalComp.text}`);
        }
      } else {
        keyInfo.push(`本卦：${result.originalNature}`);
      }
    }
    
    // 变卦组成
    if (result.changedNature && result.changedHexagram && result.changedHexagram !== result.hexagram) {
      const changedComp = parseComposition(result.changedNature);
      if (changedComp) {
        if (changedComp.symbols.length > 0) {
          keyInfo.push(`变卦：${changedComp.text}（${changedComp.symbols.join(' ')}）`);
        } else {
          keyInfo.push(`变卦：${changedComp.text}`);
        }
      } else {
        keyInfo.push(`变卦：${result.changedNature}`);
      }
    }
    
    // 4. 动爻信息（从原始数值中提取）
    if (result.originalHexagram && Array.isArray(result.originalHexagram)) {
      const movingLines = [];
      const lineNames = ['初', '二', '三', '四', '五', '上'];
      
      result.originalHexagram.forEach((value, index) => {
        if (value === 6 || value === 9) {  // 老阴或老阳为动爻
          const isYang = value === 9;
          let lineName = '';
          
          if (index === 0) {
            lineName = `初${isYang ? '九' : '六'}`;
          } else if (index === 5) {
            lineName = `上${isYang ? '九' : '六'}`;
          } else {
            lineName = `${isYang ? '九' : '六'}${lineNames[index]}`;
          }
          
          movingLines.push(lineName);
        }
      });
      
      // 特殊处理：乾卦全动用"用九"，坤卦全动用"用六"
      if (result.hexagram === '乾为天' || result.hexagram === '乾') {
        const allNine = result.originalHexagram.every(v => v === 9);
        if (allNine && movingLines.length === 6) {
          movingLines.length = 0;
          movingLines.push('用九');
        }
      } else if (result.hexagram === '坤为地' || result.hexagram === '坤') {
        const allSix = result.originalHexagram.every(v => v === 6);
        if (allSix && movingLines.length === 6) {
          movingLines.length = 0;
          movingLines.push('用六');
        }
      }
      
      if (movingLines.length > 0) {
        keyInfo.push(`动爻：${movingLines.join('、')}`);
      } else {
        keyInfo.push('动爻：无');
      }
    }
    
    // 5. 从reasoning中提取基本分析（如果有的话）
    if (result.reasoning) {
      // 尝试提取包含"卦"、"爻"、"分析"等关键词的句子
      const sentences = result.reasoning.split(/[。！？\n]/).filter(s => s.trim().length > 5);
      const keySentences = sentences.filter(s => 
        /卦|爻|组成|变化|动|静|阳|阴/.test(s)
      ).slice(0, 2);  // 最多取2句
      
      if (keySentences.length > 0) {
        keyInfo.push(`分析：${keySentences.join('。')}`);
      }
    }
    
    return keyInfo.join('\n') || '正在分析卦象...';
  };

  return (
    <div className="min-h-screen bg-black font-tech p-4 flex flex-col items-center justify-center relative overflow-hidden" style={{ color: '#22d3ee' }}>
      
      {/* 1. 赛博矩阵雨背景 (青色) */}
      <MatrixBackground />
      
      {/* 2. CRT 扫描线 */}
      <div className="fixed inset-0 z-50 pointer-events-none" 
           style={{ 
               background: 'linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06))',
               backgroundSize: '100% 2px, 3px 100%',
               pointerEvents: 'none'
           }}>
      </div>
      <div className="fixed inset-0 z-50 pointer-events-none opacity-20"
           style={{ background: 'radial-gradient(circle, rgba(6,182,212,0) 60%, rgba(0,0,0,1) 100%)' }}>
      </div>

      {/* 主面板容器 */}
      <div className="z-10 w-full max-w-3xl relative">
        
        {/* 顶部状态栏 */}
        <div className="flex justify-between items-end mb-2 px-4 border-b pb-2 bg-black backdrop-blur-sm rounded-t-lg" style={{ borderColor: 'rgba(22, 78, 99, 0.5)', backgroundColor: 'rgba(0,0,0,0.6)' }}>
            <div className="flex gap-4 text-[10px] font-bold uppercase tracking-widest font-tech" style={{ color: '#0891b2' }}>
                <div className="flex items-center gap-1"><Wifi className="w-3 h-3 animate-pulse" /> 灵网: <span style={{ color: '#22d3ee' }}>ONLINE</span></div>
                <div className="flex items-center gap-1">
                    <Battery className="w-3 h-3" /> 
                    元气: <span 
                        className={vitality.percentage <= 0 ? 'animate-pulse' : ''} 
                        style={{ 
                            color: vitality.percentage <= 0 ? '#ef4444' : 
                                   vitality.percentage <= 20 ? '#fbbf24' : '#fbbf24'
                        }}
                    >
                        {Math.round(vitality.percentage)}%
                    </span>
                </div>
            </div>
            <div className="text-[10px] font-tech" style={{ color: '#155e75' }}>OS.VER.4.0.1_NEON</div>
        </div>

        <div 
            className="bg-black border rounded-b-lg relative overflow-hidden min-h-[600px] flex flex-col backdrop-blur-md"
            style={{ borderColor: 'rgba(6, 182, 212, 0.3)', boxShadow: '0 0 30px rgba(6, 182, 212, 0.15)', backgroundColor: 'rgba(0,0,0,0.8)' }}
        >
          {/* 头部 */}
          <div className="relative z-10 p-6 border-b flex items-center justify-between" style={{ backgroundColor: 'rgba(8, 51, 68, 0.3)', borderColor: '#155e75' }}>
            <div className="flex items-center gap-4">
              <div className="relative group cursor-pointer">
                <div className="absolute inset-0 blur-lg opacity-20 group-hover:opacity-40 transition-opacity" style={{ backgroundColor: '#22d3ee' }}></div>
                <Skull className="w-12 h-12 relative z-10" style={{ color: '#22d3ee' }} />
              </div>
              <div>
                <h1 
                  className="text-4xl font-tao tracking-widest text-transparent bg-clip-text glitch-text" 
                  data-text="天国神算"
                  style={{ 
                      textShadow: '0 0 15px rgba(6, 182, 212, 0.6)',
                      backgroundImage: 'linear-gradient(to right, #67e8f9, #cffafe, #ffffff)'
                  }}
                >
                  天国神算
                </h1>
                <p className="text-[10px] font-tech tracking-[0.2em] mt-1" style={{ color: '#0891b2' }}>CELESTIAL DIVINATION // TECH_YI</p>
              </div>
            </div>
            <div className="text-right flex flex-col items-end gap-1">
                <div className="text-xs border px-2 py-1 bg-black font-tech" style={{ color: '#06b6d4', borderColor: '#155e75' }}>
                    ID: 技师No.{technicianId}
                </div>
                <div className="text-[10px] border px-2 py-0.5 font-bold font-tech" style={{ 
                    color: currentTechStatus.color, 
                    backgroundColor: currentTechStatus.bg, 
                    borderColor: currentTechStatus.border 
                }}>
                    状态: {currentTechStatus.status}
                </div>
            </div>
          </div>

          {/* --- 阶段 1: 输入界面 --- */}
          {step === 'input' && (
            <div className="flex-1 p-8 flex flex-col animate-fade-in relative z-10">
              <div className="flex-1 flex flex-col justify-center">
                  <div className="text-center mb-10 space-y-2">
                    <p className="text-xl font-tao tracking-wide" style={{ color: '#cffafe' }}>请施主输入心中困惑...</p>
                    <p className="text-xs font-tech" style={{ color: '#0e7490' }}>CAUTION: 泄露天机过多可能导致账号封禁。</p>
                  </div>
                  
                  <textarea
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="在此输入代码bug、人生bug或感情bug..."
                    className="w-full border rounded-md p-4 h-36 resize-none transition-all text-lg mb-6 custom-input-shadow font-tech"
                    style={{ 
                        backgroundColor: 'rgba(8, 51, 68, 0.2)', 
                        borderColor: 'rgba(14, 116, 144, 0.5)',
                        color: '#67e8f9',
                        outline: 'none'
                    }}
                  />
                  
                  {/* 快捷标签 */}
                  <div className="flex gap-3 mb-10 justify-center flex-wrap">
                      {['💰 什么时候暴富', '🌸 我有桃花吗', '💼 工作太累想辞职', '🐱 为什么要养猫'].map((tag) => (
                          <button 
                            key={tag}
                            onClick={() => handleStartDivination(tag)}
                            className="text-xs border px-3 py-1.5 rounded transition-colors font-tech hover:opacity-80"
                            style={{ borderColor: '#155e75', color: '#06b6d4' }}
                          >
                              {tag}
                          </button>
                      ))}
                  </div>

                  <button
                    onClick={() => handleStartDivination()}
                    disabled={!question.trim() || !vitality.can_use}
                    className="group relative w-full overflow-hidden border px-8 py-5 transition-all disabled:opacity-30 disabled:cursor-not-allowed rounded-sm"
                    style={{ backgroundColor: 'rgba(8, 51, 68, 0.4)', borderColor: '#0891b2' }}
                  >
                    <span className="relative z-10 flex items-center justify-center gap-3 font-bold text-xl tracking-widest font-tech" style={{ color: '#67e8f9' }}>
                      <Zap className="w-5 h-5 animate-pulse" />
                      启动天机引擎
                      <Zap className="w-5 h-5 animate-pulse" />
                    </span>
                    <div className="absolute inset-0 -translate-x-full group-hover:translate-x-0 transition-transform duration-500 ease-out" style={{ background: 'linear-gradient(to right, transparent, rgba(8, 145, 178, 0.2), transparent)' }} />
                  </button>
              </div>
            </div>
          )}

          {/* --- 阶段 2: 互动摇卦 (Divination) --- */}
          {step === 'divination' && (
              <div className="flex-1 flex flex-col items-center justify-center p-8 z-10 animate-fade-in">
                  <h3 className="text-2xl font-bold mb-2 font-tao tracking-widest" style={{ color: '#67e8f9' }}>请手动摇卦</h3>
                  <p className="text-sm mb-8 font-tech text-center" style={{ color: '#0891b2' }}>
                      点击全息按钮生成数据爻。<br/>
                      <span className="text-xs opacity-50 block mt-2" style={{ color: '#f59e0b' }}>PROGRESS: {Math.min(hexLines.length, 6)}/6</span>
                  </p>

                  <HexagramLoader lines={hexLines} hexagramValues={hexValues} />

                  <button
                    onClick={async (e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      if (!vitality.can_use) {
                        setShowPaymentModal(true);
                        return;
                      }
                      console.log('=== ACTIVATE 按钮被点击 ===');
                      console.log('当前 hexLines:', hexLines);
                      console.log('当前 hexValues:', hexValues);
                      console.log('hexLines.length:', hexLines.length);
                      await handleCastLine();
                    }}
                    disabled={hexLines.length >= 6 || !vitality.can_use}
                    className="mt-12 relative group w-28 h-28 rounded-full border-2 flex items-center justify-center active:scale-95 transition-all cursor-pointer z-10 disabled:opacity-50 disabled:cursor-not-allowed"
                    style={{ borderColor: '#06b6d4', boxShadow: '0 0 25px rgba(6, 182, 212, 0.3)' }}
                    type="button"
                  >
                      <div className="absolute inset-0 rounded-full border animate-ping opacity-20 pointer-events-none" style={{ borderColor: '#67e8f9' }}></div>
                      <div className="flex flex-col items-center group-hover:text-cyan-200 relative z-10" style={{ color: '#22d3ee' }}>
                          <MousePointerClick className="w-8 h-8 mb-1" />
                          <span className="font-bold font-tech text-lg">ACTIVATE</span>
                      </div>
                  </button>
              </div>
          )}

          {/* --- 阶段 3: Loading (Analysis) --- */}
          {step === 'loading' && (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-8 z-10 animate-fade-in">
              <div className="relative">
                  <div className="absolute inset-0 blur-xl opacity-20 animate-pulse rounded-full" style={{ backgroundColor: '#22d3ee' }}></div>
                  <Bagua className="w-16 h-16 mb-6 relative z-10" style={{ color: '#22d3ee' }} />
              </div>
              
              <h3 className="text-2xl font-bold text-white mb-2 tracking-widest font-tao">卦象解析中...</h3>
              <p className="text-sm mb-6 font-bold font-tech border px-4 py-1 rounded-full" style={{ color: '#06b6d4', borderColor: '#155e75', backgroundColor: 'rgba(8, 51, 68, 0.3)' }}>{loadingMsg}</p>
              
              {/* 显示用户点击生成的卦象，确保数据一致 */}
              <HexagramLoader lines={hexLines} hexagramValues={hexValues} />
              <p className="text-[10px] mt-4 font-tech animate-pulse" style={{ color: '#0e7490' }}>DECODING_HEAVENLY_SECRETS...</p>
            </div>
          )}

          {/* --- 阶段 4: 结果展示 (RPG 模式) --- */}
          {step === 'result' && finalResult && (
            <div className="flex-1 flex flex-col overflow-hidden p-6 z-10 min-h-0">
              
              {/* 顶部摘要 - 本卦和变卦 */}
              <div className="mb-6 border-b pb-6 flex-shrink-0" style={{ borderColor: 'rgba(21, 94, 117, 0.5)' }}>
                {/* 本卦 */}
                {(() => {
                  const originalInfo = finalResult.originalInfo || {
                    composition: finalResult.originalNature?.replace('\n', '上') || '未知',
                    meaning: '卦象说明生成中...',
                    quote: '卦象如人生，变化无常，需自行体悟。'
                  };
                  return (
                    <div className="grid grid-cols-3 gap-4 mb-4 p-4 rounded border" style={{ borderColor: 'rgba(21, 94, 117, 0.5)', backgroundColor: 'rgba(8, 51, 68, 0.2)' }}>
                      {/* 左侧：卦象图像 */}
                      <div className="flex flex-col gap-0.5 justify-center">
                          <HexagramLoader 
                            lines={finalResult.lines} 
                            hexagramValues={finalResult.originalHexagram || []}
                            isStatic={true} 
                          />
                      </div>
                      
                      {/* 中间：卦名和组成 */}
                      <div className="flex flex-col justify-center">
                          <div className="text-xs mb-1 font-tech uppercase" style={{ color: '#0891b2' }}>本卦 (Original)</div>
                          <div className="text-2xl font-bold font-tao tracking-widest mb-2" style={{ color: '#fbbf24', textShadow: '0 0 10px rgba(251, 191, 36, 0.5)' }}>{finalResult.hexagram}</div>
                          <div className="text-xs font-tech" style={{ color: '#06b6d4' }}>组成: {originalInfo.composition}</div>
                      </div>
                      
                      {/* 右侧：解释和名言 */}
                      <div className="flex flex-col justify-center space-y-2">
                          <div>
                            <div className="text-xs mb-1 font-tech uppercase" style={{ color: '#0891b2' }}>解释</div>
                            <div className="text-xs font-tech leading-relaxed" style={{ color: '#cffafe' }}>{originalInfo.meaning}</div>
                          </div>
                          <div className="border-t pt-2" style={{ borderColor: 'rgba(21, 94, 117, 0.3)' }}>
                            <div className="text-xs font-tech italic" style={{ color: '#fbbf24' }}>"{originalInfo.quote}"</div>
                          </div>
                      </div>
                    </div>
                  );
                })()}
                
                {/* 变卦 */}
                {finalResult.changedHexagram && (() => {
                  const changedInfo = finalResult.changedInfo || {
                    composition: finalResult.changedNature?.replace('\n', '上') || '未知',
                    meaning: '卦象说明生成中...',
                    quote: '卦象如人生，变化无常，需自行体悟。'
                  };
                  return (
                    <div className="grid grid-cols-3 gap-4 p-4 rounded border" style={{ borderColor: 'rgba(21, 94, 117, 0.5)', backgroundColor: 'rgba(8, 51, 68, 0.2)' }}>
                      {/* 左侧：卦象图像 */}
                      <div className="flex flex-col gap-0.5 justify-center">
                          <HexagramLoader 
                            lines={finalResult.changedLines || []} 
                            hexagramValues={finalResult.changedHexagramValues || []}
                            isStatic={true} 
                          />
                      </div>
                      
                      {/* 中间：卦名和组成 */}
                      <div className="flex flex-col justify-center">
                          <div className="text-xs mb-1 font-tech uppercase" style={{ color: '#0891b2' }}>变卦 (Changed)</div>
                          <div className="text-2xl font-bold font-tao tracking-widest mb-2" style={{ color: '#22d3ee', textShadow: '0 0 10px rgba(34, 211, 238, 0.5)' }}>{finalResult.changedHexagram}</div>
                          <div className="text-xs font-tech" style={{ color: '#06b6d4' }}>组成: {changedInfo.composition}</div>
                 </div>
                      
                      {/* 右侧：解释和名言 */}
                      <div className="flex flex-col justify-center space-y-2">
                 <div>
                            <div className="text-xs mb-1 font-tech uppercase" style={{ color: '#0891b2' }}>解释</div>
                            <div className="text-xs font-tech leading-relaxed" style={{ color: '#cffafe' }}>{changedInfo.meaning}</div>
                          </div>
                          <div className="border-t pt-2" style={{ borderColor: 'rgba(21, 94, 117, 0.3)' }}>
                            <div className="text-xs font-tech italic" style={{ color: '#22d3ee' }}>"{changedInfo.quote}"</div>
                          </div>
                      </div>
                 </div>
                  );
                })()}
                
                <div className="text-xs mt-2 font-tech text-center" style={{ color: '#0e7490' }}>HASH: {Math.random().toString(36).substr(2, 9).toUpperCase()}</div>
              </div>

              {/* A. 内心戏区域 */}
              <div className="mb-6 animate-slide-in-right flex-shrink-0">
                <div className="flex items-center gap-2 mb-2">
                  <span className="px-2 py-0.5 border text-[10px] font-bold uppercase font-tech" style={{ backgroundColor: 'rgba(69, 26, 3, 0.2)', borderColor: 'rgba(217, 119, 6, 0.5)', color: '#f59e0b' }}>Core_Log: Analysis</span>
                </div>
                <div 
                  className="bg-black border-l-2 p-4 text-sm italic font-tech overflow-y-auto custom-scrollbar" 
                  style={{ 
                    borderColor: '#d97706', 
                    color: '#9ca3af', 
                    backgroundColor: 'rgba(0,0,0,0.6)',
                    height: '128px',
                    maxHeight: '128px'
                  }}
                >
                  <Typewriter 
                    text={extractKeyAnalysis(finalResult)} 
                    speed={10} 
                    onComplete={() => setTimeout(() => setStage('content'), 800)}
                    className="opacity-80 font-tech"
                  />
                </div>
              </div>

              {/* B. 正式回答区域 */}
              {stage === 'content' && (
                <div className="animate-fade-in-up flex flex-col min-h-0 flex-shrink-0">
                   <div className="flex items-center gap-2 mb-2 flex-shrink-0">
                    <span className="px-2 py-0.5 border text-[10px] font-bold uppercase font-tech" style={{ backgroundColor: 'rgba(22, 78, 99, 0.2)', borderColor: 'rgba(6, 182, 212, 0.5)', color: '#22d3ee' }}>Message_From: Tech_Yi</span>
                  </div>
                  <div 
                    className="p-6 border text-base leading-relaxed rounded-tr-xl rounded-bl-xl relative overflow-y-auto custom-scrollbar"
                    style={{ 
                        backgroundColor: 'rgba(8, 51, 68, 0.1)', 
                        borderColor: 'rgba(6, 182, 212, 0.3)', 
                        color: '#cffafe',
                        boxShadow: '0 0 20px rgba(6, 182, 212, 0.05)',
                        height: '256px',
                        maxHeight: '256px'
                    }}
                  >
                    <div className="absolute top-0 right-0 p-1 z-10">
                        <div className="w-2 h-2 rounded-full animate-ping" style={{ backgroundColor: '#22d3ee' }}></div>
                    </div>
                    <Typewriter 
                      text={finalResult.content} 
                      speed={40} 
                      onComplete={null}
                      className="font-tech"
                    />
                  </div>
                  
                  {/* 底部操作栏 */}
                  <div className="mt-6 grid grid-cols-2 gap-4 animate-fade-in flex-shrink-0">
                    <button 
                        onClick={handleReset}
                        className="py-3 border text-sm transition-all flex items-center justify-center gap-2 uppercase tracking-wider font-tech group rounded hover:opacity-80"
                        style={{ borderColor: '#155e75', color: '#06b6d4' }}
                    >
                        <RefreshCcw className="w-4 h-4 group-hover:rotate-180 transition-transform" /> Reboot_System
                    </button>
                    <button 
                        onClick={() => {
                            if (vitality.percentage <= 0) {
                                setShowPaymentModal(true);
                            } else {
                                setIsPaymentThank(false);  // 主动点击，不是付费后
                                setShowCoffeeModal(true);
                            }
                        }}
                        className="py-3 border text-sm transition-all flex items-center justify-center gap-2 uppercase tracking-wider font-tech rounded hover:opacity-80"
                        style={{ backgroundColor: 'rgba(69, 26, 3, 0.1)', borderColor: '#92400e', color: '#f59e0b' }}
                    >
                        <Coffee className="w-4 h-4" /> Offer_Coffee
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* 咖啡提示框 Modal */}
      {showCoffeeModal && (
        <div 
          className="fixed inset-0 z-[100] flex items-center justify-center"
          style={{ backgroundColor: 'rgba(0, 0, 0, 0.8)' }}
          onClick={() => setShowCoffeeModal(false)}
        >
          <div 
            className="relative bg-black border rounded-lg p-6 max-w-md w-full mx-4"
            style={{ 
              borderColor: '#92400e',
              boxShadow: '0 0 30px rgba(245, 158, 11, 0.3)'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* 关闭按钮 */}
            <button
              onClick={() => setShowCoffeeModal(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-amber-500 transition-colors"
              style={{ fontSize: '24px', lineHeight: '1' }}
            >
              ×
            </button>
            
            {/* 内容 */}
            <div className="flex flex-col items-center text-center">
              <Coffee className="w-16 h-16 mb-4" style={{ color: '#f59e0b' }} />
              <h3 className="text-xl font-bold font-tech mb-4 uppercase tracking-wider" style={{ color: '#f59e0b' }}>
                {isPaymentThank ? '感谢您的支持' : '心意已收到'}
              </h3>
              <p className="text-base font-tech mb-6 leading-relaxed px-4" style={{ color: '#cffafe' }}>
                {isPaymentThank ? (
                  <>
                    技师表示：心意领了，下次记得加点钟！
                  </>
                ) : (
                  <>
                    技师微微一笑，眼中闪过一丝感激：<br/>
                    "感谢你的心意，虽然我现在元气还算充足，<br/>
                    但你的支持让我更有动力继续为你服务。<br/>
                    这份情意我会记在心里，下次需要时记得找我！"
                  </>
                )}
              </p>
              <button
                onClick={() => {
                  setShowCoffeeModal(false);
                  setIsPaymentThank(false);  // 重置状态
                }}
                className="px-6 py-2 border rounded transition-all font-tech uppercase tracking-wider hover:opacity-80"
                style={{ borderColor: '#92400e', color: '#f59e0b' }}
              >
                确定
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 付费二维码 Modal */}
      {showPaymentModal && (
        <div 
          className="fixed inset-0 z-[100] flex items-center justify-center"
          style={{ backgroundColor: 'rgba(0, 0, 0, 0.9)' }}
          onClick={() => setShowPaymentModal(false)}
        >
          <div 
            className="relative bg-black border rounded-lg p-8 max-w-md w-full mx-4"
            style={{ 
              borderColor: '#92400e',
              boxShadow: '0 0 40px rgba(245, 158, 11, 0.4)'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* 关闭按钮 */}
            <button
              onClick={() => setShowPaymentModal(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-amber-500 transition-colors"
              style={{ fontSize: '24px', lineHeight: '1' }}
            >
              ×
            </button>
            
            {/* 内容 */}
            <div className="flex flex-col items-center text-center">
              <Coffee className="w-12 h-12 mb-4" style={{ color: '#f59e0b' }} />
              <h3 className="text-xl font-bold font-tech mb-3 uppercase tracking-wider" style={{ color: '#f59e0b' }}>
                元神枯竭，需要补充元气
              </h3>
              <p className="text-sm font-tech mb-4 leading-relaxed px-4" style={{ color: '#cffafe' }}>
                技师疲惫地抬起头，眼中闪过一丝无奈：<br/>
                "天机不可泄露，窥探天机需要消耗元神...<br/>
                连续算卦让我的元气已经耗尽。<br/>
                如果你还想继续，可以请我喝杯咖啡恢复一下元气..."
              </p>
              
              {/* 二维码占位 */}
              <div 
                className="w-48 h-48 border-2 border-dashed mb-4 flex items-center justify-center"
                style={{ borderColor: '#92400e', backgroundColor: 'rgba(69, 26, 3, 0.2)' }}
              >
                <div className="text-center">
                  <div className="text-4xl mb-2">☕</div>
                  <div className="text-xs font-tech" style={{ color: '#f59e0b' }}>
                    扫码支付<br/>
                    ¥9.9
                  </div>
                </div>
              </div>
              
              <p className="text-xs font-tech mb-4 opacity-70" style={{ color: '#cffafe' }}>
                （模拟支付，实际应接入支付系统）
              </p>
              
              <button
                onClick={async () => {
                  try {
                    const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
                    const response = await fetch(`${apiUrl}/api/divination/recharge`, {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      credentials: 'omit',
                    });
                    
                    if (response.ok) {
                      // 更新元气状态
                      const data = await response.json();
                      setVitality({
                        current: data.current_vitality || 100,
                        max: data.max_vitality || 100,
                        percentage: data.karma_status?.percentage || 100,
                        can_use: true
                      });
                      // 关闭付费Modal，显示感谢提示框（标记为付费后的感谢）
                      setIsPaymentThank(true);
                      setShowPaymentModal(false);
                      setShowCoffeeModal(true);
                    } else {
                      alert('支付失败，请重试');
                    }
                  } catch (error) {
                    console.error('支付失败:', error);
                    alert('支付失败，请检查网络连接');
                  }
                }}
                className="px-8 py-3 border rounded transition-all font-tech uppercase tracking-wider hover:opacity-80 mb-2"
                style={{ borderColor: '#92400e', color: '#f59e0b', backgroundColor: 'rgba(245, 158, 11, 0.1)' }}
              >
                模拟支付成功
              </button>
              
              <button
                onClick={() => setShowPaymentModal(false)}
                className="px-6 py-2 text-sm text-gray-400 hover:text-gray-300 transition-colors font-tech"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Zhi+Mang+Xing&display=swap');

        .font-tech {
          font-family: 'Orbitron', monospace;
        }
        
        .font-tao {
          font-family: 'Zhi Mang Xing', cursive;
        }

        .glitch-text {
            position: relative;
        }
        
        .animate-slide-in-right {
          animation: slideInRight 0.5s ease-out;
        }
        @keyframes slideInRight {
          from { opacity: 0; transform: translateX(-20px); }
          to { opacity: 1; transform: translateX(0); }
        }
        .animate-fade-in {
            animation: fadeIn 0.5s ease-out;
        }
        .animate-fade-in-up {
            animation: fadeInUp 0.5s ease-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .animate-spin-slow {
            animation: spin 3s linear infinite;
        }
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        .custom-input-shadow:focus {
            box-shadow: 0 0 15px rgba(6, 182, 212, 0.3);
        }
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: #000; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #0e7490; }
      `}</style>
    </div>
  );
}
