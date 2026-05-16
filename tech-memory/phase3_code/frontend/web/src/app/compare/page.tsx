"use client";

import { useState } from "react";
import { Plus, X, BarChart2 } from "lucide-react";
import { api, type CompareResponseData } from "@/lib/api-client";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { cn } from "@/lib/utils";

export default function ComparePage() {
  const [techNames, setTechNames] = useState<string[]>(["", ""]);
  const [result, setResult] = useState<CompareResponseData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const names = techNames.filter(Boolean);
    if (names.length < 2) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.compare({ technologies: names });
      if (res.success && res.data) {
        setResult(res.data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "比較に失敗しました");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-content mx-auto px-6 py-8">
      <h1 className="text-2xl font-bold text-neutral-100 mb-6">技術比較</h1>

      <form onSubmit={handleSubmit} className="card p-6 mb-6">
        <div className="flex flex-col gap-3 mb-4">
          {techNames.map((name, i) => (
            <div key={i} className="flex gap-2">
              <input
                type="text"
                value={name}
                onChange={(e) => {
                  const updated = [...techNames];
                  updated[i] = e.target.value;
                  setTechNames(updated);
                }}
                placeholder={`技術名 ${i + 1}`}
                className="input-base flex-1"
              />
              {techNames.length > 2 && (
                <button
                  type="button"
                  onClick={() => setTechNames(techNames.filter((_, j) => j !== i))}
                  className="p-2 text-neutral-500 hover:text-neutral-100 transition-colors"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>
          ))}
        </div>

        <div className="flex gap-3">
          {techNames.length < 6 && (
            <button
              type="button"
              onClick={() => setTechNames([...techNames, ""])}
              className="btn-secondary gap-1.5"
            >
              <Plus className="h-4 w-4" />
              追加
            </button>
          )}
          <button
            type="submit"
            className="btn-primary gap-1.5"
            disabled={isLoading || techNames.filter(Boolean).length < 2}
          >
            {isLoading ? (
              <><LoadingSpinner size="sm" />比較中...</>
            ) : (
              <><BarChart2 className="h-4 w-4" />比較する</>
            )}
          </button>
        </div>
      </form>

      {error && (
        <div className="card p-4 border-semantic-error/30 bg-red-900/10 mb-4">
          <p className="text-sm text-semantic-error">{error}</p>
        </div>
      )}

      {result && (
        <div className="flex flex-col gap-4">
          {/* Comparison Table */}
          <div className="card overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-neutral-700">
                  <th className="text-left p-4 text-neutral-400 font-medium">技術</th>
                  {result.criteria.map((c) => (
                    <th key={c} className="text-center p-4 text-neutral-400 font-medium text-xs">
                      {c}
                    </th>
                  ))}
                  <th className="text-left p-4 text-neutral-400 font-medium">サマリー</th>
                </tr>
              </thead>
              <tbody>
                {result.comparison_table.map((row, i) => (
                  <tr key={i} className="border-b border-neutral-800 last:border-0">
                    <td className="p-4 font-medium text-neutral-100">{row.name}</td>
                    {result.criteria.map((c) => {
                      const score = row.scores[c] ?? 0;
                      return (
                        <td key={c} className="p-4 text-center">
                          <div className="flex flex-col items-center gap-1">
                            <span className={cn(
                              "font-mono text-xs font-semibold",
                              score >= 0.8 ? "text-semantic-success" :
                              score >= 0.6 ? "text-semantic-warning" :
                              "text-neutral-500",
                            )}>
                              {Math.round(score * 100)}
                            </span>
                            <div className="w-12 h-1.5 bg-neutral-700 rounded-full overflow-hidden">
                              <div
                                className={cn(
                                  "h-full rounded-full",
                                  score >= 0.8 ? "bg-semantic-success" :
                                  score >= 0.6 ? "bg-semantic-warning" :
                                  "bg-neutral-600",
                                )}
                                style={{ width: `${score * 100}%` }}
                              />
                            </div>
                          </div>
                        </td>
                      );
                    })}
                    <td className="p-4 text-xs text-neutral-400 max-w-xs">{row.summary}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Recommendation */}
          {result.recommendation && (
            <div className="card p-5 border-primary-700/30 bg-primary-900/10">
              <h3 className="text-xs font-semibold text-primary-400 uppercase tracking-wider mb-2">
                推薦
              </h3>
              <p className="text-sm text-neutral-200">{result.recommendation}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
