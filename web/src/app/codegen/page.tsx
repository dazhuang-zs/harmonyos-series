"use client";

import { useState } from "react";
import { Wand2, FileCode } from "lucide-react";
import { generateCode } from "@/lib/api";
import { CodeBlock, LoadingDots, ErrorBox } from "@/components/ui";

export default function CodegenPage() {
  const [requirement, setRequirement] = useState("");
  const [language, setLanguage] = useState("ArkTS");
  const [includeTests, setIncludeTests] = useState(false);
  const [result, setResult] = useState<{
    code: string;
    files: { filename: string; content: string }[];
    explanation: string;
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!requirement.trim() || loading) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const res = await generateCode(requirement, language, includeTests);
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "未知错误");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-1">📝 ArkTS 代码生成</h1>
      <p className="text-zinc-500 text-sm mb-6">用自然语言描述需求，自动生成可运行的 ArkTS/ArkUI 代码</p>

      <form onSubmit={handleSubmit} className="space-y-4 mb-8">
        <textarea
          value={requirement}
          onChange={(e) => setRequirement(e.target.value)}
          placeholder='例如："创建一个带搜索栏和下拉刷新的联系人列表页面"'
          rows={4}
          className="w-full px-4 py-3 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
        />
        <div className="flex items-center gap-4">
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="px-3 py-2 rounded-lg border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-sm"
          >
            <option value="ArkTS">ArkTS</option>
            <option value="ArkUI">ArkUI</option>
          </select>
          <label className="flex items-center gap-2 text-sm text-zinc-600 dark:text-zinc-400">
            <input
              type="checkbox"
              checked={includeTests}
              onChange={(e) => setIncludeTests(e.target.checked)}
              className="rounded"
            />
            生成单元测试
          </label>
          <button
            type="submit"
            disabled={loading || !requirement.trim()}
            className="ml-auto px-5 py-2 bg-blue-600 text-white text-sm font-medium rounded-xl disabled:opacity-40 hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <Wand2 size={16} />
            生成代码
          </button>
        </div>
      </form>

      {loading && (
        <div className="flex items-center gap-3 text-zinc-500">
          <div className="w-5 h-5 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center text-xs">🦋</div>
          <span>正在生成代码…</span>
          <LoadingDots />
        </div>
      )}

      {error && <ErrorBox message={error} />}

      {result && (
        <div className="space-y-4">
          <div className="flex items-center gap-2 text-sm text-zinc-500">
            <FileCode size={16} />
            <span>{result.explanation}</span>
          </div>
          {result.files?.map((file, i) => (
            <details key={i} open={i === 0}>
              <summary className="text-sm font-medium cursor-pointer text-zinc-700 dark:text-zinc-300 py-2">
                📄 {file.filename}
              </summary>
              <CodeBlock code={file.content} language="typescript" />
            </details>
          ))}
        </div>
      )}
    </div>
  );
}
