# はっぴー保育ブログ — AI編集部の運用ルール

保育士・保育学生・保護者向けの情報ブログ。Astro 5 の静的サイトで、記事は `src/content/posts/*.md`。

## AI編集部（10人）
`.claude/agents/` にいる10人のサブエージェントで記事を作る。メインの Claude は**編集長**として振り分け・最終報告を行う。

| # | エージェント | 役割 |
|---|---|---|
| 1 | keyword-researcher | キーワード・検索意図・競合調査 |
| 2 | outline-planner | タイトル案・見出し構成 |
| 3 | writer-genba | ライター（現場のコツ・遊び・製作） |
| 4 | writer-career | ライター（キャリア・転職）※収益の柱 |
| 5 | writer-parents | ライター（保護者向け） |
| 6 | fact-checker | 事実確認・出典付け |
| 7 | proofreader | 校正・AIっぽさ除去 |
| 8 | seo-optimizer | frontmatter・内部リンク・記事ファイル化 |
| 9 | monetization-planner | アフィリエイト配置・PR表記・収益計画 |
| 10 | sns-promoter | X / Instagram / Pinterest / Threads 投稿文 |

コマンド:
- `/new-article <テーマ>` — 1本つくる（1→2→3→6→7→8→9/10）
- `/monthly-plan [YYYY-MM]` — 月間の記事計画
- `/rewrite <slug>` — 既存記事のリライト

中間成果物は `drafts/<slug>/`（gitで管理。どのAIが何をしたか追えるように）。

## 絶対に守ること
1. **人間の確認なしに公開しない。** AI は `humanReviewed: true` / `draft: false` に変更しない。
   本番ビルドはこの2つが揃った記事だけを出力する（`src/lib/posts.ts`）。
2. **体験談を捏造しない。** 体験談の場所には `<!-- 体験談: ... -->` を残し、運営者が書く。
3. **量産しすぎない。** Google は「検索順位操作を目的とした大量生成コンテンツ」をスパム扱いする。
   独自の体験・一次情報を足せる本数（週2〜4本目安）にとどめる。
4. **ステマ規制（景品表示法）対応。** 広告を含む記事は `hasAffiliate: true` にする（PR表記が自動で出る）。
   アフィリエイトリンクには `rel="sponsored"` を付ける（`AffiliateBox` が自動で付与）。
5. **子どもの健康・安全（YMYL）は一次情報で裏取り。** 診断的な断定はしない。

## 文体
- です・ます調、「子ども」表記、1文60字以内目安、結論ファースト
- 「いかがでしたか」等の定型文禁止

## 確認コマンド
- `npm run check:articles` — 記事のルール違反チェック
- `npm run build` — 本番ビルド
