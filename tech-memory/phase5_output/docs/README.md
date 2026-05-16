# tech-memory

> 論文・技術記事・GitHub・ブログから技術情報を収集し、技術名を知らなくても「課題・目的・分野」から関連技術を検索・推薦できる個人用技術知識データベースシステム。

## できること

| 機能 | 説明 |
|---|---|
| URL収集 | Web記事・arXiv論文・GitHub READMEのURLを入力すると技術カードを自動生成 |
| キーワード収集 | キーワードを入力してGitHub・arXivから関連情報を自動収集 |
| メモ収集 | 手書きメモ・テキストから技術カードを生成 |
| 技術検索 | 技術名・課題文・分野から技術をキーワード/ベクトル検索 |
| 技術詳細表示 | メカニズム・メリット・デメリット・成立条件・関連技術を一覧表示 |
| 技術比較 | 複数技術をデバッガビリティ・スケーラビリティ等で比較 |
| 技術推薦 | 課題文から最適な技術をベクトル検索で推薦 |

---

## 動かすまでの手順

### 必要なもの

以下がインストール済みであることを確認してください。

| ツール | 必要バージョン | 確認コマンド |
|---|---|---|
| Docker | 20以上 | `docker --version` |
| docker-compose | 1.29以上 | `docker-compose --version` |
| Git | 任意 | `git --version` |

