# 統合検証レポート

## 実行日時: 2026-05-16T13:00:00+09:00

---

## 1. API インターフェース整合性

### 整合しているエンドポイント

| Method | Path | BE実装 | FE使用 | 判定 |
|---|---|---|---|---|
| GET | /api/v1/health | health.py | api.health() | OK |
| POST | /api/v1/ingest/url | ingest.py | api.ingest.url() | OK |
| POST | /api/v1/ingest/search | ingest.py | api.ingest.search() | OK |
| POST | /api/v1/ingest/memo | ingest.py | api.ingest.memo() | OK |
| POST | /api/v1/search/technologies | search.py | api.search.technologies() | OK |
| GET | /api/v1/technologies | technologies.py | api.technologies.list() | OK |
| GET | /api/v1/technologies/{id} | technologies.py | api.technologies.get(id) | OK |
| POST | /api/v1/compare | compare.py | api.compare() | OK |
| POST | /api/v1/recommend | recommend.py | 未使用（推薦画面未実装）| INFO |

**注記**: `/api/v1/recommend`はBEに実装済みだが、フロントエンドにSCR006（推薦専用画面）が未実装。
エンドポイント自体は存在するため機能的には問題なし。final_code_spec.md §8に記載済み。

### 不整合・問題

| 問題 | 詳細 | 重要度 |
|---|---|---|
| shared_core型未使用 | FEがshared_core/typesを参照せず、api-client.tsで独自に型定義 | WARNING |
| recommend画面未実装 | /api/v1/recommendは実装済みだが対応するUIがない | INFO |

---

## 2. 型定義整合性

### FE独自型定義とBEスキーマの比較

FEは`shared_core/types/`を使用せず、`api-client.ts`で独自型を定義している。
以下、BEのPydanticスキーマとFE型の手動比較結果:

| 型名 | BE (schemas.py) | FE (api-client.ts) | 整合性 |
|---|---|---|---|
| ApiResponse | `success: bool, data: T\|None, error: str\|None` | `success: boolean, data: T\|null, error: string\|null` | OK |
| IngestUrlRequest | `url, collection_mode, tags` | `url, collection_mode?, tags?` | OK |
| IngestUrlResponseData | `source_id, detected_technologies, created_items, updated_items, summary` | 同様 | OK |
| SearchTechnologiesRequest | `query, filters?, mode, limit, offset` | `query, filters?, mode?, limit?` | OK（optionalの違いのみ） |
| TechnologySearchResult | `technology_id, name, fit_score, summary, why_relevant, benefits, drawbacks, alternatives, domains, item_type, maturity_level` | 同様（TechnologySearchResult） | OK |
| TechnologiesListResponseData | `items: TechnologyListItem[], total: int` | `items: TechnologyListItem[], total: number` | OK |
| CompareRequest | `technologies: list[str] (min=2,max=10), criteria?` | `technologies: string[], criteria?` | OK（min/maxはBE側バリデーション） |
| RecommendRequest | `problem_description (min_length=10), constraints?, domains?, limit` | `problem_description, constraints?, domains?, limit?` | OK |

**shared_core未使用の詳細:**
- `shared_core/types/`はAPIリクエスト/レスポンス型を包括的に定義している
- FEの`api-client.ts`は独自型定義だが、内容はshared_coreと整合している
- 将来的にはFEが`@repo/types`を参照することで型定義の一元管理が可能
- MVP段階では機能的問題なし

---

## 3. 認証フロー整合性

| 確認項目 | 状態 | 備考 |
|---|---|---|
| BE認証ミドルウェア | N/A | 認証なし（MVP仕様：要件定義書§2） |
| FEトークン送信 | N/A | 認証なし |
| 401エラーハンドリング | N/A | 認証なし |
| Authorization ヘッダー使用 | N/A | 不使用 |

認証・認可は要件定義書§2で「MVPスコープ外」として明示済み。

---

## 4. プラットフォーム間一貫性

### 対象プラットフォーム（project_config.yaml）

project_config.yamlより対象PF: `web, api`
（mobile/desktopは非対象）

| 確認項目 | Web | API | 判定 |
|---|---|---|---|
| 同一BEエンドポイント使用 | OK (localhost:8000) | — | OK |
| 環境変数経由のAPI URL設定 | OK (NEXT_PUBLIC_API_URL) | — | OK |
| APIレスポンス形式の一貫性 | OK (ApiResponse[T]) | OK (ApiResponse[T]) | OK |

---

## 5. 環境変数の整合性

`.env.example`記載の環境変数と各アプリの使用状況:

| 変数名 | .env.example | BE (config.py) | FE (next.config.ts/.env) | 整合性 |
|---|---|---|---|---|
| DATABASE_URL | あり | あり（Settings） | N/A | OK |
| ANTHROPIC_API_KEY | あり | あり（Settings） | N/A | OK |
| OPENAI_API_KEY | あり | あり（Settings） | N/A | OK |
| APP_ENV | あり | あり（Settings） | N/A | OK |
| LOG_LEVEL | あり | あり（Settings） | N/A | OK |
| NEXT_PUBLIC_API_URL | あり | N/A | あり（next.config.ts） | OK |
| POSTGRES_USER/PASSWORD/DB | あり（docker用） | N/A（DATABASE_URL使用） | N/A | OK |

---

## 6. APIプロキシ設定の整合性

FE（Next.js）のAPIプロキシ設定:
- `next.config.ts`: `/api/:path*` → `${NEXT_PUBLIC_API_URL}/api/:path*`
- BEのポート: 8000（docker-compose.yml確認）
- CORS設定: BE側が`http://localhost:3000`を許可（FEのポート）

**整合確認**: FE（:3000）からBE（:8000）へのプロキシが適切に設定されている。

---

## 7. 総合判定

**PASS**

全MUST機能のBE/FE整合性が確認できた。
Warning事項は機能的問題ではなく、コード品質・将来拡張に関わる事項のみ。

### 確認済み整合項目

- BE APIエンドポイント9件のうち8件がFEで使用済み（/recommendのみ未使用画面だが機能は実装済み）
- FE型定義はBEスキーマと実質的に一致（手動定義だがshared_coreと整合）
- 環境変数設定が.env.exampleに全項目網羅
- APIプロキシ設定が正しくBEに向いている
- Docker Compose設定でBE/FE/DBのネットワークが適切に定義

### 要確認事項（Docker起動後）

1. `docker-compose up -d` 後に `/api/v1/health` のレスポンスが `{ "status": "ok", "db": "ok" }` を返すことを確認
2. alembic migrate後にpgvectorエクステンションが有効化されていることを確認
3. `POST /api/v1/ingest/url` でArXiv URLを使用した実際の技術カード生成フローの動作確認

### 不整合事項（修正推奨）

| 問題ID | 内容 | 重要度 | 修正担当 |
|---|---|---|---|
| INT-001 | shared_core/typesがFEで未使用（独自定義） | WARNING | 将来改善 |
| INT-002 | /recommend エンドポイントに対応するFE画面なし | INFO | 将来実装 |
| INT-003 | W-003: evidence_listのsource eager loading未設定 | WARNING | phase4_autofix |
