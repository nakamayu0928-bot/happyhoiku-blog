export const SITE = {
  title: 'はっぴー保育ブログ',
  description: '保育士・保育学生・保護者のための、現場で使える保育のヒントと働き方の情報',
  author: 'はっぴー保育ブログ編集部',
  // Google AdSense の審査通過後に ca-pub-xxxx を設定（空なら広告は出ない）
  adsenseClient: import.meta.env.PUBLIC_ADSENSE_CLIENT ?? '',
};

export const url = (path: string) =>
  `${import.meta.env.BASE_URL.replace(/\/$/, '')}/${path.replace(/^\//, '')}`;
