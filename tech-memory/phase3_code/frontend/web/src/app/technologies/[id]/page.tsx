"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, ExternalLink, CheckCircle, XCircle, AlertTriangle, ArrowRightLeft } from "lucide-react";
import { api, type TechnologyDetail } from "@/lib/api-client";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { Badge } from "@/components/ui/Badge";
import { ITEM_TYPE_LABELS, ITEM_TYPE_COLORS, MATURITY_LABELS, DIFFICULTY_LABELS, formatDate, cn } from "@/lib/utils";

export default function TechnologyDetailPage({ params }: { params: { id: string } }) {
  const [tech, setTech] = useState<TechnologyDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.technologies
      .get(params.id)
      .then((res) => {
        if (res.success && res.data) {
          setTech(res.data);
        }
      })
      .catch((err) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, [params.id]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh] gap-3 text-neutral-400">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error || !tech) {
    return (
      <div className="max-w-content mx-auto px-6 py-8">
        <div className="card p-4 border-semantic-error/30 bg-red-900/10">
          <p className="text-sm text-semantic-error">{error || "技術が見つかりません"}</p>
        </div>
      </div>
    );
  }

  const typeColor = ITEM_TYPE_COLORS[tech.item_type] || "text-neutral-400";

  return (
    <div className="max-w-content mx-auto px-6 py-8">
      {/* Back */}
      <Link href="/technologies" className="flex items-center gap-1.5 text-sm text-neutral-500 hover:text-neutral-100 mb-6 transition-colors">
        <ArrowLeft className="h-4 w-4" />
        技術一覧に戻る
      </Link>

      {/* Header */}
      <div className="card p-6 mb-4">
        <div className="flex flex-wrap items-center gap-2 mb-3">
          <span className={cn("text-xs font-mono font-medium", typeColor)}>
            {ITEM_TYPE_LABELS[tech.item_type] || tech.item_type}
          </span>
          {tech.maturity_level && (
            <Badge variant="muted">{MATURITY_LABELS[tech.maturity_level]}</Badge>
          )}
          {tech.difficulty_level && (
            <Badge variant="muted">実装難易度: {DIFFICULTY_LABELS[tech.difficulty_level]}</Badge>
          )}
          {tech.cost_level && (
            <Badge variant="muted">コスト: {DIFFICULTY_LABELS[tech.cost_level]}</Badge>
          )}
        </div>

        <h1 className="text-2xl font-bold text-neutral-100 mb-2">{tech.name}</h1>

        {tech.aliases.length > 0 && (
          <p className="text-xs text-neutral-500 mb-4">
            別名: {tech.aliases.join(", ")}
          </p>
        )}

        {tech.summary && (
          <p className="text-neutral-300 leading-relaxed mb-4">{tech.summary}</p>
        )}

        {/* Domains */}
        {tech.domains.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {tech.domains.map((d) => (
              <Badge key={d} variant="primary">{d}</Badge>
            ))}
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 gap-4">
        {/* Core Mechanism */}
        {tech.core_mechanism && (
          <Section title="コアメカニズム">
            <p className="text-sm text-neutral-300 leading-relaxed">{tech.core_mechanism}</p>
          </Section>
        )}

        {/* Abstract Principle */}
        {tech.abstract_principle && (
          <Section title="抽象原理">
            <p className="text-sm text-neutral-300 italic leading-relaxed">{tech.abstract_principle}</p>
          </Section>
        )}

        {/* Purposes */}
        {tech.purposes.length > 0 && (
          <Section title="目的・用途">
            <ul className="flex flex-col gap-2">
              {tech.purposes.map((p) => (
                <li key={p.id} className="text-sm">
                  <span className="text-neutral-200">{p.purpose}</span>
                  {p.condition && (
                    <span className="text-neutral-500 ml-2">（条件: {p.condition}）</span>
                  )}
                </li>
              ))}
            </ul>
          </Section>
        )}

        {/* Benefits */}
        {tech.benefits.length > 0 && (
          <Section title="メリット">
            <ul className="flex flex-col gap-2">
              {tech.benefits.map((b) => (
                <li key={b.id} className="flex items-start gap-2 text-sm">
                  <CheckCircle className="h-4 w-4 shrink-0 mt-0.5 text-semantic-success" />
                  <span>
                    <span className="text-neutral-200">{b.benefit}</span>
                    {b.condition && (
                      <span className="text-neutral-500 ml-2">（{b.condition}）</span>
                    )}
                  </span>
                </li>
              ))}
            </ul>
          </Section>
        )}

        {/* Drawbacks */}
        {tech.drawbacks.length > 0 && (
          <Section title="デメリット">
            <ul className="flex flex-col gap-2">
              {tech.drawbacks.map((d) => (
                <li key={d.id} className="flex items-start gap-2 text-sm">
                  <XCircle className="h-4 w-4 shrink-0 mt-0.5 text-semantic-error" />
                  <span>
                    <span className="text-neutral-200">{d.drawback}</span>
                    {d.condition && (
                      <span className="text-neutral-500 ml-2">（{d.condition}）</span>
                    )}
                    {d.severity && (
                      <Badge
                        variant={d.severity === "high" ? "error" : d.severity === "medium" ? "warning" : "muted"}
                        className="ml-2 text-[10px]"
                      >
                        {d.severity}
                      </Badge>
                    )}
                  </span>
                </li>
              ))}
            </ul>
          </Section>
        )}

        {/* Tradeoffs */}
        {tech.tradeoffs.length > 0 && (
          <Section title="トレードオフ">
            <ul className="flex flex-col gap-2">
              {tech.tradeoffs.map((t) => (
                <li key={t.id} className="flex items-start gap-2 text-sm">
                  <ArrowRightLeft className="h-4 w-4 shrink-0 mt-0.5 text-neutral-500" />
                  <span>
                    <span className="text-semantic-success">得: {t.gain}</span>
                    <span className="text-neutral-500 mx-2">|</span>
                    <span className="text-semantic-error">失: {t.cost}</span>
                    {t.condition && (
                      <span className="text-neutral-500 ml-2">（{t.condition}）</span>
                    )}
                  </span>
                </li>
              ))}
            </ul>
          </Section>
        )}

        {/* Conditions */}
        {(tech.works_when.length > 0 || tech.fails_when.length > 0 || tech.avoid_when.length > 0) && (
          <Section title="使用条件">
            <div className="flex flex-col gap-4">
              {tech.works_when.length > 0 && (
                <ConditionGroup label="有効な場合" items={tech.works_when} color="success" />
              )}
              {tech.fails_when.length > 0 && (
                <ConditionGroup label="失敗しやすい場合" items={tech.fails_when} color="warning" />
              )}
              {tech.avoid_when.length > 0 && (
                <ConditionGroup label="避けるべき場合" items={tech.avoid_when} color="error" />
              )}
            </div>
          </Section>
        )}

        {/* Relations */}
        {tech.relations.length > 0 && (
          <Section title="関連技術">
            <ul className="flex flex-col gap-2">
              {tech.relations.map((r) => (
                <li key={r.id} className="flex items-center gap-2 text-sm">
                  <Badge variant="muted" className="text-[10px] shrink-0">{r.relation_type.replace("_", " ")}</Badge>
                  <Link href={`/technologies/${r.technology_id}`} className="text-primary-400 hover:underline">
                    {r.name}
                  </Link>
                </li>
              ))}
            </ul>
          </Section>
        )}

        {/* Sources */}
        {tech.sources.length > 0 && (
          <Section title="情報源">
            <ul className="flex flex-col gap-2">
              {tech.sources.map((s) => (
                <li key={s.source_id} className="flex items-center gap-2 text-sm">
                  <Badge variant="muted" className="text-[10px] shrink-0">{s.source_type}</Badge>
                  {s.url ? (
                    <a href={s.url} target="_blank" rel="noopener noreferrer"
                       className="text-primary-400 hover:underline flex items-center gap-1 truncate">
                      {s.title}
                      <ExternalLink className="h-3 w-3 shrink-0" />
                    </a>
                  ) : (
                    <span className="text-neutral-400">{s.title}</span>
                  )}
                </li>
              ))}
            </ul>
          </Section>
        )}
      </div>

      {/* Footer */}
      <p className="text-xs text-neutral-600 mt-6">
        更新: {formatDate(tech.updated_at)}
      </p>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="card p-5">
      <h2 className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-3">
        {title}
      </h2>
      {children}
    </div>
  );
}

function ConditionGroup({
  label,
  items,
  color,
}: {
  label: string;
  items: string[];
  color: "success" | "warning" | "error";
}) {
  const Icon = color === "success" ? CheckCircle : color === "warning" ? AlertTriangle : XCircle;
  const iconColor = color === "success" ? "text-semantic-success" : color === "warning" ? "text-semantic-warning" : "text-semantic-error";

  return (
    <div>
      <p className="text-xs font-medium text-neutral-500 mb-1.5">{label}</p>
      <ul className="flex flex-col gap-1">
        {items.map((item, i) => (
          <li key={i} className="flex items-start gap-2 text-sm text-neutral-300">
            <Icon className={cn("h-3.5 w-3.5 shrink-0 mt-0.5", iconColor)} />
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
