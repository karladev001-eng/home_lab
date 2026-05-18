# Slide Templates

必要時にだけ生成するスライド用テンプレート群です。

主なファイル:

- `marp/theme.css`: Marp 用の共有テーマ
- `marp/style-guide.md`: スライド運用メモ
- `sample-slides/`: 過去の参考スライド置き場
- `assets/`: 図版、ロゴ、背景など

通常は `research/slides/templates/` にコピーして使います。

## テンプレート追加方法

1. `slides/` 配下に用途別ディレクトリを作る

- 例: `slides/seminar-compact/`
- 例: `slides/conference-2026/`

2. その中に最低限のテンプレートを置く

- `theme.css` または利用するテーマ本体
- `style-guide.md`
- 必要なら参考資料やサンプル断片

3. 共有素材は `assets/`、過去例は `sample-slides/` に分けて置く

4. この README に「何向けのテンプレートか」を追記する

## 追加時の指針

- スライドは HTML プレゼンの二次出力という前提を崩さない
- 1 スライド 1 メッセージを保てる密度にする
- フォント、余白、強調色は少数に絞る
- 特定イベント依存の要素はディレクトリを分ける

## 研究プロジェクトへの持ち込み先

- `theme.css` などのテーマ → `research/slides/templates/`
- `style-guide.md` → `research/slides/templates/style-guide.md`
- 素材 → `research/slides/assets/`
