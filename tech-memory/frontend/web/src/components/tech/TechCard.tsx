import Link from "next/link";
import { ChevronRight, CheckCircle, XCircle } from "lucide-react";
import { cn, ITEM_TYPE_LABELS, ITEM_TYPE_COLORS, MATURITY_LABELS } from "@/lib/utils";
import { Badge } from "@/components/ui/Badge";
import { FitScoreBadge } from "@/components/ui/FitScoreBadge";
import type { TechnologySearchResult } from "@/lib/api-client";

interface TechCardProps {
  tech: TechnologySearchResult;
  className?: string;
}

export function TechCard({ tech, className }: TechCardProps) {
  const typeLabel = ITEM_TYPE_LABELS[tech.item_type] || tech.item_type;
  const typeColor = ITEM_TYPE_COLORS[tech.item_type] || "text-neutral-400";

  return (
    <article
      className={cn(
        "card p-5 hover:border-neutral-600 transition-colors group",
        className,
      )}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          {/* Header row */}
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <span className={cn("text-xs font-medium font-mono", typeColor)}>
              {typeLabel}
            </span>
            {tech.maturity_level && (
              <Badge variant="muted" className="text-[10px]">
                {MATURITY_LABELS[tech.maturity_level] || tech.maturity_level}
              </Badge>
            )}
            {tech.fit_score > 0 && <FitScoreBadge score={tech.fit_score} />}
          </div>

          {/* Name */}
          <Link href={`/technologies/${tech.technology_id}`}>
            <h3 className="text-base font-semibold text-neutral-100 group-hover:text-primary-400 transition-colors mb-1 truncate">
              {tech.name}
            </h3>
          </Link>

          {/* Summary */}
          {tech.summary && (
            <p className="text-sm text-neutral-400 line-clamp-2 mb-3">
              {tech.summary}
            </p>
          )}

          {/* Why relevant */}
          {tech.why_relevant && (
            <p className="text-xs text-primary-400 mb-3 italic">
              {tech.why_relevant}
            </p>
          )}

          {/* Benefits & Drawbacks */}
          <div className="flex flex-col gap-1.5">
            {tech.benefits.slice(0, 2).map((b, i) => (
              <div key={i} className="flex items-start gap-1.5 text-xs text-neutral-400">
                <CheckCircle className="h-3 w-3 mt-0.5 shrink-0 text-semantic-success" />
                <span>{b}</span>
              </div>
            ))}
            {tech.drawbacks.slice(0, 1).map((d, i) => (
              <div key={i} className="flex items-start gap-1.5 text-xs text-neutral-400">
                <XCircle className="h-3 w-3 mt-0.5 shrink-0 text-semantic-error" />
                <span>{d}</span>
              </div>
            ))}
          </div>

          {/* Domains */}
          {tech.domains.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-3">
              {tech.domains.slice(0, 4).map((d) => (
                <Badge key={d} variant="muted" className="text-[10px]">
                  {d}
                </Badge>
              ))}
            </div>
          )}
        </div>

        {/* Arrow */}
        <ChevronRight className="h-4 w-4 text-neutral-600 group-hover:text-primary-400 shrink-0 mt-1 transition-colors" />
      </div>
    </article>
  );
}
