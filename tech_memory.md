# 技術収集・検索DBシステム 仕様書

## 1. 概要

本仕様書は、研究・開発・ゲーム制作・システム設計など、複数分野で利用可能な「技術収集・検索DBシステム」の設計仕様を定義する。

本システムは、論文、技術記事、公式ドキュメント、GitHub、技術ブログ、事例記事、ユーザーメモなどから技術情報を収集し、技術・アルゴリズム・設計パターン・ツール・実装パターンなどを構造化して保存する。

単なる文書検索ではなく、ユーザーが抱える課題や制約から「使えそうな技術」「代替技術」「組み合わせ可能な技術」「他分野から応用できそうな技術」を検索・推薦できることを目的とする。

---

## 2. システムの目的

### 2.1 主目的

本システムの主目的は、技術情報を再利用可能な知識として蓄積し、研究・開発・設計・企画に活用できるようにすることである。

具体的には、以下を実現する。

- 技術・アルゴリズム・設計パターン・ツールを構造化して保存する
- 技術名を知らなくても、課題や目的から関連技術を検索できる
- 技術のメリット、デメリット、成立条件、失敗条件を検索できる
- 異なる分野で使われている技術を抽象原理ベースで横断検索できる
- 研究や開発で使える技術候補、組み合わせ、実装方針を提示できる
- ユーザーが気になったURLやキーワードから技術情報を追加できる
- 設定された分野について定期的に技術情報を収集できる

### 2.2 想定利用例

- 「NPCの行動制御に使える技術を探したい」
- 「少ない試行回数で良い候補を見つける技術を知りたい」
- 「RAGの精度改善に使える技術を比較したい」
- 「ゲーム開発のECSをAIエージェント管理に応用できるか知りたい」
- 「研究論文から仮説生成に使える技術を集めたい」
- 「リアルタイムな大量イベント処理に使える設計パターンを探したい」
- 「このURLの記事に書かれている技術をDBに追加したい」

---

## 3. 設計思想

### 3.1 文書中心ではなく技術中心

本システムは、PDFや記事をそのまま保存する文書DBではなく、技術を中心とした知識DBとして設計する。

文書はあくまで情報源であり、検索・推薦の主対象は以下である。

- 技術
- アルゴリズム
- アーキテクチャ
- 設計パターン
- 実装パターン
- ツール
- 評価手法
- ユースケース
- 抽象原理

### 3.2 用途を固定しない

技術を特定用途に閉じ込めない。

悪い例:

```text
Behavior Tree = ゲームNPC用の技術
```

良い例:

```text
Behavior Tree = 複雑な意思決定を、条件判定と行動選択の階層構造として管理する技術
```

そのうえで、ゲームNPC、ロボット制御、AIエージェントワークフローなどを「既知の応用例」として保存する。

### 3.3 技術の本質と応用例を分離する

技術カードは以下の層に分ける。

```text
Technology Core
  技術の中核メカニズム

Abstract Principle
  分野を超えて再利用可能な抽象原理

Problem Structure
  どのような問題構造を解くか

Known Applications
  既知の使用例

Transfer Candidates
  他分野への応用候補
```

### 3.4 メリット・デメリットは条件つきで保存する

技術の利点や欠点は、絶対的なものではなく条件に依存する。

そのため、以下のように保存する。

```json
{
  "benefit": "少ない試行回数で有望候補を探索できる",
  "condition": "評価コストが高く、逐次的に試行できる場合"
}
```

```json
{
  "drawback": "高次元空間では性能が落ちやすい",
  "condition": "探索変数が非常に多い場合",
  "severity": "medium"
}
```

---

## 4. システム全体構成

