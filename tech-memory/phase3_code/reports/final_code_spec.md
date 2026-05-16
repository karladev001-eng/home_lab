# コード仕様書 — tech-memory

## 生成日時: 2026-05-16

## 1. 概要

| 項目 | 内容 |
|---|---|
| プロジェクト名 | tech-memory |
| プラットフォーム | web, api |
| 技術スタック | Python 3.12 / FastAPI / PostgreSQL 16 + pgvector / Next.js 15 / TypeScript |
| 総コード行数 | 約 5,055行（Python + TypeScript） |
| ソースファイル数 | 60ファイル |
| テストファイル数 | 3ファイル（13テストケース） |

## 2. ディレクトリ構造

```
phase3_code/
├── docker-compose.yml          # 全サービス定義（db/api/web）
├── .env.example                # 環境変数テンプレート
├── backend/                    # FastAPI バックエンド
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pyproject.toml         # ruff + pytest設定
│   ├── api/
│   │   ├── main.py            # FastAPIアプリ + ミドルウェア
│   │   ├── config.py          # pydantic-settings環境設定
│   │   ├── schemas.py         # Pydantic リクエスト/レスポンス型
│   │   ├── dependencies.py
│   │   └── routers/
│   │       ├── health.py      # GET /api/v1/health
│   │       ├── ingest.py      # POST /api/v1/ingest/{url,search,memo}
│   │       ├── search.py      # POST /api/v1/search/technologies
│   │       ├── technologies.py # GET /api/v1/technologies[/{id}]
│   │       ├── compare.py     # POST /api/v1/compare
│   │       └── recommend.py   # POST /api/v1/recommend
│   ├── db/
│   │   ├── session.py         # SQLAlchemy async engine + get_db()
│   │   ├── models/
│   │   │   ├── sources.py     # Source モデル
│   │   │   ├── technology.py  # TechnologyItem + 関連5テーブル
│   │   │   └── use_cases.py   # UseCase + UseCaseTechnology + Evidence
│   │   └── migrations/
│   │       ├── env.py         # Alembic async設定
│   │       ├── alembic.ini
│   │       └── versions/
│   │           └── 001_initial_schema.py  # 全テーブル + インデックス
│   ├── logic/
│   │   ├── collector/
│   │   │   ├── url_collector.py    # arXiv/GitHub/Web取得
│   │   │   ├── search_collector.py # GitHub/arXiv検索
│   │   │   └── memo_collector.py   # メモ入力処理
│   │   ├── extractor/
│   │   │   └── llm_extractor.py   # Claude API structured output
│   │   ├── embedder/
│   │   │   └── openai_embedder.py  # text-embedding-3-small
│   │   ├── normalizer/
│   │   │   └── deduplicator.py    # 名前正規化 + upsert
│   │   └── searcher/
│   │       ├── hybrid_search.py   # FTS + vector検索
│   │       ├── compare_service.py # LLMによる比較スコアリング
│   │       └── recommend_service.py # 問題文からの推薦
│   └── tests/
│       ├── test_schemas.py    # バリデーションテスト（7件）
│       ├── test_health.py     # ヘルスエンドポイントテスト（1件）
│       └── test_normalizer.py # 正規化ロジックテスト（5件）
├── frontend/web/               # Next.js 15 フロントエンド
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts     # デザイントークン反映済み
│   ├── next.config.ts         # APIプロキシ設定
│   └── src/
│       ├── app/
│       │   ├── layout.tsx     # ルートレイアウト + ヘッダー
│       │   ├── globals.css    # Tailwindユーティリティクラス定義
│       │   ├── page.tsx       # SCR001: 検索トップ
│       │   ├── search/        # SCR002: 検索結果一覧
│       │   ├── technologies/  # SCR004: 技術一覧
│       │   ├── technologies/[id]/ # SCR003: 技術詳細
│       │   ├── ingest/        # SCR005: URL収集（タブUI）
│       │   └── compare/       # SCR007: 技術比較
│       ├── components/
│       │   ├── layout/Header.tsx
│       │   ├── tech/TechCard.tsx
│       │   ├── tech/SearchBar.tsx
│       │   └── ui/{Badge,FitScoreBadge,LoadingSpinner}.tsx
│       └── lib/
│           ├── api-client.ts  # 全エンドポイント対応型安全クライアント
│           └── utils.ts       # cn(), formatDate(), ラベルマップ
└── shared_core/
    ├── types/                 # TypeScript エンティティ + API型定義
    └── constants/             # COLLECTION_MODES, API_PATHS等の定数
```

## 3. 実装済み API エンドポイント一覧

