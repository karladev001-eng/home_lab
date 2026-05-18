# 技術収集・検索DB — 詳細ドキュメント

URLや自然言語メモから技術カードを自動生成し、課題・分野・転用の観点で横断検索できる知識DBシステム。

---

## システム概要

| 項目 | 内容 |
|---|---|
| バックエンド | FastAPI + PostgreSQL (pgvector) |
| フロントエンド | Next.js 15 (App Router) |
| AI | Anthropic Claude（技術カード生成）+ OpenAI（埋め込み） |
| 起動 | Docker Compose |

---

## ディレクトリ構造

```
tech-memory/
├── backend/
│   ├── api/
│   │   ├── main.py          ← FastAPI エントリーポイント
│   │   ├── schemas.py       ← Pydantic スキーマ
│   │   ├── dependencies.py  ← DI設定
│   │   └── routers/
│   │       ├── ingest.py        ← URL・メモの取り込み
│   │       ├── technologies.py  ← 技術カード CRUD
│   │       ├── search.py        ← ハイブリッド検索
│   │       ├── compare.py       ← 技術比較
│   │       ├── recommend.py     ← 関連技術推薦
│   │       └── health.py        ← ヘルスチェック
│   ├── db/
│   │   ├── models/          ← SQLAlchemy モデル
│   │   └── migrations/      ← Alembic マイグレーション
│   ├── logic/
│   │   ├── collector/       ← URL・メモ・検索からのデータ収集
│   │   ├── extractor/       ← Claude による技術カード生成
│   │   ├── embedder/        ← OpenAI による埋め込み生成
│   │   ├── normalizer/      ← 重複排除・正規化
│   │   └── searcher/        ← ハイブリッド検索・比較・推薦
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   └── web/                 ← Next.js フロントエンド
│       └── src/
│           ├── app/         ← ページ（search / ingest / technologies / compare）
│           ├── components/  ← TechCard, SearchBar, Badge など
│           └── lib/         ← API クライアント
├── shared_core/             ← 共有型定義・定数
├── docker-compose.yml
└── .env.example
```

---

## セットアップ

### 1. 環境変数を設定する

```bash
cd tech-memory
cp .env.example .env
# .env を編集して API キーを設定
```

必須の設定:

| 変数 | 説明 |
|---|---|
| `ANTHROPIC_API_KEY` | Claude API キー（技術カード生成に使用） |
| `OPENAI_API_KEY` | OpenAI API キー（埋め込み生成に使用） |
| `POSTGRES_USER/PASSWORD/DB` | DB 認証情報（デフォルト値のままでも動作） |

### 2. 起動する

```bash
docker compose up -d
```

| サービス | URL |
|---|---|
| Web UI | http://localhost:3000 |
| API | http://localhost:8000 |
| API ドキュメント | http://localhost:8000/docs |

### 3. DBマイグレーションを実行する

```bash
docker compose exec api alembic upgrade head
```

---

## 主な機能

### 技術カードの取り込み

URL、自然言語メモ、検索クエリのいずれかから技術情報を取り込む。
Claude が自動で以下を抽出してカードを生成する。

- 技術名・カテゴリ
- 解決する課題
- 適用分野
- 転用可能な領域
- 類似技術との比較

### ハイブリッド検索

キーワード検索とベクトル検索を組み合わせた検索。
「この課題を解決できる技術」「この分野で使われる技術」などの自然言語クエリに対応。

### 技術比較・推薦

2つ以上の技術を並べて比較、または現在注目している技術から関連技術を推薦。

---

## API エンドポイント

| メソッド | パス | 説明 |
|---|---|---|
| POST | `/ingest/url` | URL から技術カードを生成 |
| POST | `/ingest/memo` | テキストメモから技術カードを生成 |
| GET | `/technologies` | 技術カード一覧 |
| GET | `/technologies/{id}` | 技術カード詳細 |
| GET | `/search` | ハイブリッド検索 |
| POST | `/compare` | 技術比較 |
| GET | `/recommend/{id}` | 関連技術推薦 |
| GET | `/health` | ヘルスチェック |

---

## 開発・テスト

```bash
# バックエンドテストを実行
docker compose exec api pytest

# フロントエンド開発サーバー（Docker なし）
cd frontend/web
pnpm install
pnpm dev
```
