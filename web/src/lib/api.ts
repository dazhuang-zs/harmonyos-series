export interface Conversation {
  conversation_id: string;
  title: string;
  message_count: number;
  created_at: number;
  updated_at: number;
}

export interface Message {
  role: string;
  content: string;
  timestamp: number;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  mode?: "rag" | "agent" | "codegen" | "diagnose";
  stream?: boolean;
}

export interface ChatResponse {
  reply: string;
  conversation_id: string;
  mode: string;
  sources?: { text: string; source: string; score: number }[];
  steps?: { type: string; content: string; tool?: string }[];
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

async function fetchJSON<T>(path: string, init?: RequestInit): Promise<T> {
  const url = path.startsWith("http") ? path : `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

// --- Conversations ---

export async function listConversations(): Promise<Conversation[]> {
  return fetchJSON("/api/v1/conversations/");
}

export async function createConversation(
  title = "新对话"
): Promise<Conversation> {
  return fetchJSON("/api/v1/conversations/", {
    method: "POST",
    body: JSON.stringify({ title }),
  });
}

export async function getConversation(id: string) {
  return fetchJSON<{
    conversation_id: string;
    title: string;
    messages: Message[];
    user_preferences: Record<string, unknown>;
  }>(`/api/v1/conversations/${id}`);
}

export async function deleteConversation(id: string) {
  return fetchJSON(`/api/v1/conversations/${id}`, { method: "DELETE" });
}

// --- Chat ---

export async function chat(req: ChatRequest): Promise<ChatResponse> {
  return fetchJSON("/api/v1/chat/", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export async function chatStream(
  req: ChatRequest,
  onChunk: (text: string) => void,
  onDone?: (conversationId: string) => void
): Promise<void> {
  const res = await fetch(`${API_BASE}/api/v1/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });

  if (!res.ok) throw new Error(`API error: ${res.status}`);

  const reader = res.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      // 流结束但没收到 [DONE]，也要通知完成
      onDone?.("");
      return;
    }

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      const data = line.slice(6);

      if (data === "[DONE]") {
        onDone?.("");
        return;
      }

      if (data.startsWith("[DONE:")) {
        const id = data.slice(6, -1);
        onDone?.(id);
        return;
      }

      onChunk(data);
    }
  }
}

// --- Health ---

export async function healthCheck(): Promise<{ status: string }> {
  return fetchJSON("/health");
}
