# アーキテクチャ設計書 — tech-memory

## 1. システム概要

### 1.1 全体構成

```
┌──────────────────────────────────────────────────────┐
│                   ブラウザ (ユーザー)                    │
└────────────────────────┬─────────────────────────────┘
                         │ HTTPS
         ┌───────────────▼───────────────┐
         │   Web (Next.js 15 App Router)  │
         │      Tailwind CSS + shadcn/ui  │
         │   ポート: 3000                  │
         └───────────────┬───────────────┘
                         │ HTTP/REST (JSON)
         ┌───────────────▼───────────────┐
         │   API (FastAPI / Python 3.12)  │
         │      uvicorn + async           │
         │   ポート: 8000                  │
         ├───────────────────────────────┤
         │   Collector / Parser / LLM     │
         │   Extractor / Normalizer       │
         └───────────────┬───────────────┘
                         │
         ┌───────────────▼───────────────┐
         │   PostgreSQL 16 + pgvector     │
         │   ポート: 5432                  │
         │   volumes: postgres_data       │
         └───────────────────────────────┘
```

**外部サービス接続:**

```
API → Anthropic Claude API  (技術カード抽出 / structured output)
API → OpenAI Embeddings API (text-embedding-3-small)
API → arXiv API / GitHub REST API / Web fetch (URL収集時)
```

### 1.2 ディレクトリ構造（モノレポ）

```
tech-memory/
├── phase3_code/
│   ├── backend/
│   │   ├── api/            # FastAPI エンドポイント
│   │   │   ├── routers/    # ingest, search, technologies, compare, recommend
│   │   │   ├── dependencies.py
│   │   │   └── main.py
│   │   ├── db/             # SQLAlchemy モデル・マイグレーション
│   │   │   ├── models/
│   │   │   ├── migrations/  # Alembic
│   │   │   └── session.py
│   │   └── logic/          # 収集・抽出・検索ロジック
│   │       ├── collector/  # URL fetch, arXiv, GitHub
│   │       ├── extractor/  # LLM structured output
│   │       ├── embedder/   # embedding生成
│   │       ├── normalizer/ # 同義語統合・重複排除
│   │       └── searcher/   # hybrid search
│   ├── frontend/
│   │   └── web/            # Next.js 15 App Router
│   │       ├── app/
│   │       │   ├── page.tsx           # 検索トップ
│   │       │   ├── search/page.tsx    # 検索結果一覧
│   │       │   ├── technologies/[id]/page.tsx  # 技術詳細
│   │       │   ├── ingest/page.tsx    # URL収集画面
│   │       │   ├── compare/page.tsx   # 技術比較
│   │       │   └── layout.tsx
│   │       ├── components/
│   │       └── lib/
│   └── shared_core/
│       ├── types/          # 共通型定義 (TypeScript)
│       ├── api/            # OpenAPI spec → 型自動生成
│       └── constants/      # collection_mode 等の定数
├── docker-compose.yml
├── .env.example
└── _orchestrator/
```

---

## 2. API設計

### 2.1 エンドポイント一覧

| Method | Path | 説明 | 認証 | 優先度 |
|---|---|---|---|---|
| POST | /api/v1/ingest/url | URLから技術カードを生成・保存 | なし | MUST |
| POST | /api/v1/ingest/search | キーワードで外部収集 | なし | SHOULD |
| POST | /api/v1/ingest/memo | 手入力メモから技術カード生成 | なし | SHOULD |
| POST | /api/v1/search/technologies | ハイブリッド技術検索 | なし | MUST |
| GET | /api/v1/technologies | 技術一覧（ページング） | なし | MUST |
| GET | /api/v1/technologies/{id} | 技術カード詳細 | なし | MUST |
| POST | /api/v1/compare | 複数技術の比較 | なし | SHOULD |
| POST | /api/v1/recommend | 課題・制約から技術推薦 | なし | SHOULD |
| GET | /api/v1/health | ヘルスチェック | なし | MUST |
| GET | /docs | FastAPI 自動生成 SwaggerUI | なし | MUST |

### 2.2 エンドポイント詳細仕様

#### POST /api/v1/ingest/url

**概要:** URL を入力し、技術情報を収集・解析して技術カードを DB に保存する。

