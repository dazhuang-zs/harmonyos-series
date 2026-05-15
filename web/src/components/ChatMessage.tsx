"use client";

import CodeBlock from "./CodeBlock";

export interface ChatMsg {
  role: "user" | "assistant" | "system";
  content: string;
  sources?: { text: string; source: string; score: number }[];
  steps?: { type: string; content: string; tool?: string }[];
}

export default function ChatMessage({ message }: { message: ChatMsg }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
          isUser
            ? "bg-blue-600 text-white"
            : "bg-emerald-600 text-white"
        }`}
      >
        {isUser ? "U" : "M"}
      </div>

      {/* Content */}
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-blue-600 text-white"
            : "bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100"
        }`}
      >
        <div className="prose prose-sm dark:prose-invert max-w-none break-words">
          {renderContent(message.content)}
        </div>

        {/* Sources */}
        {message.sources && message.sources.length > 0 && (
          <div className="mt-3 pt-3 border-t border-zinc-200 dark:border-zinc-700">
            <p className="text-xs font-medium text-zinc-500 mb-1">参考来源</p>
            {message.sources.map((s, i) => (
              <div key={i} className="text-xs text-zinc-500 truncate">
                [{i + 1}] {s.source} (相关度: {(s.score * 100).toFixed(0)}%)
              </div>
            ))}
          </div>
        )}

        {/* Agent Steps */}
        {message.steps && message.steps.length > 0 && (
          <div className="mt-3 pt-3 border-t border-zinc-200 dark:border-zinc-700">
            <p className="text-xs font-medium text-zinc-500 mb-2">执行步骤</p>
            {message.steps.map((step, i) => (
              <div key={i} className="text-xs mb-1">
                <span className="font-mono text-zinc-400">
                  {step.type === "thought" && "💭 "}
                  {step.type === "action" && "🔧 "}
                  {step.type === "observation" && "👀 "}
                  {step.type === "answer" && "✅ "}
                </span>
                <span className="text-zinc-600 dark:text-zinc-400">
                  {step.tool && <strong>{step.tool}: </strong>}
                  {step.content.slice(0, 100)}
                  {step.content.length > 100 && "..."}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function renderContent(content: string) {
  // Split content by code blocks
  const parts = content.split(/(```[\s\S]*?```)/g);

  return parts.map((part, i) => {
    if (part.startsWith("```")) {
      const lines = part.slice(3, -3).split("\n");
      const lang = lines[0].trim();
      const code = (lang ? lines.slice(1) : lines).join("\n");
      return <CodeBlock key={i} code={code} language={lang || undefined} />;
    }

    // Render inline code, bold, etc.
    return (
      <span key={i}>
        {part.split("\n").map((line, j) => (
          <span key={j}>
            {renderInline(line)}
            {j < part.split("\n").length - 1 && <br />}
          </span>
        ))}
      </span>
    );
  });
}

function renderInline(text: string) {
  // Simple inline code rendering
  const parts = text.split(/(`[^`]+`)/g);
  return parts.map((part, i) => {
    if (part.startsWith("`") && part.endsWith("`")) {
      return (
        <code
          key={i}
          className="px-1.5 py-0.5 rounded bg-zinc-200 dark:bg-zinc-700 text-sm font-mono"
        >
          {part.slice(1, -1)}
        </code>
      );
    }
    return <span key={i}>{part}</span>;
  });
}
