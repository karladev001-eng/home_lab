export default function Home() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold mb-2">Tech Memory</h1>
        <p className="text-gray-400">技術・アルゴリズム・設計パターンを収集・検索する知識DB</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <a href="/ingest" className="block p-6 rounded-lg border border-gray-700 hover:border-blue-500 transition-colors">
          <h2 className="text-lg font-semibold mb-2 text-blue-400">収集</h2>
          <p className="text-sm text-gray-400">URLやキーワードから技術情報を収集してDBに追加する</p>
        </a>
        <a href="/search" className="block p-6 rounded-lg border border-gray-700 hover:border-green-500 transition-colors">
          <h2 className="text-lg font-semibold mb-2 text-green-400">検索</h2>
          <p className="text-sm text-gray-400">課題・技術名・分野から関連技術を検索・推薦する</p>
        </a>
        <a href="/technologies" className="block p-6 rounded-lg border border-gray-700 hover:border-purple-500 transition-colors">
          <h2 className="text-lg font-semibold mb-2 text-purple-400">一覧</h2>
          <p className="text-sm text-gray-400">登録済みの技術カードを閲覧する</p>
        </a>
      </div>

      <div className="p-4 rounded-lg bg-gray-900 border border-gray-800">
        <h3 className="text-sm font-medium text-gray-300 mb-3">使用例</h3>
        <ul className="space-y-2 text-sm text-gray-400">
          <li>• 「少ない試行回数で良い候補を見つける技術を知りたい」</li>
          <li>• 「RAGの精度改善に使える技術を比較したい」</li>
          <li>• 「ゲーム開発のECSをAIエージェント管理に応用できるか知りたい」</li>
          <li>• URLを入力して技術カードを自動生成する</li>
        </ul>
      </div>
    </div>
  );
}
