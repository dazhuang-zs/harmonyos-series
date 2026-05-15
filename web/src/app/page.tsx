"use client";

import { useState, useRef, useEffect } from "react";
import { SendHorizontal, Bot, User, ExternalLink } from "lucide-react";
import { ragQuery } from "@/lib/api";
import { LoadingDots, ErrorBox } from "@/components/ui";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: { text: string; source: string; score: number }[];
}

function SourceCard({ source }: { source: { text: string; source: string; score: number } }) {
  return (
    <div className="mt-2 p-2 rounded bg-zinc-100 dark:bg-zinc-800 text-xs">
      <div className="flex items-center gap-1 text-zinc-500 mb-1">
        <ExternalLink size={12} />
        <span className="truncate">{source.source}</span>
        <span className="ml-auto text-zinc-400">{(source.score * 100).toFixed(0)}%</span>
      </div>
      <div className="text-zinc-600 dark:text-zinc-400 line-clamp-3">{source.text}</div>
    </div>
  );
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const q = input.trim();
    if (!q || loading) return;

    setInput("");
    setError("");
    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setLoading(true);

    try {
      const result = await ragQuery(q, 5);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: result.answer, sources: result.sources },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "未知错误");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto flex flex-col h-[calc(100vh-3.5rem)]">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-20">
            <h1 className="text-4xl mb-3">🦋</h1>
            <h2 className="text-xl font-semibold text-zinc-800 dark:text-zinc-200 mb-2">
              HarmonyOS 开发助手
            </h2>
            <p className="text-zinc-500 dark:text-zinc-400 text-sm">
              基于 RAG 的鸿蒙文档问答 · 问我 ArkTS / ArkUI 相关问题
            </p>
            <div className="mt-6 flex flex-wrap justify-center gap-2">
              {["@State 和 @Prop 有什么区别？", "怎么实现页面路由跳转？", "ArkTS 中如何发起 HTTP 请求？"].map(
                (q) => (
                  <button
                    key={q}
                    onClick={() => setInput(q)}
                    className="px-3 py-1.5 text-xs rounded-full border border-zinc-200 dark:border-zinc-700 text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
                  >
                    {q}
                  </button>
                )
              )}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className="flex gap-3">
            <div className="mt-0.5 flex-shrink-0">
              {msg.role === "user" ? (
                <div className="w-7 h-7 rounded-full bg-zinc-200 dark:bg-zinc-700 flex items-center justify-center">
                  <User size={14} />
                </div>
              ) : (
                <div className="w-7 h-7 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center text-lg">
                  🦋
                </div>
              )}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium mb-1 text-zinc-500">
                {msg.role === "user" ? "你" : "助手"}
              </div>
              <div className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap text-zinc-800 dark:text-zinc-200">
                {msg.content}
              </div>
              {msg.sources && msg.sources.length > 0 && (
                <details className="mt-2">
                  <summary className="text-xs text-zinc-400 cursor-pointer hover:text-zinc-600 dark:hover:text-zinc-300">
                    参考来源 ({msg.sources.length})
                  </summary>
                  <div className="mt-2 space-y-2">
                    {msg.sources.map((s, j) => (
                      <SourceCard key={j} source={s} />
                    ))}
                  </div>
                </details>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex gap-3">
            <div className="w-7 h-7 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center text-lg">🦋</div>
            <LoadingDots />
          </div>
        )}
        {error && <ErrorBox message={error} />}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="border-t bg-white dark:bg-zinc-900 px-4 py-3">
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="输入你的鸿蒙开发问题…"
            className="flex-1 px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="p-2.5 rounded-xl bg-blue-600 text-white disabled:opacity-40 hover:bg-blue-700 transition-colors"
          >
            <SendHorizontal size={18} />
          </button>
        </div>
      </form>
    </div>
  );
}
