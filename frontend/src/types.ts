export interface Message {
  role: "user" | "assistant" | "system";
  content: string;
  timestamp?: string;
}

export interface Session {
  session_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ToolCall {
  tool: string;
  args: Record<string, unknown>;
  start_time?: string;
  end_time?: string;
  result?: string;
}

export interface RetrievalResult {
  id: string;
  content: string;
  source: string;
  score?: number;
}

export interface ChatEvent {
  type: "token" | "tool_start" | "tool_end" | "retrieval" | "done" | "error";
  content?: string;
  tool?: string;
  args?: Record<string, unknown>;
  query?: string;
  results?: RetrievalResult[];
  session_id?: string;
  error?: string;
}

export interface AppState {
  sessions: Session[];
  currentSessionId: string | null;
  messages: Message[];
  ragMode: boolean;
  isLoading: boolean;
  error: string | null;
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
}

export type AppContextValue = AppState & AppActions;
