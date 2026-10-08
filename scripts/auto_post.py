"""Claude で記事を書き、WordPress に自動投稿するスクリプト。

使い方:
キーワードは content/keywords.csv から、執筆済みでないものを優先度の高い順に1つ選びます。

    python scripts/auto_post.py            # 記事を生成して投稿
    python scripts/auto_post.py --dry-run  # 投稿せず preview/ に記事と画像を保存する

必要な環境変数:
    ANTHROPIC_API_KEY   Claude API キー
    WP_URL              WordPress サイトの URL（例: https://example.com）
    WP_USER             WordPress のユーザー名
    WP_APP_PASSWORD     WordPress のアプリケーションパスワード
任意の環境変数:
    WP_POST_STATUS      draft（下書き, 既定）/ publish（すぐ公開）
    WP_CATEGORY_ID      投稿先カテゴリーの ID（カンマ区切りで複数可）
    PEXELS_API_KEY      Pexels の API キー（あると本文に写真が入る）
"""

import argparse
import csv
import datetime
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

import anthropic
import requests
from pydantic import BaseModel

from images import find_photo, make_eyecatch

ROOT = Path(__file__).resolve().parent.parent
PROFILE_FILE = ROOT / "content" / "blog_profile.md"
KEYWORDS_FILE = ROOT / "content" / "keywords.csv"
POSTED_FILE = ROOT / "content" / "posted.tsv"
PREVIEW_DIR = ROOT / "preview"

MODEL = "claude-opus-5-5"
JST = datetime.timezone(datetime.timedelta(hours=9))
PRIORITY_ORDER = {"最高": 0, "高": 1, "中": 2, "低": 3}


class ImageSpec(BaseModel):
    search_query: str
    alt: str


class Article(BaseModel):
    title: str
    slug: str
    excerpt: str
    content_html: str
    tags: list[str]
    images: list[ImageSpec]


def read_keywords() -> tuple[list[str], list[dict]]:
    with KEYWORDS_FILE.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames), list(reader)


def write_keywords(fields: list[str], rows: list[dict]) -> None:
    with KEYWORDS_FILE.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def pick_keyword(rows: list[dict]) -> dict | None:
    todo = [r for r in rows if r["KW"].strip() and not r["執筆済み"].strip()]
    todo.sort(key=lambda r: PRIORITY_ORDER.get(r["優先度"].strip(), 9))
    return todo[0] if todo else None


def existing_articles(rows: list[dict]) -> list[str]:
    """既存記事の一覧（内部リンクと重複回避に使う）。"""
    articles = []
    for row in POSTED_FILE.read_text(encoding="utf-8").splitlines()[1:]:
        cols = row.split("\t")
        if len(cols) >= 4:
            articles.append(f"- {cols[2]}（KW: {cols[1]}）: {cols[3]}")
    posted_kws = {a.split("KW: ")[1].split("）")[0] for a in articles}
    for r in rows:
        if r["執筆済み"].strip() and r["KW"] not in posted_kws:
            url = r.get("URL", "").strip()
            # 下書きのプレビュー URL は公開されていないのでリンクに使わない
            link = url if url and "preview" not in url else "（URL不明）"
            articles.append(f"- KW: {r['KW']}: {link}")
    return articles


