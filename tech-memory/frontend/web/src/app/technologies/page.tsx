"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, type TechnologyListItem } from "@/lib/api-client";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { Badge } from "@/components/ui/Badge";
import { ITEM_TYPE_LABELS, ITEM_TYPE_COLORS, MATURITY_LABELS, cn } from "@/lib/utils";

export default function TechnologiesPage() {
  const [items, setItems] = useState<TechnologyListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.technologies
      .list({ limit: 50 })
      .then((res) => {
        if (res.success && res.data) {
          setItems(res.data.items);
          setTotal(res.data.total);
        }
      })
      .catch((err) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div className="max-w-content mx-auto px-6 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-neutral-100">技術一覧</h1>
        <Badge variant="muted">{total}件</Badge>
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-16 gap-3 text-neutral-400">
          <LoadingSpinner />
          <span className="text-sm">読み込み中...</span>
        </div>
      )}

      {error && (
        <div className="card p-4 border-semantic-error/30 bg-red-900/10">
          <p className="text-sm text-semantic-error">{error}</p>
        </div>
      )}

      {!isLoading && items.length === 0 && !error && (
        <div className="text-center py-16 text-neutral-500">
          <p>まだ技術が登録されていません</p>
          <Link href="/ingest" className="text-primary-400 underline text-sm mt-2 inline-block">
            URLから技術を収集する
          </Link>
        </div>
      )}

      <div className="flex flex-col gap-2">
        {items.map((item) => (
          <Link
            key={item.id}
            href={`/technologies/${item.id}`}
            className="card p-4 hover:border-neutral-600 transition-colors flex items-center gap-4"
          >
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className={cn("text-xs font-mono font-medium", ITEM_TYPE_COLORS[item.item_type] || "text-neutral-400")}>
                  {ITEM_TYPE_LABELS[item.item_type] || item.item_type}
                </span>
                {item.maturity_level && (
                  <Badge variant="muted" className="text-[10px]">
                    {MATURITY_LABELS[item.maturity_level] || item.maturity_level}
                  </Badge>
                )}
              </div>
              <h3 className="text-sm font-medium text-neutral-100 truncate">{item.name}</h3>
              {item.summary && (
                <p className="text-xs text-neutral-500 mt-0.5 truncate">{item.summary}</p>
              )}
            </div>
            <div className="flex flex-wrap gap-1 shrink-0 max-w-[200px]">
              {item.domains.slice(0, 2).map((d) => (
                <Badge key={d} variant="muted" className="text-[10px]">{d}</Badge>
              ))}
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
