# Phase 1 承認ゲートサマリー

## プロジェクト
- 名前: tech-memory
- プラットフォーム: web, api

## 主要機能（MUST）
- URL収集: URLを入力するとWeb記事・arXiv・GitHub READMEから技術情報を収集・保存
- 技術カード自動生成: LLM structured outputで技術名・概要・メカニズム・メリット・デメリット・条件を抽出
- 技術名・課題・分野からの検索: キーワード検索 + pgvectorによる意味的検索のハイブリッド
- PostgreSQL + pgvector 検索基盤: 全検索をPostgreSQL + pgvectorで完結させる（別途ベクトルDB不要）
- 技術カード詳細表示: 技術の全情報（原理・条件・関係技術・ソース）をWebで表示

## 技術スタック
- BE: Python 3.12 + FastAPI + PostgreSQL 16 + pgvector → Docker Compose
- AI: Anthropic Claude API（structured output）+ OpenAI text-embedding-3-small
- FE(Web): Next.js 15 (App Router) + Tailwind CSS + shadcn/ui

## 補完した仮定（ユーザー確認推奨）
- 認証・マルチユーザーはMVPスコープ外（シングルユーザー前提）
- embeddingモデルはOpenAI text-embedding-3-smallを想定（変更可能）
- LLMはClaude APIを主とし、structured outputで技術カードをJSON直接生成する
- 定期収集（スケジューラー）はPhase 1スコープ外

## 詳細ファイル
- phase1_requirements/requirements_spec.md
- phase1_requirements/tech_stack.yaml
- phase1_requirements/idea_analysis.json
- phase1_requirements/sharing_strategy.yaml
