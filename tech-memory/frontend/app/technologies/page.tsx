const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type TechItem = {
  id: string;
  name: string;
  item_type: string;
  summary: string | null;
  domains: string[];
  maturity_level: string | null;
  created_at: string;
};

async function fetchTechnologies(): Promise<TechItem[]> {
  try {
    const res = await fetch(`${API}/api/technologies?limit=100`, { cache: "no-store" });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export default async function TechnologiesPage() {
  const techs = await fetchTechnologies();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">登録済み技術一覧</h1>
        <span className="text-sm text-gray-400">{techs.length}件</span>
      </div>

      {techs.length === 0 ? (
        <div className="p-8 text-center text-gray-500">
          <p>まだ技術が登録されていません。</p>
          <a href="/ingest" className="text-blue-400 hover:underline mt-2 inline-block">
            URLから収集する →
          </a>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {techs.map((t) => (
            <a
              key={t.id}
              href={`/technologies/${t.id}`}
              className="block p-4 rounded-lg bg-gray-900 border border-gray-700 hover:border-blue-500 transition-colors"
            >
              <div className="flex items-start justify-between gap-2">
                <span className="font-semibold">{t.name}</span>
                <span className="text-xs text-gray-500 px-2 py-0.5 rounded bg-gray-800 shrink-0">{t.item_type}</span>
              </div>
              {t.summary && <p className="text-sm text-gray-400 mt-1 line-clamp-2">{t.summary}</p>}
              {t.domains.length > 0 && (
                <div className="flex gap-1 flex-wrap mt-2">
                  {t.domains.slice(0, 4).map((d) => (
                    <span key={d} className="text-xs px-1.5 py-0.5 rounded bg-gray-800 text-gray-500">{d}</span>
                  ))}
                </div>
              )}
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