**Request Body:**
```json
{
  "url": "https://arxiv.org/abs/2005.11401",
  "collection_mode": "standard",
  "tags": ["RAG", "NLP"]
}
```

- `url`: string（必須、http/httpsで始まること、1000文字以内）
- `collection_mode`: "light" | "standard" | "deep"（デフォルト: "standard"）
- `tags`: string[]（各50文字以内、最大20個）

**Response 200:**
```json
{
  "success": true,
  "data": {
    "source_id": "uuid",
    "detected_technologies": ["Behavior Tree", "GOAP"],
    "created_items": ["uuid1"],
    "updated_items": ["uuid2"],
    "summary": "arXiv論文: Retrieval-Augmented Generation for ..."
  },
  "error": null
}
```

**処理フロー:**
```
URL入力
  → URL種別判定 (arXiv / GitHub / 一般Web)
  → コンテンツ一時取得 (httpx)
  → テキスト抽出 (BeautifulSoup4)
  → LLM 技術カード生成 (Claude API structured output)
  → embedding 生成 (OpenAI text-embedding-3-small)
  → 正規化・重複排除
  → DB保存 (sources + technology_items + ...)
  → レスポンス返却
```

**非同期考慮:** LLM API呼び出しにより30秒程度かかる可能性がある。MVPではHTTPタイムアウトを60秒に設定し、同期で返す。将来的にJobキュー化する。

---

#### POST /api/v1/ingest/search

**Request Body:**
```json
{
  "query": "behavior tree NPC AI",
  "sources": ["web", "github"],
  "max_results": 20,
  "deep_analysis_limit": 3
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "collected_count": 5,
    "created_items": [],
    "updated_items": []
  },
  "error": null
}
```

---

#### POST /api/v1/ingest/memo

**Request Body:**
```json
{
  "memo": "Behavior TreeはゲームのNPC制御に使われる木構造の意思決定手法...",
  "tags": ["game AI"]
}
```

---

#### POST /api/v1/search/technologies

**Request Body:**
```json
{
  "query": "少ない試行回数で良い候補を見つけたい",
  "filters": {
    "domains": ["AI", "optimization"],
    "max_implementation_cost": "medium",
    "maturity_level": null
  },
  "mode": "problem_search",
  "limit": 10,
  "offset": 0
}
```

- `mode`: "keyword" | "problem_search" | "domain" | "condition"

**Response 200:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "technology_id": "uuid",
        "name": "Bayesian Optimization",
        "fit_score": 0.92,
        "summary": "評価コストが高い探索空間で...",
        "why_relevant": "少ない試行回数での候補選択に適する",
        "benefits": ["少試行回数で有望候補を発見できる"],
        "drawbacks": ["高次元空間では性能低下"],
        "alternatives": ["Random Search", "Evolutionary Algorithm"],
        "domains": ["AI", "optimization"]
      }
    ],
    "total": 5,
    "query": "少ない試行回数で良い候補を見つけたい"
  },
  "error": null,
  "meta": { "page": 1, "total": 5 }
}
```

---

#### GET /api/v1/technologies/{id}

**Response 200:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Behavior Tree",
    "item_type": "architecture_pattern",
    "aliases": ["BT", "行動ツリー"],
    "summary": "複雑な意思決定を...",
    "core_mechanism": "...",
    "abstract_principle": "...",
    "domains": ["game development", "robotics"],
    "categories": ["decision making"],
    "problem_structures": ["hierarchical decision making"],
    "purposes": [{ "description": "...", "condition": "..." }],
    "benefits": [{ "benefit": "...", "condition": "..." }],
    "drawbacks": [{ "drawback": "...", "condition": "...", "severity": "medium" }],
    "tradeoffs": [{ "gain": "...", "cost": "...", "condition": "..." }],
    "works_when": ["..."],
    "fails_when": ["..."],
    "avoid_when": ["..."],
    "relations": [
      { "relation_type": "alternative_to", "technology_id": "uuid", "name": "FSM" }
    ],
    "sources": [
      { "source_id": "uuid", "title": "...", "url": "...", "source_type": "web_article" }
    ],
    "maturity_level": "mature",
    "difficulty_level": "medium",
    "created_at": "2026-05-16T10:00:00Z",
    "updated_at": "2026-05-16T10:00:00Z"
  },
  "error": null
}
```

