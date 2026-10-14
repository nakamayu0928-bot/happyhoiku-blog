// アフィリエイト案件の一覧。ASP（A8.net / もしもアフィリエイト / afb など）で提携したら href を差し替える。
// 記事内では <AffiliateBox id="..."> で呼び出す。href が空の案件は表示されない。
export type Affiliate = {
  name: string;
  category: 'career' | 'toy' | 'book' | 'study';
  catch: string;
  href: string;
};

export const AFFILIATES: Record<string, Affiliate> = {
  'career-agent-a': {
    name: '保育士専門の転職エージェント（提携後に名称を記入）',
    category: 'career',
    catch: '非公開求人の紹介・園見学の日程調整まで無料でサポート',
    href: '',
  },
  'career-agent-b': {
    name: '保育士向け求人サイト（提携後に名称を記入）',
    category: 'career',
    catch: '地域・給与・休日数で求人を比較できる',
    href: '',
  },
  'exam-course': {
    name: '保育士試験 通信講座（提携後に名称を記入）',
    category: 'study',
    catch: '働きながら資格取得を目指す人向け',
    href: '',
  },
};
