# happyhoiku-blog

Claude（AI）が保育士転職ブログ（happyhoiku-tenshoku.com）の記事を書き、WordPress に **毎朝7時（日本時間）** に **下書き保存** します。内容を確認して「公開」を押すだけで記事が公開されます。

## しくみ

1. GitHub Actions が決まった時間に `scripts/auto_post.py` を実行します
2. `content/keywords.csv`（KW選定シート）から、`執筆済み` が空のキーワードを **優先度の高い順（最高→高→中）** に1つ選びます
3. そのキーワードの検索意図・推奨記事タイプ・備考と、`content/blog_profile.md` の方針に沿って Claude が記事を書きます。既存記事への内部リンクも入れます
4. タイトル入りのアイキャッチ画像を作り、本文には Pexels の無料写真を2〜3枚入れて、WordPress に **下書き** として保存します（タグも自動で付きます）
5. `keywords.csv` の `執筆済み` に日付、`URL` に記事URLが入り、`content/posted.tsv` に投稿履歴が残ります

未執筆のキーワードがなくなったら、AI が既存記事と重ならないテーマを自分で選びます。

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
| `PEXELS_API_KEY` | （任意）Pexels の API キー。登録すると本文に写真が入ります |

> パスワードやキーは GitHub 上で暗号化して保存され、登録後は本人も含めて誰も中身を見られません。Claude に伝える必要もありません。
> アプリケーションパスワードは WordPress のログインパスワードとは別物で、不要になったらプロフィール画面からいつでも取り消せます。

**Variables**（任意）

| 名前 | 値 |
| --- | --- |
| `WP_POST_STATUS` | `draft`（下書きに保存・既定）または `publish`（すぐ公開） |
| `WP_CATEGORY_ID` | 投稿先カテゴリーの ID（複数はカンマ区切り） |

### Pexels の API キー（任意・無料）
https://www.pexels.com/ja-jp/api/ でアカウントを作り、「API キーを取得」から発行します。登録しない場合はアイキャッチ画像だけが付きます。

### 4. 試しに動かす
**Actions → 記事の自動投稿 → Run workflow** から手動実行できます。「投稿せずに生成結果だけ確認する」にチェックを入れると、投稿せずにログで記事を確認できます。

## 日々の使い方

### 毎朝の確認と公開
1. WordPress 管理画面の「投稿」→「投稿一覧」を開くと、その日の記事が「下書き」で入っています
   （GitHub の Actions の実行結果ページにも、編集画面へのリンクが表示されます）
2. 記事を開いて、内容・写真・アイキャッチを確認し、必要なら直します
3. 右上の「公開」を押せば完了です

- **キーワードを追加** → スプレッドシートに行を足したら CSV で書き出し、`content/keywords.csv` を置き換える（`執筆済み` と `URL` 列はそのまま残してください）
- **紹介サービスの情報を追加** → `content/blog_profile.md` の「紹介するサービス」に確認済みの事実と紹介リンクを書く
- **記事の雰囲気を変える** → `content/blog_profile.md` を編集
- **投稿の曜日・時間を変える** → `.github/workflows/auto-post.yml` の `cron` を編集（時刻は UTC = 日本時間 − 9時間）

## 手元で実行する場合

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=... WP_URL=... WP_USER=... WP_APP_PASSWORD=...
python scripts/auto_post.py --dry-run   # 投稿せず preview/ に記事と画像を保存
python scripts/auto_post.py             # 投稿まで
```