---

#### POST /api/v1/compare

**Request Body:**
```json
{
  "technologies": ["FSM", "Behavior Tree", "GOAP", "Utility AI"],
  "criteria": ["debuggability", "designer_control", "scalability", "runtime_cost"]
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "comparison_table": [
      {
        "name": "FSM",
        "scores": { "debuggability": 0.9, "designer_control": 0.6, "scalability": 0.4 },
        "summary": "..."
      }
    ],
    "recommendation": "...",
    "best_fit": "Behavior Tree"
  },
  "error": null
}
```

---

#### POST /api/v1/recommend

**Request Body:**
```json
{
  "goal": "研究論文から仮説を生成するシステムを作りたい",
  "constraints": ["根拠を追跡したい", "低コストでMVPを作りたい"]
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "candidates": [
      {
        "technology_id": "uuid",
        "name": "RAG",
        "fit_score": 0.95,
        "reason": "...",
        "implementation_note": "..."
      }
    ],
    "avoid": [
      { "name": "Fine-tuning", "reason": "コストが高い、MVPに不向き" }
    ]
  },
  "error": null
}
```

---

### 2.3 共通レスポンス形式

**成功レスポンス:**
```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "meta": {
    "page": 1,
    "total": 100,
    "limit": 10,
    "offset": 0
  }
}
```

**エラーレスポンス:**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "URLは http:// または https:// で始まる必要があります",
    "detail": { "field": "url", "value": "..." }
  }
}
```

**エラーコード一覧:**

| コード | HTTP Status | 説明 |
|---|---|---|
| VALIDATION_ERROR | 400 | 入力バリデーション失敗 |
| NOT_FOUND | 404 | 技術カード等のリソースが存在しない |
| FETCH_FAILED | 422 | URL取得失敗（タイムアウト・404等） |
| LLM_ERROR | 500 | Claude API エラー |
| INTERNAL_ERROR | 500 | その他のサーバー内部エラー |

---

## 3. 認証設計

### 3.1 MVPフェーズの認証方針

MVP段階はシングルユーザー・個人利用を前提とし、認証なしで動作する。

ただし、以下の将来拡張に備えた設計を維持する:
- 全エンドポイントに `Authorization` ヘッダーを受け付ける口を設ける（無視する）
- FastAPI の `Depends()` 機構を使い、将来的にAPIキー認証やJWT認証に差し替えられる構造にする

```python
# 現在（MVP）
async def get_current_user():
    return {"user_id": "default", "role": "admin"}

# 将来
async def get_current_user(token: str = Depends(oauth2_scheme)):
    return verify_token(token)
```

### 3.2 将来の認証フロー（参考）

```
クライアント → POST /api/v1/auth/token
  ← { "access_token": "...", "expires_in": 3600 }

クライアント → GET /api/v1/technologies
  Authorization: Bearer {access_token}
```

---

## 4. データフロー

### 4.1 URL収集フロー（メインフロー）

```
ユーザー入力 (URL)
    │
    ▼
POST /api/v1/ingest/url
    │
    ▼
URL種別判定
    ├─ arXiv URL → arXiv API でメタデータ取得
    ├─ GitHub URL → GitHub REST API で README 取得
    └─ 一般URL → httpx + BeautifulSoup4 でページ取得
    │
    ▼
テキスト抽出 / セクション分割
    │
    ▼
Claude API structured output
    → 技術カード JSON 生成
    (name, type, summary, core_mechanism, abstract_principle,
     domains, benefits, drawbacks, tradeoffs, works_when, fails_when)
    │
    ▼
embedding 生成
    → text-embedding-3-small
    → 1536次元ベクトル
    │
    ▼
正規化・重複排除
    → 既存技術カードとの照合
    → 重複の場合: 情報をマージ
    → 新規の場合: 新規作成
    │
    ▼
PostgreSQL 保存
    → sources テーブル
    → technology_items テーブル（embedding含む）
    → technology_purposes / benefits / drawbacks 等
    │
    ▼
レスポンス返却
```

### 4.2 技術検索フロー

```
ユーザー入力 (自然言語クエリ)
    │
    ▼
POST /api/v1/search/technologies
    │
    ▼
クエリ embedding 生成
    → text-embedding-3-small
    │
    ▼
