# happyhoiku-blog（はっぴー保育ブログ）

保育士・保育学生・保護者向けの情報ブログ。**10人のAI編集部**（Claude Code サブエージェント）が下調べ〜下書き〜SNS投稿文まで作り、運営者が体験談を加えて公開します。

- 運用ルールとAI編集部の一覧: [`CLAUDE.md`](CLAUDE.md)
- 収益化ロードマップ: [`docs/monetization.md`](docs/monetization.md)

## 使い方

```bash
npm install
npm run dev            # http://localhost:4321 （下書きもプレビューできる）
```

Claude Code で:

```
/new-article 保育士 転職 タイミング   # 記事を1本つくる
/monthly-plan 2026-12                 # 月間の記事計画
/rewrite shinbunshi-asobi-1-2sai      # 既存記事のリライト
```

## 公開の流れ
1. AI編集部が `src/content/posts/<slug>.md` を `draft: true` で作る
2. 運営者が `<!-- 体験談 -->` を埋め、内容を確認
3. `humanReviewed: true` と `draft: false` にして main に push → GitHub Pages に自動公開

初回のみ: リポジトリの Settings → Pages → Source を「GitHub Actions」にする。
