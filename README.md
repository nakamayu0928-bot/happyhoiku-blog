# happyhoiku-blog

Claude（AI）が保育ブログの記事を書き、WordPress に **月・水・金の朝7時（日本時間）** に自動投稿します。

## しくみ

1. GitHub Actions が決まった時間に `scripts/auto_post.py` を実行します
2. `content/topics.txt` の一番上のテーマで、`content/blog_profile.md` の方針に沿って Claude が記事を書きます
3. WordPress の REST API で投稿します（タグも自動で付きます）
4. 使ったテーマは `topics.txt` から消え、`content/posted.tsv` に投稿履歴が残ります

テーマが空になったら、AI が過去記事と重ならないテーマを自分で選びます。

## 初期設定

### 1. WordPress でアプリケーションパスワードを発行
WordPress 管理画面 →「ユーザー」→「プロフィール」→ 下の方の「アプリケーションパスワード」で名前（例: `auto-post`）を入れて発行します。表示されたパスワードを控えておきます。

### 2. Claude API キーを用意
https://platform.claude.com/ で API キーを発行します（記事1本あたり数十円程度の利用料がかかります）。

### 3. GitHub に登録
リポジトリの **Settings → Secrets and variables → Actions** で登録します。

**Secrets**（必須）

| 名前 | 値 |
| --- | --- |
| `ANTHROPIC_API_KEY` | Claude API キー |
| `WP_URL` | ブログの URL（例: `https://happyhoiku.example.com`） |
| `WP_USER` | WordPress のユーザー名 |
| `WP_APP_PASSWORD` | 手順1のアプリケーションパスワード |

**Variables**（任意）

| 名前 | 値 |
| --- | --- |
| `WP_POST_STATUS` | `publish`（すぐ公開・既定）または `draft`（下書きに保存） |
| `WP_CATEGORY_ID` | 投稿先カテゴリーの ID（複数はカンマ区切り） |

> はじめのうちは `WP_POST_STATUS` を `draft` にして、内容を確認してから公開するのがおすすめです。

### 4. 試しに動かす
**Actions → 記事の自動投稿 → Run workflow** から手動実行できます。「投稿せずに生成結果だけ確認する」にチェックを入れると、投稿せずにログで記事を確認できます。

## 日々の使い方

- **書いてほしいテーマを追加** → `content/topics.txt` に1行ずつ追記
- **記事の雰囲気を変える** → `content/blog_profile.md` を編集
- **投稿の曜日・時間を変える** → `.github/workflows/auto-post.yml` の `cron` を編集（時刻は UTC = 日本時間 − 9時間）

## 手元で実行する場合

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=... WP_URL=... WP_USER=... WP_APP_PASSWORD=...
python scripts/auto_post.py --dry-run   # 生成だけ
python scripts/auto_post.py             # 投稿まで
```
