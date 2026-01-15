export interface HexagramInfo {
  composition: string;
  meaning: string;
  quote: string;
}

export interface DivinationResult {
  hexagram: string;  // 本卦名称
  hexagramSymbol: string[];  // 本卦符号
  changedHexagram: string;  // 变卦名称
  changedHexagramSymbol: string[];  // 变卦符号
  originalNature: string;  // 本卦属性
  changedNature: string;  // 变卦属性
  originalHexagram: number[];  // 本卦原始数值数组 [6,7,8,9]
  changedHexagramValues: number[];  // 变卦原始数值数组 [6,7,8,9]
  changedBinary: number[];  // 变卦二进制数组 [0,1]
  originalInfo: HexagramInfo | null;  // 本卦说明（AI生成）
  changedInfo: HexagramInfo | null;  // 变卦说明（AI生成）
  reasoning: string;
  content: string;
}

export interface TechStatus {
  status: string;
  color: string;
  bg: string;
  border: string;
}

export type Step = 'input' | 'divination' | 'loading' | 'result';
export type Stage = 'reasoning' | 'content';