def generate_article(kw: dict | None, rows: list[dict]) -> Article:
    profile = PROFILE_FILE.read_text(encoding="utf-8")
    history = "\n".join(existing_articles(rows)[-100:]) or "（まだありません）"

    if kw:
        task = f"""次のキーワードで検索上位を狙うブログ記事を1本書いてください。

- メインキーワード: {kw["KW"]}
- 想定検索意図: {kw["想定検索意図"]}
- 推奨記事タイプ: {kw["推奨記事タイプ"]}
- 読者（ペルソナ）との一致度: {kw["読者との一致度"]}
- 申し込み（CV）への近さ: {kw["CVへの近さ"]}
- 編集メモ: {kw["備考"]}

検索した人の疑問に最初から最後まで答えきる内容にし、メインキーワードはタイトル・導入文・見出しに自然に含めてください。"""
    else:
        task = "ブログの方針に合ったテーマを自分で1つ選び、ブログ記事を1本書いてください。既存の記事とテーマが重ならないようにしてください。"

    prompt = f"""{task}

## このブログの既存記事
内容が重ならないようにし、関連する記事で URL がわかるものは本文中で自然に内部リンク（<a href>）してください。
{history}

## 出力の形式
- title: 検索されやすく、読みたくなる日本語タイトル（32文字前後）
- slug: URL 用の短い英小文字とハイフンの文字列（例: rainy-day-indoor-play）
- excerpt: 記事の要約（120文字以内）
- content_html: 記事本文の HTML。<h2>, <h3>, <p>, <ul>, <ol>, <li>, <strong>, <a>, <table>, <tr>, <th>, <td> のみ使う。<h1> とタイトルは含めない。導入→本文（見出しで区切る）→まとめ の構成にする
- tags: 記事に合うタグを3〜5個
- images: 本文に入れる写真を2〜3枚。content_html の中で写真を入れたい位置（主な <h2> の直後など）に <p>[[画像1]]</p>, <p>[[画像2]]</p> … と書き、同じ順番で images に指定する
  - search_query: 無料写真サイトで探すための英語の検索語（例: "tired mother with child", "nursery school teacher"）。人物の顔がはっきり写る写真に頼らず、雰囲気が伝わるものを選ぶ
  - alt: 写真の説明（日本語・30文字以内）"""

    client = anthropic.Anthropic()
    with client.messages.stream(
        model=MODEL,
        max_tokens=64000,
        system=f"あなたは保育ブログの記事を書くライターです。以下のブログ方針に従ってください。\n\n{profile}",
        messages=[{"role": "user", "content": prompt}],
        output_format=Article,
        output_config={"effort": "medium"},
        # 安全フィルターで断られたときに、別のモデルで自動的に書き直してもらう
        extra_headers={"anthropic-beta": "server-side-fallback-2026-07-01"},
        extra_body={"fallbacks": "default"},
    ) as stream:
        response = stream.get_final_message()
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


def upload_media(data: bytes, filename: str, mime: str, alt: str) -> dict:
    res = requests.post(
        wp_api("media"),
        data=data,
        headers={"Content-Type": mime, "Content-Disposition": f'attachment; filename="{filename}"'},
        auth=wp_auth(),
        timeout=120,
    )
    if not res.ok:
        sys.exit(f"画像のアップロードに失敗しました: {res.status_code} {res.text[:300]}")
    media = res.json()
    requests.post(wp_api(f"media/{media['id']}"), json={"alt_text": alt}, auth=wp_auth(), timeout=30)
    return media


def photo_figure(src: str, alt: str, photo: dict) -> str:
    return (
        f'<figure class="wp-block-image size-large"><img src="{src}" alt="{alt}"/>'
        f'<figcaption>Photo: <a href="{photo["page_url"]}" target="_blank" rel="noopener">'
        f'{photo["photographer"]}</a> / Pexels</figcaption></figure>'
    )


def insert_photos(article: Article, upload: bool) -> str:
    """[[画像N]] の位置に写真を入れる。写真が用意できない位置は印を消す。"""
    html = article.content_html
    for i, spec in enumerate(article.images, start=1):
        marker = f"<p>[[画像{i}]]</p>"
        photo = find_photo(spec.search_query)
        figure = ""
        if photo:
            if upload:
                media = upload_media(photo["bytes"], f"{article.slug}-{i}.jpg", "image/jpeg", spec.alt)
                src = media["source_url"]
            else:
                (PREVIEW_DIR / f"photo{i}.jpg").write_bytes(photo["bytes"])
                src = f"photo{i}.jpg"
            figure = photo_figure(src, spec.alt, photo)
        html = html.replace(marker, figure).replace(f"[[画像{i}]]", figure)
    return html


