"use client";
import { useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type SearchResult = {
  technology_id: string;
  name: string;
  item_type: string;
  summary: string | null;
  domains: string[];
  fit_score: number;
  why_relevant: string | null;
  benefits: string[];
  drawbacks: string[];
  alternatives: string[];
};

const MODES = [
  { value: "keyword", label: "技術名検索", desc: "技術名・ツール名で検索" },
  { value: "problem", label: "課題検索", desc: "解決したい課題から検索" },
  { value: "domain", label: "分野検索", desc: "特定分野の技術を探す" },
  { value: "transfer", label: "転用検索", desc: "別分野への応用候補を探す" },
];

const EXAMPLES = [
  { query: "少ない試行回数で良い候補を見つける", mode: "problem" },
  { query: "NPCの行動制御に使える技術", mode: "problem" },
  { query: "RAG evaluation", mode: "keyword" },
  { query: "game development", mode: "domain" },
  { query: "ゲーム開発の技術をAIエージェントに応用", mode: "transfer" },
];

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState("keyword");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SearchResult[] | null>(null);
  const [searchedQuery, setSearchedQuery] = useState("");

  async function handleSearch(q = query, m = mode) {
    if (!q.trim()) return;
    setLoading(true);
    setResults(null);
    setSearchedQuery(q);

    try {
      const res = await fetch(`${API}/api/search/technologies`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: q, mode: m, limit: 10 }),
      });
      const data = await res.json();
      setResults(data.results);
    } catch (err) {
      setResults([]);
    } finally {
      setLoading(false);
    }
  }

  function useExample(ex: typeof EXAMPLES[0]) {
    setQuery(ex.query);
    setMode(ex.mode);
    handleSearch(ex.query, ex.mode);
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">技術を検索</h1>

      <div className="space-y-3">
        <div className="flex gap-2 flex-wrap">
          {MODES.map((m) => (
            <button
              key={m.value}
              onClick={() => setMode(m.value)}
              className={`px-3 py-1.5 rounded text-sm transition-colors ${
                mode === m.value
                  ? "bg-blue-600 text-white"
                  : "bg-gray-800 text-gray-400 hover:text-gray-200"
              }`}
              title={m.desc}
            >
              {m.label}
            </button>
          ))}
        </div>

        <form
          onSubmit={(e) => { e.preventDefault(); handleSearch(); }}
          className="flex gap-2"
        >
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={
              mode === "problem" ? "解決したい課題を入力..." :
              mode === "domain" ? "分野名を入力（例: game development, RAG）..." :
              mode === "transfer" ? "応用したい技術領域を入力..." :
              "技術名を入力..."
            }
            className="flex-1 px-3 py-2 rounded bg-gray-800 border border-gray-700 text-gray-100 focus:outline-none focus:border-blue-500"
          />
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 rounded bg-blue-600 hover:bg-blue-500 disabled:opacity-50 font-medium transition-colors"
          >
            {loading ? "検索中..." : "検索"}
          </button>
        </form>

        <div className="flex gap-2 flex-wrap">
          <span className="text-xs text-gray-500 self-center">例:</span>
          {EXAMPLES.map((ex) => (
            <button
              key={ex.query}
              onClick={() => useExample(ex)}
              className="text-xs px-2 py-1 rounded bg-gray-800 text-gray-400 hover:text-gray-200 hover:bg-gray-700 transition-colors"
            >
              {ex.query}
            </button>
          ))}
        </div>
      </div>

      {results !== null && (
        <div className="space-y-4">
          <p className="text-sm text-gray-400">
            「{searchedQuery}」の検索結果: {results.length}件
          </p>

          {results.length === 0 ? (
            <p className="text-gray-500">結果が見つかりません。URLから技術を収集してみてください。</p>
          ) : (
            results.map((r) => (
              <a
                key={r.technology_id}
                href={`/technologies/${r.technology_id}`}
                className="block p-4 rounded-lg bg-gray-900 border border-gray-700 hover:border-blue-500 transition-colors space-y-2"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-lg">{r.name}</span>
                    <span className="text-xs text-gray-500 px-2 py-0.5 rounded bg-gray-800">{r.item_type}</span>
                  </div>
                  <span className="text-sm font-mono text-green-400">
                    {(r.fit_score * 100).toFixed(0)}%
                  </span>
                </div>

                {r.why_relevant && (
                  <p className="text-sm text-blue-300">{r.why_relevant}</p>
                )}

                {r.summary && (
                  <p className="text-sm text-gray-400">{r.summary}</p>
                )}

                {r.domains.length > 0 && (
                  <div className="flex gap-1 flex-wrap">
                    {r.domains.map((d) => (
                      <span key={d} className="text-xs px-2 py-0.5 rounded bg-gray-800 text-gray-500">{d}</span>
                    ))}
                  </div>
                )}

                {r.benefits.length > 0 && (
                  <div className="text-xs text-gray-400">
                    <span className="text-green-500">利点:</span> {r.benefits.slice(0, 2).join(" / ")}
                  </div>
                )}
                {r.drawbacks.length > 0 && (
                  <div className="text-xs text-gray-400">
                    <span className="text-red-400">注意:</span> {r.drawbacks.slice(0, 2).join(" / ")}
                  </div>
                )}
                {r.alternatives.length > 0 && (
                  <div className="text-xs text-gray-500">
                    代替: {r.alternatives.join(", ")}
                  </div>
                )}
              </a>
            ))
          )}
        </div>
      )}
    </div>
  );
}
