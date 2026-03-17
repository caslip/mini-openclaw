export interface Message {
  role: "user" | "assistant" | "system";
  content: string;
  timestamp?: string | number;
  thinking?: string;       // LLM 思考过程
  toolCalls?: ToolCall[];  // 工具调用列表
}

export interface Session {
  session_id: string;
  title: string;
  created_at: string | number;
  updated_at: string | number;
}

export interface ToolCall {
  id?: string;
  tool: string;
  args: Record<string, unknown>;
  start_time?: string;
  end_time?: string;
  result?: string;
  status?: "pending" | "completed";
}

export interface RetrievalResult {
  id: string;
  content: string;
  source: string;
  score?: number;
}

export interface ChatEvent {
  type: "token" | "thinking" | "tool_start" | "tool_end" | "retrieval" | "done" | "error";
  content?: string;
  tool?: string;
  args?: Record<string, unknown>;
  query?: string;
  results?: RetrievalResult[];
  session_id?: string;
  error?: string;
}

export type ThemeMode = "light" | "dark" | "system";
export type FontSize = "small" | "medium" | "large";
export type AIModel = "gpt-4" | "gpt-4-turbo" | "claude-3" | "gemini-pro";

export interface Settings {
  theme: ThemeMode;
  fontSize: FontSize;
  model: AIModel;
  ragEnabled: boolean;
}

export interface AppState {
  sessions: Session[];
  currentSessionId: string | null;
  messages: Message[];
  ragMode: boolean;
  isLoading: boolean;
  error: string | null;
  settings: Settings;
}

export interface AppActions {
  loadSessions: () => Promise<void>;
  createSession: () => Promise<string | null>;
  renameSession: (sessionId: string, title: string) => Promise<void>;
  deleteSession: (sessionId: string) => Promise<void>;
  selectSession: (sessionId: string) => Promise<void>;
  sendMessage: (message: string) => Promise<void>;
  loadRagMode: () => Promise<void>;
  setRagMode: (enabled: boolean) => Promise<void>;
  clearError: () => void;
  updateSettings: (settings: Partial<Settings>) => void;
  clearCurrentSession: () => Promise<void>;
  clearAllSessions: () => Promise<void>;
}

export type AppContextValue = AppState & AppActions;
