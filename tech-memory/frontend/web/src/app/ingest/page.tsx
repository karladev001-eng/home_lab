"use client";

import { useState } from "react";
import { Link2, FileText, MessageSquare, CheckCircle, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { api } from "@/lib/api-client";

type TabType = "url" | "search" | "memo";

const TABS: { id: TabType; label: string; icon: typeof Link2 }[] = [
  { id: "url", label: "URLから収集", icon: Link2 },
  { id: "search", label: "検索収集", icon: FileText },
  { id: "memo", label: "メモ入力", icon: MessageSquare },
];

const COLLECTION_MODES = [
  { value: "light", label: "Light — タイトル・概要のみ" },
  { value: "standard", label: "Standard — 主要情報を抽出（推奨）" },
  { value: "deep", label: "Deep — 詳細分析（時間がかかります）" },
] as const;

interface IngestResult {
  success: boolean;
  summary?: string;
  detected?: string[];
  created?: number;
  updated?: number;
  error?: string;
}

export default function IngestPage() {
  const [activeTab, setActiveTab] = useState<TabType>("url");

  // URL form
  const [url, setUrl] = useState("");
  const [mode, setMode] = useState<"light" | "standard" | "deep">("standard");
  const [tags, setTags] = useState("");

  // Search form
  const [searchQuery, setSearchQuery] = useState("");

  // Memo form
  const [memo, setMemo] = useState("");

  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<IngestResult | null>(null);

  const handleUrlSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;
    setIsLoading(true);
    setResult(null);
    try {
      const tagList = tags.split(",").map((t) => t.trim()).filter(Boolean);
      const res = await api.ingest.url({ url, collection_mode: mode, tags: tagList });
      if (res.success && res.data) {
        setResult({
          success: true,
          summary: res.data.summary,
          detected: res.data.detected_technologies,
          created: res.data.created_items.length,
          updated: res.data.updated_items.length,
        });
      }
    } catch (err) {
      setResult({ success: false, error: err instanceof Error ? err.message : "収集に失敗しました" });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setIsLoading(true);
    setResult(null);
    try {
      const res = await api.ingest.search({ query: searchQuery, sources: ["web", "github"] });
      if (res.success && res.data) {
        setResult({
          success: true,
          summary: `${res.data.collected_count}件のソースを収集`,
          created: res.data.created_items.length,
          updated: res.data.updated_items.length,
        });
      }
    } catch (err) {
      setResult({ success: false, error: err instanceof Error ? err.message : "収集に失敗しました" });
    } finally {
      setIsLoading(false);
    }
  };

  const handleMemoSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!memo.trim()) return;
    setIsLoading(true);
    setResult(null);
    try {
      const tagList = tags.split(",").map((t) => t.trim()).filter(Boolean);
      const res = await api.ingest.memo({ memo, tags: tagList });
      if (res.success && res.data) {
        setResult({
          success: true,
          summary: res.data.summary,
          detected: res.data.detected_technologies,
          created: res.data.created_items.length,
          updated: res.data.updated_items.length,
        });
      }
    } catch (err) {
      setResult({ success: false, error: err instanceof Error ? err.message : "収集に失敗しました" });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-content mx-auto px-6 py-8">
      <h1 className="text-2xl font-bold text-neutral-100 mb-6">技術情報の収集</h1>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 border-b border-neutral-800 pb-0">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => { setActiveTab(id); setResult(null); }}
            className={cn(
              "flex items-center gap-1.5 px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors",
              activeTab === id
                ? "border-primary-500 text-primary-400"
                : "border-transparent text-neutral-500 hover:text-neutral-100",
            )}
          >
            <Icon className="h-4 w-4" />
            {label}
          </button>
        ))}
      </div>

      {/* Result */}
      {result && (
        <div className={cn(
          "card p-4 mb-6 flex items-start gap-3",
          result.success ? "border-semantic-success/30 bg-green-900/10" : "border-semantic-error/30 bg-red-900/10",
        )}>
          {result.success ? (
            <CheckCircle className="h-4 w-4 text-semantic-success shrink-0 mt-0.5" />
          ) : (
            <XCircle className="h-4 w-4 text-semantic-error shrink-0 mt-0.5" />
          )}
          <div className="text-sm">
            {result.success ? (
              <>
                <p className="text-neutral-100 font-medium">{result.summary}</p>
                {result.detected && result.detected.length > 0 && (
                  <p className="text-neutral-400 mt-1">
                    検出技術: {result.detected.join(", ")}
                  </p>
                )}
                <p className="text-neutral-500 mt-1">
                  新規: {result.created}件 / 更新: {result.updated}件
                </p>
              </>
            ) : (
              <p className="text-semantic-error">{result.error}</p>
            )}
          </div>
        </div>
      )}

      {/* URL Form */}
      {activeTab === "url" && (
        <form onSubmit={handleUrlSubmit} className="card p-6 flex flex-col gap-4">
          <div>
            <label className="block text-sm font-medium text-neutral-300 mb-1.5">
              URL <span className="text-semantic-error">*</span>
            </label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://arxiv.org/abs/... または https://github.com/..."
              className="input-base"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-neutral-300 mb-1.5">
              収集モード
            </label>
            <div className="flex flex-col gap-2">
              {COLLECTION_MODES.map(({ value, label }) => (
                <label key={value} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="mode"
                    value={value}
                    checked={mode === value}
                    onChange={() => setMode(value)}
                    className="accent-primary-500"
                  />
                  <span className="text-sm text-neutral-300">{label}</span>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-neutral-300 mb-1.5">
              タグ <span className="text-neutral-500 text-xs">(カンマ区切り、最大20個)</span>
            </label>
            <input
              type="text"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              placeholder="RAG, NLP, Retrieval"
              className="input-base"
            />
          </div>

          <button type="submit" className="btn-primary self-start" disabled={isLoading}>
            {isLoading ? (
              <span className="flex items-center gap-2"><LoadingSpinner size="sm" />収集中...</span>
            ) : "収集を開始"}
          </button>
        </form>
      )}

      {/* Search Form */}
      {activeTab === "search" && (
        <form onSubmit={handleSearchSubmit} className="card p-6 flex flex-col gap-4">
          <div>
            <label className="block text-sm font-medium text-neutral-300 mb-1.5">
              検索キーワード <span className="text-semantic-error">*</span>
            </label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="behavior tree NPC AI"
              className="input-base"
              required
            />
          </div>
          <p className="text-xs text-neutral-500">
            GitHub・arXivをキーワード検索し、上位結果から技術情報を収集します
          </p>
          <button type="submit" className="btn-primary self-start" disabled={isLoading}>
            {isLoading ? (
              <span className="flex items-center gap-2"><LoadingSpinner size="sm" />収集中...</span>
            ) : "検索して収集"}
          </button>
        </form>
      )}

      {/* Memo Form */}
      {activeTab === "memo" && (
        <form onSubmit={handleMemoSubmit} className="card p-6 flex flex-col gap-4">
          <div>
            <label className="block text-sm font-medium text-neutral-300 mb-1.5">
              メモ <span className="text-semantic-error">*</span>
            </label>
            <textarea
              value={memo}
              onChange={(e) => setMemo(e.target.value)}
              placeholder="Behavior TreeはゲームのNPC制御に使われる木構造の意思決定手法です..."
              className="input-base h-40 resize-y"
              required
              minLength={10}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-300 mb-1.5">
              タグ <span className="text-neutral-500 text-xs">(カンマ区切り)</span>
            </label>
            <input
              type="text"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              placeholder="game AI, decision making"
              className="input-base"
            />
          </div>
          <button type="submit" className="btn-primary self-start" disabled={isLoading}>
            {isLoading ? (
              <span className="flex items-center gap-2"><LoadingSpinner size="sm" />処理中...</span>
            ) : "技術カードを生成"}
          </button>
        </form>
      )}
    </div>
  );
}