ハイブリッド検索
    ├─ キーワード検索: PostgreSQL full-text search (tsvector)
    │   → 技術名・aliases・summary・abstract_principle を対象
    └─ ベクトル検索: pgvector cosine similarity
        → technology_items.embedding と比較
    │
    ▼
スコア合成 (weighted sum)
    → キーワードスコア × 0.3 + ベクトルスコア × 0.7
    │
    ▼
メタデータフィルタ（任意）
    → domains, maturity_level, implementation_cost
    │
    ▼
上位N件取得 + 関連情報 JOIN
    → benefits, drawbacks, relations, sources
    │
    ▼
レスポンス返却
```

---

## 5. Webアーキテクチャ詳細

### 5.1 Next.js App Router 構成

**レンダリング方針:**

| ページ | レンダリング | 理由 |
|---|---|---|
| / (検索トップ) | CSR + Server Action | 動的な検索入力 |
| /search | CSR | クエリパラメータ依存 |
| /technologies/[id] | SSR（動的） | SEO不要だが最新データ必要 |
| /ingest | CSR | フォーム操作中心 |
| /compare | CSR | 動的操作 |

**キャッシュ戦略:**
- 技術カード詳細: `cache: 'no-store'`（常に最新を取得）
- 検索結果: キャッシュなし（クエリ依存）

### 5.2 状態管理

```
Zustand Store
├── searchStore: { query, results, loading, filters }
├── ingestStore: { url, status, result }
└── compareStore: { selectedTechnologies, comparison }
```

### 5.3 APIクライアント

FastAPI が自動生成する OpenAPI spec を使い、openapi-typescript で TypeScript 型を自動生成する。

```bash
# 型生成コマンド（Makefile に記載）
pnpm openapi-typescript http://localhost:8000/openapi.json -o src/lib/api-types.ts
```

---

## 6. Docker Compose 構成

```yaml
services:
  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: techmemory
      POSTGRES_USER: techmemory
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  api:
    build:
      context: ./phase3_code/backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://techmemory:${DB_PASSWORD}@db:5432/techmemory
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - db
    volumes:
      - ./phase3_code/backend:/app

  web:
    build:
      context: ./phase3_code/frontend/web
      dockerfile: Dockerfile
    environment:
      NEXT_PUBLIC_API_BASE_URL: http://localhost:8000
    ports:
      - "3000:3000"
    depends_on:
      - api

volumes:
  postgres_data:
```

---

## 7. 共通設計決定

### 7.1 エラーハンドリング方針

**バックエンド:**
- FastAPI の `HTTPException` を使いエラーを統一フォーマットで返す
- LLM API エラーはリトライ（最大3回、指数バックオフ）
- URL取得失敗はクライアントに `FETCH_FAILED` エラーを返す（処理継続しない）
- DB接続エラーは `INTERNAL_ERROR` を返す

**フロントエンド:**
- 全 API 呼び出しに try-catch を設ける
- エラー時はトースト通知（shadcn/ui Toast）で表示
- 収集処理（長時間）にはローディングスピナーとタイムアウト表示

### 7.2 ロギング方針

```
バックエンド:
- Python logging（structlog 推奨）
- リクエスト/レスポンスをミドルウェアでログ出力
- LLM API呼び出し: latency、token数をログ出力
- エラー: スタックトレース付きで ERROR レベル出力
- DB クエリ: SQLAlchemy echo（開発時のみ）

フロントエンド:
- console.error（開発時のみ詳細）
- 本番では最小限のエラーログ
```

### 7.3 環境変数管理

**.env.example:**
```
# Database
DB_PASSWORD=changeme

# Anthropic Claude API
ANTHROPIC_API_KEY=sk-ant-...

# OpenAI Embeddings API
OPENAI_API_KEY=sk-...

# Frontend
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Collection limits
MAX_FETCH_TIMEOUT=60
MAX_CONTENT_LENGTH=100000
LLM_MAX_RETRIES=3
```

環境変数は `.env` ファイルで管理し、Git には `.env.example` のみコミットする。

### 7.4 CORS設定

```python
# FastAPI CORS設定（開発時）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 7.5 OpenAPI spec の公開

FastAPI 自動生成の OpenAPI spec を以下で公開する:
- SwaggerUI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- JSON: `http://localhost:8000/openapi.json`
