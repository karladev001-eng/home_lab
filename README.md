# home_lab — Claude Code マルチエージェント集

Claude Code のサブエージェント機能を活用した自動化システムの集合リポジトリです。
各システムは独立したサブディレクトリに格納されており、全体クローンまたは個別クローンで利用できます。

---

## システム一覧

| ディレクトリ | システム名 | 説明 |
| --- | --- | --- |
| [`app-dev/`](app-dev/) | アプリ自動生成 | アイデアから5フェーズでアプリを自動生成する21エージェントシステム |
| [`tech-memory/`](tech-memory/) | 技術収集・検索DB | URLから技術カードを自動生成し課題・分野・転用で検索できる知識DBシステム |

> **開発経緯・設計ドキュメント付きのバージョン**: [`dev` ブランチ](https://github.com/karladev001-eng/home_lab/tree/dev)

---

## クローン方法

```bash
git clone https://github.com/karladev001-eng/home_lab.git
cd home_lab
```

---

## 各システムの詳細

- **アプリ自動生成**: [`app-dev/README.md`](app-dev/README.md)
- **技術収集・検索DB**: [`tech-memory/README.md`](tech-memory/README.md)

---

## ブランチ構成

| ブランチ | 内容 |
| --- | --- |
| `main` | 仕様書 + 実装コードのみ（クリーン版） |
| `dev` | 要件定義・設計書・QA報告書・成果物ドキュメントを含む開発版 |
