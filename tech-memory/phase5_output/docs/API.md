# API 仕様書 — tech-memory

## ベース URL

| 環境 | URL |
|---|---|
| 開発 | `http://localhost:8000/api/v1` |
| SwaggerUI | `http://localhost:8000/docs` |
| ReDoc | `http://localhost:8000/redoc` |

## 認証

認証不要（MVP・単一ユーザー前提）。全エンドポイントに認証ヘッダーは不要です。

## 共通レスポンス形式

### 成功レスポンス
```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

### ページネーション付き成功レスポンス
```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "meta": { "page": 1, "total": 42 }
}
```

### エラーレスポンス（FastAPIバリデーション）
```json
{
  "detail": [
    {
      "loc": ["body", "url"],
      "msg": "URL must start with http:// or https://",
      "type": "value_error"
    }
  ]
}
```

### エラーコード一覧

| HTTP Status | 説明 |
|---|---|
| 422 | バリデーションエラー（入力値不正） |
| 404 | リソースが存在しない |
| 500 | サーバー内部エラー |
| 504 | コンテンツ取得タイムアウト（60秒超過） |

---

## エンドポイント一覧

### ヘルス

#### GET `/health`

**説明**: APIサーバーとDBの稼働状態を確認します。

**認証**: 不要

**リクエスト**: なし

**レスポンス（成功）**: `200 OK`
```json
{
  "success": true,
  "data": {
    "status": "ok",
    "db": "ok",
    "version": "0.1.0"
  },
  "error": null
}
```

| フィールド | 型 | 説明 |
|---|---|---|
| `status` | `"ok" \| "degraded"` | DBが正常なら "ok"、エラーなら "degraded" |
| `db` | `"ok" \| "error"` | DB接続状態 |
| `version` | string | APIバージョン |

---

### 収集 (Ingest)

#### POST `/ingest/url`

**説明**: URLを入力してコンテンツを取得し、技術カードを自動生成・保存します。

**認証**: 不要

**リクエスト**:
```json
{
  "url": "https://arxiv.org/abs/2005.11401",
  "collection_mode": "standard",
  "tags": ["RAG", "NLP"]
}
```

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `url` | string | 必須 | `http://` または `https://` で始まること。1000文字以内。 |
| `collection_mode` | `"light" \| "standard" \| "deep"` | 任意 | デフォルト: `"standard"`。lightは高速・低精度、deepは時間がかかる高精度。 |
| `tags` | string[] | 任意 | 各50文字以内、最大20個。 |

**対応URL種別**:
- `arxiv.org/abs/{ID}` → arXiv APIで論文のタイトル・アブストラクトを取得
- `github.com/{owner}/{repo}` → GitHub APIでREADMEを取得
- その他 → httpx + BeautifulSoup4でHTMLからテキスト抽出

**レスポンス（成功）**: `200 OK`
```json
{
  "success": true,
  "data": {
    "source_id": "550e8400-e29b-41d4-a716-446655440000",
    "detected_technologies": ["Behavior Tree", "GOAP"],
    "created_items": ["uuid1"],
    "updated_items": ["uuid2"],
    "summary": "arXiv論文: Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"
  },
  "error": null
}
```

| フィールド | 型 | 説明 |
|---|---|---|
| `source_id` | UUID | 保存されたソースのID |
| `detected_technologies` | string[] | 検出された技術名一覧 |
| `created_items` | UUID[] | 新規作成された技術カードのID一覧 |
| `updated_items` | UUID[] | 更新された技術カードのID一覧 |
| `summary` | string | ソースの種別とタイトル |

**注意**: LLM API呼び出しのため最大60秒かかります。

---

#### POST `/ingest/search`

**説明**: キーワードでGitHub・arXivを検索して技術情報を収集・保存します。

**認証**: 不要

**リクエスト**:
```json
{
  "query": "behavior tree NPC AI",
  "sources": ["web", "github"],
  "max_results": 20,
  "deep_analysis_limit": 3
}
```

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `query` | string | 必須 | 検索キーワード |
| `sources` | string[] | 任意 | デフォルト: `["web"]`。`"web"`, `"github"`, `"arxiv"` から選択。 |
| `max_results` | int | 任意 | 1〜100。デフォルト: 20 |
| `deep_analysis_limit` | int | 任意 | 0〜10。詳細解析するURLの最大数。デフォルト: 3 |

**レスポンス（成功）**: `200 OK`
```json
{
  "success": true,
  "data": {
    "collected_count": 5,
    "created_items": ["uuid1", "uuid2"],
    "updated_items": []
  },
  "error": null
}
```

---

#### POST `/ingest/memo`

**説明**: 手入力のメモ・テキストから技術カードを生成・保存します。

**認証**: 不要

**リクエスト**:
```json
{
  "memo": "Behavior TreeはゲームのNPC制御に使われる木構造の意思決定手法。スポンジの概念で構成されており、Compositeノード(Sequence/Selector)とLeafノード(Action/Condition)から成る。",
  "tags": ["game AI", "decision making"]
}
```

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `memo` | string | 必須 | 最小10文字 |
| `tags` | string[] | 任意 | 各50文字以内、最大20個 |

