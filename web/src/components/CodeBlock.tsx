"use client";

import { useState } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

interface CodeBlockProps {
  code: string;
  language?: string;
}

export default function CodeBlock({ code, language }: CodeBlockProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const detectedLang = language || detectLanguage(code);

  return (
    <div className="relative group my-3 rounded-lg overflow-hidden border border-zinc-200 dark:border-zinc-700">
      <div className="flex items-center justify-between px-4 py-2 bg-zinc-100 dark:bg-zinc-800 text-xs text-zinc-500">
        <span>{detectedLang}</span>
        <button
          onClick={handleCopy}
          className="opacity-0 group-hover:opacity-100 transition-opacity px-2 py-1 rounded hover:bg-zinc-200 dark:hover:bg-zinc-700"
        >
          {copied ? "已复制" : "复制"}
        </button>
      </div>
      <SyntaxHighlighter
        language={detectedLang}
        style={oneDark}
        customStyle={{ margin: 0, borderRadius: 0, fontSize: "0.875rem" }}
        showLineNumbers
      >
        {code}
      </SyntaxHighlighter>
    </div>
  );
}

function detectLanguage(code: string): string {
  if (code.includes("@Entry") || code.includes("@Component") || code.includes("struct ") && code.includes("build()")) return "typescript";
  if (code.includes("import ") && code.includes("from ")) return "typescript";
  if (code.includes("def ") || code.includes("import ") && code.includes("python")) return "python";
  if (code.includes("fun ") || code.includes("class ") && code.includes("Kt")) return "kotlin";
  if (code.includes("public class") || code.includes("void main")) return "java";
  if (code.includes("<") && code.includes("/>")) return "xml";
  return "typescript";
}