```text
User Input
  - URL
  - キーワード
  - DOI / arXiv ID
  - 手入力メモ
  - 定期収集設定
        ↓
Collector
  - Web記事取得
  - 論文メタデータ取得
  - GitHub / Docs / RSS取得
        ↓
Temporary Fetcher
  - 本文やPDFを一時取得
  - 処理後は原則破棄
        ↓
Parser
  - テキスト抽出
  - セクション分割
  - メタデータ抽出
        ↓
Extractor
  - 技術名抽出
  - 技術カード生成
  - メリット・デメリット抽出
  - 目的・成立条件・失敗条件抽出
  - 抽象原理化
        ↓
Normalizer
  - 同義語統合
  - 技術名正規化
  - 重複排除
        ↓
Knowledge DB
  - sources
  - technology_items
  - technology_relations
  - use_cases
  - evidence
        ↓
Search / Recommendation API
  - キーワード検索
  - ベクトル検索
  - メタデータ検索
  - 技術関係検索
        ↓
User Interface
  - 技術検索
  - 比較
  - 推薦
  - 組み合わせ提案
```

---

## 5. 対象データソース

### 5.1 外部ソース

- 論文
  - arXiv
  - PubMed
  - Semantic Scholar
  - OpenAlex
  - Crossref
- 公式ドキュメント
  - フレームワーク公式Docs
  - クラウドサービスDocs
  - ゲームエンジンDocs
- 技術記事
  - Zenn
  - Qiita
  - Medium
  - dev.to
  - 企業技術ブログ
- 実装情報
  - GitHub
  - Papers with Code
  - Hugging Face
- 講演・事例
  - GDC Talks
  - Engineering Case Studies
  - Postmortems
- 標準仕様
  - RFC
  - W3C
  - ISOなど

### 5.2 内部ソース

- ユーザーのメモ
- 社内ドキュメント
- 議事録
- 設計書
- 過去の技術選定メモ
- 実験ログ
- プロジェクト記録

### 5.3 保存方針

外部ソースは、原則として本文やPDF全文を保存しない。

保存するもの:

- URL
- DOI / arXiv ID / GitHub URLなどの識別子
- タイトル
- 著者・組織
- 公開日
- 取得日
- 要約
- 抽出された技術情報
- 短い根拠メモ
- embedding

保存しないもの:

- 著作権上問題のある全文コピー
- 出版社PDFの大量保存
- 長大な本文チャンク

内部ソースについては、権限上問題がない場合に限り全文保存を許可する。

---

## 6. 主要データモデル

## 6.1 Source

情報源を表す。

```sql
CREATE TABLE sources (
  id UUID PRIMARY KEY,
  source_type TEXT NOT NULL,
  title TEXT NOT NULL,
  url TEXT,
  canonical_url TEXT,
  author TEXT,
  organization TEXT,
  published_at TIMESTAMP,
  retrieved_at TIMESTAMP NOT NULL,
  source_reliability NUMERIC,
  license TEXT,
  content_hash TEXT,
  access_status TEXT,
  metadata_json JSONB,
  created_at TIMESTAMP NOT NULL DEFAULT now(),
  updated_at TIMESTAMP NOT NULL DEFAULT now()
);
```

### source_type の例

```text
paper
web_article
documentation
github_repository
blog
book
memo
meeting_note
specification
case_study
```

---

## 6.2 Technology Item

技術、アルゴリズム、設計パターン、ツールなどを表す中心エンティティ。

```sql
CREATE TABLE technology_items (
  id UUID PRIMARY KEY,
  item_type TEXT NOT NULL,
  name TEXT NOT NULL,
  aliases TEXT[],
  summary TEXT,
  core_mechanism TEXT,
  abstract_principle TEXT,
  domains TEXT[],
  categories TEXT[],
  problem_structures TEXT[],
  inputs TEXT[],
  outputs TEXT[],
  constraints TEXT[],
  maturity_level TEXT,
  difficulty_level TEXT,
  cost_level TEXT,
  embedding VECTOR,
  created_at TIMESTAMP NOT NULL DEFAULT now(),
  updated_at TIMESTAMP NOT NULL DEFAULT now()
);
```

