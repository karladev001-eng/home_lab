# アプリ自動生成システム

マルチエージェントオーケストレーションによるアプリ自動生成システム。ユーザーがアイデアを入力すると、21の専門エージェントが協調して要件定義からデプロイ準備まで自動実行する。

## 使い方

ユーザーがアプリのアイデアを話したら、まず以下の情報を収集し、`orchestrator` エージェントを起動する。

収集する情報:
1. **プロジェクト名** — 英数字とハイフンのみ（例: `my-todo-app`）
2. **アプリのアイデア** — 何を作りたいかの自然言語説明
3. **対象プラットフォーム** — `web` / `mobile` / `desktop` / `api`（複数選択可）

orchestratorへの起動プロンプト例:
```
PROJECT_NAME: my-todo-app
PLATFORMS: web,mobile
IDEA: チームでタスクを共有できるTodoアプリ。リアルタイム同期・優先度設定・期限通知機能を持つ。
```

## 前提条件

- `gh` CLI がログイン済みであること（GitHub連携のため）
- `~/design_library/` にデザイン参考画像・テーマを事前配置しておくと、デザイナーエージェントの品質が向上する

## エージェント一覧

| エージェント | フェーズ | 役割 |
|---|---|---|
| orchestrator | 常駐 | 全体指揮・進捗管理・承認ゲート |
| phase1_idea_analysis | Phase 1 | アイデア解析・機能抽出 |
| phase1_requirements | Phase 1 | 要件定義・共有度判定 |
| phase1_tech_stack | Phase 1 | 技術スタック選定 |
| phase2_architecture | Phase 2 | アーキテクチャ設計 |
| phase2_data_model | Phase 2 | データモデル設計 |
| phase2_uiux | Phase 2 | UI/UX設計・ワイヤーフレーム |
| phase2_designer | Phase 2 | デザイントークン・モックアップ |
| phase3_shared_core_lead | Phase 3 | 共有コアのタスク管理 |
| phase3_be_lead | Phase 3 | バックエンドのタスク管理 |
| phase3_fe_lead | Phase 3 | フロントエンドのタスク管理 |
| phase3_coder | Phase 3 | コード実装（タスク単位） |
| phase3_debugger | Phase 3 | コード検証・修正指示 |
| phase3_optimizer | Phase 3 | 横断的最適化 |
| phase3_reporter | Phase 3 | コード仕様書生成 |
| phase4_test | Phase 4 | E2E・統合テスト |
| phase4_review | Phase 4 | セキュリティ・品質レビュー |
| phase4_integration | Phase 4 | BE/FE結合検証 |
| phase4_autofix | Phase 4 | 問題自動修正 |
| phase5_docs | Phase 5 | ドキュメント生成 |
| phase5_packaging | Phase 5 | ビルド・パッケージング |

## ワークスペース構造

各プロジェクトは `~/projects/{project_name}/` に生成される。
