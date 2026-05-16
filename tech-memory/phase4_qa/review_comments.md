# コードレビュー指摘一覧

## 実行日時: 2026-05-16T12:30:00+09:00

## 指摘サマリー

- Critical: 0件
- Warning: 3件
- Info: 5件

---

## Critical 指摘（必須修正）

*Critical指摘なし*

- SQLインジェクション: SQLAlchemyのORMを正しく使用しており、プリペアドステートメントが適用されている
- XSS: フロントエンドでdangerouslySetInnerHTMLの使用なし
- ハードコードシークレット: 全APIキーは環境変数経由（`api/config.py`で`pydantic-settings`）
- 認証: MVP仕様として認証なしが要件定義書に明記済み
- パスワード平文保存: 認証機能未実装のため該当なし

---

## Warning 指摘（推奨修正）

### [W-001] N+1クエリ: `_build_results`でループ内DB実行

- **場所**: `backend/logic/searcher/hybrid_search.py:150-163`
- **問題**: 検索結果の各技術アイテムに対してループ内でbenefitsとdrawbacksの2クエリを発行している。10件の検索結果で最大20クエリが発生する。
  ```python
  for item in items:
      benefits_result = await db.execute(  # N+1
          select(TechnologyBenefit).where(...)
      )
      drawbacks_result = await db.execute(  # N+1
          select(TechnologyDrawback).where(...)
      )
  ```
- **修正方法**: 検索時に `selectinload(TechnologyItem.benefits, TechnologyItem.drawbacks)` を使用してeager loadingを行う、または `WHERE technology_id IN (...)` で一括取得する。
- **影響**: 検索レスポンス時間（現在2秒目標に対して高負荷時に超過リスク）

### [W-002] `compare_service.py`でループ内DB実行（resolve時）

- **場所**: `backend/logic/searcher/compare_service.py:23-36`
- **問題**: 比較技術名のリストをループで1件ずつDB検索している。
  ```python
  for name in technologies:
      result = await db.execute(...)  # N+1
  ```
- **修正方法**: `WHERE name_normalized IN (...)` で一括取得して後でマッピングする。
- **影響**: 比較技術数が10件の場合、最大10クエリが発生する。

### [W-003] `technologies.py`のevidenceローディングに未実装プレースホルダー

- **場所**: `backend/api/routers/technologies.py:99-103`
- **問題**: `evidence_list`のsource relationship loadingが`type(None)`プレースホルダーのままで、sourceデータが実際にはeager loadされない可能性がある。
  ```python
  selectinload(TechnologyItem.evidence_list).selectinload(
      type(None)  # placeholder
  ),
  ```
- **修正方法**: `type(None)` を `Evidence.source` に置き換える。
  ```python
  selectinload(TechnologyItem.evidence_list).selectinload(Evidence.source),
  ```
  （`Evidence`をインポートする必要あり）
- **影響**: `ev.source` へのアクセス時にN+1または`AttributeError`が発生する可能性がある。

---

## Info 指摘（任意）

### [I-001] `fit_score`が固定値0.8

- **場所**: `backend/logic/searcher/hybrid_search.py:171`
- **内容**: keyword検索の場合、fit_scoreが常に0.8の固定値。実際のtf-idfスコアや類似度スコアを使うと精度が向上する。
- **対応**: 将来の改善事項として記録。MVP段階では許容範囲内。

### [I-002] CORS設定がlocalhostのみ

- **場所**: `backend/api/main.py:27`
- **内容**: `allow_origins=["http://localhost:3000"]` のみ許可。本番環境URLをデプロイ時に環境変数で設定できるよう改善を推奨。
  ```python
  # 推奨
  allow_origins=settings.ALLOWED_ORIGINS.split(",")
  ```
- **対応**: 本番デプロイ時に対応要。

### [I-003] 構造化ログの未使用

- **場所**: 全バックエンドファイル
- **内容**: `logging`モジュールが未使用で、エラー情報が構造化されていない。FastAPIの内部エラーログのみ。本番運用では`structlog`や`loguru`の導入を推奨。
- **対応**: MVP段階では許容範囲内。

### [I-004] `_fetch_web`でlxmlパーサーを使用（要インストール確認）

- **場所**: `backend/logic/collector/url_collector.py:145`
- **内容**: `BeautifulSoup(resp.text, "lxml")` はlxmlがインストールされていない場合エラーになる。`requirements.txt`に`lxml`が記載されているかを確認要。
- **対応**: requirements.txtの確認のみでよい。

### [I-005] `collect_url`でDB commit漏れリスク

- **場所**: `backend/logic/collector/url_collector.py:59-82`
- **内容**: `db.flush()`を使用しているが、ロジック側では`commit()`を呼んでいない。`db.session.get_db()`のfinally節でcommitが行われる設計のため、例外が発生した場合にロールバックされる正しい設計になっている。ただし、途中でflushされたデータが例外後に残る可能性を確認推奨。
- **対応**: 現設計は正しい。追加確認のみ推奨。

---

## セキュリティチェックリスト

| 確認項目 | 状態 | 備考 |
|---|---|---|
| SQLインジェクション対策 | OK | SQLAlchemy ORM使用 |
| XSS対策 | OK | dangerouslySetInnerHTML未使用 |
| CSRF対策 | N/A | 認証なし（MVP仕様） |
| 認証・認可チェック | N/A | MVP単一ユーザー前提（要件定義書§2） |
| パスワードハッシュ化 | N/A | 認証機能未実装 |
| センシティブ情報のログ出力禁止 | OK | ログ出力なし |
| 環境変数でシークレット管理 | OK | pydantic-settingsで管理 |
| HTTPS強制設定 | N/A | Docker/インフラ層で対応（MVP外） |

## パフォーマンスチェックリスト

| 確認項目 | 状態 | 備考 |
|---|---|---|
| DBクエリのN+1問題 | WARNING | W-001, W-002参照 |
| インデックスの適切な設定 | OK | 001_initial_schema.pyにインデックス定義あり |
| 不要なデータの取得（SELECT *） | OK | ORM経由で必要フィールドのみ |
| キャッシュ戦略 | N/A | MVP段階 |
| 大量データのページネーション | OK | limit/offsetが全エンドポイントに実装済み |

## ベストプラクティスチェックリスト

| 確認項目 | 状態 | 備考 |
|---|---|---|
| エラーハンドリングの一貫性 | OK | 全ルーターでtry/except+HTTPException |
| ログ出力の適切さ | INFO | 構造化ログ未使用（I-003参照） |
| 環境変数のバリデーション | OK | pydantic-settingsで型検証 |
| TypeScript型の適切な使用 | OK | anyの不使用、型安全なAPIクライアント |
| APIレスポンスの一貫性 | OK | ApiResponse[T]で全エンドポイント統一 |
