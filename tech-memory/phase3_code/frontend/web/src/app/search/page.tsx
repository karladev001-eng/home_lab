"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { SearchBar } from "@/components/tech/SearchBar";
import { TechCard } from "@/components/tech/TechCard";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { Badge } from "@/components/ui/Badge";
import { api, type TechnologySearchResult } from "@/lib/api-client";

export default function SearchPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const query = searchParams.get("q") || "";
  const mode = searchParams.get("mode") || "keyword";

  const [results, setResults] = useState<TechnologySearchResult[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!query) return;
    doSearch(query, mode);
  }, [query, mode]);

  const doSearch = async (q: string, m: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.search.technologies({ query: q, mode: m as "keyword", limit: 20 });
      if (res.success && res.data) {
        setResults(res.data.results);
        setTotal(res.data.total);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "検索に失敗しました");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = (newQuery: string, newMode: string) => {
    router.push(`/search?q=${encodeURIComponent(newQuery)}&mode=${newMode}`);
  };

  return (
    <div className="max-w-[1200px] mx-auto px-6 py-8">
      {/* Search bar */}
      <div className="mb-6">
        <SearchBar
          onSearch={handleSearch}
          defaultQuery={query}
          defaultMode={mode}
          isLoading={isLoading}
        />
      </div>

      {/* Results header */}
      {!isLoading && query && (
        <div className="flex items-center gap-3 mb-4 text-sm text-neutral-400">
          <span>
            <span className="text-neutral-100 font-medium">"{query}"</span> の検索結果
          </span>
          <Badge variant="muted">{total}件</Badge>
        </div>
      )}

      {/* Loading */}
      {isLoading && (
        <div className="flex items-center justify-center py-16 gap-3 text-neutral-400">
          <LoadingSpinner />
          <span className="text-sm">検索中...</span>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="card p-4 border-semantic-error/30 bg-red-900/10">
          <p className="text-sm text-semantic-error">{error}</p>
        </div>
      )}

      {/* Empty state */}
      {!isLoading && !error && query && results.length === 0 && (
        <div className="text-center py-16 text-neutral-500">
          <p className="text-base">"{query}" に一致する技術が見つかりませんでした</p>
          <p className="text-sm mt-2">キーワードを変えるか、URLから技術を収集してみてください</p>
        </div>
      )}

      {/* Results */}
      {!isLoading && results.length > 0 && (
        <div className="flex flex-col gap-3">
          {results.map((tech) => (
            <TechCard key={tech.technology_id} tech={tech} />
          ))}
        </div>
      )}
    </div>
  );
}
