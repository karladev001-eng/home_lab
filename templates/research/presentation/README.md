# HTML Presentation Templates

共有用の HTML プレゼンページに使うテンプレート群です。

主なファイル:

- `base/index.html`: 最小構成の HTML テンプレート
- `base/styles.css`: ベーススタイル
- `base/style-guide.md`: デザイン運用メモ
- `assets/`: 共有ロゴ、背景、図版など

通常はこの内容を各研究プロジェクトの `research/presentation/` 配下へコピーして使います。

## テンプレート追加方法

1. `presentation/` 配下に新しいテンプレート用ディレクトリを作る

- 例: `presentation/lab-meeting/`
- 例: `presentation/paper-reading/`

2. その中に次のファイルを置く

- `index.html`: ページ構造の雛形
- `styles.css`: 見た目の定義
- `style-guide.md`: ルール、意図、使用上の注意

3. 必要なら `assets/` に共通素材を追加する

4. どんな場面向けのテンプレートかをこの README に追記する

## 追加時の指針

- まずは静的な `HTML + CSS` を優先する
- 重い依存やビルド前提の構成は避ける
- 見出し、本文、図表、注釈の階層が最初から分かる構造にする
- `TODO` を置ける余白を残し、未確認情報を埋め込まない

## 研究プロジェクトへの持ち込み先

- `index.html` → `research/presentation/index.html`
- `styles.css` → `research/presentation/styles.css`
- `style-guide.md` → `research/presentation/templates/style-guide.md`
- 画像やロゴ → `research/presentation/assets/`
