import { createContext, useContext, useState, useCallback, useEffect, ReactNode } from "react";
import {
  AppContextValue,
  Session,
  Message,
  ChatEvent,
  Settings,
  ToolCall,
} from "./types";
import * as api from "./api";

const AppContext = createContext<AppContextValue | null>(null);

interface AppProviderProps {
  children: ReactNode;
}

export function AppProvider({ children }: AppProviderProps) {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [ragMode, setRagModeState] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [settings, setSettings] = useState<Settings>({
    theme: "dark",
    fontSize: "medium",
    model: "gpt-4",
    ragEnabled: false,
  });

  // Apply theme to document
  useEffect(() => {
    const root = document.documentElement;
    if (settings.theme === "system") {
      const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      root.setAttribute("data-theme", prefersDark ? "dark" : "light");
    } else {
      root.setAttribute("data-theme", settings.theme);
    }
  }, [settings.theme]);

  // Apply font size to document
  useEffect(() => {
    const fontSizes = { small: "13px", medium: "14px", large: "15px" };
    document.documentElement.style.fontSize = fontSizes[settings.fontSize];
  }, [settings.fontSize]);

  const updateSettings = useCallback((newSettings: Partial<Settings>) => {
    setSettings((prev) => ({ ...prev, ...newSettings }));
  }, []);

  const clearCurrentSession = useCallback(async () => {
    if (currentSessionId) {
      try {
        await api.deleteSession(currentSessionId);
        setSessions((prev) => prev.filter((s) => s.session_id !== currentSessionId));
        setCurrentSessionId(null);
        setMessages([]);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to clear current session");
      }
    }
  }, [currentSessionId]);

  const clearAllSessions = useCallback(async () => {
    try {
      for (const session of sessions) {
        await api.deleteSession(session.session_id);
      }
      setSessions([]);
      setCurrentSessionId(null);
      setMessages([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to clear all sessions");
    }
  }, [sessions]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const loadSessions = useCallback(async () => {
    try {
      setIsLoading(true);
      const sessionList = await api.listSessions();
      setSessions(sessionList);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load sessions");
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createSession = useCallback(async (): Promise<string | null> => {
    try {
      setIsLoading(true);
      const result = await api.createSession();
      const now = Math.floor(Date.now() / 1000);
      const newSession: Session = {
        session_id: result.session_id,
        title: result.title,
        created_at: now,
        updated_at: now,
      };
      setSessions((prev) => [newSession, ...prev]);
      setCurrentSessionId(result.session_id);
      setMessages([]);
      return result.session_id;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create session");
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const renameSession = useCallback(
    async (sessionId: string, title: string) => {
      try {
        await api.renameSession(sessionId, title);
        setSessions((prev) =>
          prev.map((s) =>
            s.session_id === sessionId
              ? { ...s, title, updated_at: Math.floor(Date.now() / 1000) }
              : s
          )
        );
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to rename session");
      }
    },
    []
  );

  const deleteSession = useCallback(async (sessionId: string) => {
    try {
      await api.deleteSession(sessionId);
      setSessions((prev) => prev.filter((s) => s.session_id !== sessionId));
      if (currentSessionId === sessionId) {
        setCurrentSessionId(null);
        setMessages([]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete session");
    }
  }, [currentSessionId]);

  const selectSession = useCallback(async (sessionId: string) => {
    if (sessionId === currentSessionId) return;
    try {
      setCurrentSessionId(sessionId);
      const { history } = await api.getSessionHistory(sessionId);
      setMessages(history);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load session");
    }
  }, [currentSessionId]);

  const sendMessage = useCallback(
    async (messageText: string) => {
      // 无选中 session 时先自动创建，再用新 session 发消息，避免依赖异步 state 导致报错
      let sessionId = currentSessionId;
      if (!sessionId) {
        const newId = await createSession();
        if (!newId) {
          setError("Failed to create session");
          return;
        }
        sessionId = newId;
      }

      const userMessage: Message = {
        role: "user",
        content: messageText,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setError(null);

      let assistantContent = "";
      let thinkingContent = "";
      let toolCalls: ToolCall[] = [];

      api.streamChat(
        messageText,
        sessionId,
        (event: ChatEvent) => {
          switch (event.type) {
            case "thinking":
              // LLM thinking/reasoning process
              thinkingContent += event.content || "";
              setMessages((prev) => {
                const lastMsg = prev[prev.length - 1];
                if (lastMsg?.role === "assistant") {
                  return [
                    ...prev.slice(0, -1),
                    { ...lastMsg, thinking: thinkingContent },
                  ];
                }
                return [
                  ...prev,
                  {
                    role: "assistant",
                    content: "",
                    thinking: thinkingContent,
                    timestamp: new Date().toISOString(),
                  },
                ];
              });
              break;

            case "token":
              assistantContent += event.content || "";
              setMessages((prev) => {
                const lastMsg = prev[prev.length - 1];
                if (lastMsg?.role === "assistant") {
                  return [
                    ...prev.slice(0, -1),
                    { ...lastMsg, content: assistantContent },
                  ];
                }
                return [
                  ...prev,
                  {
                    role: "assistant",
                    content: assistantContent,
                    timestamp: new Date().toISOString(),
                  },
                ];
              });
              break;

            case "tool_start":
              // Tool call started
              const newToolCall: ToolCall = {
                tool: event.tool || "",
                args: event.args || {},
                status: "pending",
              };
              toolCalls = [...toolCalls, newToolCall];
              setMessages((prev) => {
                const lastMsg = prev[prev.length - 1];
                if (lastMsg?.role === "assistant") {
                  return [
                    ...prev.slice(0, -1),
                    { ...lastMsg, toolCalls },
                  ];
                }
                return [
                  ...prev,
                  {
                    role: "assistant",
                    content: "",
                    toolCalls,
                    timestamp: new Date().toISOString(),
                  },
                ];
              });
              break;

            case "tool_end":
              // Tool call completed - update the last tool call
              toolCalls = toolCalls.map((tc, idx) =>
                idx === toolCalls.length - 1
                  ? { ...tc, status: "completed", result: event.content }
                  : tc
              );
              setMessages((prev) => {
                const lastMsg = prev[prev.length - 1];
                if (lastMsg?.role === "assistant") {
                  return [
                    ...prev.slice(0, -1),
                    { ...lastMsg, toolCalls },
                  ];
                }
                return prev;
              });
              break;

            case "retrieval":
              // RAG retrieval results
              break;

            case "done":
              setIsLoading(false);
              break;

            case "error":
              setError(event.error || "An error occurred");
              setIsLoading(false);
              break;
          }
        }
      );

      // Note: streamChat returns a cancel function but we don't expose it
    },
    [currentSessionId, createSession]
  );

  const loadRagMode = useCallback(async () => {
    try {
      const { enabled } = await api.getRagMode();
      setRagModeState(enabled);
    } catch (err) {
      console.error("Failed to load RAG mode:", err);
    }
  }, []);

  const setRagModeAction = useCallback(async (enabled: boolean) => {
    try {
      await api.setRagMode(enabled);
      setRagModeState(enabled);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to set RAG mode");
    }
  }, []);

  const value: AppContextValue = {
    sessions,
    currentSessionId,
    messages,
    ragMode,
    isLoading,
    error,
    settings,
    loadSessions,
    createSession,
    renameSession,
    deleteSession,
    selectSession,
    sendMessage,
    loadRagMode,
    setRagMode: setRagModeAction,
    clearError,
    updateSettings,
    clearCurrentSession,
    clearAllSessions,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp(): AppContextValue {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error("useApp must be used within an AppProvider");
  }
  return context;
}
