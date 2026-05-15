"use client";
import { useState } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

export function CodeBlock({ code, language = "typescript" }: { code: string; language?: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative my-3 rounded-lg overflow-hidden border border-zinc-200 dark:border-zinc-700">
      <div className="flex items-center justify-between px-4 py-1.5 bg-zinc-100 dark:bg-zinc-800 text-xs text-zinc-500">
        <span>{language}</span>
        <button onClick={handleCopy} className="hover:text-zinc-700 dark:hover:text-zinc-300 transition-colors">
          {copied ? "已复制 ✓" : "复制"}
        </button>
      </div>
      <SyntaxHighlighter
        language={language}
        style={oneDark}
        customStyle={{ margin: 0, borderRadius: 0, fontSize: "0.85rem" }}
        showLineNumbers
      >
        {code}
      </SyntaxHighlighter>
    </div>
  );
}

export function LoadingDots() {
  return (
    <div className="flex items-center gap-1 py-4">
      <span className="w-2 h-2 rounded-full bg-zinc-400 animate-bounce" style={{ animationDelay: "0ms" }} />
      <span className="w-2 h-2 rounded-full bg-zinc-400 animate-bounce" style={{ animationDelay: "150ms" }} />
      <span className="w-2 h-2 rounded-full bg-zinc-400 animate-bounce" style={{ animationDelay: "300ms" }} />
    </div>
  );
}

export function ErrorBox({ message }: { message: string }) {
  return (
    <div className="my-3 p-4 rounded-lg bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 text-sm">
      {message}
    </div>
  );
}
