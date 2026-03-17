import { useState } from "react";
import type { ToolCall as ToolCallType } from "../types";
import "./ThinkingChain.css";

interface ThinkingChainProps {
  thinking?: string;
  toolCalls?: ToolCallType[];
}

export function ThinkingChain({ thinking, toolCalls }: ThinkingChainProps) {
  const [collapsed, setCollapsed] = useState(false);

  if (!thinking && !toolCalls?.length) return null;

  return (
    <div className="thinking-chain">
      <div className="thinking-header" onClick={() => setCollapsed(!collapsed)}>
        <span className="thinking-toggle">{collapsed ? "▶" : "▼"}</span>
        <span className="thinking-title">思维过程</span>
        {thinking && <span className="thinking-badge">思考中</span>}
        {toolCalls && toolCalls.length > 0 && (
          <span className="tool-badge">{toolCalls.length} 个工具</span>
        )}
      </div>

      {!collapsed && (
        <div className="thinking-content">
          {thinking && (
            <div className="thinking-reasoning">
              <span className="thinking-icon">🤔</span>
              <pre className="thinking-text">{thinking}</pre>
            </div>
          )}

          {toolCalls?.map((call, idx) => (
            <div key={idx} className={`tool-call ${call.status}`}>
              <div className="tool-call-header">
                <span className="tool-icon">
                  {call.status === "pending" ? "⏳" : "🔧"}
                </span>
                <span className="tool-name">{call.tool}</span>
                <span className="tool-status">
                  {call.status === "pending" ? "执行中..." : "已完成"}
                </span>
              </div>
              {call.args && Object.keys(call.args).length > 0 && (
                <pre className="tool-args">
                  {JSON.stringify(call.args, null, 2)}
                </pre>
              )}
              {call.result && (
                <pre className="tool-result">{call.result}</pre>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
