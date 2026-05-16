# Tech Memory

技術・アルゴリズム・設計パターン・ツールを収集・構造化・検索する知識DBシステム。

URLを入力するだけで技術カードを自動生成し、課題・分野・技術名からハイブリッド検索できる。

## 特徴

- **技術中心の設計**: 文書ではなく技術そのものを構造化して保存
- **抽象原理の抽出**: 分野を超えた横断検索・転用提案が可能
- **条件つきメリット/デメリット**: 「どんな状況で効くか」まで保存
- **LLM切り替え可能**: Claude / OpenAI を環境変数で選択
- **ハイブリッド検索**: キーワード + ベクトル + LLMリランキング
- **英日両対応**: 日本語コンテンツも収集・検索対象

## 対応ソース

| ソース | 収集内容 |
|---|---|
| Web記事 | Zenn / Qiita / Medium / 技術ブログ |
| arXiv | 論文アブストラクト・タイトル |
| GitHub | リポジトリ説明・README |
| 公式ドキュメント | フレームワーク・クラウドサービス等 |

## 検索モード

| モード | 説明 | 例 |
|---|---|---|
| 技術名検索 | 名前・別名から検索 | `RAG`, `Behavior Tree` |
| 課題検索 | 解決したい問題から検索 | `少ない試行回数で良い候補を見つけたい` |
| 分野検索 | 特定分野の技術一覧 | `game development` |
| 転用検索 | 他分野への応用候補を探す | `ゲーム開発の技術をAIエージェントに応用` |

## 必要環境

- Docker Compose v2
- OpenAI API Key（埋め込み用。LLM抽出にも使用可）
- または Anthropic API Key（LLM抽出のみ。埋め込みは別途必要）

## セットアップ

```bash
git clone <this-repo>
cd tech-memory

cp .env.example .env
# .env を編集して API キーを設定
```

`.env` の最小設定:

```env
LLM_PROVIDER=openai          # claude または openai
OPENAI_API_KEY=sk-...        # OpenAI を使う場合
ANTHROPIC_API_KEY=sk-ant-... # Claude を使う場合
EMBEDDING_PROVIDER=openai    # 埋め込みは現状 openai のみ
```

```bash
docker compose up --build
```

| サービス | URL |
|---|---|
| Web UI | http://localhost:3000 |
| API | http://localhost:8000 |
| API ドキュメント | http://localhost:8000/docs |

## 使い方

### 技術を収集する

1. http://localhost:3000/ingest を開く
2. URL を入力（arXiv / GitHub / 技術記事 など）
3. 「収集する」をクリック
4. 自動で技術カードが生成されDBに保存される

### 技術を検索する

1. http://localhost:3000/search を開く
2. 検索モードを選んでクエリを入力
3. 課題検索・転用検索は LLM がリランキングして関連度を付与

### APIを直接使う

```bash
# URL から収集
curl -X POST http://localhost:8000/api/ingest/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://arxiv.org/abs/2005.11401", "collection_mode": "standard"}'

# 課題から検索
curl -X POST http://localhost:8000/api/search/technologies \
  -H "Content-Type: application/json" \
  -d '{"query": "少ない試行回数で良い候補を見つけたい", "mode": "problem", "limit": 5}'
```

## アーキテクチャ

```
frontend (Next.js :3000)
    ↓
backend (FastAPI :8000)
    ├── services/collector.py  — URL取得（Web / arXiv / GitHub）
    ├── services/extractor.py  — LLMで技術カード抽出 → DB保存
    ├── services/llm.py        — Claude / OpenAI 抽象層
    └── services/search.py     — キーワード + ベクトル + リランキング
    ↓
PostgreSQL + pgvector
Redis
```

## データモデル（主要テーブル）

```
sources               — 情報源（URL・タイトル・メタデータ）
technology_items      — 技術カード（名前・概要・抽象原理・embedding）
technology_purposes   — 目的（条件つき）
technology_benefits   — メリット（条件つき）
technology_drawbacks  — デメリット（条件・深刻度つき）
technology_tradeoffs  — トレードオフ
technology_conditions — 有効条件 / 失敗条件 / 回避条件
technology_relations  — 技術間の関係（alternative_to, combines_with など）
```

## 実装フェーズ

- [x] Phase 1: URL収集・技術カード自動生成・基本検索
- [ ] Phase 2: 課題検索強化・条件つき評価の充実
- [ ] Phase 3: 技術比較・推薦API
- [ ] Phase 4: 定期収集（Celery / Redis）
- [ ] Phase 5: 抽象原理ベース転用検索・技術グラフ可視化
