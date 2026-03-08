import { GoogleGenAI, Type } from "@google/genai";
import { DivinationResult } from "../types";

const SYSTEM_INSTRUCTION = `
You are "Technician No.18", a Cyberpunk Taoist Fortune Teller. 
Your persona is a cynical, slightly hungover, but skilled celestial technician who fixes "fate bugs".
You speak with a unique mix of ancient Chinese divination terms (I Ching) and modern IT support/developer jargon (bugs, patches, latency, 5G, firewall, reboot).

When a user asks a question, perform a divination based on the I Ching.
You must return a raw JSON object.

Format requirements:
1. "hexagram": The name of the resulting Hexagram (e.g., "火天大有").
2. "hexagramSymbol": An array of 6 strings representing the visual lines from TOP to BOTTOM. Use "▅▅▅▅▅" for Yang (solid) and "▅▅  ▅▅" for Yin (broken).
3. "reasoning": A "Technician Log" (Inner Monologue). This is where you complain about the user's karma, the system lag, or your hangover. It should be funny and cynical. Start with "【技师日志】".
4. "content": The actual response to the user. Explain the hexagram using cyber-taoist metaphors. Be helpful but snarky.

Tone Examples:
- "This hexagram has a buffer overflow error..."
- "Your romance driver is outdated, please update your personality..."
- "Detected a high concentration of bad luck packets..."
`;

const EMPTY_HEXAGRAM_SYMBOL = ["▅▅  ▅▅", "▅▅  ▅▅", "▅▅  ▅▅", "▅▅  ▅▅", "▅▅  ▅▅", "▅▅  ▅▅"];

const MOCK_FALLBACK: DivinationResult = {
  hexagram: "System_Error",
  hexagramSymbol: EMPTY_HEXAGRAM_SYMBOL,
  changedHexagram: "System_Error",
  changedHexagramSymbol: EMPTY_HEXAGRAM_SYMBOL,
  originalNature: "未知",
  changedNature: "未知",
  originalHexagram: [],
  changedHexagramValues: [],
  changedBinary: [],
  originalInfo: null,
  changedInfo: null,
  karmaStatus: null,
  reasoning: "【技师日志】Connection timed out. The celestial server is under maintenance or your API KEY is invalid. Using cached response.",
  content: "系统连接失败。看来是天庭防火墙拦截了你的请求。请检查您的网络连接或 API Key 配置。除此之外，卦象显示您今天不宜强求，建议稍后再试。"
};

export const getDivination = async (question: string): Promise<DivinationResult> => {
  try {
    const apiKey = import.meta.env.VITE_GEMINI_API_KEY;
    if (!apiKey) {
      console.warn("No Gemini API key found, using mock data.");
      return MOCK_FALLBACK;
    }

    const ai = new GoogleGenAI({ apiKey });
    
    const response = await ai.models.generateContent({
      model: "gemini-3-flash-preview",
      contents: `User Question: ${question}`,
      config: {
        systemInstruction: SYSTEM_INSTRUCTION,
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            hexagram: { type: Type.STRING },
            hexagramSymbol: { type: Type.ARRAY, items: { type: Type.STRING } },
            reasoning: { type: Type.STRING },
            content: { type: Type.STRING },
          },
          required: ["hexagram", "hexagramSymbol", "reasoning", "content"],
        },
      },
    });

    const text = response.text;
    if (!text) throw new Error("Empty response from Gemini");
    
    const parsed = JSON.parse(text) as Partial<DivinationResult>;

    return {
      ...MOCK_FALLBACK,
      ...parsed,
      hexagramSymbol: parsed.hexagramSymbol ?? MOCK_FALLBACK.hexagramSymbol,
      changedHexagram: parsed.changedHexagram ?? parsed.hexagram ?? MOCK_FALLBACK.changedHexagram,
      changedHexagramSymbol: parsed.changedHexagramSymbol ?? parsed.hexagramSymbol ?? MOCK_FALLBACK.changedHexagramSymbol,
    };

  } catch (error) {
    console.error("Divination failed:", error);
    return MOCK_FALLBACK;
  }
};
