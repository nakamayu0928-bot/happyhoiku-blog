// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// 公開URLは環境変数で切り替える（GitHub Pages / 独自ドメインどちらでも動くように）
export default defineConfig({
  site: process.env.SITE_URL || 'https://example.com',
  base: process.env.BASE_PATH || '/',
  integrations: [sitemap()],
});
