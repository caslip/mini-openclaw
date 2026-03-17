import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Message } from '../types';
import { ThinkingChain } from './ThinkingChain';
import './ChatMessage.css';

interface ChatMessageProps {
  message: Message;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`chat-message ${message.role}`}>
      <div className="message-avatar">
        {isUser ? '👤' : '🤖'}
      </div>
      <div className="message-body">
        {/* Show thinking chain for assistant messages */}
        {!isUser && (message.thinking || message.toolCalls?.length) && (
          <ThinkingChain
            thinking={message.thinking}
            toolCalls={message.toolCalls}
          />
        )}
        <div className="message-content">
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