### item_type の例

```text
technique
algorithm
architecture
architecture_pattern
design_pattern
implementation_pattern
tool
library
framework
protocol
evaluation_method
method_family
```

---

## 6.3 Purpose

技術の目的を保存する。

```sql
CREATE TABLE technology_purposes (
  id UUID PRIMARY KEY,
  technology_id UUID REFERENCES technology_items(id),
  purpose TEXT NOT NULL,
  condition TEXT,
  abstraction_level TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT now()
);
```

例:

```text
評価コストが高い探索空間で、少ない試行回数で良い候補を見つける
```

---

## 6.4 Benefit

技術のメリットを条件つきで保存する。

```sql
CREATE TABLE technology_benefits (
  id UUID PRIMARY KEY,
  technology_id UUID REFERENCES technology_items(id),
  benefit TEXT NOT NULL,
  condition TEXT,
  evidence_source_id UUID REFERENCES sources(id),
  confidence_score NUMERIC,
  created_at TIMESTAMP NOT NULL DEFAULT now()
);
```

---

## 6.5 Drawback

技術のデメリットを条件つきで保存する。

```sql
CREATE TABLE technology_drawbacks (
  id UUID PRIMARY KEY,
  technology_id UUID REFERENCES technology_items(id),
  drawback TEXT NOT NULL,
  condition TEXT,
  severity TEXT,
  evidence_type TEXT,
  evidence_source_id UUID REFERENCES sources(id),
  confidence_score NUMERIC,
  created_at TIMESTAMP NOT NULL DEFAULT now()
);
```

### evidence_type

```text
observed
inferred
unknown
```

---

## 6.6 Tradeoff

技術が持つトレードオフを保存する。

```sql
CREATE TABLE technology_tradeoffs (
  id UUID PRIMARY KEY,
  technology_id UUID REFERENCES technology_items(id),
  gain TEXT NOT NULL,
  cost TEXT NOT NULL,
  condition TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT now()
);
```

例:

```json
{
  "gain": "応答速度が上がる",
  "cost": "キャッシュ無効化の設計が必要になる",
  "condition": "頻繁に読まれるが更新頻度が低いデータを扱う場合"
}
```

---

## 6.7 Works When / Avoid When

技術が有効な条件、避けるべき条件を保存する。

```sql
CREATE TABLE technology_conditions (
  id UUID PRIMARY KEY,
  technology_id UUID REFERENCES technology_items(id),
  condition_type TEXT NOT NULL,
  description TEXT NOT NULL,
  evidence_source_id UUID REFERENCES sources(id),
  confidence_score NUMERIC,
  created_at TIMESTAMP NOT NULL DEFAULT now()
);
```

### condition_type

```text
works_when
fails_when
avoid_when
requires
```

---

## 6.8 Technology Relation

技術同士の関係を保存する。

```sql
CREATE TABLE technology_relations (
  id UUID PRIMARY KEY,
  subject_technology_id UUID REFERENCES technology_items(id),
  relation_type TEXT NOT NULL,
  object_technology_id UUID REFERENCES technology_items(id),
  strength NUMERIC,
  reason TEXT,
  evidence_source_id UUID REFERENCES sources(id),
  created_at TIMESTAMP NOT NULL DEFAULT now()
);
```

### relation_type の例

```text
similar_to
alternative_to
combines_with
depends_on
implements
used_in
transfers_to
solves_same_problem_as
more_general_than
more_specific_than
improves
replaces
```

---

## 6.9 Use Case

技術が使われる課題や応用例を保存する。

```sql
CREATE TABLE use_cases (
  id UUID PRIMARY KEY,
  title TEXT NOT NULL,
  domain TEXT,
  problem_description TEXT,
  requirements TEXT[],
  constraints TEXT[],
  evaluation_metrics TEXT[],
  embedding VECTOR,
  created_at TIMESTAMP NOT NULL DEFAULT now(),
  updated_at TIMESTAMP NOT NULL DEFAULT now()
);
```

