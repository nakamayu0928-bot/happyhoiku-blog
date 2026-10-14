// 記事の機械チェック。AI編集部の最後と CI で実行する。
// 使い方: npm run check:articles
import { readdir, readFile } from 'node:fs/promises';
import { join } from 'node:path';

const DIR = 'src/content/posts';
const BANNED = [
  ['いかがでしたか', 'AI定型文'],
  ['と言えるでしょう', 'AI定型文'],
  ['絶対に', '断定表現（景表法・ASP規約に注意）'],
  ['必ず治', '医療的な断定'],
  ['No.1', '根拠のない最上級表現'],
  ['子供', '表記ゆれ（「子ども」に統一）'],
];

const files = (await readdir(DIR).catch(() => [])).filter((f) => f.endsWith('.md'));
let errors = 0;
let warnings = 0;

for (const file of files) {
  const text = await readFile(join(DIR, file), 'utf8');
  const fm = text.match(/^---\n([\s\S]*?)\n---/)?.[1] ?? '';
  const body = text.slice(fm.length + 8);
  const get = (key) => fm.match(new RegExp(`^${key}:\\s*(.+)$`, 'm'))?.[1].trim();
  const err = (msg) => { errors++; console.log(`✗ ${file}: ${msg}`); };
  const warn = (msg) => { warnings++; console.log(`△ ${file}: ${msg}`); };

  const affiliates = get('affiliates');
  if (affiliates && affiliates !== '[]' && get('hasAffiliate') !== 'true') {
    err('affiliates があるのに hasAffiliate が true ではない（PR表記が出ない）');
  }

  const published = get('draft') === 'false';
  if (published && get('humanReviewed') !== 'true') {
    err('draft: false なのに humanReviewed が true ではない');
  }

  const experience = (body.match(/<!--\s*体験談/g) ?? []).length;
  const unverified = (body.match(/【要確認】/g) ?? []).length;
  if (published && experience) err(`体験談の未記入が ${experience} 箇所あるまま公開しようとしている`);
  else if (experience) warn(`体験談の未記入 ${experience} 箇所`);
  if (published && unverified) err(`【要確認】が ${unverified} 箇所あるまま公開しようとしている`);
  else if (unverified) warn(`【要確認】 ${unverified} 箇所`);

  for (const [word, reason] of BANNED) {
    if (body.includes(word)) warn(`「${word}」: ${reason}`);
  }
}

console.log(`\n${files.length} 記事をチェック: エラー ${errors} / 注意 ${warnings}`);
process.exit(errors ? 1 : 0);
