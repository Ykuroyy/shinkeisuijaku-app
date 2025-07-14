# 🌸 神経衰弱ゲーム 🌸

可愛いカードを使った神経衰弱ゲームです！AIと対戦して、同じカードを揃えましょう。

## 🎮 ゲームの特徴

- **20枚のカード**: 可愛い絵文字カード（桜、花、星、ハート、リボン、ユニコーン、虹、キャンディ、サーカス、メリーゴーランド）
- **AI対戦**: 1人でAIと対戦できます
- **可愛いデザイン**: 女子中高生向けのピンク系の可愛いデザイン
- **使いやすいUI**: パソコンが苦手な人でも簡単に操作できる
- **ゲーム履歴**: 過去のゲーム結果を保存・表示

## 🚀 機能

- 🎮 新しいゲーム開始（シャッフルアニメーション付き）
- ✨ カードマッチ時のキラキラ効果
- 🤖 AI対戦機能
- 📊 ゲーム履歴の保存・表示
- 🎯 カードをクリックすると浮き上がってから表になるアニメーション

## 🛠️ 技術スタック

- **バックエンド**: Python + Flask
- **フロントエンド**: HTML + CSS + JavaScript
- **データベース**: PostgreSQL (本番環境) / SQLite (開発環境)
- **デプロイ**: Render

## 📦 セットアップ

### ローカル開発

1. リポジトリをクローン
```bash
git clone <repository-url>
cd shinkeisuijaku-app
```

2. 仮想環境を作成・アクティベート
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 依存関係をインストール
```bash
pip install -r requirements.txt
```

4. アプリケーションを実行
```bash
python app.py
```

5. ブラウザで `http://localhost:5000` にアクセス

### 本番環境（Render）

1. Renderで新しいWeb Serviceを作成
2. GitHubリポジトリと連携
3. 環境変数を設定：
   - `DATABASE_URL`: PostgreSQLの接続URL
   - `SECRET_KEY`: セッション用の秘密鍵

## 🎯 ゲームの遊び方

1. 「🎮 新しいゲーム」ボタンをクリックしてゲーム開始
2. カードをクリックして2枚ずつめくる
3. 同じ絵柄のカードを揃えるとポイント獲得
4. カードが一致しない場合はAIのターン
5. すべてのカードを揃えたらゲーム終了

## 🎨 デザインの特徴

- **カラーパレット**: ピンク系のグラデーション
- **フォント**: 読みやすいArial
- **アニメーション**: カードのホバー効果とフリップアニメーション
- **レスポンシブ**: スマートフォンでも遊べる

## 📱 対応デバイス

- デスクトップPC
- タブレット
- スマートフォン

## 🔧 開発者向け

### プロジェクト構造
```
shinkeisuijaku-app/
├── app.py              # メインアプリケーション
├── requirements.txt    # Python依存関係
├── render.yaml        # Render設定
├── templates/
│   └── index.html     # メインHTMLテンプレート
└── README.md          # このファイル
```

### API エンドポイント

- `GET /` - メインページ
- `GET /api/new-game` - 新しいゲーム開始
- `POST /api/flip-card` - カードをめくる
- `GET /api/ai-turn` - AIのターン
- `POST /api/save-game` - ゲーム結果を保存
- `GET /api/game-history` - ゲーム履歴を取得

## 🎉 100本アプリ挑戦

このアプリは100本アプリ挑戦の11本目です！

---

**開発者**: アプリ開発初学者向けプロジェクト
**言語**: Python (Flask)
**デプロイ**: Render 