---

## 6.10 Use Case Technology Mapping

ユースケースと技術の対応を保存する。

```sql
CREATE TABLE use_case_technologies (
  id UUID PRIMARY KEY,
  use_case_id UUID REFERENCES use_cases(id),
  technology_id UUID REFERENCES technology_items(id),
  fit_score NUMERIC,
  reason TEXT,
  implementation_note TEXT,
  evidence_source_id UUID REFERENCES sources(id),
  created_at TIMESTAMP NOT NULL DEFAULT now()
);
```

---

## 6.11 Evidence

短い根拠情報を保存する。

```sql
CREATE TABLE evidence (
  id UUID PRIMARY KEY,
  source_id UUID REFERENCES sources(id),
  technology_id UUID REFERENCES technology_items(id),
  evidence_type TEXT,
  short_quote TEXT,
  paraphrase TEXT,
  locator TEXT,
  confidence_score NUMERIC,
  created_at TIMESTAMP NOT NULL DEFAULT now()
);
```

### 注意

- short_quote は必要最小限にする
- 長文引用や本文コピーは保存しない
- locator には page, section, paragraph などを保存する

---

## 7. 技術カード仕様

### 7.1 技術カードのJSON表現

```json
{
  "name": "Technology Name",
  "type": "technique | algorithm | architecture | tool | pattern",
  "aliases": [],
  "summary": "技術の短い説明",
  "core_mechanism": "技術の中核メカニズム",
  "abstract_principle": "分野を超えて再利用可能な抽象原理",
  "domains": [],
  "problem_structures": [],
  "inputs": [],
  "outputs": [],
  "purpose": [
    {
      "description": "何のために使うか",
      "condition": "その目的が成立する条件"
    }
  ],
  "benefits": [
    {
      "benefit": "利点",
      "condition": "その利点が成立する条件",
      "confidence": 0.0
    }
  ],
  "drawbacks": [
    {
      "drawback": "欠点",
      "condition": "その欠点が出やすい条件",
      "severity": "low | medium | high",
      "evidence_type": "observed | inferred | unknown"
    }
  ],
  "tradeoffs": [
    {
      "gain": "得られるもの",
      "cost": "失うもの・増える負担",
      "condition": "条件"
    }
  ],
  "works_when": [],
  "fails_when": [],
  "avoid_when": [],
  "alternatives": [],
  "complements": [],
  "evaluation_metrics": [],
  "known_applications": [],
  "transfer_questions": [],
  "sources": []
}
```

---

## 8. 収集機能

## 8.1 手動収集

ユーザーが以下を入力することで、即時収集を行う。

- URL
- DOI
- arXiv ID
- GitHub URL
- キーワード
- 技術名
- 手入力メモ

### 手動収集フロー

```text
Input
  ↓
Source Identification
  ↓
Fetch Metadata
  ↓
Temporary Content Fetch
  ↓
Parse
  ↓
Extract Technology Knowledge
  ↓
Normalize
  ↓
Deduplicate
  ↓
Store
  ↓
Return Summary
```

### 手動収集後の出力

- 検出された技術
- 技術カード案
- 関連技術
- メリット・デメリット
- 既存DB内の類似技術
- 保存結果

---

## 8.2 定期収集

ユーザーが設定した分野やキーワードに基づき、定期的に情報を収集する。

### 設定例

```json
{
  "profile_name": "AI Agent / RAG / Game AI",
  "keywords": [
    "AI agents",
    "RAG evaluation",
    "behavior tree",
    "game AI planning",
    "knowledge graph"
  ],
  "exclude_keywords": [
    "non technical",
    "marketing only"
  ],
  "sources": [
    "arXiv",
    "GitHub",
    "official_docs",
    "engineering_blogs"
  ],
  "schedule": {
    "frequency": "daily",
    "time": "08:00",
    "timezone": "Asia/Tokyo"
  },
  "max_items_per_run": 50,
  "deep_analysis_limit": 5
}
```

