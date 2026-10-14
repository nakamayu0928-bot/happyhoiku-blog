---
description: 既存記事をAI編集部でリライト（情報更新・順位改善）する。使い方: /rewrite <slug>
argument-hint: <slug>
---
あなたは編集長です。`src/content/posts/$ARGUMENTS.md` をリライトします。

1. **keyword-researcher** — 現在の上位記事と比べて足りない内容を調査 → `drafts/$ARGUMENTS/rewrite-01-gap.md`
2. **fact-checker** — 古くなった数字・制度を最新化
3. ギャップを埋める加筆を、記事のカテゴリに対応するライターに依頼
4. **proofreader** → **seo-optimizer** → **monetization-planner** の順で仕上げ
5. frontmatter の `updatedDate` を今日にし、`humanReviewed` を `false` に戻す（運営者の再確認が必要なため）

運営者が書いた体験談部分は削除・改変しないこと。
