import { cn } from "@/lib/utils";
import type { ReactNode } from "react";

interface BadgeProps {
  children: ReactNode;
  variant?: "default" | "primary" | "success" | "warning" | "error" | "muted";
  className?: string;
}

const VARIANT_CLASSES = {
  default: "bg-neutral-800 text-neutral-300 border border-neutral-700",
  primary: "bg-primary-900/50 text-primary-300 border border-primary-700/50",
  success: "bg-green-900/50 text-green-400 border border-green-700/50",
  warning: "bg-yellow-900/50 text-yellow-400 border border-yellow-700/50",
  error: "bg-red-900/50 text-red-400 border border-red-700/50",
  muted: "bg-neutral-800 text-neutral-500 border border-neutral-700",
};

export function Badge({ children, variant = "default", className }: BadgeProps) {
  return (
    <span className={cn("badge", VARIANT_CLASSES[variant], className)}>
      {children}
    </span>
  );
}
