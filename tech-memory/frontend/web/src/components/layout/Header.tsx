"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Brain, Search, Database, PlusCircle, GitCompare } from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/", label: "検索", icon: Search },
  { href: "/technologies", label: "技術一覧", icon: Database },
  { href: "/ingest", label: "収集", icon: PlusCircle },
  { href: "/compare", label: "比較", icon: GitCompare },
];

export function Header() {
  const pathname = usePathname();

  return (
    <header className="fixed top-0 left-0 right-0 z-sticky h-nav bg-neutral-900/95 backdrop-blur-sm border-b border-neutral-800">
      <div className="max-w-[1400px] mx-auto px-6 h-full flex items-center gap-8">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 shrink-0">
          <Brain className="h-5 w-5 text-primary-400" />
          <span className="font-semibold text-neutral-100 tracking-tight">
            Tech Memory
          </span>
        </Link>

        {/* Nav */}
        <nav className="flex items-center gap-1">
          {NAV_ITEMS.map(({ href, label, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors",
                pathname === href
                  ? "bg-neutral-800 text-neutral-100"
                  : "text-neutral-400 hover:text-neutral-100 hover:bg-neutral-800/50",
              )}
            >
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
