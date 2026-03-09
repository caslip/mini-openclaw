import React, { useMemo, useState } from 'react';
import { Session } from '../types';
import './Sidebar.css';

type TimeGroup = 'today' | 'yesterday' | 'week' | 'older';

function getTimeGroup(dateString: string): TimeGroup {
  const date = new Date(dateString);
  const now = new Date();
  const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
  if (diffDays === 0) return 'today';
  if (diffDays === 1) return 'yesterday';
  if (diffDays < 7) return 'week';
  return 'older';
}

const GROUP_LABELS: Record<TimeGroup, string> = {
  today: 'Today',
  yesterday: 'Yesterday',
  week: 'Previous 7 Days',
  older: 'Previous 30 Days',
};

interface SidebarProps {
  sessions: Session[];
  currentSessionId: string | null;
  onSelect: (sessionId: string) => void;
  onCreate: () => void;
  onDelete: (sessionId: string, e: React.MouseEvent) => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  sessions,
  currentSessionId,
  onSelect,
  onCreate,
  onDelete,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [pendingDeleteId, setPendingDeleteId] = useState<string | null>(null);

  const groupedSessions = useMemo(() => {
    const groups: Record<TimeGroup, Session[]> = {
      today: [],
      yesterday: [],
      week: [],
      older: [],
    };
    const q = searchQuery.trim().toLowerCase();
    sessions.forEach((s) => {
      if (q && !(s.title || '').toLowerCase().includes(q)) return;
      const g = getTimeGroup(s.updated_at);
      groups[g].push(s);
    });
    return groups;
  }, [sessions, searchQuery]);

  const handleDeleteClick = (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setPendingDeleteId(sessionId);
  };

  const handleConfirmDelete = () => {
    if (pendingDeleteId) {
      onDelete(pendingDeleteId, { stopPropagation: () => {} } as React.MouseEvent);
      setPendingDeleteId(null);
    }
  };

  const handleCancelDelete = () => {
    setPendingDeleteId(null);
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <button
          className="new-chat-button"
          onClick={onCreate}
          aria-label="New chat"
        >
          <span className="new-chat-icon">+</span>
          New chat
        </button>
        <div className="sidebar-search-wrap">
          <svg className="sidebar-search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <input
            type="text"
            className="sidebar-search"
            placeholder="Search chats"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            aria-label="Search chats"
          />
        </div>
      </div>

      <div className="sessions-list">
        {sessions.length === 0 ? (
          <div className="sessions-empty">
            <p>No chats yet.</p>
            <p>Click "New chat" to start.</p>
          </div>
        ) : (
          (['today', 'yesterday', 'week', 'older'] as TimeGroup[]).map((group) => {
            const list = groupedSessions[group];
            if (list.length === 0) return null;
            return (
              <div key={group} className="session-group">
                <div className="session-group-label">{GROUP_LABELS[group]}</div>
                {list.map((session) => (
                  <div
                    key={session.session_id}
                    className={`session-item ${
                      session.session_id === currentSessionId ? 'active' : ''
                    }`}
                    onClick={() => onSelect(session.session_id)}
                  >
                    <div className="session-info">
                      <div className="session-title">{session.title || 'New chat'}</div>
                    </div>
                    <button
                      className="delete-button"
                      onClick={(e) => handleDeleteClick(session.session_id, e)}
                      aria-label="Delete chat"
                    >
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <line x1="18" y1="6" x2="6" y2="18" />
                        <line x1="6" y1="6" x2="18" y2="18" />
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
            );
          })
        )}
      </div>

      {pendingDeleteId && (
        <div className="delete-confirm-overlay" onClick={handleCancelDelete}>
          <div className="delete-confirm-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="delete-confirm-title">Delete chat?</div>
            <div className="delete-confirm-message">
              This will permanently delete this conversation and all its messages.
            </div>
            <div className="delete-confirm-actions">
              <button
                type="button"
                className="delete-confirm-cancel"
                onClick={handleCancelDelete}
              >
                Cancel
              </button>
              <button
                type="button"
                className="delete-confirm-delete"
                onClick={handleConfirmDelete}
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Sidebar;
