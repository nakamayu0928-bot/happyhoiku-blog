import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const posts = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/posts' }),
  schema: z.object({
    title: z.string().max(60),
    description: z.string().max(160),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    category: z.enum(['現場のコツ', '遊び・製作', 'キャリア・転職', '保護者向け', '制度・ニュース']),
    tags: z.array(z.string()).default([]),
    // 執筆を担当したAIエージェント名（内部管理用。表示はしない）
    agent: z.string().optional(),
    // 人間（運営者）が内容を確認したか。false の記事は公開しない
    humanReviewed: z.boolean().default(false),
    // アフィリエイトリンクを含む場合は true（PR表記を自動表示）
    hasAffiliate: z.boolean().default(false),
    // 記事末尾に表示するアフィリエイト案件ID（src/data/affiliates.ts のキー）
    affiliates: z.array(z.string()).default([]),
    draft: z.boolean().default(true),
  }),
});

export const collections = { posts };
