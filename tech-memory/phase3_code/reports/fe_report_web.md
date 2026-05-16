# フロントエンド実装報告書 (web)

## 実装完了

### 実装画面一覧

| 画面ID | 画面名 | 実装パス | 備考 |
|---|---|---|---|
| SCR001 | 検索トップ | `frontend/web/src/app/page.tsx` | SearchBarコンポーネント + ヒーローセクション |
| SCR002 | 検索結果一覧 | `frontend/web/src/app/search/page.tsx` | TechCardリスト + フィルタ（URLパラメータ） |
| SCR003 | 技術詳細 | `frontend/web/src/app/technologies/[id]/page.tsx` | 全情報 + 条件付きメリット/デメリット/トレードオフ + 関係技術 |
| SCR004 | 技術一覧 | `frontend/web/src/app/technologies/page.tsx` | ページング対応リスト |
| SCR005 | URL収集 | `frontend/web/src/app/ingest/page.tsx` | タブ（URL/検索収集/メモ）+ 収集モード選択 |
| SCR007 | 技術比較 | `frontend/web/src/app/compare/page.tsx` | 複数技術の評価軸別スコア表 + 推薦 |

### コンポーネント一覧

| コンポーネント | パス | 説明 |
|---|---|---|
| Header | `components/layout/Header.tsx` | ナビゲーションバー（固定ヘッダー） |
| TechCard | `components/tech/TechCard.tsx` | 検索結果の技術カード表示 |
| SearchBar | `components/tech/SearchBar.tsx` | 検索モードタブ + 入力フォーム + 例示クエリ |
| Badge | `components/ui/Badge.tsx` | 汎用バッジコンポーネント |
| FitScoreBadge | `components/ui/FitScoreBadge.tsx` | 適合度スコア表示バッジ |
| LoadingSpinner | `components/ui/LoadingSpinner.tsx` | ローディングインジケータ |

### 設定ファイル

| ファイル | 内容 |
|---|---|
| `tailwind.config.ts` | デザイントークン反映済みTailwind設定 |
| `next.config.ts` | APIプロキシ設定（/api/* → バックエンド） |
| `src/app/globals.css` | グローバルスタイル（card, badge, btn-primary等のユーティリティクラス） |
| `src/lib/api-client.ts` | 型安全APIクライアント（全エンドポイント対応） |
| `src/lib/utils.ts` | cn(), formatDate(), ラベルマッピング等 |

### ビルド結果

Docker Compose経由で実行可能。Next.js 15 App Routerベース。
`pnpm dev` で開発サーバー起動（ポート3000）。

### デザイントークン準拠チェック結果

- カラー: `#6366f1`（primary-500）、`#0f172a`（neutral-900）をtailwind.config.tsに反映済み
- フォント: Inter + Noto Sans JPをfont-sansとして設定
- ダークモード: デフォルトdarkクラス付きで全ページダーク表示
- コンポーネントトークン: nav-height(56px)、max-content-width(900px)適用済み

### 未実装・既知の課題

- SCR006（技術推薦画面）は /recommend APIは実装済みだが、専用UIページは未実装（比較ページで代替可）
- 認証なし（MVP設計通り）
- ページネーションUI（nextページボタン等）は未実装（APIは対応済み）
- モバイル最適化は基本レスポンシブのみ
