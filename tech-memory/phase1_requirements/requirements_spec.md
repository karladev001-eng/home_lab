# 要件定義書 — tech-memory

## 1. 機能要件

### 1.1 機能一覧

| 機能ID | 機能名 | 優先度 | 対象PF |
|---|---|---|---|
| F001 | URL収集 | MUST | web, api |
| F002 | 技術カード自動生成 | MUST | api |
| F003 | 技術名・課題・分野からの検索 | MUST | web, api |
| F004 | PostgreSQL + pgvector 検索基盤 | MUST | api |
| F005 | 技術カード詳細表示 | MUST | web |
| F006 | キーワード収集 | SHOULD | web, api |
| F007 | 技術比較 | SHOULD | web, api |
| F008 | 技術推薦 | SHOULD | web, api |
| F009 | 手入力メモからの技術カード生成 | SHOULD | web, api |
| F010 | 技術間関係の保存と表示 | SHOULD | web, api |
| F011 | 定期収集・スケジューラー | COULD | api |
| F012 | 抽象原理ベースの転用検索 | COULD | web, api |
| F013 | 技術グラフ可視化 | COULD | web |

### 1.2 API仕様（概要）

#### POST /api/ingest/url
- 概要: URLを入力し、技術カードを生成してDBに保存する
- 認証: 不要（MVP単一ユーザー前提）
- Request:
  ```json
  {
    "url": "https://example.com/article",
    "collection_mode": "standard",
    "tags": ["game AI"]
  }
  ```
- Response:
  ```json
  {
    "source_id": "uuid",
    "detected_technologies": ["Behavior Tree", "GOAP"],
    "created_items": ["uuid"],
    "updated_items": ["uuid"]
  }
  ```

#### POST /api/ingest/search
- 概要: キーワードで外部ソースを検索し収集する（SHOULD）
- Request: `{ "query": "behavior tree NPC AI", "sources": ["web", "github"], "max_results": 20 }`
- Response: 収集された技術カード一覧

#### POST /api/search/technologies
- 概要: 技術名・課題・分野でDB内を検索する
- Request:
  ```json
  {
    "query": "少ない試行回数で良い候補を見つけたい",
    "filters": { "domains": ["AI"], "max_implementation_cost": "medium" },
    "mode": "problem_search"
  }
  ```
- Response: `{ "results": [{ "technology_id": "uuid", "name": "...", "fit_score": 0.92, "summary": "...", ... }] }`

#### GET /api/technologies/{id}
- 概要: 技術カード詳細を取得する
- Response: 技術カード全フィールド（名前・概要・メカニズム・抽象原理・目的・メリット・デメリット・条件・関係技術・ソース）

#### POST /api/compare
- 概要: 複数技術を比較する（SHOULD）
- Request: `{ "technologies": ["FSM", "Behavior Tree", "GOAP"], "criteria": ["debuggability", "scalability"] }`

#### POST /api/recommend
- 概要: 課題・制約から技術を推薦する（SHOULD）
- Request: `{ "goal": "...", "constraints": ["低コスト", "実装容易"] }`

### 1.3 画面一覧

| 画面名 | 目的 | 遷移元 | 遷移先 |
|---|---|---|---|
| 検索トップ | 技術名・課題・分野で検索 | ー | 検索結果一覧 |
| 検索結果一覧 | 検索結果のカード一覧表示 | 検索トップ | 技術詳細 |
| 技術詳細 | 技術カードの全情報を表示 | 検索結果一覧 | 関連技術詳細 |
| 収集（URL入力） | URLを入力して技術カードを生成 | ナビ | 収集結果確認 |
| 収集結果確認 | 生成された技術カードのプレビュー | 収集 | 技術詳細 |
| 技術比較 | 複数技術のメリット・デメリット比較 | 検索結果一覧 | ー |

### 1.4 バリデーションルール

- URL: `http://` または `https://` で始まること。1000文字以内。
- 検索クエリ: 1文字以上、1000文字以内
- tags: 各タグは50文字以内、最大20タグ
- collection_mode: `light | standard | deep` のいずれか（デフォルト: `standard`）
- 技術カード: `name` は必須・500文字以内。`summary` は2000文字以内。

---

## 2. 非機能要件

| 項目 | 目標値 | 根拠 |
|---|---|---|
| レスポンスタイム（検索） | 想定: 2秒以内 | ユーザー体験として許容できる上限 |
| レスポンスタイム（収集） | 想定: 30秒以内 | LLM API呼び出し含むため長め |
| 同時接続数 | 想定: 1〜5（MVP・個人利用） | シングルユーザー前提 |
| 可用性 | 想定: ベストエフォート（個人用途） | MVP段階 |
| セキュリティ | 認証なし（MVP）、将来的にAPIキー認証 | 個人利用前提 |
| データ保護 | 著作権上問題のある全文は保存しない | 仕様書16.1節に基づく |
| スケーラビリティ | 想定: 数百〜数千件の技術カード | MVP段階 |
| アクセシビリティ | WCAG 2.1 AA準拠（推奨） | Web前提 |
| Docker対応 | Docker Composeでの起動必須 | インフラ要件 |

---

## 3. 制約条件

### 技術的制約

- バックエンドはPython + FastAPIを使用する（仕様書推奨）
- データベースはPostgreSQL + pgvectorを使用する
- フロントエンドはNext.js + Tailwind CSSを使用する
- コンテナはDocker Composeで管理する
- 外部コンテンツの全文保存は禁止（仕様書16.1節）
- 著作権上問題のある出版社PDFのコピー保存は禁止
- pip install・Python仮想環境は不使用（Docker管理）

### ビジネス制約

- MVPはPhase 1スコープ（URL収集・技術カード生成・検索・詳細表示）に限定する
- 認証・マルチユーザーはMVPスコープ外
- 定期収集・大規模クローリングはMVPスコープ外

---

## 4. 用語定義

| 用語 | 定義 |
|---|---|
| 技術カード | 1つの技術・アルゴリズム・設計パターン・ツールを表す構造化データ |
| 抽象原理 | 技術の分野を超えて再利用可能なメカニズムの抽象表現 |
| 中核メカニズム | 技術の本質的な動作原理 |
| 成立条件 (works_when) | その技術が有効に機能する条件 |
| 失敗条件 (fails_when) | その技術が機能しなくなる条件 |
| ソース (Source) | 技術情報の情報源（URL・論文・GitHub等） |
| fit_score | ユーザーの課題・制約に対する技術の適合度スコア（0〜1） |
| embedding | テキストの意味的表現ベクトル（pgvector使用） |
| ingest | URLやキーワードから技術情報を収集してDBに保存するプロセス |
| collection_mode | 収集の深さ（light: メタデータのみ / standard: 要約付き / deep: 詳細抽出） |