def site_name() -> str:
    return urlparse(os.environ.get("WP_URL", "")).netloc or "happyhoiku-tenshoku.com"


def post_to_wordpress(article: Article) -> dict:
    eyecatch = upload_media(
        make_eyecatch(article.title, site_name(), article.slug),
        f"{article.slug}-eyecatch.png",
        "image/png",
        article.title,
    )
    data = {
        "title": article.title,
        "slug": article.slug,
        "excerpt": article.excerpt,
        "content": insert_photos(article, upload=True),
        "status": os.environ.get("WP_POST_STATUS") or "draft",
        "featured_media": eyecatch["id"],
        "tags": get_or_create_tag_ids(article.tags),
    }
    categories = os.environ.get("WP_CATEGORY_ID", "").strip()
    if categories:
        data["categories"] = [int(c) for c in categories.split(",") if c.strip()]

    res = requests.post(wp_api("posts"), json=data, auth=wp_auth(), timeout=60)
    if not res.ok:
        sys.exit(f"WordPress への投稿に失敗しました: {res.status_code} {res.text[:500]}")
    return res.json()


def save_preview(article: Article) -> None:
    PREVIEW_DIR.mkdir(exist_ok=True)
    (PREVIEW_DIR / "eyecatch.png").write_bytes(make_eyecatch(article.title, site_name(), article.slug))
    body = insert_photos(article, upload=False)
    (PREVIEW_DIR / "article.html").write_text(
        f"""<!doctype html><meta charset="utf-8"><title>{article.title}</title>
<style>body{{max-width:760px;margin:2em auto;padding:0 16px;font-family:sans-serif;line-height:1.9;color:#333}}
img{{max-width:100%}}table{{border-collapse:collapse}}td,th{{border:1px solid #ccc;padding:6px 10px}}
figcaption{{font-size:12px;color:#888}}h2{{border-left:6px solid #F28C6B;padding-left:10px}}</style>
<h1>{article.title}</h1><img src="eyecatch.png" alt="アイキャッチ">
<p style="color:#888">タグ: {", ".join(article.tags)}<br>要約: {article.excerpt}</p>
{body}""",
        encoding="utf-8",
    )
    print(f"プレビューを保存しました: {PREVIEW_DIR / 'article.html'}")


def write_summary(text: str) -> None:
    """GitHub Actions の実行結果ページに表示する。"""
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(text + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="投稿せずに生成結果を表示する")
    args = parser.parse_args()

    fields, rows = read_keywords()
    kw = pick_keyword(rows)
    print(f"キーワード: {kw['KW'] if kw else '（未執筆のキーワードがないためAIにおまかせ）'}")
    article = generate_article(kw, rows)
    print(f"タイトル: {article.title}")

    if args.dry_run:
        save_preview(article)
        return

    post = post_to_wordpress(article)
    url = post["link"]
    edit_url = os.environ["WP_URL"].rstrip("/") + f"/wp-admin/post.php?post={post['id']}&action=edit"
    state = "公開" if post["status"] == "publish" else "下書き保存"
    print(f"{state}しました: {url}\n編集画面: {edit_url}")
    write_summary(f"## {state}しました\n\n**{article.title}**\n\n- キーワード: {kw['KW'] if kw else '(AIにおまかせ)'}\n- [編集画面を開く（確認して「公開」を押す）]({edit_url})")

    today = datetime.datetime.now(JST).strftime("%Y-%m-%d")
    if kw:
        kw["執筆済み"] = f"✓ {today}"
        kw["URL"] = url
        write_keywords(fields, rows)
    with POSTED_FILE.open("a", encoding="utf-8") as f:
        f.write(f"{today}\t{kw['KW'] if kw else '(auto)'}\t{article.title}\t{url}\n")


if __name__ == "__main__":
    main()
