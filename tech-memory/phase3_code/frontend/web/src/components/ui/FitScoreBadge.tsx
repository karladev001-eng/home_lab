import { cn } from "@/lib/utils";

interface FitScoreBadgeProps {
  score: number;
  className?: string;
}

export function FitScoreBadge({ score, className }: FitScoreBadgeProps) {
  const pct = Math.round(score * 100);
  const isHigh = score >= 0.9;
  const isMedium = score >= 0.7;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-semibold font-mono",
        isHigh
          ? "bg-green-900/50 text-green-400 border border-green-700/50"
          : isMedium
            ? "bg-yellow-900/50 text-yellow-400 border border-yellow-700/50"
            : "bg-neutral-800 text-neutral-400 border border-neutral-700",
        className,
      )}
    >
      {pct}%
    </span>
  );
}
