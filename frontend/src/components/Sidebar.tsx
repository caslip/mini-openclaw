import React, { useMemo, useState, useEffect, useRef } from 'react';
import { Session } from '../types';
import './Sidebar.css';

const PINNED_STORAGE_KEY = 'sidebar-pinned-session-ids';

type TimeGroup = 'today' | 'yesterday' | 'older';

function getTimeGroup(dateString: string | number): TimeGroup {
  // 后端存的是 Unix 时间戳（秒），需要乘以 1000 转为毫秒
  const timestamp = typeof dateString === 'number' ? dateString : parseInt(dateString, 10);
  const date = new Date(timestamp * 1000);
  const now = new Date();
  const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
  if (diffDays === 0) return 'today';
  if (diffDays === 1) return 'yesterday';
  return 'older';
}

function formatSessionTime(dateString: string | number): string {
  // 后端存的是 Unix 时间戳（秒），需要乘以 1000 转为毫秒
  const timestamp = typeof dateString === 'number' ? dateString : parseInt(dateString, 10);
  const date = new Date(timestamp * 1000);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffMins < 1) return '刚刚';
  if (diffMins < 60) return `${diffMins}分钟前`;
  if (diffHours < 24) return `${diffHours}小时前`;
  if (diffDays === 1) return '昨天';
  if (diffDays < 7) return `${diffDays}天前`;
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
}

function loadPinnedIds(): Set<string> {
  try {
    const raw = localStorage.getItem(PINNED_STORAGE_KEY);
    if (!raw) return new Set();
    const arr = JSON.parse(raw) as string[];
    return new Set(Array.isArray(arr) ? arr : []);
  } catch {
    return new Set();
  }
}

function savePinnedIds(ids: Set<string>) {
  localStorage.setItem(PINNED_STORAGE_KEY, JSON.stringify([...ids]));
}

const GROUP_LABELS: Record<TimeGroup, string> = {
  today: '今天',
  yesterday: '昨天',
  older: '更早',
};

