# SNS自動投稿の設定

公開済みの記事を、GitHub Actions が **毎日 12:15 と 21:15（日本時間）** に X・Threads・Bluesky へ自動投稿します。
**認証情報を登録したSNSだけ** 投稿されます（未登録のSNSはスキップ）。まずは無料で簡単な Bluesky と Threads から始めるのがおすすめです。

登録先: GitHub のリポジトリ → **Settings → Secrets and variables → Actions → New repository secret**

## Bluesky（いちばん簡単・無料）
1. Bluesky アプリで **設定 → プライバシーとセキュリティ → アプリパスワード** を作成
2. Secrets に登録
   - `BLUESKY_HANDLE`: `xxxx.bsky.social`
   - `BLUESKY_APP_PASSWORD`: 作成したアプリパスワード（ログイン用パスワードは使わない）

## Threads（無料）
1. [Meta for Developers](https://developers.facebook.com/) でアプリを作成し、ユースケースに「Threads API にアクセス」を追加
2. 権限 `threads_basic` と `threads_content_publish` を付け、自分の Threads アカウントをテスターに追加して承認
3. アクセストークンを発行し、**長期トークン（有効期限60日）** に交換
4. Secrets に登録
   - `THREADS_ACCESS_TOKEN`: 長期トークン
   - `THREADS_USER_ID`: （任意）Threads のユーザーID。空なら `me` を使う

> ⚠️ 長期トークンは **60日で失効** します。期限が切れる前に、Meta の更新用エンドポイント
> （`refresh_access_token`）で新しいトークンを取得し、Secret を差し替えてください。
> 失効すると Actions の「SNS auto post」が赤くなるので気づけます。

## X（旧Twitter）
1. [X Developer Portal](https://developer.x.com/) でプロジェクトとアプリを作成
2. アプリの **User authentication settings** で権限を **Read and write** にする（※先にこれをしないと投稿できない）
3. **Keys and tokens** で API Key/Secret と Access Token/Secret を発行（権限変更後に再発行する）
4. Secrets に登録: `X_API_KEY` / `X_API_SECRET` / `X_ACCESS_TOKEN` / `X_ACCESS_SECRET`

> ⚠️ X API は料金プラン・無料枠が頻繁に変わります。登録前に Developer Portal で、
> 投稿に必要なプランと費用を必ず確認してください。この仕組みは1日最大2投稿です。

## 動作確認
1. Actions タブ → **SNS auto post** → **Run workflow**（「投稿せずに内容だけ確認する」にチェックが入った状態）
2. ログに、次に投稿される文面が表示されれば OK
3. チェックを外して実行すると本当に投稿されます

手元で確認する場合: `npm run sns:dry-run`

## 細かい設定（Settings → Variables）
| 変数 | 意味 | 既定値 |
|---|---|---|
| `SITE_URL` | 記事URLの先頭（独自ドメインにしたら設定） | `https://<ユーザー名>.github.io/<リポジトリ名>/` |
| `SNS_RESHARE_DAYS` | 何日たった記事を再シェアするか。`0` で再シェアしない | `30` |

投稿時刻を変えたい場合は `.github/workflows/sns.yml` の `cron`（UTC、日本時間−9時間）を編集します。

## Instagram・Pinterest について
画像が必須のため自動投稿には含めていません。`drafts/<slug>/08-sns.md` にカルーセル構成やピンの文面があるので、
Canva などで画像を作って手動で投稿してください（遊び・製作の記事は Pinterest と特に相性が良いです）。

## しくみ
- 投稿文: `sns/<slug>.json`（AI編集部の sns-promoter が記事ごとに作る）
- 投稿履歴: `sns/posted.json`（Actions が自動でコミット。二重投稿防止に使うので手で編集しない）
- 記事URLには `utm_source=x` などが付くので、Google アナリティクスでどのSNSから来たか分かります