また、以下のAPIキーが必要です:
- **Anthropic API Key**: [console.anthropic.com](https://console.anthropic.com) で取得
- **OpenAI API Key**: [platform.openai.com](https://platform.openai.com) で取得

---

### ステップ 1: リポジトリを取得する

```bash
git clone <リポジトリURL>
cd tech-memory
```

> クローンが完了するとプロジェクトフォルダが作成されます。

---

### ステップ 2: 環境変数を設定する

```bash
cp phase3_code/.env.example phase3_code/.env
```

`phase3_code/.env` をテキストエディタで開き、以下の項目を設定してください。

| 変数名 | 説明 | 設定例 |
|---|---|---|
| `ANTHROPIC_API_KEY` | Anthropic Claude APIキー（技術カード抽出に使用） | `sk-ant-api03-...` |
| `OPENAI_API_KEY` | OpenAI APIキー（embedding生成に使用） | `sk-...` |
| `POSTGRES_USER` | PostgreSQLユーザー名 | `techuser`（デフォルトのまま可） |
| `POSTGRES_PASSWORD` | PostgreSQLパスワード | `techpass`（本番環境では変更推奨） |
| `POSTGRES_DB` | データベース名 | `techdb`（デフォルトのまま可） |
| `DATABASE_URL` | DB接続文字列 | `postgresql+asyncpg://techuser:techpass@db:5432/techdb` |
| `NEXT_PUBLIC_API_URL` | バックエンドAPIのURL | `http://localhost:8000` |

**重要**: Docker Compose環境では `DATABASE_URL` のホスト部分を `localhost` ではなく `db` にしてください:
```
DATABASE_URL=postgresql+asyncpg://techuser:techpass@db:5432/techdb
```

---

### ステップ 3: Docker Composeでサービスを起動する

```bash
cd phase3_code
docker-compose up -d
```

> 3つのサービスが起動します:
> - **db**: PostgreSQL 16 + pgvector（ポート5432）
> - **api**: FastAPI バックエンド（ポート8000）
> - **web**: Next.js フロントエンド（ポート3000）
>
> 初回起動時はDockerイメージのビルドで数分かかります。

起動状態を確認する:
```bash
docker-compose ps
```

> 全サービスの `State` が `Up` になれば成功です。

---

### ステップ 4: データベースをセットアップする

```bash
docker-compose exec api alembic upgrade head
```

> テーブルが作成されます。`INFO [alembic.runtime.migration] Running upgrade ... -> 001_initial_schema` と表示されれば成功です。

---

### ステップ 5: 動作確認する

ブラウザで `http://localhost:3000` を開くとアプリが表示されます。

API の動作確認:
```bash
curl http://localhost:8000/api/v1/health
```

```json
{"success": true, "data": {"status": "ok", "db": "ok", "version": "0.1.0"}}
```

> `"status": "ok"` と `"db": "ok"` が返れば正常です。

---

## 使い方

### URL収集（技術カードの自動生成）

1. `http://localhost:3000/ingest` を開く
2. 「URL収集」タブで技術記事のURLを入力する
3. 収集モード（`standard` 推奨）を選択する
4. 「収集」ボタンをクリックする

> LLMが自動で技術カードを生成・保存します（30秒程度かかります）。

**例: arXiv論文の収集**
```
URL: https://arxiv.org/abs/2303.08774
モード: deep
```

**例: GitHub READMEの収集**
```
URL: https://github.com/langchain-ai/langchain
モード: standard
```

### キーワード収集

1. `http://localhost:3000/ingest` を開く
2. 「キーワード収集」タブでキーワードを入力する（例: `behavior tree NPC AI`）
3. 「収集」ボタンをクリックする

> GitHub・arXivから関連情報を検索して技術カードを生成します。

### 技術検索

1. `http://localhost:3000` または `http://localhost:3000/search` を開く
2. 検索バーに技術名・課題・分野を入力する
   - 例: `少ない試行回数で良い候補を見つけたい`（課題文）
   - 例: `Behavior Tree`（技術名）
   - 例: `AI`（分野）
3. 検索結果から技術カードをクリックして詳細を確認する

### 技術比較

1. `http://localhost:3000/compare` を開く
2. 比較したい技術名を入力する（2〜10件）
3. 「比較」ボタンをクリックする

> デバッガビリティ・スケーラビリティ・実装コスト・成熟度のスコア比較表が表示されます。

---

## テストを実行する

```bash
cd phase3_code
docker-compose exec api pytest tests/ -v
```

> 13件のテストが実行されます。`13 passed` と表示されれば成功です。

---

## 本番向けビルドを作成する

```bash
cd phase3_code
docker-compose build
```

> `api` と `web` の本番用Dockerイメージがビルドされます。

---

## デプロイする

詳しくは [デプロイ手順書](./DEPLOY.md) を参照してください。

Docker Composeのセットアップがあればそのままサーバーに展開できます。
VPS・クラウドサーバーに `phase3_code/` を転送し、`.env` を設定して `docker-compose up -d` を実行してください。

---

## トラブルシューティング

### Docker Composeが起動しない

`.env` ファイルが存在するか確認してください:
```bash
ls phase3_code/.env
```
存在しない場合: `cp phase3_code/.env.example phase3_code/.env` を実行してAPIキーを設定してください。

### DBに接続できない / healthが `"db": "error"` を返す

1. DBコンテナが起動しているか確認:
   ```bash
   docker-compose ps db
   ```
2. `DATABASE_URL` のホストが `db`（`localhost` ではない）になっているか確認:
   ```
   DATABASE_URL=postgresql+asyncpg://techuser:techpass@db:5432/techdb
   ```

### alembic upgrade headが失敗する

pgvectorエクステンションが有効化されているか確認:
```bash
docker-compose exec db psql -U techuser -d techdb -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### URL収集でエラーが発生する

- `ANTHROPIC_API_KEY` と `OPENAI_API_KEY` が正しく設定されているか確認
- 対象URLがアクセス可能か確認（`curl <URL>` でテスト）
- arXiv URLは `https://arxiv.org/abs/{ID}` 形式を使用してください

### ポートが使用中というエラーが出る

```bash
# 3000番ポートを使用しているプロセスを確認
lsof -i :3000
# 8000番ポートを使用しているプロセスを確認
lsof -i :8000
# プロセスを終了
kill -9 {PID}
```

---

## ドキュメント一覧

| ドキュメント | 内容 |
|---|---|
| [API仕様書](./API.md) | 全エンドポイントの詳細仕様 |
| [デプロイ手順書](./DEPLOY.md) | 本番環境へのデプロイ方法 |
