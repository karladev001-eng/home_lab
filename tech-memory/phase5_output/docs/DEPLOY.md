# デプロイ手順書 — tech-memory

## 使用インフラ

Docker Compose（ローカルまたはVPS）。
PostgreSQL 16 + pgvector を含む全サービスをDockerコンテナで管理します。

---

## 本番環境へのデプロイ

### 前提条件

- VPS / サーバーに Docker と docker-compose がインストール済み
- Anthropic API Key・OpenAI API Key を取得済み
- サーバーのポート 3000（Web）と 8000（API）を公開可能

---

### ステップ 1: サーバーにコードを転送する

```bash
# ローカルからサーバーへ転送
scp -r ./phase3_code user@your-server:/opt/tech-memory/
ssh user@your-server
cd /opt/tech-memory/
```

または:
```bash
# サーバー上でリポジトリをクローン
git clone <リポジトリURL> /opt/tech-memory
cd /opt/tech-memory
```

---

### ステップ 2: 本番用環境変数を設定する

```bash
cp phase3_code/.env.example phase3_code/.env
nano phase3_code/.env
```

以下の値を本番用に設定してください:

```env
# Database（強力なパスワードに変更必須）
POSTGRES_USER=techuser
POSTGRES_PASSWORD=<強力なランダムパスワード>
POSTGRES_DB=techdb
DATABASE_URL=postgresql+asyncpg://techuser:<パスワード>@db:5432/techdb

# AI APIs（必須）
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-...

# App settings
APP_ENV=production
LOG_LEVEL=info

# Frontend（サーバーのIPまたはドメインに変更）
NEXT_PUBLIC_API_URL=http://your-server-ip:8000
```

**セキュリティ注意事項**:
- `POSTGRES_PASSWORD` は必ず変更してください
- `.env` ファイルのパーミッションを制限: `chmod 600 phase3_code/.env`
- `.env` ファイルをGitにコミットしないでください

---

### ステップ 3: 本番用ビルドを実行する

開発モード（ボリュームマウント＋ホットリロード）のデプロイを避けるため、
本番環境では `docker-compose.override.yml` を作成するか、`command` を変更します。

```bash
# 本番用コマンドで上書き（docker-compose.override.yml）
cat > phase3_code/docker-compose.override.yml << 'EOF'
services:
  api:
    command: uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 2
    volumes: []  # ボリュームマウント無効化
  web:
    volumes: []  # ボリュームマウント無効化（ビルド済みイメージを使用）
EOF
```

---

### ステップ 4: サービスを起動する

```bash
cd phase3_code
docker-compose up -d --build
```

> 初回はDockerイメージのビルドで5〜10分かかります。
> 以降の更新は `docker-compose up -d --build` で再ビルドできます。

起動状態の確認:
```bash
docker-compose ps
```

> 全サービスの `State` が `Up` になれば成功です。

---

### ステップ 5: データベースをマイグレーションする

```bash
docker-compose exec api alembic upgrade head
```

> テーブルが作成されます。`Running upgrade ... -> 001_initial_schema` と表示されれば成功です。

---

### ステップ 6: 稼働確認する

```bash
# APIヘルスチェック
curl http://your-server-ip:8000/api/v1/health
# 期待レスポンス: {"success": true, "data": {"status": "ok", "db": "ok", "version": "0.1.0"}}

# フロントエンド確認
curl -I http://your-server-ip:3000
# 期待レスポンス: HTTP/1.1 200 OK
```

ブラウザで `http://your-server-ip:3000` を開いてアプリが表示されれば完了です。

---

## リバースプロキシ（Nginx）の設定（任意）

ポート80/443でHTTPSを使用する場合はNginxをリバースプロキシとして設定します。

```nginx
# /etc/nginx/sites-available/tech-memory
server {
    listen 80;
    server_name your-domain.com;

    # フロントエンド
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # API（直接アクセス用）
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        # タイムアウトを60秒に（URL収集の長時間処理対応）
        proxy_read_timeout 60s;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/tech-memory /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

HTTPS化にはCertbotを使用:
```bash
sudo certbot --nginx -d your-domain.com
```

---

## 更新デプロイ（既存環境への更新）

```bash
cd /opt/tech-memory

# 最新コードを取得
git pull origin main

# コンテナを再ビルドして起動
cd phase3_code
docker-compose up -d --build

# DBマイグレーション（新規テーブルがある場合）
docker-compose exec api alembic upgrade head
```

---

## ロールバック

デプロイに問題が発生した場合:

```bash
# 前のGitコミットに戻す
git revert HEAD
git push origin main

# またはタグを使って特定バージョンに戻す
git checkout v0.3-code
cd phase3_code
docker-compose up -d --build
```

DBスキーマのロールバック:
```bash
docker-compose exec api alembic downgrade -1
```

---

## バックアップ

### DBのバックアップ

```bash
# バックアップを作成
docker-compose exec db pg_dump -U techuser techdb > backup_$(date +%Y%m%d_%H%M%S).sql

# バックアップからリストア
docker-compose exec -T db psql -U techuser techdb < backup_20260516_120000.sql
```

### 定期バックアップ（cron）

```bash
# crontabに追加（毎日午前3時にバックアップ）
0 3 * * * cd /opt/tech-memory/phase3_code && docker-compose exec -T db pg_dump -U techuser techdb > /opt/backups/techdb_$(date +\%Y\%m\%d).sql
```

---

## ログの確認

```bash
# 全サービスのログ
docker-compose logs -f

# APIのみ
docker-compose logs -f api

# DBのみ
docker-compose logs -f db
```

---

## サービスの停止・再起動

```bash
# 停止
docker-compose stop

# 停止してコンテナ削除（DBデータは保持）
docker-compose down

# 停止してデータも削除（完全クリア）
docker-compose down -v
```

---

## トラブルシューティング

### APIが起動しない

```bash
docker-compose logs api
```

`ANTHROPIC_API_KEY` や `DATABASE_URL` の設定ミスがよく見られます。

### DBに接続できない

`DATABASE_URL` のホストが `db`（コンテナ名）になっているか確認:
```
DATABASE_URL=postgresql+asyncpg://techuser:techpass@db:5432/techdb
```

### ポートが使用中

```bash
# 5432ポートを使用しているプロセス
lsof -i :5432
# 8000ポートを使用しているプロセス
lsof -i :8000
```

### Alembicのマイグレーションが失敗する

pgvectorエクステンションが有効か確認:
```bash
docker-compose exec db psql -U techuser -d techdb -c "\dx"
```

`vector` が表示されなければ:
```bash
docker-compose exec db psql -U techuser -d techdb -c "CREATE EXTENSION IF NOT EXISTS vector;"
```
