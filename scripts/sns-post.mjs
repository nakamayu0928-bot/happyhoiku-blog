// SNS自動投稿。公開済み記事の投稿文（sns/<slug>.json）を X / Threads / Bluesky に投稿する。
//
//   node scripts/sns-post.mjs --check     投稿文の文字数・形式チェックのみ
//   node scripts/sns-post.mjs --dry-run   何が投稿されるか表示するだけ（投稿・記録しない）
//   node scripts/sns-post.mjs             投稿して sns/posted.json に記録する
//
// 1回の実行で、各SNSに最大1件だけ投稿する（スパム判定を避けるため）。
// 優先順: まだそのSNSに出していない公開記事（古い順）→ 再シェア（最後の投稿から RESHARE_DAYS 日以上たった記事）
// 認証情報が未設定のSNSはスキップする。
import { createHmac, randomBytes } from 'node:crypto';
import { readdir, readFile, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';

const POSTS_DIR = 'src/content/posts';
const SNS_DIR = 'sns';
const LOG_FILE = join(SNS_DIR, 'posted.json');
const PLATFORMS = ['x', 'threads', 'bluesky'];

const args = new Set(process.argv.slice(2));
const CHECK = args.has('--check');
const DRY_RUN = args.has('--dry-run') || process.env.DRY_RUN === '1';
const env = process.env;
const RESHARE_DAYS = Number(env.RESHARE_DAYS ?? 30); // 0 で再シェアしない
const SITE_URL = (env.SITE_URL ?? 'https://example.com/').replace(/\/?$/, '/');

// ---------- 記事と投稿文の読み込み ----------

function frontmatter(text) {
  const fm = text.match(/^---\n([\s\S]*?)\n---/)?.[1] ?? '';
  const get = (key) => fm.match(new RegExp(`^${key}:\\s*(.+)$`, 'm'))?.[1].trim().replace(/^"(.*)"$/, '$1');
  return { title: get('title'), description: get('description'), pubDate: get('pubDate'), draft: get('draft'), humanReviewed: get('humanReviewed') };
}

async function loadArticles() {
  const files = (await readdir(POSTS_DIR).catch(() => [])).filter((f) => f.endsWith('.md'));
  const articles = [];
  for (const file of files) {
    const slug = file.replace(/\.md$/, '');
    const fm = frontmatter(await readFile(join(POSTS_DIR, file), 'utf8'));
    const snsPath = join(SNS_DIR, `${slug}.json`);
    const sns = existsSync(snsPath) ? JSON.parse(await readFile(snsPath, 'utf8')) : null;
    articles.push({ slug, ...fm, published: fm.draft === 'false' && fm.humanReviewed === 'true', sns });
  }
  return articles.sort((a, b) => String(a.pubDate).localeCompare(String(b.pubDate)));
}

const articleUrl = (slug, platform) =>
  `${SITE_URL}posts/${slug}/?utm_source=${platform}&utm_medium=social&utm_campaign=sns-auto`;

// ---------- 文字数 ----------

// X の文字数（twitter-text 準拠の簡易版）: 日本語は2、URLは23としてカウント。上限280
function xLength(text) {
  let n = 0;
  for (const part of text.split(/(https?:\/\/\S+)/)) {
    if (/^https?:\/\//.test(part)) { n += 23; continue; }
    for (const ch of part) {
      const c = ch.codePointAt(0);
      const light = c <= 0x10ff || (c >= 0x2000 && c <= 0x200d) || (c >= 0x2010 && c <= 0x201f) || (c >= 0x2032 && c <= 0x2037);
      n += light ? 1 : 2;
    }
  }
  return n;
}
const graphemes = (text) => [...new Intl.Segmenter('ja', { granularity: 'grapheme' }).segment(text)].length;

// プラットフォームごとの最終的な投稿本文
function compose(platform, text, slug) {
  // Bluesky はリンクカードで記事に飛ばすので本文にURLを入れない
  return platform === 'bluesky' ? text : `${text}\n${articleUrl(slug, platform)}`;
}

const LIMITS = {
  x: { max: 280, len: xLength, unit: '（日本語は1文字=2でカウント）' },
  threads: { max: 500, len: (t) => [...t].length, unit: '' },
  bluesky: { max: 300, len: graphemes, unit: '' },
};

function validate(article) {
  const problems = [];
  if (!article.sns) return problems;
  for (const platform of PLATFORMS) {
    const list = article.sns[platform];
    if (list === undefined) continue;
    if (!Array.isArray(list) || list.some((t) => typeof t !== 'string' || !t.trim())) {
      problems.push(`${platform}: 文字列の配列にしてください`);
      continue;
    }
    list.forEach((text, i) => {
      const { max, len, unit } = LIMITS[platform];
      const n = len(compose(platform, text, article.slug));
      if (n > max) problems.push(`${platform}[${i}]: ${n}/${max} 文字${unit}で長すぎます`);
      if (/https?:\/\//.test(text)) problems.push(`${platform}[${i}]: URLは自動で付くので本文に書かないでください`);
    });
  }
  return problems;
}

// ---------- 各SNSへの投稿 ----------

const rfc3986 = (s) => encodeURIComponent(s).replace(/[!'()*]/g, (c) => `%${c.charCodeAt(0).toString(16).toUpperCase()}`);

// OAuth 1.0a 署名（X API のユーザー認証）
export function oauthHeader({ method, url, consumerKey, consumerSecret, token, tokenSecret, nonce, timestamp }) {
  const oauth = {
    oauth_consumer_key: consumerKey,
    oauth_nonce: nonce ?? randomBytes(16).toString('hex'),
    oauth_signature_method: 'HMAC-SHA1',
    oauth_timestamp: timestamp ?? String(Math.floor(Date.now() / 1000)),
    oauth_token: token,
    oauth_version: '1.0',
  };
  const u = new URL(url);
  const params = { ...Object.fromEntries(u.searchParams), ...oauth };
  const paramString = Object.keys(params).sort().map((k) => `${rfc3986(k)}=${rfc3986(params[k])}`).join('&');
  const base = [method.toUpperCase(), rfc3986(`${u.origin}${u.pathname}`), rfc3986(paramString)].join('&');
  oauth.oauth_signature = createHmac('sha1', `${rfc3986(consumerSecret)}&${rfc3986(tokenSecret)}`).update(base).digest('base64');
  return 'OAuth ' + Object.keys(oauth).sort().map((k) => `${rfc3986(k)}="${rfc3986(oauth[k])}"`).join(', ');
}

async function request(url, init) {
  const res = await fetch(url, init);
  const body = await res.text();
  if (!res.ok) throw new Error(`${res.status} ${url.split('?')[0]}: ${body.slice(0, 300)}`);
  return body ? JSON.parse(body) : {};
}

const clients = {
  x: {
    enabled: () => env.X_API_KEY && env.X_API_SECRET && env.X_ACCESS_TOKEN && env.X_ACCESS_SECRET,
    async post(text) {
      const url = 'https://api.x.com/2/tweets';
      const auth = oauthHeader({
        method: 'POST', url,
        consumerKey: env.X_API_KEY, consumerSecret: env.X_API_SECRET,
        token: env.X_ACCESS_TOKEN, tokenSecret: env.X_ACCESS_SECRET,
      });
      const json = await request(url, {
        method: 'POST',
        headers: { Authorization: auth, 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });
      return json.data?.id;
    },
  },

  threads: {
    enabled: () => env.THREADS_ACCESS_TOKEN,
    async post(text) {
      const base = `https://graph.threads.net/v1.0/${env.THREADS_USER_ID || 'me'}`;
      const token = env.THREADS_ACCESS_TOKEN;
      const container = await request(`${base}/threads?${new URLSearchParams({ media_type: 'TEXT', text, access_token: token })}`, { method: 'POST' });
      // コンテナ作成直後は公開に失敗することがあるので少し待つ
      await new Promise((r) => setTimeout(r, 5000));
      const published = await request(`${base}/threads_publish?${new URLSearchParams({ creation_id: container.id, access_token: token })}`, { method: 'POST' });
      return published.id;
    },
  },

  bluesky: {
    enabled: () => env.BLUESKY_HANDLE && env.BLUESKY_APP_PASSWORD,
    async post(text, article) {
      const host = 'https://bsky.social/xrpc';
      const session = await request(`${host}/com.atproto.server.createSession`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identifier: env.BLUESKY_HANDLE, password: env.BLUESKY_APP_PASSWORD }),
      });
      const record = {
        $type: 'app.bsky.feed.post',
        text,
        langs: ['ja'],
        createdAt: new Date().toISOString(),
        facets: hashtagFacets(text),
        embed: {
          $type: 'app.bsky.embed.external',
          external: { uri: articleUrl(article.slug, 'bluesky'), title: article.title ?? '', description: article.description ?? '' },
        },
      };
      const json = await request(`${host}/com.atproto.repo.createRecord`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${session.accessJwt}` },
        body: JSON.stringify({ repo: session.did, collection: 'app.bsky.feed.post', record }),
      });
      return json.uri;
    },
  },
};

// Bluesky はハッシュタグを facet（UTF-8 のバイト位置）で指定しないとリンクにならない
export function hashtagFacets(text) {
  const enc = new TextEncoder();
  const facets = [];
  for (const m of text.matchAll(/(^|\s)([#＃]([^\s#＃]+))/gu)) {
    const start = enc.encode(text.slice(0, m.index + m[1].length)).length;
    facets.push({
      index: { byteStart: start, byteEnd: start + enc.encode(m[2]).length },
      features: [{ $type: 'app.bsky.richtext.facet#tag', tag: m[3] }],
    });
  }
  return facets;
}

// ---------- 何を投稿するか選ぶ ----------

function pickNext(platform, articles, log, now) {
  const candidates = articles.filter((a) => a.published && a.sns?.[platform]?.length);
  const history = (a) => log[a.slug]?.[platform] ?? [];

  const fresh = candidates.find((a) => history(a).length === 0);
  if (fresh) return { article: fresh, pattern: 0, reshare: false };

  if (!RESHARE_DAYS) return null;
  const last = (a) => Date.parse(history(a).at(-1).at);
  const due = candidates
    .filter((a) => now - last(a) >= RESHARE_DAYS * 86400_000)
    .sort((a, b) => last(a) - last(b))[0];
  if (!due) return null;
  return { article: due, pattern: history(due).length % due.sns[platform].length, reshare: true };
}

// ---------- メイン ----------

async function main() {
  const articles = await loadArticles();

  let invalid = 0;
  for (const a of articles) {
    for (const p of validate(a)) { invalid++; console.log(`✗ sns/${a.slug}.json ${p}`); }
    if (a.published && !a.sns) console.log(`△ ${a.slug}: 公開済みだが sns/${a.slug}.json がない（SNSに投稿されません）`);
  }
  if (CHECK || invalid) {
    console.log(`SNS投稿文チェック: エラー ${invalid}`);
    return invalid ? 1 : 0;
  }

  const log = existsSync(LOG_FILE) ? JSON.parse(await readFile(LOG_FILE, 'utf8')) : {};
  const now = Date.now();
  let failed = 0;
  let changed = false;

  for (const platform of PLATFORMS) {
    const client = clients[platform];
    if (!client.enabled() && !DRY_RUN) { console.log(`- ${platform}: 認証情報が未設定のためスキップ`); continue; }

    const next = pickNext(platform, articles, log, now);
    if (!next) { console.log(`- ${platform}: 投稿する記事なし`); continue; }

    const { article, pattern, reshare } = next;
    const text = compose(platform, article.sns[platform][pattern], article.slug);
    console.log(`\n▶ ${platform}: ${article.slug}（パターン${pattern + 1}${reshare ? '・再シェア' : ''}）\n${text}`);
    if (DRY_RUN) continue;

    try {
      const id = await client.post(text, article);
      ((log[article.slug] ??= {})[platform] ??= []).push({ at: new Date(now).toISOString(), pattern, id });
      changed = true;
      console.log(`✓ 投稿しました: ${id}`);
    } catch (e) {
      failed++;
      console.log(`✗ ${platform} への投稿に失敗: ${e.message}`);
    }
  }

  if (changed) await writeFile(LOG_FILE, JSON.stringify(log, null, 2) + '\n');
  return failed ? 1 : 0;
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) process.exit(await main());