| Method | Path | 認証 | 説明 | 優先度 |
|---|---|---|---|---|
| GET | /api/v1/health | 不要 | DBヘルスチェック含む | MUST |
| POST | /api/v1/ingest/url | 不要 | URLから技術カード生成（LLM抽出） | MUST |
| POST | /api/v1/ingest/search | 不要 | GitHub/arXivキーワード検索収集 | SHOULD |
| POST | /api/v1/ingest/memo | 不要 | メモテキストから技術カード生成 | SHOULD |
| POST | /api/v1/search/technologies | 不要 | ハイブリッド検索（FTS+vector） | MUST |
| GET | /api/v1/technologies | 不要 | 技術一覧（ページング・フィルタ） | MUST |
| GET | /api/v1/technologies/{id} | 不要 | 技術詳細（全関連データ付き） | MUST |
| POST | /api/v1/compare | 不要 | 複数技術のLLMスコア比較 | SHOULD |
| POST | /api/v1/recommend | 不要 | 問題文からベクトル推薦 | SHOULD |

## 4. 依存関係

### Backend（Python）

| パッケージ | バージョン | 用途 |
|---|---|---|
| fastapi | 0.115.5 | Webフレームワーク |
| uvicorn | 0.32.1 | ASGIサーバー |
| sqlalchemy | 2.0.36 | ORM（非同期対応） |
| asyncpg | 0.30.0 | PostgreSQL非同期ドライバ |
| alembic | 1.14.0 | DBマイグレーション |
| pgvector | 0.3.6 | pgvector SQLAlchemy連携 |
| anthropic | 0.40.0 | Claude API（技術抽出） |
| openai | 1.55.3 | embedding生成 |
| httpx | 0.28.0 | 非同期HTTPクライアント |
| beautifulsoup4 | 4.12.3 | HTML解析 |
| arxiv | 2.1.3 | arXiv API |
| pydantic | 2.10.2 | スキーマバリデーション |
| ruff | 0.8.3 | linter/formatter |
| pytest + pytest-asyncio | 8.3.4 / 0.24.0 | テスト |

### Frontend（TypeScript / Next.js）

| パッケージ | バージョン | 用途 |
|---|---|---|
| next | 15.0.3 | フレームワーク |
| react | 18.2.0 | UIライブラリ |
| @tanstack/react-query | 5.x | サーバー状態管理 |
| zustand | 5.x | クライアント状態管理 |
| tailwindcss | 3.4.x | スタイリング |
| lucide-react | 0.400.x | アイコン |
| clsx + tailwind-merge | 2.x | クラス名ユーティリティ |

## 5. テスト結果サマリー

| 対象 | テストファイル | テスト数 |
|---|---|---|
| バリデーションスキーマ | tests/test_schemas.py | 7 |
| ヘルスエンドポイント | tests/test_health.py | 1 |
| 正規化ロジック | tests/test_normalizer.py | 5 |
| 合計 | 3ファイル | 13テスト |

注: DB依存テストはDocker Compose環境での実行が前提

## 6. 技術的決定事項

1. **embeddingフォールバック**: OpenAI API失敗時はembedding=NULLで保存。ベクトル検索失敗時はキーワード検索にフォールバック
2. **技術名重複排除**: name_normalizedをUNIQUEキーとし、小文字化・記号除去済みの正規化名で一意性保証
3. **LLMモデル選択戦略**: lightモードはclaude-haiku（高速・低コスト）、standard/deepはclaude-sonnet（高品質）
4. **API収集タイムアウト**: 60秒の同期処理（MVP。将来Jobキュー化）
5. **tsvector更新**: PostgreSQLのGENERATED ALWAYSはpgvectorのVector型列と共存できないためアプリ側更新を採用
6. **APIプロキシ**: Next.jsのrewrites機能でフロントエンドからバックエンドへの/api/*をプロキシ

## 7. オプティマイザー修正サマリー

- ハードコードシークレット: なし（全て環境変数経由）
- 命名規則: Python(snake_case) / TypeScript(camelCase) 統一済み
- APIレスポンス形式: `ApiResponse[T]`で全エンドポイント統一
- 環境変数: `.env.example`に全変数を明記

## 8. 既知の制限事項・未実装事項

- tsvector自動更新トリガー未設定（手動更新 or 定期バッチで対応要）
- 技術比較のLLMレスポンスパース: 正規表現ベース（堅牢性向上余地あり）
- GitHub API未認証時のレート制限（環境変数でトークン設定可能）
- ページネーションUI（次ページボタン）未実装
- SCR006（推薦専用画面）未実装（/recommendエンドポイントは実装済み）
- E2Eテスト（Playwright等）未実装

## 9. 起動・実行方法

```bash
# 1. 環境変数設定
cd phase3_code
cp .env.example .env
# .envのANTHROPIC_API_KEY・OPENAI_API_KEYを設定

# 2. Docker Compose起動
docker-compose up -d

# 3. DBマイグレーション
docker-compose exec api alembic upgrade head

# 4. 動作確認
# API: http://localhost:8000/docs
# Web: http://localhost:3000
# Health: curl http://localhost:8000/api/v1/health
```
