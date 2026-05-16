# tech-memory — ドキュメントインデックス

> ここに生成された全ドキュメントへのリンクをまとめます。

## 進捗状況

- [x] Phase 1: 要件分析
- [x] Phase 2: 設計
- [x] Phase 3: コード生成
- [x] Phase 4: 品質保証
- [x] Phase 5: 成果物生成

## ドキュメント一覧

## Phase 1 — 要件分析

| ドキュメント | 内容 |
|---|---|
| [idea_analysis.json](phase1_requirements/idea_analysis.json) | 機能一覧・ユースケース・優先度 |
| [requirements_spec.md](phase1_requirements/requirements_spec.md) | 機能要件・非機能要件・制約条件 |
| [tech_stack.yaml](phase1_requirements/tech_stack.yaml) | 採用技術と選定理由 |
| [sharing_strategy.yaml](phase1_requirements/sharing_strategy.yaml) | PF間の共有・分離方針 |
| [phase1_gate_summary.md](phase1_requirements/phase1_gate_summary.md) | Phase 1 承認ゲートサマリー |

## Phase 2 — 設計

| ドキュメント | 内容 |
|---|---|
| [architecture.md](phase2_design/architecture.md) | 構成図・APIエンドポイント定義・認証方式・Docker Compose |
| [data_model.json](phase2_design/data_model.json) | 11テーブルのER設計・インデックス戦略・マイグレーション方針 |
| [screen_flow.md](phase2_design/ui_ux/screen_flow.md) | 7画面の遷移図・PF別UI方針 |
| [wireframes/](phase2_design/ui_ux/wireframes/) | 全7画面のASCIIワイヤーフレーム |
| [design_tokens.json](phase2_design/design/design_tokens.json) | カラー・タイポグラフィ・スペーシングのデザイントークン |
| [mockups/](phase2_design/design/mockups/) | HTML/CSSモックアップ（5画面） |
| [phase2_gate_summary.md](phase2_design/phase2_gate_summary.md) | Phase 2 承認ゲートサマリー |

## Phase 3 — コード生成

| ドキュメント | 内容 |
|---|---|
| [be_report.md](phase3_code/reports/be_report.md) | バックエンド実装状況・API実装報告 |
| [fe_report.md](phase3_code/reports/fe_report.md) | フロントエンド実装状況・デザイン適合 |
| [final_code_spec.md](phase3_code/reports/final_code_spec.md) | ファイル構成・API一覧・依存関係・起動方法 |
| [backend/](phase3_code/backend/) | FastAPI バックエンド実装 |
| [frontend/web/](phase3_code/frontend/web/) | Next.js フロントエンド実装 |
| [shared_core/](phase3_code/shared_core/) | 共有型定義・定数 |
| [docker-compose.yml](phase3_code/docker-compose.yml) | 全サービス定義（db/api/web） |

## Phase 4 — 品質保証

| ドキュメント | 内容 |
|---|---|
| [test_results/results.md](phase4_qa/test_results/results.md) | ユニットテスト13件・API結合テスト24件の実行結果（全PASS） |
| [test_results/api/test_api_integration.py](phase4_qa/test_results/api/test_api_integration.py) | Phase 4生成の結合テストスイート（24ケース） |
| [review_comments.md](phase4_qa/review_comments.md) | セキュリティ・パフォーマンス・品質レビュー（Critical 0件・Warning 3件） |
| [integration_report.md](phase4_qa/integration_report.md) | BE/FE結合・型整合性・環境変数の統合検証（PASS） |
| [autofix_log.md](phase4_qa/autofix_log.md) | W-003自動修正（Evidence.sourceのeager loading修正）ログ |

## Phase 5 — 成果物生成

| ドキュメント | 内容 |
|---|---|
| [README.md](phase5_output/docs/README.md) | セットアップ〜使い方の完全ガイド（ステップ1〜5で起動） |
| [API.md](phase5_output/docs/API.md) | 全エンドポイント（9件）の詳細仕様・リクエスト/レスポンス例 |
| [DEPLOY.md](phase5_output/docs/DEPLOY.md) | VPS/本番環境へのデプロイ手順・Nginx設定・バックアップ |
| [packages/api/Dockerfile](phase5_output/packages/api/Dockerfile) | API本番用マルチステージDockerfile |
| [packages/docker-compose.yml](phase5_output/packages/docker-compose.yml) | 本番用Docker Compose設定 |
| [packages/PACKAGING_REPORT.md](phase5_output/packages/PACKAGING_REPORT.md) | パッケージングレポート・チェックリスト |

---

**すべてのフェーズが完了しました。**