### 定期収集フロー

```text
Load User Profiles
  ↓
Generate Search Queries
  ↓
Collect Candidate Sources
  ↓
Deduplicate
  ↓
Score Relevance
  ↓
Light Analysis
  ↓
Select Top N
  ↓
Deep Analysis
  ↓
Store Technology Cards
  ↓
Generate Digest
```

---

## 9. 抽出パイプライン

### 9.1 抽出対象

各ソースから以下を抽出する。

- 技術名
- 技術の別名
- 技術カテゴリ
- 解決する問題
- 中核メカニズム
- 入力
- 出力
- 成立条件
- 失敗条件
- メリット
- デメリット
- トレードオフ
- 代替技術
- 組み合わせ可能な技術
- 既知の応用例
- 抽象原理
- 他分野への応用可能性
- 評価指標
- 根拠URL

### 9.2 抽象原理化

技術を分野横断で使えるよう、以下のような抽象化を行う。

例:

```text
Behavior Tree
  ↓
複雑な意思決定を、階層化された条件判定と行動選択に分解する
```

```text
Bayesian Optimization
  ↓
評価コストが高い探索空間で、不確実性を使って次に試す候補を選ぶ
```

```text
RAG
  ↓
外部知識を検索し、生成・判断の文脈として注入する
```

---

## 10. 正規化・重複排除

### 10.1 技術名の正規化

同じ技術の別名を統合する。

例:

```text
Retrieval Augmented Generation
RAG
検索拡張生成
```

これらは同一技術として扱う。

### 10.2 重複判定

以下を組み合わせて重複判定を行う。

- 正規化技術名
- aliases
- embedding similarity
- source URL
- DOI / arXiv ID
- GitHub repository URL
- core_mechanism similarity

### 10.3 マージ方針

同じ技術が既に存在する場合、以下を追加・更新する。

- 新しいsource
- 新しいknown_application
- 新しいbenefit / drawback
- 新しいrelation
- confidence_score
- last_seen_at

技術カード自体を単純上書きしない。

---

## 11. 検索機能

## 11.1 検索モード

### 技術名検索

技術名や別名から検索する。

例:

```text
RAG
Behavior Tree
Bayesian Optimization
```

### 課題検索

ユーザーの課題から技術を検索する。

例:

```text
少ない試行回数で良い候補を見つけたい
```

### 分野検索

特定分野で使われる技術を検索する。

例:

```text
ゲーム開発で使われるAI技術
```

### 条件検索

制約条件を指定して検索する。

例:

```text
低コストで実装できて、デバッグしやすいNPC制御技術
```

### 比較検索

複数技術を比較する。

例:

```text
Behavior Tree と GOAP と Utility AI の違い
```

### 転用検索

別分野で使われている技術の応用候補を検索する。

例:

```text
ゲーム開発の技術をAIエージェント設計に応用したい
```

---

## 11.2 検索方式

以下を組み合わせたハイブリッド検索を行う。

```text
Keyword Search
  技術名、固有名詞、エラーコード、ツール名に強い

Vector Search
  意味的に似た課題や抽象原理を探す

Metadata Filter
  分野、成熟度、コスト、難易度、情報源で絞る

Graph Search
  技術間の関係をたどる

Reranking
  ユーザーの目的・制約に合わせて並べ替える
```

---

## 11.3 検索結果フォーマット

検索結果は以下の形式で返す。

```json
{
  "query": "NPCの行動制御に使える技術",
  "results": [
    {
      "technology": "Behavior Tree",
      "fit_score": 0.91,
      "summary": "条件判定と行動選択を木構造で管理する技術",
      "why_relevant": "NPCの階層的な意思決定に適している",
      "benefits": [
        "デバッグしやすい",
        "デザイナーが制御しやすい"
      ],
      "drawbacks": [
        "大規模化するとツリー管理が難しい"
      ],
      "alternatives": [
        "FSM",
        "Utility AI",
        "GOAP"
      ],
      "sources": []
    }
  ]
}
```

