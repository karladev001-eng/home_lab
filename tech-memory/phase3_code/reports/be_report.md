# バックエンド実装報告書

## 実装完了エンドポイント一覧

| Method | Path | 機能 | 実装ファイル |
|---|---|---|---|
| GET | /api/v1/health | ヘルスチェック（DB疎通確認含む） | `api/routers/health.py` |
| POST | /api/v1/ingest/url | URLから技術カードを生成・保存 | `api/routers/ingest.py` + `logic/collector/url_collector.py` |
| POST | /api/v1/ingest/search | キーワード検索収集（GitHub/arXiv） | `api/routers/ingest.py` + `logic/collector/search_collector.py` |
| POST | /api/v1/ingest/memo | メモから技術カード生成 | `api/routers/ingest.py` + `logic/collector/memo_collector.py` |
| POST | /api/v1/search/technologies | ハイブリッド技術検索 | `api/routers/search.py` + `logic/searcher/hybrid_search.py` |
| GET | /api/v1/technologies | 技術一覧（ページング） | `api/routers/technologies.py` |
| GET | /api/v1/technologies/{id} | 技術詳細（全関連データ付き） | `api/routers/technologies.py` |
| POST | /api/v1/compare | 複数技術の比較（LLMスコアリング） | `api/routers/compare.py` + `logic/searcher/compare_service.py` |
| POST | /api/v1/recommend | 課題・制約から推薦 | `api/routers/recommend.py` + `logic/searcher/recommend_service.py` |

## DBスキーマサマリー

| テーブル | 役割 | 主なインデックス |
|---|---|---|
| sources | 情報源（URL・論文・GitHub等） | canonical_url (unique partial), source_type, retrieved_at |
| technology_items | 技術・アルゴリズム等の主エンティティ | name_normalized (unique), embedding (ivfflat cosine), tsv (gin) |
| technology_purposes | 技術の目的（条件付き） | technology_id |
| technology_benefits | メリット（条件付き） | technology_id |
| technology_drawbacks | デメリット（条件付き・重大度付き） | technology_id |
| technology_tradeoffs | トレードオフ | technology_id |
| technology_conditions | works_when/fails_when/avoid_when | technology_id, condition_type |
| technology_relations | 技術間関係 | subject/object (unique pair+type) |
| use_cases | ユースケース（embedding付き） | embedding (ivfflat cosine) |
| use_case_technologies | ユースケース×技術マッピング | use_case_id, technology_id (unique pair) |
| evidence | 根拠（ソースへの参照） | source_id, technology_id |

## 実装上の決定事項

1. **埋め込みフォールバック**: OpenAI API失敗時はembedding=NULLで保存し、ベクトル検索失敗時はキーワード検索にフォールバック
2. **重複排除**: name_normalizedをUNIQUEキーとし、同名技術はupsertでマージ
3. **URL収集タイムアウト**: httpxの60秒タイムアウトで同期処理（MVP設計通り）
4. **Claude APIモデル選択**: lightモードはhaiku、standard/deepはsonnetを使用してコスト最適化
5. **tsvector**: マイグレーションで`ALTER TABLE`を使いpgvectorの`vector(1536)`型を設定（SQLAlchemyのORM定義と分離）

## テスト結果サマリー

| テストファイル | テスト数 | 内容 |
|---|---|---|
| `tests/test_schemas.py` | 7 | Pydanticスキーマのバリデーション検証 |
| `tests/test_health.py` | 1 | ヘルスエンドポイントの基本動作 |
| `tests/test_normalizer.py` | 5 | 技術名正規化ロジック |

注: DBを要するE2Eテストはdocker-compose環境での実行が前提（pytest-asyncioで対応済み）

## 未実装・既知の問題

- `tsv`カラムの自動更新トリガーは未設定（手動更新または定期バッチで対応予定）
- `technology_relations`の逆方向登録ロジックは未実装（BEからのみ参照）
- GitHub API認証トークン未設定時はレート制限あり
- compare_serviceのJSONパース処理は正規表現ベースのため、LLMレスポンス形式変化に注意
