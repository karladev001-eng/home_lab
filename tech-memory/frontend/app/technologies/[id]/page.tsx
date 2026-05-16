import { notFound } from "next/navigation";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type TechDetail = {
  id: string;
  name: string;
  item_type: string;
  aliases: string[];
  summary: string | null;
  core_mechanism: string | null;
  abstract_principle: string | null;
  domains: string[];
  problem_structures: string[];
  maturity_level: string | null;
  difficulty_level: string | null;
  cost_level: string | null;
  purposes: { purpose: string; condition?: string }[];
  benefits: { benefit: string; condition?: string; confidence?: number }[];
  drawbacks: { drawback: string; condition?: string; severity?: string }[];
  tradeoffs: { gain: string; cost: string; condition?: string }[];
  conditions: { type: string; description: string }[];
  relations: { relation_type: string; name: string; reason?: string }[];
  sources: { title: string; url?: string; source_type: string }[];
};

async function fetchTech(id: string): Promise<TechDetail | null> {
  try {
    const res = await fetch(`${API}/api/technologies/${id}`, { cache: "no-store" });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="space-y-2">
      <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">{title}</h2>
      {children}
    </div>
  );
}

function Badge({ text, color = "gray" }: { text: string; color?: string }) {
  const colors: Record<string, string> = {
    gray: "bg-gray-800 text-gray-400",
    green: "bg-green-900/40 text-green-300",
    red: "bg-red-900/40 text-red-300",
    blue: "bg-blue-900/40 text-blue-300",
    yellow: "bg-yellow-900/40 text-yellow-300",
  };
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs ${colors[color] ?? colors.gray}`}>
      {text}
    </span>
  );
}

export default async function TechDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const tech = await fetchTech(id);

  if (!tech) notFound();

  const worksConds = tech.conditions.filter((c) => c.type === "works_when");
  const failsConds = tech.conditions.filter((c) => c.type === "fails_when");
  const avoidConds = tech.conditions.filter((c) => c.type === "avoid_when");

  return (
    <div className="space-y-8 max-w-3xl">
      <div>
        <div className="flex items-center gap-3 mb-1">
          <h1 className="text-3xl font-bold">{tech.name}</h1>
          <Badge text={tech.item_type} color="blue" />
        </div>
        {tech.aliases.length > 0 && (
          <p className="text-sm text-gray-500">別名: {tech.aliases.join(", ")}</p>
        )}
      </div>

      {(tech.maturity_level || tech.difficulty_level || tech.cost_level) && (
        <div className="flex gap-2 flex-wrap">
          {tech.maturity_level && <Badge text={`成熟度: ${tech.maturity_level}`} />}
          {tech.difficulty_level && <Badge text={`難易度: ${tech.difficulty_level}`} />}
          {tech.cost_level && <Badge text={`コスト: ${tech.cost_level}`} />}
        </div>
      )}

      {tech.domains.length > 0 && (
        <div className="flex gap-1 flex-wrap">
          {tech.domains.map((d) => <Badge key={d} text={d} />)}
        </div>
      )}

      {tech.summary && (
        <Section title="概要">
          <p className="text-gray-300">{tech.summary}</p>
        </Section>
      )}

      {tech.core_mechanism && (
        <Section title="中核メカニズム">
          <p className="text-gray-300">{tech.core_mechanism}</p>
        </Section>
      )}

      {tech.abstract_principle && (
        <Section title="抽象原理">
          <p className="text-blue-300 italic">{tech.abstract_principle}</p>
        </Section>
      )}

      {tech.purposes.length > 0 && (
        <Section title="目的">
          <ul className="space-y-1">
            {tech.purposes.map((p, i) => (
              <li key={i} className="text-gray-300 text-sm">
                • {p.purpose}
                {p.condition && <span className="text-gray-500"> （{p.condition}）</span>}
              </li>
            ))}
          </ul>
        </Section>
      )}

      {tech.benefits.length > 0 && (
        <Section title="メリット">
          <ul className="space-y-2">
            {tech.benefits.map((b, i) => (
              <li key={i} className="p-3 rounded bg-green-900/20 border border-green-900/40">
                <p className="text-green-300 text-sm">{b.benefit}</p>
                {b.condition && <p className="text-xs text-gray-500 mt-1">条件: {b.condition}</p>}
              </li>
            ))}
          </ul>
        </Section>
      )}

      {tech.drawbacks.length > 0 && (
        <Section title="デメリット">
          <ul className="space-y-2">
            {tech.drawbacks.map((d, i) => (
              <li key={i} className="p-3 rounded bg-red-900/20 border border-red-900/40">
                <div className="flex items-start justify-between gap-2">
                  <p className="text-red-300 text-sm">{d.drawback}</p>
                  {d.severity && <Badge text={d.severity} color={d.severity === "high" ? "red" : "yellow"} />}
                </div>
                {d.condition && <p className="text-xs text-gray-500 mt-1">条件: {d.condition}</p>}
              </li>
            ))}
          </ul>
        </Section>
      )}

      {tech.tradeoffs.length > 0 && (
        <Section title="トレードオフ">
          <ul className="space-y-2">
            {tech.tradeoffs.map((t, i) => (
              <li key={i} className="p-3 rounded bg-gray-900 border border-gray-700 text-sm">
                <span className="text-green-400">得: {t.gain}</span>
                <span className="text-gray-500 mx-2">/</span>
                <span className="text-red-400">失: {t.cost}</span>
                {t.condition && <p className="text-xs text-gray-500 mt-1">条件: {t.condition}</p>}
              </li>
            ))}
          </ul>
        </Section>
      )}

      {(worksConds.length > 0 || failsConds.length > 0 || avoidConds.length > 0) && (
        <Section title="適用条件">
          {worksConds.length > 0 && (
            <div className="mb-2">
              <p className="text-xs text-green-500 mb-1">有効な場合</p>
              <ul className="space-y-1">
                {worksConds.map((c, i) => <li key={i} className="text-sm text-gray-300">• {c.description}</li>)}
              </ul>
            </div>
          )}
          {failsConds.length > 0 && (
            <div className="mb-2">
              <p className="text-xs text-red-400 mb-1">失敗しやすい場合</p>
              <ul className="space-y-1">
                {failsConds.map((c, i) => <li key={i} className="text-sm text-gray-300">• {c.description}</li>)}
              </ul>
            </div>
          )}
          {avoidConds.length > 0 && (
            <div>
              <p className="text-xs text-yellow-500 mb-1">避けるべき場合</p>
              <ul className="space-y-1">
                {avoidConds.map((c, i) => <li key={i} className="text-sm text-gray-300">• {c.description}</li>)}
              </ul>
            </div>
          )}
        </Section>
      )}

      {tech.relations.length > 0 && (
        <Section title="関連技術">
          <div className="flex flex-wrap gap-2">
            {tech.relations.map((r, i) => (
              <div key={i} className="px-3 py-1.5 rounded bg-gray-800 border border-gray-700 text-sm">
                <span className="text-gray-500 text-xs">{r.relation_type}</span>
                <span className="ml-1 text-gray-200">{r.name}</span>
              </div>
            ))}
          </div>
        </Section>
      )}

      {tech.sources.length > 0 && (
        <Section title="参照ソース">
          <ul className="space-y-1">
            {tech.sources.map((s, i) => (
              <li key={i} className="text-sm">
                {s.url ? (
                  <a href={s.url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">
                    {s.title}
                  </a>
                ) : (
                  <span className="text-gray-400">{s.title}</span>
                )}
                <span className="text-gray-600 ml-2 text-xs">[{s.source_type}]</span>
              </li>
            ))}
          </ul>
        </Section>
      )}
    </div>
  );
}