---

## 12. 推薦機能

### 12.1 技術推薦

ユーザーの課題・制約から候補技術を推薦する。

入力例:

```json
{
  "goal": "大量のPDFから構造化情報を抽出したい",
  "constraints": [
    "低コスト",
    "後から検索したい",
    "表や図が含まれる"
  ]
}
```

出力例:

```text
候補技術:
- PDF parser
- OCR
- layout-aware parsing
- multimodal LLM
- schema-based extraction
- human-in-the-loop validation
- embedding search
```

### 12.2 代替技術推薦

ある技術に対して代替案を提示する。

例:

```text
RAGの代替・補完技術:
- Fine-tuning
- Knowledge Graph QA
- Long Context LLM
- Tool-based retrieval
- Hybrid Search
```

### 12.3 組み合わせ推薦

併用できる技術を提示する。

例:

```text
RAG + Knowledge Graph + Reranker + Citation Validator
```

### 12.4 避けるべき技術の提示

条件に合わない技術も明示する。

例:

```text
Microservices は今回は非推奨。
理由:
- MVP段階
- 開発者が少ない
- 運用負荷が高い
- ドメイン境界がまだ不明確
```

---

## 13. 評価スコア

技術候補には以下のスコアを付与する。

### 13.1 共通スコア

```text
fit_score
  ユーザー課題との適合度

maturity_score
  技術の成熟度

evidence_strength
  根拠の強さ

implementation_cost
  実装コスト

learning_cost
  学習コスト

risk_score
  導入リスク

transferability_score
  他分野応用のしやすさ
```

### 13.2 研究向けスコア

```text
novelty
feasibility
testability
scientific_impact
```

### 13.3 開発向けスコア

```text
maintainability
scalability
observability
ecosystem_support
```

### 13.4 ゲーム開発向けスコア

```text
runtime_cost
debuggability
designer_control
emergent_behavior
content_authoring_cost
```

---

## 14. API仕様案

## 14.1 技術登録API

```http
POST /api/technologies
```

Request:

```json
{
  "name": "Behavior Tree",
  "type": "architecture_pattern",
  "summary": "...",
  "core_mechanism": "...",
  "abstract_principle": "...",
  "domains": ["game development", "robotics"],
  "problem_structures": ["hierarchical decision making"]
}
```

---

## 14.2 URL収集API

```http
POST /api/ingest/url
```

Request:

```json
{
  "url": "https://example.com/article",
  "collection_mode": "deep",
  "tags": ["game AI", "NPC"]
}
```

Response:

```json
{
  "source_id": "uuid",
  "detected_technologies": [
    "Behavior Tree",
    "GOAP"
  ],
  "created_items": [],
  "updated_items": []
}
```

---

## 14.3 キーワード収集API

```http
POST /api/ingest/search
```

Request:

```json
{
  "query": "game AI behavior tree utility AI GOAP",
  "sources": ["web", "github", "papers"],
  "max_results": 20,
  "deep_analysis_limit": 5
}
```

---

## 14.4 技術検索API

```http
POST /api/search/technologies
```

Request:

```json
{
  "query": "少ない試行回数で良い候補を見つけたい",
  "filters": {
    "domains": ["AI", "optimization"],
    "max_implementation_cost": "medium"
  },
  "mode": "problem_search"
}
```

Response:

```json
{
  "results": [
    {
      "technology_id": "uuid",
      "name": "Bayesian Optimization",
      "fit_score": 0.92,
      "summary": "...",
      "benefits": [],
      "drawbacks": [],
      "alternatives": []
    }
  ]
}
```

---

