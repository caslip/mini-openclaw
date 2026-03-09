import React, { useState } from 'react';
import './FileEditor.css';

interface FileEditorProps {
  filePath: string;
  fileContent: string;
  onPathChange: (path: string) => void;
  onContentChange: (content: string) => void;
  onSave: () => void;
  availableFiles?: string[];
  isLoading?: boolean;
  error?: string | null;
}

const FileEditor: React.FC<FileEditorProps> = ({
  filePath,
  fileContent,
  onPathChange,
  onContentChange,
  onSave,
  availableFiles = [],
  isLoading = false,
  error = null,
}) => {
  const [isDirty, setIsDirty] = useState(false);

  const handlePathChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onPathChange(e.target.value);
  };

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setIsDirty(true);
    onContentChange(e.target.value);
  };

  const handleSave = () => {
    onSave();
    setIsDirty(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
      e.preventDefault();
      handleSave();
    }
  };

  return (
    <div className="file-editor">
      {isLoading && <div className="file-editor-loading">Loading...</div>}
      {error && <div className="file-editor-error">{error}</div>}
      <div className="file-editor-header">
        <div className="file-path-section">
          <label htmlFor="file-path" className="file-path-label">File Path:</label>
          {availableFiles.length > 0 ? (
            <select
              id="file-path"
              className="file-path-select"
              value={filePath}
              onChange={(e) => onPathChange(e.target.value)}
            >
              <option value="">Select a file...</option>
              {availableFiles.map((file) => (
                <option key={file} value={file}>{file}</option>
              ))}
            </select>
          ) : (
            <input
              id="file-path"
              type="text"
              className="file-path-input"
              value={filePath}
              onChange={handlePathChange}
              placeholder="Enter file path..."
            />
          )}
        </div>
        <button
          className={`save-button ${isDirty ? 'dirty' : ''}`}
          onClick={handleSave}
          disabled={!filePath}
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
            <polyline points="17 21 17 13 7 13 7 21"></polyline>
            <polyline points="7 3 7 8 15 8"></polyline>
          </svg>
          {isDirty ? 'Save*' : 'Save'}
        </button>
      </div>

      <div className="file-editor-content">
        <textarea
          className="file-content-textarea"
          value={fileContent}
          onChange={handleContentChange}
          onKeyDown={handleKeyDown}
          placeholder="File content will appear here..."
          spellCheck={false}
        />
      </div>
    </div>
  );
};

export default FileEditor;
