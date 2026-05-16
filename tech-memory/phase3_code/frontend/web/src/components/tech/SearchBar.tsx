"use client";

import { useState, type FormEvent } from "react";
import { Search } from "lucide-react";
import { cn } from "@/lib/utils";

interface SearchBarProps {
  onSearch: (query: string, mode: string) => void;
  defaultQuery?: string;
  defaultMode?: string;
  isLoading?: boolean;
  className?: string;
}

const SEARCH_MODES = [
  { value: "keyword", label: "キーワード" },
  { value: "problem_search", label: "課題から探す" },
  { value: "domain", label: "ドメイン" },
  { value: "condition", label: "条件から探す" },
] as const;

const EXAMPLE_QUERIES = [
  "少ない試行回数で良い候補を見つけたい",
  "NPCの行動制御に使える技術",
  "RAGの精度改善手法",
  "大量イベントのリアルタイム処理",
];

export function SearchBar({
  onSearch,
  defaultQuery = "",
  defaultMode = "keyword",
  isLoading = false,
  className,
}: SearchBarProps) {
  const [query, setQuery] = useState(defaultQuery);
  const [mode, setMode] = useState(defaultMode);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    onSearch(query.trim(), mode);
  };

  return (
    <div className={cn("w-full", className)}>
      <form onSubmit={handleSubmit}>
        {/* Search mode tabs */}
        <div className="flex gap-1 mb-3">
          {SEARCH_MODES.map(({ value, label }) => (
            <button
              key={value}
              type="button"
              onClick={() => setMode(value)}
              className={cn(
                "px-3 py-1 rounded text-xs font-medium transition-colors",
                mode === value
                  ? "bg-primary-600 text-white"
                  : "bg-neutral-800 text-neutral-400 hover:text-neutral-100 border border-neutral-700",
              )}
            >
              {label}
            </button>
          ))}
        </div>

        {/* Search input */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-neutral-500 pointer-events-none" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={
              mode === "problem_search"
                ? "解決したい課題を自然言語で入力..."
                : mode === "domain"
                  ? "ドメイン名を入力（例: AI, game development）"
                  : "技術名・キーワードを入力..."
            }
            className="input-base pl-10 pr-24 py-3 text-base"
            disabled={isLoading}
          />
          <button
            type="submit"
            className="absolute right-2 top-1/2 -translate-y-1/2 btn-primary py-1.5 px-4 text-xs"
            disabled={isLoading || !query.trim()}
          >
            {isLoading ? "検索中..." : "検索"}
          </button>
        </div>
      </form>

      {/* Example queries */}
      {!defaultQuery && (
        <div className="flex flex-wrap gap-2 mt-3">
          {EXAMPLE_QUERIES.map((q) => (
            <button
              key={q}
              type="button"
              onClick={() => {
                setQuery(q);
                setMode("problem_search");
              }}
              className="text-xs text-neutral-500 hover:text-primary-400 transition-colors underline underline-offset-2"
            >
              {q}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
