"""Claude で記事を書き、WordPress に自動投稿するスクリプト。

使い方:
    python scripts/auto_post.py            # 記事を生成して投稿
    python scripts/auto_post.py --dry-run  # 生成だけして投稿しない（中身を確認したいとき）

必要な環境変数:
    ANTHROPIC_API_KEY   Claude API キー
    WP_URL              WordPress サイトの URL（例: https://example.com）
    WP_USER             WordPress のユーザー名
    WP_APP_PASSWORD     WordPress のアプリケーションパスワード
任意の環境変数:
    WP_POST_STATUS      publish（公開, 既定）/ draft（下書き）/ future など
    WP_CATEGORY_ID      投稿先カテゴリーの ID（カンマ区切りで複数可）
"""

import argparse
import datetime
import os
import sys
from pathlib import Path

import anthropic
import requests
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent
PROFILE_FILE = ROOT / "content" / "blog_profile.md"
TOPICS_FILE = ROOT / "content" / "topics.txt"
POSTED_FILE = ROOT / "content" / "posted.tsv"

MODEL = "claude-opus-5-5"
JST = datetime.timezone(datetime.timedelta(hours=9))


class Article(BaseModel):
    title: str
    slug: str
    excerpt: str
    content_html: str
    tags: list[str]


def read_topics() -> tuple[list[str], str | None]:
    lines = TOPICS_FILE.read_text(encoding="utf-8").splitlines()
    for line in lines:
        if line.strip() and not line.lstrip().startswith("#"):
            return lines, line.strip()
    return lines, None


def remove_topic(lines: list[str], topic: str) -> None:
    for i, line in enumerate(lines):
        if line.strip() == topic:
            del lines[i]
            break
    TOPICS_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def past_titles() -> list[str]:
    rows = POSTED_FILE.read_text(encoding="utf-8").splitlines()[1:]
    return [row.split("\t")[2] for row in rows if row.count("\t") >= 3]


def generate_article(topic: str | None) -> Article:
    profile = PROFILE_FILE.read_text(encoding="utf-8")
    titles = past_titles()
    history = "\n".join(f"- {t}" for t in titles[-100:]) or "（まだありません）"

    if topic:
        task = f"次のテーマでブログ記事を1本書いてください。\n\nテーマ: {topic}"
    else:
        task = "ブログの方針に合ったテーマを自分で1つ選び、ブログ記事を1本書いてください。過去の記事とテーマが重ならないようにしてください。"

    prompt = f"""{task}

## 過去に投稿した記事のタイトル
{history}

## 出力の形式
- title: 検索されやすく、読みたくなる日本語タイトル（32文字前後）
- slug: URL 用の短い英小文字とハイフンの文字列（例: rainy-day-indoor-play）
- excerpt: 記事の要約（120文字以内）
- content_html: 記事本文の HTML。<h2>, <h3>, <p>, <ul>, <ol>, <li>, <strong> のみ使う。<h1> とタイトルは含めない。導入→本文（見出しで区切る）→まとめ の構成にする
- tags: 記事に合うタグを3〜5個"""

    client = anthropic.Anthropic()
    response = client.messages.parse(
        model=MODEL,
        max_tokens=16000,
        system=f"あなたは保育ブログの記事を書くライターです。以下のブログ方針に従ってください。\n\n{profile}",
        messages=[{"role": "user", "content": prompt}],
        output_format=Article,
        output_config={"effort": "medium"},
        # 安全フィルターで断られたときに、別のモデルで自動的に書き直してもらう
        extra_headers={"anthropic-beta": "server-side-fallback-2026-07-01"},
        extra_body={"fallbacks": "default"},
    )
    if response.stop_reason == "refusal":
        sys.exit("記事の生成が断られました。テーマを変えて再度お試しください。")
    if response.stop_reason == "max_tokens":
        sys.exit("記事が長すぎて途中で切れました。もう一度実行してください。")
    return response.parsed_output


def wp_auth() -> tuple[str, str]:
    return os.environ["WP_USER"], os.environ["WP_APP_PASSWORD"].replace(" ", "")


def wp_api(path: str) -> str:
    return os.environ["WP_URL"].rstrip("/") + "/wp-json/wp/v2/" + path


def get_or_create_tag_ids(names: list[str]) -> list[int]:
    ids = []
    for name in names:
        res = requests.get(wp_api("tags"), params={"search": name}, auth=wp_auth(), timeout=30)
        res.raise_for_status()
        match = next((t for t in res.json() if t["name"] == name), None)
        if match:
            ids.append(match["id"])
            continue
        res = requests.post(wp_api("tags"), json={"name": name}, auth=wp_auth(), timeout=30)
        if res.ok:
            ids.append(res.json()["id"])
        else:
            print(f"タグ「{name}」を作成できませんでした（{res.status_code}）。スキップします。")
    return ids


def post_to_wordpress(article: Article) -> str:
    data = {
        "title": article.title,
        "slug": article.slug,
        "excerpt": article.excerpt,
        "content": article.content_html,
        "status": os.environ.get("WP_POST_STATUS") or "publish",
        "tags": get_or_create_tag_ids(article.tags),
    }
    categories = os.environ.get("WP_CATEGORY_ID", "").strip()
    if categories:
        data["categories"] = [int(c) for c in categories.split(",") if c.strip()]

    res = requests.post(wp_api("posts"), json=data, auth=wp_auth(), timeout=60)
    if not res.ok:
        sys.exit(f"WordPress への投稿に失敗しました: {res.status_code} {res.text[:500]}")
    return res.json()["link"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="投稿せずに生成結果を表示する")
    args = parser.parse_args()

    lines, topic = read_topics()
    print(f"テーマ: {topic or '（AIにおまかせ）'}")
    article = generate_article(topic)
    print(f"タイトル: {article.title}")

    if args.dry_run:
        print(f"スラッグ: {article.slug}\nタグ: {', '.join(article.tags)}\n要約: {article.excerpt}\n")
        print(article.content_html)
        return

    url = post_to_wordpress(article)
    print(f"投稿しました: {url}")

    if topic:
        remove_topic(lines, topic)
    today = datetime.datetime.now(JST).strftime("%Y-%m-%d")
    with POSTED_FILE.open("a", encoding="utf-8") as f:
        f.write(f"{today}\t{topic or '(auto)'}\t{article.title}\t{url}\n")


if __name__ == "__main__":
    main()