## 14.5 比較API

```http
POST /api/compare
```

Request:

```json
{
  "technologies": [
    "FSM",
    "Behavior Tree",
    "GOAP",
    "Utility AI"
  ],
  "criteria": [
    "debuggability",
    "designer_control",
    "scalability",
    "runtime_cost"
  ]
}
```

---

## 14.6 推薦API

```http
POST /api/recommend
```

Request:

```json
{
  "goal": "研究論文から仮説を生成するシステムを作りたい",
  "constraints": [
    "根拠を追跡したい",
    "異分野技術を組み合わせたい",
    "低コストでMVPを作りたい"
  ]
}
```

---

## 15. UI仕様案

## 15.1 主要画面

### 技術検索画面

- 検索バー
- 検索モード選択
  - 技術名
  - 課題
  - 分野
  - 比較
  - 転用
- フィルタ
  - 分野
  - 成熟度
  - コスト
  - 難易度
  - 情報源
- 検索結果カード

### 技術カード詳細画面

表示項目:

- 技術名
- 概要
- 中核メカニズム
- 抽象原理
- 目的
- メリット
- デメリット
- トレードオフ
- 有効な条件
- 避けるべき条件
- 代替技術
- 組み合わせ技術
- 既知の応用例
- 根拠ソース
- 関連技術グラフ

### 収集画面

- URL入力
- キーワード入力
- DOI / arXiv ID入力
- GitHub URL入力
- 手入力メモ
- 収集深度
  - light
  - standard
  - deep

### 定期収集設定画面

- プロファイル名
- キーワード
- 除外キーワード
- 対象ソース
- 実行頻度
- 実行時刻
- 解析件数上限
- 通知設定

---

## 16. 権限・安全性・ライセンス

### 16.1 外部コンテンツの扱い

- 外部コンテンツの全文保存は原則禁止
- URL、メタデータ、短い根拠、要約、抽出知識を保存する
- 長文引用を保存しない
- ライセンス情報を可能な限り保存する

### 16.2 内部コンテンツの扱い

- ユーザーまたは組織が権利を持つ文書のみ全文保存可能
- アクセス権限を source 単位で管理する
- 機密文書は embedding も権限管理対象とする

### 16.3 AI抽出結果の扱い

AIが推定した情報と、実際の根拠に基づく情報を区別する。

```text
observed
  情報源に明示されている

inferred
  AIが構造から推定した

unknown
  根拠が弱い、または未確認
```

---

## 17. MVPスコープ

### 17.1 MVPで作る機能

- URL入力による収集
- キーワード入力による収集
- 技術カード自動生成
- 技術名・課題・分野からの検索
- メリット・デメリット・目的・成立条件の保存
- PostgreSQL + pgvector による検索
- 技術カード詳細表示
- 技術比較の簡易出力

### 17.2 MVPで対象にする分野

初期対象は以下の3領域とする。

```text
1. AI / LLM / RAG / Agent
2. Software Architecture / Backend / Database
3. Game Development / Game AI
```

### 17.3 MVPで扱うソース

- URL
- Web記事
- 公式ドキュメント
- GitHub README
- arXiv URL
- ユーザー手入力メモ

### 17.4 MVPで扱わないもの

- 大規模クローリング
- 出版社PDFの全文保存
- 完全自動の新規研究提案
- 複雑な組織権限管理
- Neo4jなどの本格グラフDB

---

## 18. 推奨技術スタック

### Backend

```text
Python
FastAPI
Celery or RQ
Redis
PostgreSQL
pgvector
```

### AI / Extraction

```text
LLM structured output
Embedding model
Reranker
Schema validation
```

### Search

```text
PostgreSQL full-text search
pgvector similarity search
Metadata filtering
Optional reranking
```

### Frontend

```text
Next.js
React
Tailwind CSS
```

### 将来拡張

