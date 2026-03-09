import React, { useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Message, RetrievalResult } from '../types';
import './ChatPanel.css';

interface ChatPanelProps {
  messages: Message[];
  isStreaming: boolean;
  retrievals: RetrievalResult[];
}

const ChatPanel: React.FC<ChatPanelProps> = ({ messages, isStreaming, retrievals }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isStreaming]);

  const handleCopy = (content: string) => {
    navigator.clipboard.writeText(content);
  };

  return (
    <div className="chat-panel">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty">
            <p>Start a conversation — type a message below.</p>
          </div>
        )}

        {messages.map((message, index) => {
          const isUser = message.role === 'user';
          return (
            <div key={index} className={`chat-message ${message.role}`}>
              {!isUser && (
                <div className="message-avatar assistant-avatar" aria-hidden>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 2a10 10 0 0 1 10 10c0 5.52-4.48 10-10 10S2 17.52 2 12 6.48 2 12 2z" />
                    <path d="M8 14s1.5 2 4 2 4-2 4-2" />
                    <line x1="9" y1="9" x2="9.01" y2="9" />
                    <line x1="15" y1="9" x2="15.01" y2="9" />
                  </svg>
                </div>
              )}
              <div className="message-block">
                <div className="message-content">
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>
                {!isUser && message.content && (
                  <div className="message-actions">
                    <button type="button" className="message-action-btn" aria-label="Like">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3" />
                      </svg>
                    </button>
                    <button type="button" className="message-action-btn" aria-label="Dislike">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h3a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-3" />
                      </svg>
                    </button>
                    <button type="button" className="message-action-btn" aria-label="Copy" onClick={() => handleCopy(message.content)}>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                      </svg>
                    </button>
                    <button type="button" className="message-action-btn" aria-label="Regenerate">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="23 4 23 10 17 10" />
                        <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
                      </svg>
                    </button>
                  </div>
                )}
              </div>
              {isUser && (
                <div className="message-avatar user-avatar" aria-hidden>U</div>
              )}
            </div>
          );
        })}

        {isStreaming && messages.length > 0 && messages[messages.length - 1].role !== 'assistant' && (
          <div className="chat-message assistant streaming">
            <div className="message-avatar assistant-avatar" aria-hidden>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2a10 10 0 0 1 10 10c0 5.52-4.48 10-10 10S2 17.52 2 12 6.48 2 12 2z" />
                <path d="M8 14s1.5 2 4 2 4-2 4-2" />
                <line x1="9" y1="9" x2="9.01" y2="9" />
                <line x1="15" y1="9" x2="15.01" y2="9" />
              </svg>
            </div>
            <div className="message-block">
              <div className="message-content">
                <span className="typing-indicator">
                  <span className="dot"></span>
                  <span className="dot"></span>
                  <span className="dot"></span>
                </span>
              </div>
            </div>
          </div>
        )}

        {retrievals.length > 0 && (
          <div className="retrieval-results">
            <div className="retrieval-header">
              <span className="retrieval-icon">📚</span>
              <span>Retrieved {retrievals.length} results</span>
            </div>
            {retrievals.map((result) => (
              <div key={result.id} className="retrieval-item">
                <div className="retrieval-source">{result.source}</div>
                <div className="retrieval-content">{result.content}</div>
                {result.score !== undefined && (
                  <div className="retrieval-score">Score: {(result.score * 100).toFixed(1)}%</div>
                )}
              </div>
            ))}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default ChatPanel;
