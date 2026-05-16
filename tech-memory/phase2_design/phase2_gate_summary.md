# Phase 2 承認ゲートサマリー

## アーキテクチャ
- 構成: モノレポ（backend / frontend/web / shared_core）
- 認証方式: なし（MVP・シングルユーザー）。将来拡張に向けFastAPI Depends()で差し替え可能な構造
- 主要APIエンドポイント: 8本
  - POST /api/v1/ingest/url（MUST）
  - POST /api/v1/ingest/search / POST /api/v1/ingest/memo（SHOULD）
  - POST /api/v1/search/technologies（MUST）
  - GET /api/v1/technologies / GET /api/v1/technologies/{id}（MUST）
  - POST /api/v1/compare / POST /api/v1/recommend（SHOULD）
- 収集処理は同期（最大60秒タイムアウト）。将来的にJobキュー化する設計
- Docker Compose: db(pgvector/pgvector:pg16) + api(Python 3.12) + web(Node.js 20)

## データモデル
- エンティティ数: 11テーブル
- 主要エンティティ: sources, technology_items（embedding+tsvector含む）, technology_purposes, technology_benefits, technology_drawbacks, technology_tradeoffs, technology_conditions, technology_relations, use_cases, use_case_technologies, evidence
- embedding: vector(1536) — text-embedding-3-small
- 全文検索: tsvector + GINインデックス（PostgreSQL FTS）
- ベクトル検索: ivfflat インデックス（pgvector cosine）

## 画面構成
- 画面数: 7画面（SCR001〜SCR007）
- 主要画面: 検索トップ / 検索結果一覧 / 技術詳細 / URL収集 / 収集結果確認 / 技術比較 / 技術推薦
- Next.js 15 App Router, CSR中心, デスクトップファースト, shadcn/ui

## デザイン
- テーマ: ダーク・テクニカル（コードエディタ的、プロフェッショナル・ミニマル）
- カラー: primary=#6366f1（indigo）, background=#0f172a（slate-900）
- フォント: Inter + Noto Sans JP（和文対応）
- ダークモード: デフォルトでダーク

## 生成済みモックアップ
- SCR001: 検索トップ（検索バー + 検索例 + 検索モードタブ）
- SCR002: 検索結果一覧（技術カード + フィルタサイドバー + 比較フローティングバー）
- SCR003: 技術詳細（全情報 + 条件付きメリット/デメリット/トレードオフ + 関係技術）
- SCR005: URL収集（タブ + 深度ラジオ + タグ入力）

## 詳細ファイル
- phase2_design/architecture.md
- phase2_design/data_model.json
- phase2_design/ui_ux/screen_flow.md
- phase2_design/ui_ux/wireframes/（7ファイル）
- phase2_design/design/design_tokens.json
- phase2_design/design/mockups/（5ファイル）
