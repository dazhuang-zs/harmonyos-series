"use client";

import { useState } from "react";
import { Bug, Lightbulb } from "lucide-react";
import { diagnoseError } from "@/lib/api";
import { LoadingDots, ErrorBox } from "@/components/ui";

export default function DiagnosePage() {
  const [errorMessage, setErrorMessage] = useState("");
  const [codeContext, setCodeContext] = useState("");
  const [result, setResult] = useState<{
    diagnosis: string;
    fix_suggestions: string[];
    related_docs: { text: string; source: string; score: number }[];
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!errorMessage.trim() || loading) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const res = await diagnoseError(errorMessage, codeContext);
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "未知错误");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-1">🔧 错误诊断</h1>
      <p className="text-zinc-500 text-sm mb-6">粘贴编译错误信息，自动定位原因并给出修复方案</p>

      <form onSubmit={handleSubmit} className="space-y-4 mb-8">
        <div>
          <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">
            错误信息
          </label>
          <textarea
            value={errorMessage}
            onChange={(e) => setErrorMessage(e.target.value)}
            placeholder='例："Cannot find module @ohos/net" 或 "Type mismatch: expected string, got number"'
            rows={4}
            className="w-full px-4 py-3 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-red-500 resize-none"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">
            相关代码片段 <span className="text-zinc-400 font-normal">（可选）</span>
          </label>
          <textarea
            value={codeContext}
            onChange={(e) => setCodeContext(e.target.value)}
            placeholder="粘贴出错的代码片段…"
            rows={4}
            className="w-full px-4 py-3 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          />
        </div>
        <button
          type="submit"
          disabled={loading || !errorMessage.trim()}
          className="px-5 py-2 bg-red-600 text-white text-sm font-medium rounded-xl disabled:opacity-40 hover:bg-red-700 transition-colors flex items-center gap-2"
        >
          <Bug size={16} />
          开始诊断
        </button>
      </form>

      {loading && (
        <div className="flex items-center gap-3 text-zinc-500">
          <span>正在分析错误…</span>
          <LoadingDots />
        </div>
      )}

      {error && <ErrorBox message={error} />}

      {result && (
        <div className="space-y-6">
          {/* 诊断报告 */}
          <div className="p-6 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-900">
            <div className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap text-zinc-800 dark:text-zinc-200">
              {result.diagnosis}
            </div>
          </div>

          {/* 修复建议 */}
          {result.fix_suggestions.length > 0 && (
            <div className="p-6 rounded-xl border border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-950">
              <h3 className="flex items-center gap-2 font-semibold text-green-800 dark:text-green-200 mb-3">
                <Lightbulb size={16} />
                修复建议
              </h3>
              <ul className="space-y-2">
                {result.fix_suggestions.map((s, i) => (
                  <li key={i} className="text-sm text-green-700 dark:text-green-300 flex items-start gap-2">
                    <span className="mt-0.5">▸</span>
                    <span>{s}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* 参考文档 */}
          {result.related_docs?.length > 0 && (
            <details className="p-4 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-900">
              <summary className="text-sm font-medium text-zinc-600 dark:text-zinc-400 cursor-pointer">
                相关文档参考 ({result.related_docs.length})
              </summary>
              <div className="mt-3 space-y-2">
                {result.related_docs.map((doc, i) => (
                  <div key={i} className="p-3 rounded-lg bg-zinc-50 dark:bg-zinc-800 text-xs text-zinc-600 dark:text-zinc-400 line-clamp-3">
                    <span className="font-medium text-zinc-500">{doc.source}</span>
                    <span className="ml-2">{(doc.score * 100).toFixed(0)}%</span>
                    <p className="mt-1">{doc.text}</p>
                  </div>
                ))}
              </div>
            </details>
          )}
        </div>
      )}
    </div>
  );
}
