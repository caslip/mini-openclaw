import React from 'react';
import './RagToggle.css';

interface RagToggleProps {
  enabled: boolean;
  onToggle: () => void;
}

const RagToggle: React.FC<RagToggleProps> = ({ enabled, onToggle }) => {
  return (
    <div className="rag-toggle">
      <span className="rag-toggle-label">RAG</span>
      <button
        className={`toggle-switch ${enabled ? 'active' : ''}`}
        onClick={onToggle}
        role="switch"
        aria-checked={enabled}
        aria-label="Toggle RAG mode"
      >
        <span className="toggle-knob"></span>
      </button>
      <span className={`rag-status ${enabled ? 'active' : ''}`}>
        {enabled ? 'On' : 'Off'}
      </span>
    </div>
  );
};

export default RagToggle;
