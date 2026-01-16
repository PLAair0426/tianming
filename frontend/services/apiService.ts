/**
 * 后端API服务
 * 前后端分离 - 前端API调用封装
 */
import { DivinationResult } from '../types';

// API基础URL - 根据环境变量或默认值
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * 生成卦象
 */
export const generateHexagram = async () => {
  const response = await fetch(`${API_BASE_URL}/api/divination/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '生成卦象失败' }));
    throw new Error(error.detail || '生成卦象失败');
  }

  return await response.json();
};

/**
 * 生成单个爻
 * 所有卦象数据都由后端processor生成
 */
export const generateSingleLine = async () => {
  console.log('🔍 开始调用 generateSingleLine，API_BASE_URL:', API_BASE_URL);
  
  try {
    const url = `${API_BASE_URL}/api/divination/generate-line`;
    console.log('📡 请求URL:', url);
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      // 添加mode和credentials配置以确保CORS正常工作
      mode: 'cors',
      credentials: 'omit',  // 不使用credentials以避免CORS问题
    });

    console.log('📥 响应状态:', response.status, response.statusText);
    console.log('📥 响应头:', Object.fromEntries(response.headers.entries()));

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ 响应错误:', errorText);
      
      let errorData;
      try {
        errorData = JSON.parse(errorText);
      } catch {
        errorData = { detail: `HTTP ${response.status}: ${response.statusText}` };
      }
      
      // 处理详细的错误信息
      let errorMessage = '';
      
      // 如果是429错误（限流），特殊处理
      if (response.status === 429 && errorData.detail) {
        const detail = typeof errorData.detail === 'object' ? errorData.detail : {};
        const errorType = detail.error || '';
        
        if (errorType === '请求过于频繁' || detail.limit_info) {
          // 限流错误
          const limitInfo = detail.limit_info || {};
          const windowHours = (limitInfo.window_seconds || 3600) / 3600;
          const retryAfterMinutes = Math.ceil((limitInfo.retry_after || 3600) / 60);
          errorMessage = `请求过于频繁\n\n` +
            `每小时最多${limitInfo.max_requests || 30}次请求，请在 ${retryAfterMinutes} 分钟后重试。\n\n` +
            `当前请求数：${limitInfo.current_requests || 0}/${limitInfo.max_requests || 30}`;
        } else {
          // 其他429错误
          errorMessage = detail.message || detail.error || '请求被限制';
        }
      } else if (typeof errorData.detail === 'string') {
        errorMessage = errorData.detail;
      } else if (errorData.detail && typeof errorData.detail === 'object') {
        // 如果是对象，提取 message 和 hint
        errorMessage = errorData.detail.message || errorData.detail.error || '未知错误';
        if (errorData.detail.hint) {
          errorMessage += '\n\n提示: ' + errorData.detail.hint;
        }
      } else {
        errorMessage = `生成爻失败 (HTTP ${response.status})`;
      }
      
      throw new Error(errorMessage);
    }

    const data = await response.json();
    console.log('✅ 成功获取数据:', data);
    return data;
  } catch (error) {
    console.error('❌ generateSingleLine 错误:', error);
    
    // 如果是网络错误，提供更详细的错误信息和解决方案
    if (error instanceof TypeError && (error.message.includes('fetch') || error.message.includes('Failed to fetch'))) {
      const errorMsg = `无法连接到后端服务 (${API_BASE_URL})\n\n` +
        `请按照以下步骤启动后端服务：\n\n` +
        `1. 打开终端（命令行）\n` +
        `2. 执行命令：cd backend\n` +
        `3. 执行命令：python start_server.py\n` +
        `4. 等待看到 "Uvicorn running on http://0.0.0.0:8000" 提示\n` +
        `5. 保持终端窗口打开，然后刷新此页面\n\n` +
        `或者访问 http://localhost:8000/docs 检查后端服务是否运行\n\n` +
        `当前API地址: ${API_BASE_URL}`;
      throw new Error(errorMsg);
    }
    throw error;
  }
};

/**
 * 获取占卜解读
 * @param question 用户问题
 * @param hexValues 六爻原始数值（可选，6,7,8,9数组）
 */
