import type { Metadata } from "next";
import "./globals.css";
import { Header } from "@/components/layout/Header";

export const metadata: Metadata = {
  title: "Tech Memory — 技術知識DB",
  description: "技術・アルゴリズム・設計パターンを収集・検索・推薦するシステム",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja" className="dark">
      <body className="min-h-screen bg-neutral-900">
        <Header />
        <main className="pt-nav min-h-screen">
          {children}
        </main>
      </body>
    </html>
  );
}
