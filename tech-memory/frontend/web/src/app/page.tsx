"use client";

import { useRouter } from "next/navigation";
import { Brain } from "lucide-react";
import { SearchBar } from "@/components/tech/SearchBar";

export default function HomePage() {
  const router = useRouter();

  const handleSearch = (query: string, mode: string) => {
    router.push(`/search?q=${encodeURIComponent(query)}&mode=${mode}`);
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-56px)] px-6">
      <div className="w-full max-w-content">
        {/* Hero */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-6">
            <Brain className="h-12 w-12 text-primary-400" />
          </div>
          <h1 className="text-4xl font-bold text-neutral-100 mb-3 tracking-tight">
            Tech Memory
          </h1>
          <p className="text-lg text-neutral-400 max-w-xl mx-auto">
            技術・アルゴリズム・設計パターンを収集し、
            <br />
            課題や制約から最適な技術を検索・推薦します
          </p>
        </div>

        {/* Search */}
        <div className="bg-surface rounded-xl border border-neutral-700 p-6 shadow-card">
          <SearchBar onSearch={handleSearch} />
        </div>

        {/* Features */}
        <div className="grid grid-cols-3 gap-4 mt-8">
          {[
            {
              title: "課題から検索",
              desc: "技術名を知らなくても、課題や目的から関連技術を発見できます",
            },
            {
              title: "条件付きメリット",
              desc: "メリット・デメリットは「どんな条件下で」を明示して保存します",
            },
            {
              title: "分野横断",
              desc: "ゲームAI・機械学習・システム設計など分野を超えて技術を発見します",
            },
          ].map(({ title, desc }) => (
            <div key={title} className="card p-4">
              <h3 className="text-sm font-semibold text-neutral-100 mb-1">{title}</h3>
              <p className="text-xs text-neutral-500">{desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