export const getDivination = async (
  question: string,
  hexValues?: number[]
): Promise<DivinationResult> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/divination/interpret`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
        hex_lines: hexValues,  // 传递原始数值数组 [6,7,8,9]
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ 占卜解读响应错误:', errorText);
      
      let errorData;
      try {
        errorData = JSON.parse(errorText);
      } catch {
        errorData = { detail: `HTTP ${response.status}: ${response.statusText}` };
      }
      
      // 如果是429错误，区分限流和元气不足
      if (response.status === 429 && errorData.detail) {
        // 确保 detail 是对象
        let detail: any = {};
        if (typeof errorData.detail === 'string') {
          try {
            detail = JSON.parse(errorData.detail);
          } catch {
            detail = { message: errorData.detail };
          }
        } else if (typeof errorData.detail === 'object' && errorData.detail !== null) {
          detail = errorData.detail;
        }
        
        const errorType = detail.error || '';
        const hasLimitInfo = detail.limit_info !== undefined && detail.limit_info !== null;
        
        // 调试日志
        console.log('🔍 429错误详情:', {
          errorData,
          detail,
          errorType,
          hasLimitInfo,
          limitInfo: detail.limit_info
        });
        
        // 判断是限流错误还是元气不足错误
        // 优先检查 limit_info，因为这是限流错误的最明确标识
        if (hasLimitInfo || errorType === '请求过于频繁') {
          // 限流错误
          const limitInfo = detail.limit_info || {};
          const retryAfterMinutes = Math.ceil((limitInfo.retry_after || 3600) / 60);
          const errorMsg = `请求过于频繁\n\n` +
            `每小时最多${limitInfo.max_requests || 10}次请求，请在 ${retryAfterMinutes} 分钟后重试。\n\n` +
            `当前请求数：${limitInfo.current_requests || 0}/${limitInfo.max_requests || 10}`;
          console.log('✅ 识别为限流错误:', errorMsg);
          throw new Error(errorMsg);
        } else {
          // 元气不足错误
          const errorMsg = `元气不足：${detail.message || '无法完成占卜'}\n\n` +
            `当前元气：${detail.current_vitality || 0}%\n` +
            `需要消耗：${detail.required_cost || 0}%\n\n` +
            `请稍等片刻，让元气恢复后再试。`;
          console.log('✅ 识别为元气不足错误:', errorMsg);
          throw new Error(errorMsg);
        }
      }
      
      // 处理500错误的详细错误信息
      if (response.status === 500 && errorData.detail) {
        let errorMessage = '';
        if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        } else if (errorData.detail && typeof errorData.detail === 'object') {
          // 如果是对象，提取 message 和 hint
          errorMessage = errorData.detail.message || errorData.detail.error || '未知错误';
          if (errorData.detail.hint) {
            errorMessage += '\n\n提示: ' + errorData.detail.hint;
          }
        } else {
          errorMessage = '占卜解读失败';
        }
        throw new Error(errorMessage);
      }
      
      throw new Error(errorData.detail || '占卜解读失败');
    }

    const data = await response.json();
    
    // 将后端响应格式转换为前端需要的格式
    const hexagramData = data.hexagram_data;
    
    // 生成本卦符号数组（从二进制转换为符号）
    // original_binary 是从下往上的数组：[初爻, 二爻, 三爻, 四爻, 五爻, 上爻]
    const hexagramSymbol = hexagramData.original_binary.map((bit: number) => 
      bit === 1 ? '▅▅▅▅▅' : '▅▅  ▅▅'
    );
    
    // 生成变卦符号数组
    // changed_binary 是从下往上的数组：[初爻, 二爻, 三爻, 四爻, 五爻, 上爻]
    const changedHexagramSymbol = hexagramData.changed_binary.map((bit: number) => 
      bit === 1 ? '▅▅▅▅▅' : '▅▅  ▅▅'
    );
    
    // 解析AI解读结果
    const interpretation = data.interpretation || '';
    let reasoning = '';
    let content = '';
    
    if (interpretation.includes('【技师在思考】') && interpretation.includes('【正式解读】')) {
      const parts = interpretation.split('【正式解读】');
      reasoning = parts[0].replace('【技师在思考】', '').trim();
      content = parts[1]?.trim() || '';
    } else if (interpretation.includes('【正式解读】')) {
      const parts = interpretation.split('【正式解读】');
      reasoning = '（技师直觉敏锐，无需多言）';
      content = parts[1]?.trim() || interpretation;
    } else {
      reasoning = '（技师直觉敏锐，无需多言）';
      content = interpretation;
    }

    return {
      hexagram: hexagramData.original_name,
      hexagramSymbol,
      changedHexagram: hexagramData.changed_name,
      changedHexagramSymbol,
      originalNature: hexagramData.original_nature,
      changedNature: hexagramData.changed_nature,
      originalHexagram: hexagramData.original_hexagram || [],  // 本卦原始数值 [6,7,8,9]
      changedHexagramValues: hexagramData.changed_hexagram || [],  // 变卦原始数值 [6,7,8,9]
      changedBinary: hexagramData.changed_binary || [],  // 变卦二进制数组，直接使用
      originalInfo: data.original_info || null,
      changedInfo: data.changed_info || null,
      reasoning: reasoning || '【技师日志】系统运行正常，开始分析...',
      content: content || '解读结果生成中...',
      karma_status: data.karma_status || null,  // 元气状态（完成6个爻后统一结算）
    };
  } catch (error) {
    console.error('占卜服务调用失败:', error);
    
    // 如果是限流错误或元气不足错误，直接重新抛出，让 App.tsx 处理
    if (error instanceof Error) {
      const errorMessage = error.message;
      if (errorMessage.includes('请求过于频繁') || errorMessage.includes('元气不足')) {
        throw error;  // 重新抛出，让上层处理
      }
    }
    
    // 其他错误返回降级响应
    return {
      hexagram: 'System_Error',
      hexagramSymbol: ['▅▅  ▅▅', '▅▅  ▅▅', '▅▅  ▅▅', '▅▅  ▅▅', '▅▅  ▅▅', '▅▅  ▅▅'],
      changedHexagram: 'System_Error',
      changedHexagramSymbol: ['▅▅  ▅▅', '▅▅  ▅▅', '▅▅  ▅▅', '▅▅  ▅▅', '▅▅  ▅▅', '▅▅  ▅▅'],
      originalNature: '未知',
      changedNature: '未知',
      originalHexagram: [],
      changedHexagramValues: [],
      changedBinary: [],
      originalInfo: null,
      changedInfo: null,
      reasoning: '【技师日志】Connection timed out. 后端服务连接失败，请检查后端服务是否运行。',
      content: error instanceof Error 
        ? `系统连接失败：${error.message}。请检查后端API服务是否正常运行（默认地址：http://localhost:8000）。`
        : '系统连接失败，请稍后重试。',
    };
  }
};
