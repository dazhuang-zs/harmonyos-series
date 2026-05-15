"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import ChatSidebar from "@/components/ChatSidebar";
import ChatMessage, { ChatMsg } from "@/components/ChatMessage";
import ChatInput from "@/components/ChatInput";
import {
  listConversations,
  createConversation,
  getConversation,
  deleteConversation,
  chatStream,
  type Conversation,
} from "@/lib/api";

export default function Home() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConvId, setActiveConvId] = useState("");
  const [messages, setMessages] = useState<ChatMsg[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [mode, setMode] = useState("rag");
  const [streamingContent, setStreamingContent] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);
  const streamingConvIdRef = useRef<string>("");

  // Load conversations on mount
  useEffect(() => {
    listConversations().then(setConversations).catch(console.error);
  }, []);

  // Load messages when conversation changes
  useEffect(() => {
    if (!activeConvId) {
      setMessages([]);
      return;
    }
    getConversation(activeConvId)
      .then((data) => {
        setMessages(
          data.messages.map((m) => ({
            role: m.role as ChatMsg["role"],
            content: m.content,
          }))
        );
      })
      .catch(console.error);
  }, [activeConvId]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent]);

  // Cancel stream and clear when switching conversation
  const handleSelectConversation = useCallback(
    (id: string) => {
      if (id === activeConvId) return;
      // Cancel ongoing stream
      if (abortRef.current) {
        abortRef.current.abort();
        abortRef.current = null;
      }
      // If streaming was for a different conv, finalize its message
      if (streamingContent && streamingConvIdRef.current && streamingConvIdRef.current !== id) {
        setMessages((prev) => {
          const lastMsg = prev[prev.length - 1];
          if (lastMsg?.role === "assistant" && lastMsg.content === streamingContent) return prev;
          return [...prev, { role: "assistant" as const, content: streamingContent }];
        });
      }
      setStreamingContent("");
      setIsLoading(false);
      setActiveConvId(id);
    },
    [activeConvId, streamingContent]
  );

  const handleNewConversation = async () => {
    try {
      const conv = await createConversation();
      setConversations((prev) => [conv, ...prev]);
      setActiveConvId(conv.conversation_id);
      setMessages([]);
      setStreamingContent("");
    } catch (e) {
      console.error(e);
    }
  };

  const handleDeleteConversation = async (id: string) => {
    try {
      await deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.conversation_id !== id));
      if (activeConvId === id) {
        setActiveConvId("");
        setMessages([]);
        setStreamingContent("");
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleSend = async (message: string) => {
    // Cancel any previous stream
    if (abortRef.current) {
      abortRef.current.abort();
    }
    const controller = new AbortController();
    abortRef.current = controller;

    // Add user message
    const userMsg: ChatMsg = { role: "user", content: message };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);
    setStreamingContent("");

    try {
      let convId = activeConvId;

      // Create conversation if none selected
      if (!convId) {
        const conv = await createConversation(message.slice(0, 20));
        convId = conv.conversation_id;
        setActiveConvId(convId);
        setConversations((prev) => [conv, ...prev]);
      }

      streamingConvIdRef.current = convId;

      // Stream response
      let fullReply = "";
      await chatStream(
        { message, conversation_id: convId, mode },
        (chunk) => {
          // Only update if still on same conversation
          if (streamingConvIdRef.current === activeConvId || !activeConvId) {
            fullReply += chunk;
            setStreamingContent(fullReply);
          }
        },
        (doneConvId) => {
          // Only finalize if still on same conversation
          if (streamingConvIdRef.current === activeConvId || !activeConvId) {
            const assistantMsg: ChatMsg = {
              role: "assistant",
              content: fullReply,
            };
            setMessages((prev) => [...prev, assistantMsg]);
            setStreamingContent("");
          }

          listConversations().then(setConversations);

          if (doneConvId && doneConvId !== convId) {
            setActiveConvId(doneConvId);
          }
        },
        controller.signal
      );
    } catch (e: unknown) {
      if (e instanceof Error && e.name === "AbortError") return;
      console.error(e);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "抱歉，发生了错误。请检查后端服务是否启动。",
        },
      ]);
      setStreamingContent("");
    } finally {
      setIsLoading(false);
      if (abortRef.current === controller) {
        abortRef.current = null;
      }
    }
  };

  return (
    <div className="flex h-screen bg-white dark:bg-zinc-900">
      {/* Sidebar */}
      <ChatSidebar
        conversations={conversations}
        activeId={activeConvId}
        onSelect={handleSelectConversation}
        onNew={handleNewConversation}
        onDelete={handleDeleteConversation}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
          {messages.length === 0 && !streamingContent && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-16 h-16 rounded-2xl bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center mb-4">
                <span className="text-3xl">🤖</span>
              </div>
              <h2 className="text-2xl font-bold text-zinc-900 dark:text-white mb-2">
                HarmonyOS 开发助手
              </h2>
              <p className="text-zinc-500 max-w-md">
                MiMo 大模型驱动的鸿蒙开发助手。支持 RAG 文档问答、ArkTS
                代码生成、错误诊断和 Agent 自主决策。
              </p>
              <div className="grid grid-cols-2 gap-3 mt-8 max-w-lg w-full">
                {[
                  { icon: "📚", title: "文档问答", desc: "基于华为官方文档回答问题" },
                  { icon: "🤖", title: "Agent 模式", desc: "自动调用工具解决问题" },
                  { icon: "💻", title: "代码生成", desc: "生成 ArkTS/ArkUI 代码" },
                  { icon: "🔍", title: "错误诊断", desc: "分析编译错误并修复" },
                ].map((item) => (
                  <button
                    key={item.title}
                    onClick={() => {
                      setMode(
                        item.title === "文档问答"
                          ? "rag"
                          : item.title === "Agent 模式"
                          ? "agent"
                          : item.title === "代码生成"
                          ? "codegen"
                          : "diagnose"
                      );
                    }}
                    className="flex items-start gap-3 p-4 rounded-xl border border-zinc-200 dark:border-zinc-700 hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors text-left"
                  >
                    <span className="text-2xl">{item.icon}</span>
                    <div>
                      <p className="font-medium text-sm text-zinc-900 dark:text-white">
                        {item.title}
                      </p>
                      <p className="text-xs text-zinc-500 mt-0.5">{item.desc}</p>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <ChatMessage key={i} message={msg} />
          ))}

          {/* Streaming content — only show for active conversation */}
          {streamingContent && (
            <ChatMessage
              message={{ role: "assistant", content: streamingContent }}
            />
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <ChatInput
          onSend={handleSend}
          isLoading={isLoading}
          mode={mode}
          onModeChange={setMode}
        />
      </div>
    </div>
  );
}
