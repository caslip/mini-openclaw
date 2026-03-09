import { Session, ChatEvent, Message } from "./types";

const API_BASE = "/api";

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

export async function listSessions(): Promise<Session[]> {
  return request<Session[]>("/sessions");
}

export async function createSession(): Promise<{ session_id: string; title: string }> {
  return request<{ session_id: string; title: string }>("/sessions", {
    method: "POST",
  });
}

export async function renameSession(
  sessionId: string,
  title: string
): Promise<{ ok: boolean }> {
  return request<{ ok: boolean }>(`/sessions/${sessionId}`, {
    method: "PUT",
    body: JSON.stringify({ title }),
  });
}

export async function deleteSession(sessionId: string): Promise<{ ok: boolean }> {
  return request<{ ok: boolean }>(`/sessions/${sessionId}`, {
    method: "DELETE",
  });
}

export async function getSessionHistory(
  sessionId: string
): Promise<{ history: Message[] }> {
  return request<{ history: Message[] }>(`/sessions/${sessionId}/history`);
}

export async function getSessionMessages(
  sessionId: string
): Promise<{ messages: Message[] }> {
  return request<{ messages: Message[] }>(`/sessions/${sessionId}/messages`);
}

type EventCallback = (event: ChatEvent) => void;

export function streamChat(
  message: string,
  sessionId: string,
  onEvent: EventCallback
): () => void {
  let aborted = false;
  const controller = new AbortController();

  (async () => {
    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message,
          session_id: sessionId,
          stream: true,
        }),
        signal: controller.signal,
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Request failed" }));
        onEvent({ type: "error", error: error.detail || `HTTP ${response.status}` });
        return;
      }

      if (!response.body) {
        onEvent({ type: "error", error: "No response body" });
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (!aborted) {
        const { done, value } = await reader.read();

        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (aborted) break;
          if (!line.trim()) continue;

          if (line.startsWith("event: ")) {
            // const eventType = line.slice(7).trim();
            continue;
          }

          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              onEvent({ type: data.type || "token", ...data } as ChatEvent);
            } catch {
              // Skip invalid JSON
            }
          }
        }
      }
    } catch (err) {
      if (err instanceof Error && err.name !== "AbortError") {
        onEvent({ type: "error", error: err.message });
      }
    }
  })();

  return () => {
    aborted = true;
    controller.abort();
  };
}

export async function readFile(path: string): Promise<{ path: string; content: string }> {
  return request<{ path: string; content: string }>(`/files?path=${encodeURIComponent(path)}`);
}

export async function saveFile(
  path: string,
  content: string
): Promise<{ ok: boolean; path: string }> {
  return request<{ ok: boolean; path: string }>("/files", {
    method: "POST",
    body: JSON.stringify({ path, content }),
  });
}

export async function getRagMode(): Promise<{ enabled: boolean }> {
  return request<{ enabled: boolean }>("/config/rag-mode");
}

export async function setRagMode(enabled: boolean): Promise<{ enabled: boolean }> {
  return request<{ enabled: boolean }>("/config/rag-mode", {
    method: "PUT",
    body: JSON.stringify({ enabled }),
  });
}