**レスポンス（成功）**: `200 OK`（`/ingest/url` と同形式）

---

### 検索

#### POST `/search/technologies`

**説明**: 技術名・課題文・分野でDB内の技術をハイブリッド検索します。

**認証**: 不要

**リクエスト**:
```json
{
  "query": "少ない試行回数で良い候補を見つけたい",
  "filters": {
    "domains": ["AI", "optimization"],
    "max_implementation_cost": "medium",
    "maturity_level": "mature",
    "item_types": ["algorithm", "technique"]
  },
  "mode": "problem_search",
  "limit": 10,
  "offset": 0
}
```

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `query` | string | 必須 | 最小1文字 |
| `filters` | object | 任意 | 絞り込み条件 |
| `filters.domains` | string[] | 任意 | ドメインフィルタ（AND条件） |
| `filters.max_implementation_cost` | `"low" \| "medium" \| "high"` | 任意 | 実装コストの上限 |
| `filters.maturity_level` | `"experimental" \| "emerging" \| "mature" \| "legacy"` | 任意 | 成熟度フィルタ |
| `filters.item_types` | string[] | 任意 | 技術種別フィルタ |
| `mode` | `"keyword" \| "problem_search" \| "domain" \| "condition"` | 任意 | デフォルト: `"keyword"` |
| `limit` | int | 任意 | 1〜100。デフォルト: 10 |
| `offset` | int | 任意 | 0以上。デフォルト: 0 |

**検索モード説明**:
| モード | 説明 |
|---|---|
| `keyword` | PostgreSQL全文検索（tsvector）。技術名・概要の完全/部分一致 |
| `problem_search` | pgvectorコサイン類似度検索。課題文の意味的マッチング |
| `domain` | ドメインフィールドによるフィルタ検索 |
| `condition` | `problem_search` と同様（ベクトル検索） |

**レスポンス（成功）**: `200 OK`
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "technology_id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "Bayesian Optimization",
        "fit_score": 0.8,
        "summary": "評価コストが高い探索空間での効率的な最適化手法",
        "why_relevant": "Matches query: 少ない試行回数で良い候補を見つけたい",
        "benefits": ["少試行回数で有望候補を発見できる"],
        "drawbacks": ["高次元空間では性能低下"],
        "alternatives": [],
        "domains": ["AI", "optimization"],
        "item_type": "algorithm",
        "maturity_level": "mature"
      }
    ],
    "total": 3,
    "query": "少ない試行回数で良い候補を見つけたい"
  },
  "error": null,
  "meta": { "page": 1, "total": 3 }
}
```

---

### 技術一覧

#### GET `/technologies`

**説明**: 登録済み技術の一覧をページング付きで取得します。

**認証**: 不要

**クエリパラメータ**:

| パラメータ | 型 | 必須 | 説明 |
|---|---|---|---|
| `limit` | int | 任意 | 1〜100。デフォルト: 10 |
| `offset` | int | 任意 | 0以上。デフォルト: 0 |
| `domain` | string | 任意 | ドメインフィルタ |
| `item_type` | string | 任意 | 種別フィルタ（例: `algorithm`） |
| `maturity_level` | string | 任意 | 成熟度フィルタ |
| `difficulty_level` | string | 任意 | 難易度フィルタ |

**例**:
```
GET /api/v1/technologies?limit=20&offset=0&domain=AI
```

**レスポンス（成功）**: `200 OK`
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "Behavior Tree",
        "item_type": "architecture_pattern",
        "summary": "複雑なNPC行動を階層的に記述する意思決定手法",
        "domains": ["game development", "robotics"],
        "maturity_level": "mature",
        "difficulty_level": "medium",
        "created_at": "2026-05-16T10:00:00Z",
        "updated_at": "2026-05-16T10:00:00Z"
      }
    ],
    "total": 42
  },
  "error": null,
  "meta": { "page": 1, "total": 42 }
}
```

---

#### GET `/technologies/{technology_id}`

**説明**: 技術カードの全詳細情報を取得します。

**認証**: 不要

**パスパラメータ**:

| パラメータ | 型 | 説明 |
|---|---|---|
| `technology_id` | UUID | 技術カードのID |