export interface SidebarProps {
  sessions: Session[];
  currentSessionId: string | null;
  onSelect: (sessionId: string) => void;
  onCreate: () => void;
  onRename: (sessionId: string, title: string) => Promise<void>;
  onDelete: (sessionId: string, e: React.MouseEvent) => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  sessions,
  currentSessionId,
  onSelect,
  onCreate,
  onRename,
  onDelete,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [pendingDeleteId, setPendingDeleteId] = useState<string | null>(null);
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);
  const [pinnedIds, setPinnedIds] = useState<Set<string>>(loadPinnedIds);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    savePinnedIds(pinnedIds);
  }, [pinnedIds]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (openMenuId && menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setOpenMenuId(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [openMenuId]);

  const groupedSessions = useMemo(() => {
    const groups: Record<TimeGroup, Session[]> = {
      today: [],
      yesterday: [],
      older: [],
    };
    const q = searchQuery.trim().toLowerCase();
    sessions.forEach((s) => {
      if (q && !(s.title || '').toLowerCase().includes(q)) return;
      const g = getTimeGroup(s.updated_at);
      groups[g].push(s);
    });
    // Sort each group: pinned first, then by updated_at desc
    (['today', 'yesterday', 'older'] as TimeGroup[]).forEach((key) => {
      groups[key].sort((a, b) => {
        const aPin = pinnedIds.has(a.session_id) ? 1 : 0;
        const bPin = pinnedIds.has(b.session_id) ? 1 : 0;
        if (bPin !== aPin) return bPin - aPin;
        const getTimestamp = (ts: string | number) => typeof ts === 'number' ? ts : parseInt(ts, 10);
        return getTimestamp(b.updated_at) - getTimestamp(a.updated_at);
      });
    });
    return groups;
  }, [sessions, searchQuery, pinnedIds]);

  const handleMenuToggle = (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setOpenMenuId((prev) => (prev === sessionId ? null : sessionId));
  };

  const handleRenameClick = (session: Session) => {
    setOpenMenuId(null);
    setEditingId(session.session_id);
    setEditTitle(session.title || '新会话');
  };

  const handleRenameSubmit = async (sessionId: string) => {
    const title = editTitle.trim() || '新会话';
    setEditingId(null);
    setEditTitle('');
    await onRename(sessionId, title);
  };

  const handlePinClick = (sessionId: string) => {
    setOpenMenuId(null);
    setPinnedIds((prev) => {
      const next = new Set(prev);
      if (next.has(sessionId)) next.delete(sessionId);
      else next.add(sessionId);
      return next;
    });
  };

  const handleDeleteClick = (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setOpenMenuId(null);
    setPendingDeleteId(sessionId);
  };

  const handleConfirmDelete = () => {
    if (pendingDeleteId) {
      onDelete(pendingDeleteId, { stopPropagation: () => {} } as React.MouseEvent);
      setPinnedIds((prev) => {
        const next = new Set(prev);
        next.delete(pendingDeleteId);
        return next;
      });
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
          (['today', 'yesterday', 'older'] as TimeGroup[]).map((group) => {
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
                    } ${pinnedIds.has(session.session_id) ? 'pinned' : ''}`}
                    onClick={() => {
                      if (editingId !== session.session_id) onSelect(session.session_id);
                    }}
                  >
                    <div className="session-info">
                      {editingId === session.session_id ? (
                        <input
                          className="session-rename-input"
                          value={editTitle}
                          onChange={(e) => setEditTitle(e.target.value)}
                          onKeyDown={(e) => {
                            e.stopPropagation();
                            if (e.key === 'Enter') handleRenameSubmit(session.session_id);
                            if (e.key === 'Escape') {
                              setEditingId(null);
                              setEditTitle('');
                            }
                          }}
                          onClick={(e) => e.stopPropagation()}
                          onBlur={() => handleRenameSubmit(session.session_id)}
                          autoFocus
                          aria-label="Rename session"
                        />
                      ) : (
                        <>
                          <div className="session-title">{session.title || '新会话'}</div>
                          <div className="session-time">{formatSessionTime(session.updated_at)}</div>
                        </>
                      )}
                    </div>
                    <div className="session-item-actions" ref={openMenuId === session.session_id ? menuRef : undefined}>
                      <button
                        type="button"
                        className="session-menu-trigger"
                        onClick={(e) => handleMenuToggle(session.session_id, e)}
                        aria-label="Session menu"
                        aria-expanded={openMenuId === session.session_id}
                      >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
                          <circle cx="12" cy="6" r="1.5" />
                          <circle cx="12" cy="12" r="1.5" />
                          <circle cx="12" cy="18" r="1.5" />
                        </svg>
                      </button>
                      {openMenuId === session.session_id && (
                        <div className="session-menubar" role="menu">
                          <button
                            type="button"
                            className="session-menubar-item"
                            role="menuitem"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleRenameClick(session);
                            }}
                          >
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
                              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                            </svg>
                            <span>重命名</span>
                          </button>
                          <button
                            type="button"
                            className="session-menubar-item"
                            role="menuitem"
                            onClick={(e) => {
                              e.stopPropagation();
                              handlePinClick(session.session_id);
                            }}
                          >
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
                              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                              <circle cx="12" cy="10" r="3" />
                            </svg>
                            <span>{pinnedIds.has(session.session_id) ? '取消置顶' : '置顶'}</span>
                          </button>
                          <button
                            type="button"
                            className="session-menubar-item session-menubar-item-danger"
                            role="menuitem"
                            onClick={(e) => handleDeleteClick(session.session_id, e)}
                          >
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
                              <polyline points="3 6 5 6 21 6" />
                              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                              <line x1="10" y1="11" x2="10" y2="17" />
                              <line x1="14" y1="11" x2="14" y2="17" />
                            </svg>
                            <span>删除</span>
                          </button>
                        </div>
                      )}
                    </div>
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
