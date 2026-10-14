import { getCollection } from 'astro:content';

// 公開条件: draft ではなく、かつ運営者が内容を確認済み（humanReviewed）であること。
// 開発サーバーでは確認前の記事もプレビューできるようにする。
export async function getPublishedPosts() {
  const posts = await getCollection('posts', ({ data }) =>
    import.meta.env.DEV ? true : !data.draft && data.humanReviewed,
  );
  return posts.sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());
}
