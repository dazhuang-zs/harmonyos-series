"use client";

import { useState } from "react";
import { Send, Tags } from "lucide-react";
import { publishArticle } from "@/lib/api";
import { LoadingDots, ErrorBox } from "@/components/ui";

export default function PublishPage() {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [tagsInput, setTagsInput] = useState("");
  const [result, setResult] = useState<{ article_id: string; url: string; status: string } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !content.trim() || loading) return;

    const tags = tagsInput.split(",").map((t) => t.trim()).filter(Boolean);
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const res = await publishArticle(title, content, tags);
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "未知错误");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-1">📄 CSDN 文章发布</h1>
      <p className="text-zinc-500 text-sm mb-6">将技术文章自动发布到 CSDN 草稿箱</p>

      <form onSubmit={handleSubmit} className="space-y-4 mb-8">
        <div>
          <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">
            文章标题
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="输入文章标题…"
            className="w-full px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">
            文章内容 <span className="text-zinc-400 font-normal">（Markdown 格式）</span>
          </label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="输入 Markdown 格式的文章内容…"
            rows={12}
            className="w-full px-4 py-3 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">
            <Tags size={14} className="inline mr-1" />
            标签（逗号分隔）
          </label>
          <input
            type="text"
            value={tagsInput}
            onChange={(e) => setTagsInput(e.target.value)}
            placeholder="鸿蒙, HarmonyOS, ArkTS"
            className="w-full px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <button
          type="submit"
          disabled={loading || !title.trim() || !content.trim()}
          className="px-5 py-2 bg-green-600 text-white text-sm font-medium rounded-xl disabled:opacity-40 hover:bg-green-700 transition-colors flex items-center gap-2"
        >
          <Send size={16} />
          保存到 CSDN 草稿箱
        </button>
      </form>

      {loading && (
        <div className="flex items-center gap-3 text-zinc-500">
          <span>正在发布到 CSDN…</span>
          <LoadingDots />
        </div>
      )}

      {error && <ErrorBox message={error} />}

      {result && (
        <div className="p-6 rounded-xl border border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-950">
          <h3 className="flex items-center gap-2 font-semibold text-green-800 dark:text-green-200 mb-3">
            ✅ 发布成功
          </h3>
          <dl className="space-y-2 text-sm">
            <div className="flex gap-3">
              <dt className="text-green-600 dark:text-green-400 w-20">状态</dt>
              <dd className="text-green-700 dark:text-green-300 capitalize">{result.status}</dd>
            </div>
            {result.article_id && (
              <div className="flex gap-3">
                <dt className="text-green-600 dark:text-green-400 w-20">文章 ID</dt>
                <dd className="text-green-700 dark:text-green-300 font-mono">{result.article_id}</dd>
              </div>
            )}
            {result.url && (
              <div className="flex gap-3">
                <dt className="text-green-600 dark:text-green-400 w-20">链接</dt>
                <dd>
                  <a
                    href={result.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 dark:text-blue-400 hover:underline"
                  >
                    {result.url}
                  </a>
                </dd>
              </div>
            )}
          </dl>
        </div>
      )}
    </div>
  );
}
