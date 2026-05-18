# home_lab — Claude Code マルチエージェント集

Claude Code のサブエージェント機能を活用した自動化システムの集合リポジトリです。
各システムは独立したサブディレクトリに格納されており、全体クローンまたは個別クローンで利用できます。

---

## システム一覧

| システム | 説明 | 詳細ドキュメント |
| --- | --- | --- |
| アプリ自動生成 | アイデアから5フェーズでアプリを自動生成する21エージェントシステム | [`docs/app-dev.md`](docs/app-dev.md) |
| 技術収集・検索DB | URLから技術カードを自動生成し課題・分野・転用で検索できる知識DBシステム | [`docs/tech-memory.md`](docs/tech-memory.md) |
| 研究支援エージェント | 文献調査・コード実装・実験・スライド生成を専門サブエージェントに委譲する研究ワークフローシステム | [`docs/research-agents.md`](docs/research-agents.md) |

> **開発経緯・設計ドキュメント付きのバージョン**: [`dev` ブランチ](https://github.com/karladev001-eng/home_lab/tree/dev)

---

## クローン方法

```bash
git clone https://github.com/karladev001-eng/home_lab.git
cd home_lab
```

---

## home_lab から始める

このリポジトリを開いた Claude Code セッションから、以下のコマンドで各システムを起動できます。

| コマンド | 説明 |
| --- | --- |
| `/new-app <name>` | アプリ自動生成を開始する（scratch / 仕様書から / 中断再開） |
| `/new-research <name>` | 新しい研究プロジェクトをセットアップする（scratch / 仕様書から / 既存引き継ぎ） |

---

## 各システムの詳細

- **アプリ自動生成**: [「アプリ自動生成」セクション](#アプリ自動生成)を参照
- **技術収集・検索DB**: [`docs/tech-memory.md`](docs/tech-memory.md)
- **研究支援エージェント**: [「研究支援エージェント」セクション](#研究支援エージェント)を参照

---

## アプリ自動生成

アイデアを入力するだけで、21の専門エージェントが要件定義・設計・コード生成・テスト・ドキュメント生成まで自動実行する5フェーズシステムです。

詳細設計: [`docs/app-dev.md`](docs/app-dev.md)

### エージェント一覧

`.claude/agents/app-dev/` に格納されています（全21エージェント）。

| フェーズ | エージェント | 役割 |
| --- | --- | --- |
| 常駐 | `orchestrator` | 全体指揮・進捗管理・承認ゲート |
| Phase 1 | `phase1_idea_analysis` | アイデア解析・機能抽出 |
| Phase 1 | `phase1_requirements` | 要件定義・共有度判定 |
| Phase 1 | `phase1_tech_stack` | 技術スタック選定 |
| Phase 2 | `phase2_architecture` | アーキテクチャ設計 |
| Phase 2 | `phase2_data_model` | データモデル設計 |
| Phase 2 | `phase2_uiux` | UI/UX設計・ワイヤーフレーム |
| Phase 2 | `phase2_designer` | デザイントークン・モックアップ |
| Phase 3 | `phase3_shared_core_lead` | 共有コアのタスク管理 |
| Phase 3 | `phase3_be_lead` | バックエンドのタスク管理 |
| Phase 3 | `phase3_fe_lead` | フロントエンドのタスク管理 |
| Phase 3 | `phase3_coder` | コード実装（タスク単位） |
| Phase 3 | `phase3_debugger` | コード検証・修正指示 |
| Phase 3 | `phase3_optimizer` | 横断的最適化 |
| Phase 3 | `phase3_reporter` | コード仕様書生成 |
| Phase 4 | `phase4_test` | E2E・統合テスト |
| Phase 4 | `phase4_review` | セキュリティ・品質レビュー |
| Phase 4 | `phase4_integration` | BE/FE結合検証 |
| Phase 4 | `phase4_autofix` | 問題自動修正 |
| Phase 5 | `phase5_docs` | ドキュメント生成 |
| Phase 5 | `phase5_packaging` | ビルド・パッケージング |

### 新しいアプリプロジェクトの始め方

```bash
# home_lab で Claude Code を起動
cd home_lab
claude

# アプリ生成を開始（3つのモードから選択）
/new-app my-todo-app
```

`/new-app` を実行すると起動モードを選択できます。

| モード | 説明 |
| --- | --- |
| **Scratch** | アイデアを口頭で説明してゼロから生成 |
| **From spec** | 要件定義書・設計書・メモなどのファイルを読み込んで Phase 1 の入力にする |
| **Resume** | `pipeline_state.yaml` が残っている中断済みプロジェクトを再開する |

フラグで直接指定することもできます：
```bash
/new-app my-todo-app --from ~/docs/requirements.md
/new-app my-todo-app --resume ~/projects/my-todo-app
```

セットアップ後に自動で行われること:
- `~/projects/<name>/` にワークスペースを作成
- エージェント群をコピー
- `git init` と GitHub リポジトリ作成（任意）
- `orchestrator` エージェントを起動

以降は Phase 1 → 2 → 3 の各承認ゲートでフィードバックするだけで、コード生成・テスト・ドキュメントまで自動進行します。

### 前提条件

| ツール | 用途 |
| --- | --- |
| `gh` CLI（ログイン済み） | GitHub リポジトリ自動作成 |
| Node.js 20以上 + pnpm | 生成プロジェクトのビルド |
| `~/design_library/`（任意） | デザイナーエージェントの品質向上 |

---

## 研究支援エージェント

文献調査・コード実装・実験・スライド生成を専門サブエージェントに委譲しながら、Claude Code メインセッションを研究パートナーとして使い続けるためのワークフローシステムです。

詳細設計: [`docs/research-agents.md`](docs/research-agents.md)

### エージェント一覧

`.claude/agents/research/`, `.claude/agents/code/`, `.claude/agents/slides/` に格納されています。

| カテゴリ | エージェント | 役割 |
| --- | --- | --- |
| research | `research-state-loader` | セッション開始時に研究状態を読み込み `session-brief.md` を生成 |
| research | `literature-surveyor` | 文献検索・研究マップ作成・関連論文の優先順位付け |
| research | `paper-reader` | 論文・arXiv・PDFを読み、構造化された paper card を生成 |
| research | `result-analyst` | 実験結果・ログ・表を研究上の示唆へ変換 |
| research | `research-critic` | 仮説・主張・実験設計を査読者目線で批判的にレビュー |
| code | `code-manager` | 全コードファイルの統括・バージョン管理・スタイル維持・他エージェントへの委譲 |
| code | `code-implementer` | 新規実装（GitHub公式実装を優先）・スタイルガイド準拠 |
| code | `code-debugger` | バグ修正・pytestによる検証・デバッグ |
| code | `code-validator` | 実装した動作がユーザーの研究意図と合っているか自動検証 |
| code | `experiment-runner` | 実験実行・ログ要約・`registry.md` への記録 |
| slides | `template-style-extractor` | テンプレートや既存資料からHTML/スライド用スタイルガイドを抽出 |
| slides | `html-presentation-builder` | 研究内容から軽量なHTMLプレゼンページを生成 |
| slides | `html-consistency-reviewer` | HTMLプレゼンページと研究ファイルの内容整合性を検査 |
| slides | `html-style-reviewer` | HTMLプレゼンページのスタイル準拠と可読性を検査 |
| slides | `html-presentation-reviser` | HTMLプレゼンページの内容・見た目をレビュー結果に基づいて修正 |
| slides | `slide-deck-builder` | 必要時にHTMLまたは研究内容からMarpスライドを生成 |
| slides | `slide-consistency-reviewer` | スライドと研究ファイルの内容整合性を検査（書き込みなし） |
| slides | `slide-style-reviewer` | スライドとテンプレートのスタイル準拠を検査（書き込みなし） |
| slides | `slide-deck-reviser` | 内容レビュー結果に基づき主張・数値・制約表現を修正 |
| slides | `slide-style-reviser` | スタイルレビュー結果に基づき見た目・密度・階層を修正 |

### スラッシュコマンド一覧

`.claude/commands/` に格納されています。

| コマンド | 説明 |
| --- | --- |
| `/new-research <name>` | 新しい研究リポジトリをセットアップする |
| `/research-start` | セッション開始時に研究状態を読み込んで続きから再開する |
| `/research-sync` | セッション終了時に進捗・意思決定・次アクションを保存し、必要なら git commit / push する |
| `/make-presentation` | 研究内容から軽量なHTMLプレゼンページを生成し、内容・スタイルをレビューする |
| `/review-presentation` | 既存HTMLプレゼンページの内容整合性とスタイルをチェックする |
| `/revise-presentation` | HTMLプレゼンページを修正し、再レビューする |
| `/make-slides` | 必要時にHTMLプレゼンページまたは研究内容からMarpスライドを生成する |
| `/review-slides` | 既存スライドの内容整合性とスタイル整合性をチェックする |
| `/revise-slides` | レビュー結果を元にスライドを修正し、再レビューする |

### 新しい研究プロジェクトの始め方

```bash
# home_lab で Claude Code を起動
cd home_lab
claude

# コマンドを実行（3つのモードから選択）
/new-research my-research-2026
```

`/new-research` を実行すると起動モードを選択できます。

| モード | 説明 |
| --- | --- |
| **Scratch** | 空のテンプレートを生成してゼロから開始 |
| **From files** | 研究計画書・論文草稿・ノートなどを読み込んで研究ファイルを自動生成 |
| **Resume** | 既存の研究プロジェクトディレクトリを引き継いで継続 |

フラグで直接指定することもできます：

```bash
/new-research my-research-2026 --from ~/docs/research-proposal.md
/new-research my-research-2026 --resume ~/projects/old-research
```

以降は `cd my-research-2026 && claude` → `/research-start` で研究開始です。

`/new-research` は初期状態で共有テンプレートも取り込みます。

- HTML プレゼン雛形: [`templates/research/presentation/base/`](templates/research/presentation/base/)
- スライド雛形: [`templates/research/slides/marp/`](templates/research/slides/marp/)

また、初期化時に以下も行う想定です。

- `git init`
- 初期コミット作成
- 任意で `gh repo create ... --private --source=. --push`

### 典型的なセッションフロー

```
開始:        /research-start        ← 前回の状態を読み込む
研究中:      literature-surveyor / code-implementer / experiment-runner に委譲
共有用HTML:  /make-presentation     ← 軽量な成果共有ページを生成
必要時スライド: /make-slides         ← 発表提出が必要なときだけ生成
終了:        /research-sync         ← 進捗保存と必要な version 管理を行う
```

### コード実装原則（code-implementer）

- Python: 全関数に型アノテーション必須
- テスト: 新機能には必ず pytest を書く
- ファイル操作: `pathlib.Path` を使用
- 依存関係: `requirements.txt` または `pyproject.toml` に追記

### プロジェクト管理原則

- 研究プロジェクトはローカル Git で管理する
- 新規作成時に初期コミットを作る
- まとまりのあるコード変更は `code-manager` 主導でコミットする
- 実験結果は可能な限りコミットハッシュと一緒に `registry.md` に残す
- GitHub リモートがある場合は、節目ごとに push してバックアップする

### HTMLプレゼン生成原則（html-presentation-builder）

- 主成果物: `research/presentation/index.html`
- 構成: まず軽量な `HTML + CSS` を優先し、重いビルドは避ける
- 結果: `research/experiments/results/` の実ファイルから読む・捏造しない
- 不足: 未確認の図・数値は `TODO` で明示
- 優先順位: 研究内容の正確性 → 可読性 → テンプレート準拠 → 見た目
- 共有テンプレート置き場: [`templates/research/presentation/`](templates/research/presentation/)

### スライド生成原則（slide-deck-builder）

- フォーマット: Marp（`marp: true` フロントマター）
- 位置づけ: HTMLプレゼンページから必要な情報を凝縮する二次出力
- 結果: `research/experiments/results/` の実ファイルから読む・捏造しない
- 不足: 未確認の図・数値は `<!-- TODO -->` で明示
- 優先順位: 研究内容の正確性 → テンプレート準拠 → 読みやすさ → 見た目
- 共有テンプレート置き場: [`templates/research/slides/`](templates/research/slides/)

---

## ブランチ構成

| ブランチ | 内容 |
| --- | --- |
| `main` | 仕様書 + 実装コードのみ（クリーン版） |
| `dev` | 要件定義・設計書・QA報告書・成果物ドキュメントを含む開発版 |
