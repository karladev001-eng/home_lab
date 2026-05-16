# home_lab — Claude Code マルチエージェント集

Claude Code のサブエージェント機能を活用した自動化システムの集合リポジトリです。  
各システムは独立したサブディレクトリに格納されており、全体クローンまたは個別クローンで利用できます。

---

## システム一覧

| ディレクトリ | システム名 | 説明 | 最新タグ |
|---|---|---|---|
| [`app-dev/`](app-dev/) | アプリ自動生成 | アイデアから5フェーズでアプリを自動生成する21エージェントシステム | `app-dev-v1.0` |
| [`research/`](research/) | 研究支援（準備中） | 論文調査・実験管理・レポート生成エージェント（開発予定） | — |

---

## クローン方法

### 全システムを取得する（推奨）

```bash
git clone https://github.com/karladev001/home_lab.git
cd home_lab
```

### 特定タグ時点の全システムを取得する

```bash
git clone --branch app-dev-v1.0 https://github.com/karladev001/home_lab.git
```

### 特定システムだけを sparse checkout で取得する

```bash
git clone --filter=blob:none --sparse https://github.com/karladev001/home_lab.git
cd home_lab
git sparse-checkout set app-dev
```

---

## 各システムの詳細

- **アプリ自動生成**: [`app-dev/README.md`](app-dev/README.md)
- **研究支援**: [`research/README.md`](research/README.md)（準備中）

---

## タグ一覧

| タグ | 対象システム | 内容 |
|---|---|---|
| `app-dev-v1.0` | app-dev | 21エージェント構成の初回リリース |
| `research-v1.0` | research | （未作成） |