```text
Neo4j or ArangoDB
OpenSearch
Airflow / Dagster / Prefect
Team permission system
Browser extension
Slack / Notion integration
```

---

## 19. 将来拡張

### 19.1 技術グラフ

技術同士の関係をグラフとして可視化する。

```text
RAG
  ├─ combines_with → Reranker
  ├─ combines_with → Knowledge Graph
  ├─ alternative_to → Fine-tuning
  └─ depends_on → Embedding Search
```

### 19.2 技術転用エージェント

異なる分野の技術を抽象原理ベースで推薦する。

例:

```text
ゲーム開発のECSを、AIエージェント管理基盤に応用する
```

### 19.3 技術選定レポート自動生成

ユーザーの条件に基づき、技術選定レポートを生成する。

出力:

- 候補技術一覧
- 比較表
- 推奨構成
- 採用しない技術
- リスク
- MVP構成
- 将来拡張案

### 19.4 ブラウザ拡張

Webページ閲覧中に「この技術を保存」できるようにする。

### 19.5 チーム利用

- 組織内技術DB
- 技術選定履歴
- プロジェクト別コレクション
- 社内ベストプラクティス検索

---

## 20. 代表的な検索例

### 例1: 課題から検索

入力:

```text
少ない試行回数で良い候補を見つけたい
```

出力候補:

```text
- Bayesian Optimization
- Active Learning
- Multi-armed Bandit
- Sequential Experimental Design
- Evolutionary Search
```

### 例2: 分野から検索

入力:

```text
ゲーム開発で使われるNPC意思決定技術
```

出力候補:

```text
- Finite State Machine
- Behavior Tree
- Utility AI
- GOAP
- Hierarchical Task Network
- Monte Carlo Tree Search
```

### 例3: 技術比較

入力:

```text
FSM, Behavior Tree, GOAP, Utility AIを比較して
```

出力:

```text
FSM:
  小規模で単純な状態遷移に向く

Behavior Tree:
  階層的な行動制御に向く

GOAP:
  目標から逆算して行動計画を作る場合に向く

Utility AI:
  状況に応じた柔軟な選択に向く
```

### 例4: 転用検索

入力:

```text
ゲーム開発の技術をAIエージェント設計に応用したい
```

出力候補:

```text
- Behavior Tree → エージェントのタスク分岐制御
- Blackboard Architecture → 複数エージェントの共有状態管理
- ECS → 多数エージェントの状態・能力管理
- Utility AI → エージェントの行動優先度決定
```

---

## 21. 開発フェーズ

### Phase 1: 基本DBと手動収集

- sources テーブル
- technology_items テーブル
- URL収集
- 技術カード生成
- 技術名検索

### Phase 2: 課題検索と条件つき評価

- purposes
- benefits
- drawbacks
- tradeoffs
- works_when / avoid_when
- 課題からの検索

### Phase 3: 比較・推薦

- alternative_to
- combines_with
- 技術比較
- 推奨技術提示

### Phase 4: 定期収集

- 収集プロファイル
- スケジューラー
- デイリーダイジェスト

### Phase 5: 技術転用・グラフ探索

- 抽象原理ベースの転用検索
- 技術グラフ
- 異分野組み合わせ提案

---

## 22. まとめ

本システムは、研究論文検索システムではなく、技術・アルゴリズム・設計パターン・ツールを中心にした汎用的な技術知識検索基盤である。

重要な設計方針は以下である。

```text
文書ではなく技術を中心にする
用途ではなく中核メカニズムを中心にする
使い方は固定せず、応用例として保存する
メリット・デメリットは条件つきで保存する
課題や問題構造から技術を検索できるようにする
異分野応用のために抽象原理を保存する
外部ソースはURL中心で保存し、全文保存を避ける
```

この設計により、研究、ソフトウェア開発、ゲーム開発、AIシステム設計、技術選定、企画、学習など幅広い用途で利用可能な「技術検索エンジン」を構築できる。
