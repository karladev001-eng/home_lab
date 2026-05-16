import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Tech Memory",
  description: "Technology knowledge collection and search system",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-950 text-gray-100 min-h-screen">
        <header className="border-b border-gray-800 px-6 py-4">
          <nav className="max-w-6xl mx-auto flex items-center gap-6">
            <a href="/" className="text-lg font-bold text-blue-400">Tech Memory</a>
            <a href="/ingest" className="text-sm text-gray-400 hover:text-gray-200">収集</a>
            <a href="/search" className="text-sm text-gray-400 hover:text-gray-200">検索</a>
            <a href="/technologies" className="text-sm text-gray-400 hover:text-gray-200">一覧</a>
          </nav>
        </header>
        <main className="max-w-6xl mx-auto px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
