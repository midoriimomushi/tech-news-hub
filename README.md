# ⚡ Tech News Hub (はてなブックマーク技術ニュースダイジェスト)

はてなブックマークの「テクノロジー全般」「AI・機械学習」「プログラミング」の各新着エントリーを自動または手動バッチで集約し、日付ごとに一覧表示する**完全無料（GitHub Pages + GitHub Actions）**の自分専用ニュースダッシュボードです。

---

## 🌟 特徴・機能

- **完全無料 (0円)**: GitHub Actions + GitHub Pages のみで動作。
- **固定URLでアクセス**: 毎日同じURLを開くだけで最新の技術ニュースにアクセスできます（スマホのホーム画面追加に対応）。
- **過去ログ閲覧機能**: 過去の日付を選択して過去のニュースを遡って読めます。
- **カテゴリフィルター & リアルタイム検索**: 「AI・機械学習」「プログラミング」「テクノロジー全般」の切り替え、キーワード検索に対応。
- **「あとで読む」お気に入り機能**: 気になる記事をローカルストレージに保持可能。
- **自動化 (全自動)**: 毎日朝 7:00 JST に自動で最新データを更新。手動実行ボタンも用意。

---

## 🚀 初回セットアップ手順（簡単3ステップ）

### 1. GitHubリポジトリの作成とプッシュ
作成したこのコード一式を、ご自身の GitHub リポジトリ（Public または Private）にプッシュします。

```bash
git init
git add .
git commit -m "feat: initial commit for Tech News Hub"
git branch -M main
git remote add origin https://github.com/<あなたのユーザー名>/<リポジトリ名>.git
git push -u origin main
```

### 2. GitHub Pages の有効化
1. GitHub上のリポジトリ画面で **[Settings]** タブを開きます。
2. 左メニューの **[Pages]** を選択します。
3. **Build and deployment** の **Source** で **`Deploy from a branch`** を選択。
4. **Branch** を `main` / `/docs` に設定して **[Save]** ボタンをクリックします。

数分後に `https://<あなたのユーザー名>.github.io/<リポジトリ名>/` という固定URLが発行されます！

### 3. GitHub Actions の権限確認
1. リポジトリの **[Settings]** -> **[Actions]** -> **[General]** を開きます。
2. **Workflow permissions** で **`Read and write permissions`** が選択されていることを確認して保存します。

---

## 🔄 手動での最新ニュース更新方法

通常は毎日朝 7:00 (JST) に全自動で最新ニュースが更新されますが、いつでも手動で今すぐ更新できます：

1. GitHubリポジトリの **[Actions]** タブを開く。
2. 左側の **[Daily Tech News Fetcher]** ワークフローを選択。
3. 右上の **[Run workflow]** ボタンをクリック。

---

## 📁 ディレクトリ構造

```text
.
├── .github/
│   └── workflows/
│       └── fetch-news.yml   # 毎日自動実行＆GitHubデプロイ設定
├── scripts/
│   └── fetch_rss.py         # はてブRSS取得・JSON出力Pythonスクリプト
├── docs/                    # GitHub Pages 公開用静的Webサイト
│   ├── index.html           # ニュースダッシュボード画面
│   ├── style.css            # モダンスタイル（ダークモード対応）
│   ├── app.js               # フロントエンド表示・フィルタリング処理
│   └── data/                # ニュースデータの蓄積JSON
│       ├── dates.json       # 過去ログ日付リスト
│       ├── latest.json      # 最新ニュース
│       └── YYYY-MM-DD.json  # 日付別アーカイブ
└── README.md
```
