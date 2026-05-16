import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

/** Format a date string to locale date. */
export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("ja-JP", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

/** Map item_type to display label. */
export const ITEM_TYPE_LABELS: Record<string, string> = {
  technique: "テクニック",
  algorithm: "アルゴリズム",
  architecture: "アーキテクチャ",
  architecture_pattern: "アーキテクチャパターン",
  design_pattern: "デザインパターン",
  implementation_pattern: "実装パターン",
  tool: "ツール",
  library: "ライブラリ",
  framework: "フレームワーク",
  protocol: "プロトコル",
  evaluation_method: "評価手法",
  method_family: "手法ファミリー",
};

/** Map maturity_level to display label. */
export const MATURITY_LABELS: Record<string, string> = {
  experimental: "実験的",
  emerging: "新興",
  mature: "成熟",
  legacy: "レガシー",
};

/** Map difficulty_level to display label. */
export const DIFFICULTY_LABELS: Record<string, string> = {
  low: "低",
  medium: "中",
  high: "高",
};

/** Item type to color mapping (Tailwind classes from design tokens). */
export const ITEM_TYPE_COLORS: Record<string, string> = {
  algorithm: "text-primary-400",
  architecture: "text-accent-teal",
  design_pattern: "text-accent-orange",
  tool: "text-purple-400",
  technique: "text-blue-400",
  framework: "text-emerald-400",
  library: "text-orange-400",
};

/** Fit score to color class. */
export function fitScoreColor(score: number): string {
  if (score >= 0.9) return "text-semantic-success";
  if (score >= 0.7) return "text-semantic-warning";
  return "text-neutral-400";
}
