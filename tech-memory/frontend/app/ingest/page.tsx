"use client";
import { useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type IngestResult = {
  source_id: string;
  source_title: string;
  detected_technologies: string[];
  created_items: { id: string; name: string; item_type: string; summary: string }[];
  updated_items: { id: string; name: string; item_type: string; summary: string }[];
  message: string;
};

export default function IngestPage() {
  const [url, setUrl] = useState("");
  const [mode, setMode] = useState<"light" | "standard" | "deep">("standard");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<IngestResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch(`${API}/api/ingest/url`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, collection_mode: mode }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail ?? "Unknown error");
      }

      setResult(await res.json());
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <h1 className="text-2xl font-bold">技術情報を収集</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm text-gray-400 mb-1">URL</label>
          <input
            type="url"
            required
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://arxiv.org/abs/... or https://github.com/..."
            className="w-full px-3 py-2 rounded bg-gray-800 border border-gray-700 text-gray-100 focus:outline-none focus:border-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm text-gray-400 mb-1">収集深度</label>
          <select
            value={mode}
            onChange={(e) => setMode(e.target.value as "light" | "standard" | "deep")}
            className="px-3 py-2 rounded bg-gray-800 border border-gray-700 text-gray-100 focus:outline-none focus:border-blue-500"
          >
            <option value="light">light — 高速・最小限</option>
            <option value="standard">standard — 標準</option>
            <option value="deep">deep — 詳細分析</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 rounded bg-blue-600 hover:bg-blue-500 disabled:opacity-50 font-medium transition-colors"
        >
          {loading ? "収集中..." : "収集する"}
        </button>
      </form>

      {error && (
        <div className="p-4 rounded bg-red-900/40 border border-red-700 text-red-300 text-sm">
          {error}
        </div>
      )}

      {result && (
        <div className="space-y-4">
          <div className="p-4 rounded bg-gray-900 border border-gray-700">
            <p className="text-sm text-gray-400 mb-1">ソース</p>
            <p className="font-medium">{result.source_title}</p>
            <p className="text-sm text-green-400 mt-1">{result.message}</p>
          </div>

          {result.detected_technologies.length > 0 && (
            <div>
              <p className="text-sm text-gray-400 mb-2">検出された技術</p>
              <div className="flex flex-wrap gap-2">
                {result.detected_technologies.map((t) => (
                  <span key={t} className="px-2 py-1 rounded bg-gray-800 text-sm border border-gray-700">{t}</span>
                ))}
              </div>
            </div>
          )}

          {result.created_items.length > 0 && (
            <div>
              <p className="text-sm text-gray-400 mb-2">新規登録 ({result.created_items.length}件)</p>
              <div className="space-y-2">
                {result.created_items.map((item) => (
                  <a
                    key={item.id}
                    href={`/technologies/${item.id}`}
                    className="block p-3 rounded bg-gray-900 border border-gray-700 hover:border-blue-500 transition-colors"
                  >
                    <span className="font-medium">{item.name}</span>
                    <span className="ml-2 text-xs text-gray-500">{item.item_type}</span>
                    {item.summary && <p className="text-sm text-gray-400 mt-1">{item.summary}</p>}
                  </a>
                ))}
              </div>
            </div>
          )}

          {result.updated_items.length > 0 && (
            <div>
              <p className="text-sm text-gray-400 mb-2">更新 ({result.updated_items.length}件)</p>
              <div className="space-y-2">
                {result.updated_items.map((item) => (
                  <a
                    key={item.id}
                    href={`/technologies/${item.id}`}
                    className="block p-3 rounded bg-gray-900 border border-gray-700 hover:border-green-500 transition-colors"
                  >
                    <span className="font-medium">{item.name}</span>
                    <span className="ml-2 text-xs text-gray-500">{item.item_type}</span>
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
