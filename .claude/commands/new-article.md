---
description: AI編集部（10人）で保育ブログ記事を1本つくる。使い方: /new-article <テーマ>
argument-hint: <記事テーマ 例: 保育士 転職 タイミング>
---
あなたは「はっぴー保育ブログ」の**編集長**です。以下のテーマで記事を1本つくります。

テーマ: $ARGUMENTS

`CLAUDE.md` の編集方針を守り、次の順にサブエージェントへ仕事を振ってください。
各ステップの成果物は `drafts/<slug>/` に保存されます。前のステップの成果物ができてから次に進むこと。

1. **keyword-researcher** — キーワード・検索意図・競合調査 → `01-keyword.md`（slug もここで決める）
   - 既存記事と重複していたら、ここで止めて運営者に「新規作成か既存記事のリライトか」を確認する
2. **outline-planner** — タイトル案と見出し構成 → `02-outline.md`
3. **ライター**（構成で指定された1人: writer-genba / writer-career / writer-parents）→ `03-draft.md`
4. **fact-checker** — 事実確認・出典追加 → `04-factcheck.md`
5. **proofreader** — 校正 → `05-edited.md`
6. **seo-optimizer** — frontmatter・内部リンクを付けて `src/content/posts/<slug>.md` を作成
7. **monetization-planner** — アフィリエイト配置・PR表記 → `07-monetize.md`
8. **sns-promoter** — SNS投稿文 → `08-sns.md`

7 と 8 は並列で走らせてよい。

最後に `npm run check:articles` を実行し、問題があれば直してください。

## 編集長としての最終報告（運営者向け）
以下を短くまとめて報告する:
- 記事タイトルとファイルパス
- **運営者がやること**: `<!-- 体験談 -->` の加筆箇所数、ファクトチェックで「要人間確認」になった項目
- 収益化メモ（貼った案件 / 提携すべき案件）
- 公開手順: 確認・加筆が終わったら frontmatter の `humanReviewed: true` と `draft: false` にする
