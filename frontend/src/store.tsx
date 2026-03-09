import { createContext, useContext, useState, useCallback, ReactNode } from "react";
import {
  AppContextValue,
  Session,
  Message,
  ChatEvent,
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
      const newSession: Session = {
        session_id: result.session_id,
        title: result.title,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
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
              ? { ...s, title, updated_at: new Date().toISOString() }
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
      if (!currentSessionId) {
        setError("No active session");
        return;
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

      // Call streamChat and ignore the returned cancel function
      api.streamChat(
        messageText,
        currentSessionId,
        (event: ChatEvent) => {
          switch (event.type) {
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
              // Tool started - could show loading indicator
              break;

            case "tool_end":
              // Tool completed - could update UI
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
    [currentSessionId]
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
    loadSessions,
    createSession,
    renameSession,
    deleteSession,
    selectSession,
    sendMessage,
    loadRagMode,
    setRagMode: setRagModeAction,
    clearError,
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
