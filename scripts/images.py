"""記事に付ける画像の作成・取得。

- アイキャッチ: 記事タイトル入りの画像をその場で作る（追加の設定は不要）
- 本文の写真: PEXELS_API_KEY があれば Pexels の無料写真を探して使う
"""

import io
import os
import random
import re
import textwrap
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
USED_PHOTOS_FILE = ROOT / "content" / "used_photos.txt"

FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
    "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
    "C:/Windows/Fonts/meiryob.ttc",
]

# やさしい印象の背景色とアクセント色の組み合わせ
PALETTES = [
    ("#FFF4E8", "#F28C6B"),
    ("#EEF7F1", "#5BAE85"),
    ("#FDF0F4", "#E07A9A"),
    ("#EEF4FB", "#5B8FD1"),
    ("#FFF9E6", "#E5A82E"),
]


def _font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    raise RuntimeError("日本語フォントが見つかりません（fonts-noto-cjk をインストールしてください）")


def make_eyecatch(title: str, site_name: str, seed: str) -> bytes:
    """タイトル入りのアイキャッチ画像（1200x630 PNG）を作る。"""
    rnd = random.Random(seed)
    bg, accent = rnd.choice(PALETTES)
    w, h = 1200, 630
    img = Image.new("RGB", (w, h), bg)
    draw = ImageDraw.Draw(img)

    # 背景の水玉
    for _ in range(14):
        r = rnd.randint(30, 110)
        x, y = rnd.randint(-50, w + 50), rnd.randint(-50, h + 50)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=_mix(bg, accent, 0.18))

    # 中央の白いカード
    margin = 70
    draw.rounded_rectangle((margin, margin, w - margin, h - margin), radius=36, fill="white")
    draw.rounded_rectangle((margin, margin, w - margin, margin + 14), radius=7, fill=accent)

    # タイトル（長さに合わせて文字サイズと折り返しを調整）
    for size in (64, 58, 52, 46, 40):
        font = _font(size)
        per_line = (w - margin * 2 - 100) // size
        lines = _wrap(title, per_line)
        if len(lines) <= 3:
            break
    line_h = int(size * 1.45)
    top = (h - line_h * len(lines)) // 2 - 20
    for i, line in enumerate(lines):
        tw = draw.textlength(line, font=font)
        draw.text(((w - tw) / 2, top + i * line_h), line, font=font, fill="#3A3A3A")

    small = _font(28)
    sw = draw.textlength(site_name, font=small)
    draw.text(((w - sw) / 2, h - margin - 70), site_name, font=small, fill=accent)

    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=True)
    return buf.getvalue()


def _wrap(text: str, width: int) -> list[str]:
    """句読点や「｜」の後ろで改行し、長すぎるかたまりだけ文字数で折り返す。"""
    chunks = [c for c in re.split(r"(?<=[、。！？!?｜|】」』])", text) if c]
    lines, cur = [], ""
    for chunk in chunks:
        if len(cur) + len(chunk) <= width:
            cur += chunk
            continue
        if cur:
            lines.append(cur)
        parts = textwrap.wrap(chunk, width) or [""]
        lines.extend(parts[:-1])
        cur = parts[-1]
    if cur:
        lines.append(cur)
    return lines


def _mix(c1: str, c2: str, t: float) -> tuple[int, int, int]:
    a = [int(c1[i : i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i : i + 2], 16) for i in (1, 3, 5)]
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def find_photo(query: str) -> dict | None:
    """Pexels で写真を1枚探す。キー未設定・見つからないときは None。"""
    key = os.environ.get("PEXELS_API_KEY")
    if not key:
        return None
    res = requests.get(
        "https://api.pexels.com/v1/search",
        params={"query": query, "orientation": "landscape", "per_page": 15},
        headers={"Authorization": key},
        timeout=30,
    )
    if not res.ok:
        print(f"写真検索に失敗しました（{res.status_code}）: {query}")
        return None
    used = set(USED_PHOTOS_FILE.read_text().split()) if USED_PHOTOS_FILE.exists() else set()
    for photo in res.json().get("photos", []):
        if str(photo["id"]) in used:
            continue
        img = requests.get(photo["src"]["large"], timeout=60)
        if not img.ok:
            continue
        with USED_PHOTOS_FILE.open("a") as f:
            f.write(f"{photo['id']}\n")
        return {
            "bytes": img.content,
            "photographer": photo["photographer"],
            "page_url": photo["url"],
        }
    return None
