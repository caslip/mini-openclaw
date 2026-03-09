import { useEffect, useState } from "react";
import { AppProvider, useApp } from "./store";
import Sidebar from "./components/Sidebar";
import ChatHeader from "./components/ChatHeader";
import ChatPanel from "./components/ChatPanel";
import ChatInput from "./components/ChatInput";
import "./App.css";

function AppContent() {
  const {
    sessions,
    currentSessionId,
    messages,
    isLoading,
    error,
    loadSessions,
    createSession,
    selectSession,
    deleteSession,
    sendMessage,
    clearError,
  } = useApp();

  const [retrievals, setRetrievals] = useState<Array<{id: string; content: string; source: string; score?: number}>>([]);

  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  const handleSelectSession = async (sessionId: string) => {
    await selectSession(sessionId);
  };

  const handleDeleteSession = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    await deleteSession(sessionId);
  };

  const handleNewSession = async () => {
    await createSession();
  };

  const handleSendMessage = async (text: string) => {
    setRetrievals([]);
    if (!currentSessionId) {
      const newSessionId = await createSession();
      if (newSessionId) {
        await sendMessage(text);
      }
    } else {
      await sendMessage(text);
    }
  };

  const handleSettingsClick = () => {
    // TODO: Implement settings modal
    console.log("Settings clicked");
  };

  return (
    <div className="app-container">
      <div className="app-main">
        <aside className="sidebar-container">
          <Sidebar
            sessions={sessions}
            currentSessionId={currentSessionId}
            onSelect={handleSelectSession}
            onCreate={handleNewSession}
            onDelete={handleDeleteSession}
          />
        </aside>

        <section className="chat-container">
          <ChatHeader onSettingsClick={handleSettingsClick} />
          <ChatPanel 
            messages={messages} 
            isStreaming={isLoading} 
            retrievals={retrievals}
          />
          <ChatInput onSend={handleSendMessage} disabled={isLoading} />
        </section>
      </div>

      {error && (
        <div className="error-toast" onClick={clearError}>
          {error}
        </div>
      )}
    </div>
  );
}

function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}

export default App;
