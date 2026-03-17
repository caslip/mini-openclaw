import React, { useState, useEffect, useRef } from 'react';
import { useApp } from '../store';
import { ThemeMode, FontSize, AIModel } from '../types';
import './SettingsModal.css';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type TabType = 'chat' | 'interface' | 'about';

const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose }) => {
  const { settings, updateSettings, clearCurrentSession, clearAllSessions, sessions, messages } = useApp();
  const [activeTab, setActiveTab] = useState<TabType>('chat');
  const [showClearConfirm, setShowClearConfirm] = useState<'current' | 'all' | null>(null);
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = '';
    };
  }, [isOpen, onClose]);

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) onClose();
  };

  const handleExport = () => {
    const exportData = {
      sessions: sessions,
      currentMessages: messages,
      exportedAt: new Date().toISOString(),
    };
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `mini-openclaw-export-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleClearCurrent = async () => {
    await clearCurrentSession();
    setShowClearConfirm(null);
  };

  const handleClearAll = async () => {
    await clearAllSessions();
    setShowClearConfirm(null);
  };

  if (!isOpen) return null;

  return (
    <div className="settings-overlay" onClick={handleBackdropClick}>
      <div className="settings-modal" ref={modalRef} role="dialog" aria-modal="true" aria-labelledby="settings-title">
        <div className="settings-header">
          <h2 id="settings-title" className="settings-title">Settings</h2>
          <button type="button" className="settings-close" onClick={onClose} aria-label="Close settings">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        <div className="settings-tabs">
          <button
            type="button"
            className={`settings-tab ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            Chat
          </button>
          <button
            type="button"
            className={`settings-tab ${activeTab === 'interface' ? 'active' : ''}`}
            onClick={() => setActiveTab('interface')}
          >
            Interface
          </button>
          <button
            type="button"
            className={`settings-tab ${activeTab === 'about' ? 'active' : ''}`}
            onClick={() => setActiveTab('about')}
          >
            About
          </button>
        </div>

        <div className="settings-content">
          {activeTab === 'chat' && (
            <div className="settings-section">
              <div className="settings-item">
                <div className="settings-item-label">
                  <span className="settings-item-title">AI Model</span>
                  <span className="settings-item-desc">Choose the AI model for responses</span>
                </div>
                <select
                  className="settings-select"
                  value={settings.model}
                  onChange={(e) => updateSettings({ model: e.target.value as AIModel })}
                >
                  <option value="gpt-4">GPT-4</option>
                  <option value="gpt-4-turbo">GPT-4 Turbo</option>
                  <option value="claude-3">Claude 3</option>
                  <option value="gemini-pro">Gemini Pro</option>
                </select>
              </div>

              <div className="settings-item">
                <div className="settings-item-label">
                  <span className="settings-item-title">RAG Mode</span>
                  <span className="settings-item-desc">Enable knowledge base retrieval</span>
                </div>
                <label className="settings-toggle">
                  <input
                    type="checkbox"
                    checked={settings.ragEnabled}
                    onChange={(e) => updateSettings({ ragEnabled: e.target.checked })}
                  />
                  <span className="settings-toggle-slider"></span>
                </label>
              </div>

              <div className="settings-divider"></div>

              <div className="settings-item">
                <div className="settings-item-label">
                  <span className="settings-item-title">Clear Current Session</span>
                  <span className="settings-item-desc">Delete current chat history</span>
                </div>
                {showClearConfirm === 'current' ? (
                  <div className="settings-confirm">
                    <button type="button" className="settings-btn-cancel" onClick={() => setShowClearConfirm(null)}>
                      Cancel
                    </button>
                    <button type="button" className="settings-btn-danger" onClick={handleClearCurrent}>
                      Confirm
                    </button>
                  </div>
                ) : (
                  <button type="button" className="settings-btn" onClick={() => setShowClearConfirm('current')}>
                    Clear
                  </button>
                )}
              </div>

              <div className="settings-item">
                <div className="settings-item-label">
                  <span className="settings-item-title">Clear All Sessions</span>
                  <span className="settings-item-desc">Delete all chat histories</span>
                </div>
                {showClearConfirm === 'all' ? (
                  <div className="settings-confirm">
                    <button type="button" className="settings-btn-cancel" onClick={() => setShowClearConfirm(null)}>
                      Cancel
                    </button>
                    <button type="button" className="settings-btn-danger" onClick={handleClearAll}>
                      Confirm
                    </button>
                  </div>
                ) : (
                  <button type="button" className="settings-btn" onClick={() => setShowClearConfirm('all')}>
                    Clear All
                  </button>
                )}
              </div>

              <div className="settings-item">
                <div className="settings-item-label">
                  <span className="settings-item-title">Export Data</span>
                  <span className="settings-item-desc">Download chat data as JSON</span>
                </div>
                <button type="button" className="settings-btn" onClick={handleExport}>
                  Export
                </button>
              </div>
            </div>
          )}

          {activeTab === 'interface' && (
            <div className="settings-section">
              <div className="settings-item">
                <div className="settings-item-label">
                  <span className="settings-item-title">Theme</span>
                  <span className="settings-item-desc">Choose your preferred color scheme</span>
                </div>
                <select
                  className="settings-select"
                  value={settings.theme}
                  onChange={(e) => updateSettings({ theme: e.target.value as ThemeMode })}
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                  <option value="system">System</option>
                </select>
              </div>

              <div className="settings-item">
                <div className="settings-item-label">
                  <span className="settings-item-title">Font Size</span>
                  <span className="settings-item-desc">Adjust text size for better readability</span>
                </div>
                <select
                  className="settings-select"
                  value={settings.fontSize}
                  onChange={(e) => updateSettings({ fontSize: e.target.value as FontSize })}
                >
                  <option value="small">Small</option>
                  <option value="medium">Medium</option>
                  <option value="large">Large</option>
                </select>
              </div>
            </div>
          )}

          {activeTab === 'about' && (
            <div className="settings-section">
              <div className="settings-about">
                <div className="settings-about-logo">
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 2a10 10 0 0 1 10 10c0 5.52-4.48 10-10 10S2 17.52 2 12 6.48 2 12 2z" />
                    <path d="M8 14s1.5 2 4 2 4-2 4-2" />
                    <line x1="9" y1="9" x2="9.01" y2="9" />
                    <line x1="15" y1="9" x2="15.01" y2="9" />
                  </svg>
                </div>
                <h3 className="settings-about-title">Mini-OpenClaw</h3>
                <p className="settings-about-version">Version 1.0.0</p>
                <p className="settings-about-desc">
                  A lightweight AI chat application with RAG capabilities.
                </p>
              </div>

              <div className="settings-divider"></div>

              <div className="settings-item">
                <div className="settings-item-label">
                  <span className="settings-item-title">API Status</span>
                  <span className="settings-item-desc">Backend connection status</span>
                </div>
                <span className="settings-status settings-status-ok">Connected</span>
              </div>

              <div className="settings-item">
                <div className="settings-item-label">
                  <span className="settings-item-title">Total Sessions</span>
                  <span className="settings-item-desc">Number of chat sessions</span>
                </div>
                <span className="settings-value">{sessions.length}</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SettingsModal;