**レスポンス（成功）**: `200 OK`
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "Behavior Tree",
    "item_type": "architecture_pattern",
    "aliases": ["BT", "行動ツリー"],
    "summary": "複雑なNPC行動を階層的に記述する意思決定手法",
    "core_mechanism": "Composite/Leafノードによるツリー構造で行動を表現",
    "abstract_principle": "状態管理の階層化と再利用可能な行動モジュール化",
    "domains": ["game development", "robotics"],
    "categories": ["decision making"],
    "problem_structures": ["hierarchical decision making"],
    "purposes": [
      { "id": "uuid", "purpose": "NPC行動制御", "condition": "複雑な行動が必要な場合", "abstraction_level": "concrete" }
    ],
    "benefits": [
      { "id": "uuid", "benefit": "デバッグが容易", "condition": null, "confidence_score": 0.9 }
    ],
    "drawbacks": [
      { "id": "uuid", "drawback": "ツリーが大きくなると管理が複雑", "condition": "大規模プロジェクト", "severity": "medium", "confidence_score": 0.8 }
    ],
    "tradeoffs": [
      { "id": "uuid", "gain": "読みやすさ", "cost": "実行オーバーヘッド", "condition": null }
    ],
    "works_when": ["行動が階層的に分解できる場合"],
    "fails_when": ["リアクティブな即座の判断が必要な場合"],
    "avoid_when": ["極めてシンプルなAIで済む場合"],
    "relations": [
      { "id": "uuid", "relation_type": "alternative_to", "technology_id": "uuid2", "name": "FSM", "strength": 0.8 }
    ],
    "sources": [
      { "source_id": "uuid", "title": "Behavior Trees for AI", "url": "https://...", "source_type": "web_article" }
    ],
    "maturity_level": "mature",
    "difficulty_level": "medium",
    "cost_level": "low",
    "known_applications": ["Halo AI", "Unreal Engine"],
    "transfer_questions": ["この階層化の原理は他の意思決定問題に適用できるか？"],
    "created_at": "2026-05-16T10:00:00Z",
    "updated_at": "2026-05-16T10:00:00Z"
  },
  "error": null
}
```

**レスポンス（失敗）**: `404 Not Found`
```json
{
  "detail": "Technology not found"
}
```

---

### 比較

#### POST `/compare`

**説明**: 複数の技術を指定した評価軸でスコア比較します。

**認証**: 不要

**リクエスト**:
```json
{
  "technologies": ["FSM", "Behavior Tree", "GOAP"],
  "criteria": ["debuggability", "scalability", "implementation_cost", "maturity"]
}
```

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `technologies` | string[] | 必須 | 技術名のリスト。最小2件・最大10件。 |
| `criteria` | string[] | 任意 | デフォルト: `["debuggability", "scalability", "implementation_cost", "maturity"]` |

**レスポンス（成功）**: `200 OK`
```json
{
  "success": true,
  "data": {
    "comparison_table": [
      {
        "name": "FSM",
        "technology_id": "uuid1",
        "scores": { "debuggability": 0.9, "scalability": 0.4, "implementation_cost": 0.8, "maturity": 0.95 },
        "summary": "シンプルで実装容易だが、状態数が増えると複雑化"
      },
      {
        "name": "Behavior Tree",
        "technology_id": "uuid2",
        "scores": { "debuggability": 0.85, "scalability": 0.75, "implementation_cost": 0.6, "maturity": 0.9 },
        "summary": "階層化で大規模AIに対応できる"
      }
    ],
    "criteria": ["debuggability", "scalability", "implementation_cost", "maturity"],
    "recommendation": "複雑なNPCにはBehavior Treeを推奨"
  },
  "error": null
}
```

**レスポンス（失敗 — 技術がDBにない場合）**: `422 Unprocessable Entity`
```json
{
  "detail": "No technologies found in database"
}
```

---

### 推薦

#### POST `/recommend`

**説明**: 課題文と制約条件から最適な技術をベクトル検索で推薦します。

**認証**: 不要

**リクエスト**:
```json
{
  "problem_description": "研究論文から自動で仮説を生成し、根拠を追跡できるシステムを低コストで作りたい",
  "constraints": ["根拠を追跡したい", "低コストでMVPを作りたい"],
  "domains": ["AI", "NLP"],
  "limit": 5
}
```

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `problem_description` | string | 必須 | 最小10文字の課題・目標の説明 |
| `constraints` | string[] | 任意 | 制約条件一覧 |
| `domains` | string[] | 任意 | 検索対象ドメインの絞り込み |
| `limit` | int | 任意 | 1〜20。デフォルト: 5 |

**レスポンス（成功）**: `200 OK`
```json
{
  "success": true,
  "data": {
    "recommendations": [
      {
        "technology_id": "uuid",
        "name": "RAG (Retrieval-Augmented Generation)",
        "fit_score": 0.8,
        "reasoning": "Matches query: 研究論文から自動で仮説を生成し...",
        "implementation_suggestion": null
      }
    ],
    "problem_summary": "研究論文から自動で仮説を生成し、根拠を追跡できるシステムを低コストで作りたい"
  },
  "error": null
}
```

---

## `item_type` 値一覧

| 値 | 説明 |
|---|---|
| `technique` | 技法・手法 |
| `algorithm` | アルゴリズム |
| `architecture` | アーキテクチャ |
| `architecture_pattern` | アーキテクチャパターン |
| `design_pattern` | デザインパターン |
| `implementation_pattern` | 実装パターン |
| `tool` | ツール |
| `library` | ライブラリ |
| `framework` | フレームワーク |
| `protocol` | プロトコル |
| `evaluation_method` | 評価手法 |
| `method_family` | 手法ファミリー |

## `maturity_level` 値一覧

| 値 | 説明 |
|---|---|
| `experimental` | 実験的 |
| `emerging` | 新興 |
| `mature` | 成熟 |
| `legacy` | レガシー |
