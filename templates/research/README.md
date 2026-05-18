# Research Templates

このディレクトリは、研究プロジェクトで使い回す共有テンプレートの保存場所です。

想定用途:

- `presentation/`: 軽量な HTML プレゼンページのベース
- `slides/`: 必要時のみ生成するスライド用テンプレート

新しい研究プロジェクトでは、ここにあるファイルを `research/presentation/` や
`research/slides/` にコピーして使う想定です。

## テンプレート追加方法

1. 追加先を選ぶ

- HTML プレゼン用なら `presentation/`
- スライド用なら `slides/`

2. 既存テンプレートを壊さないように、新しいサブディレクトリを作る

- 例: `presentation/lab-a/`
- 例: `slides/conf-2026/`

3. 最低限必要なファイルを置く

- HTML プレゼン: `index.html`, `styles.css`, `style-guide.md`
- スライド: `theme.css` またはテンプレート本体, `style-guide.md`

4. 画像やロゴなどの補助素材は `assets/` に入れる

5. 追加したテンプレートの用途を各 README に追記する

## 命名の目安

- ディレクトリ名は用途が分かる短い名前にする
- 個人名より研究室名、発表名、イベント名を優先する
- 例: `lab-meeting`, `thesis-defense`, `conference-poster`

## 運用メモ

- 共通の雛形は残し、特定用途の派生版は別ディレクトリに分ける
- 未確定素材は入れず、再利用できるものだけを共有テンプレートに置く
- 研究プロジェクト側へコピーした後の個別調整は、共有テンプレートへ即時逆流させなくてよい
