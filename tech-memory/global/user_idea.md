# tech-memory — User Idea

技術収集・検索DBシステム。
研究・開発・ゲーム制作・システム設計など複数分野で使える技術知識DBを構築する。

## 主目的

- 論文、技術記事、GitHub、公式Docs、技術ブログなどから技術情報を収集
- 技術・アルゴリズム・設計パターン・ツールを構造化して保存
- 技術名を知らなくても課題・目的から関連技術を検索できる
- 技術のメリット、デメリット、成立条件、失敗条件を検索できる
- 異なる分野の技術を抽象原理ベースで横断検索できる
- URLやキーワードから技術情報を追加できる

## MVPスコープ（Phase 1）

- URL入力による収集（Web記事 / arXiv / GitHub README）
- 技術カード自動生成（LLM structured output）
- 技術名・課題・分野からの検索（キーワード + pgvector）
- PostgreSQL + pgvector による検索
- 技術カード詳細表示

## 推奨技術スタック

- Backend: Python, FastAPI, PostgreSQL, pgvector
- AI/Extraction: LLM structured output（Claude or OpenAI）, Embedding model
- Frontend: Next.js, React, Tailwind CSS
- Infrastructure: Docker Compose
