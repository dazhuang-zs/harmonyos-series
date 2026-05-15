"use client";

import { useState } from "react";
import { ArrowLeftRight } from "lucide-react";
import { migrateCode } from "@/lib/api";
import { CodeBlock, LoadingDots, ErrorBox } from "@/components/ui";

export default function MigratePage() {
  const [androidCode, setAndroidCode] = useState("");
  const [sourceLanguage, setSourceLanguage] = useState("Kotlin");
  const [result, setResult] = useState<{
    migrated_code: string;
    migration_notes: string[];
    before_after: { before: string; after: string };
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!androidCode.trim() || loading) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const res = await migrateCode(androidCode, sourceLanguage);
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "未知错误");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-1">🔄 代码迁移</h1>
      <p className="text-zinc-500 text-sm mb-6">粘贴 Android Java/Kotlin 代码，自动转换为等价的 ArkTS 实现</p>

      <form onSubmit={handleSubmit} className="space-y-4 mb-8">
        <div className="flex items-center gap-3 mb-2">
          <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">源语言：</span>
          <select
            value={sourceLanguage}
            onChange={(e) => setSourceLanguage(e.target.value)}
            className="px-3 py-1.5 rounded-lg border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-sm"
          >
            <option value="Kotlin">Kotlin</option>
            <option value="Java">Java</option>
          </select>
        </div>
        <textarea
          value={androidCode}
          onChange={(e) => setAndroidCode(e.target.value)}
          placeholder={`粘贴 ${sourceLanguage} 代码，例如一个 Activity 或 Retrofit 请求…`}
          rows={10}
          className="w-full px-4 py-3 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
        />
        <button
          type="submit"
          disabled={loading || !androidCode.trim()}
          className="px-5 py-2 bg-purple-600 text-white text-sm font-medium rounded-xl disabled:opacity-40 hover:bg-purple-700 transition-colors flex items-center gap-2"
        >
          <ArrowLeftRight size={16} />
          开始迁移
        </button>
      </form>

      {loading && (
        <div className="flex items-center gap-3 text-zinc-500">
          <span>正在转换代码…</span>
          <LoadingDots />
        </div>
      )}

      {error && <ErrorBox message={error} />}

      {result && (
        <div className="space-y-6">
          {/* 迁移结果 */}
          <div>
            <h3 className="text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
              ⬇️ ArkTS 转换结果
            </h3>
            <CodeBlock code={result.migrated_code} language="typescript" />
          </div>

          {/* 迁移注释 */}
          {result.migration_notes.length > 0 && (
            <details className="p-4 rounded-xl border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-950" open>
              <summary className="text-sm font-medium text-amber-800 dark:text-amber-200 cursor-pointer">
                ⚠️ 迁移注意事项 ({result.migration_notes.length})
              </summary>
              <ul className="mt-3 space-y-1.5">
                {result.migration_notes.map((note, i) => (
                  <li key={i} className="text-xs text-amber-700 dark:text-amber-300 font-mono">
                    {note}
                  </li>
                ))}
              </ul>
            </details>
          )}

          {/* Before/After 对比 */}
          {result.before_after?.before && (
            <details className="p-4 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-900">
              <summary className="text-sm font-medium text-zinc-600 dark:text-zinc-400 cursor-pointer">
                对比视图（原始 vs 迁移后）
              </summary>
              <div className="mt-3 grid grid-cols-1 lg:grid-cols-2 gap-4">
                <div>
                  <div className="text-xs font-medium text-zinc-500 mb-1">Before ({sourceLanguage})</div>
                  <CodeBlock code={result.before_after.before} language={sourceLanguage.toLowerCase()} />
                </div>
                <div>
                  <div className="text-xs font-medium text-green-600 mb-1">After (ArkTS)</div>
                  <CodeBlock code={result.before_after.after} language="typescript" />
                </div>
              </div>
            </details>
          )}
        </div>
      )}
    </div>
  );
}
