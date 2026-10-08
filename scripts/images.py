"""記事に付ける画像の作成・取得。

- アイキャッチ: キャッチコピー＋写真風画像。GEMINI_API_KEY があれば Google の画像生成 AI で作り、
  なければ Pexels の写真、それもなければイラスト（illustrations.py）を使う
- 本文の写真: PEXELS_API_KEY があれば Pexels の無料写真を探して使う
"""

import io
import os
import re
import textwrap
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
USED_PHOTOS_FILE = ROOT / "content" / "used_photos.txt"

FONT_DIR = ROOT / "assets" / "fonts"

# イラストごとの背景色とアクセント色
THEMES = {
    "mom_and_kids": ("#FFF3EC", "#F28C6B"),
    "tired_night": ("#EEF1FA", "#5B6FA8"),
    "teacher": ("#EFF8F2", "#4FA27A"),
    "checklist": ("#EEF4FB", "#4F86C9"),
    "step_forward": ("#FFF8E8", "#E8913A"),
}


def _font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    name = "ZenMaruGothic-Bold.ttf" if bold else "ZenMaruGothic-Medium.ttf"
    return ImageFont.truetype(str(FONT_DIR / name), size)


def _illustration_png(name: str, size: int) -> Image.Image:
    import cairosvg

    from illustrations import ILLUSTRATIONS

    svg = ILLUSTRATIONS.get(name, ILLUSTRATIONS["mom_and_kids"])()
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=size, output_height=size)
    return Image.open(io.BytesIO(png)).convert("RGBA")


# AI に写真風の画像を作らせるときに毎回付ける指定
PHOTO_STYLE = (
    "Photorealistic lifestyle photograph of Japanese people, natural soft daylight, warm and gentle tones, "
    "shallow depth of field, shot on a full-frame camera with a 50mm lens, high quality stock photo. "
    "Place the main subject on the right half of the frame; keep the left half a calm, softly blurred, "
    "uncluttered background. No text, no letters, no logos, no watermarks."
)
EYECATCH_ACCENT = "#F28C6B"


def generate_ai_photo(scene: str) -> bytes | None:
    """Google の画像生成 AI で写真風の画像を作る。GEMINI_API_KEY がないときは None。"""
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        return None
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=key)
    model = os.environ.get("GEMINI_IMAGE_MODEL") or "imagen-4.0-generate-001"
    # 子どもが写る場面もあるので ALLOW_ALL を先に試し、使えない地域・設定なら大人のみで作り直す
    for person in ("ALLOW_ALL", "ALLOW_ADULT"):
        try:
            res = client.models.generate_images(
                model=model,
                prompt=f"{scene}. {PHOTO_STYLE}",
                config=types.GenerateImagesConfig(
                    number_of_images=1, aspect_ratio="16:9", person_generation=person
                ),
            )
        except Exception as e:  # 設定や地域の制限で断られたら次を試す
            print(f"AI画像の生成に失敗しました（{person}）: {e}")
            continue
        for generated in res.generated_images or []:
            if generated.image and generated.image.image_bytes:
                return generated.image.image_bytes
        print(f"AI画像が安全フィルターで除外されました（{person}）")
    return None


def make_eyecatch(copy: str, label: str, site_name: str, scene: str = "",
                  photo_query: str = "", illustration: str = "mom_and_kids") -> bytes:
    """アイキャッチ画像（1200x630 PNG）を作る。

    AI の写真風画像 → Pexels の写真 → イラスト の順に、用意できたものを使う。
    copy は「／」で改行位置を指定できる（例: 子持ち保育士の転職／勇気が出ない人へ）。
    """
    photo = generate_ai_photo(scene) if scene else None
    if not photo and photo_query:
        found = find_photo(photo_query)
        photo = found["bytes"] if found else None
    if photo:
        return _photo_eyecatch(photo, copy, label, site_name)
    return _illustration_eyecatch(copy, label, illustration, site_name)


def _photo_eyecatch(photo: bytes, copy: str, label: str, site_name: str) -> bytes:
    w, h = 1200, 630
    src = Image.open(io.BytesIO(photo)).convert("RGB")
    scale = max(w / src.width, h / src.height)
    src = src.resize((round(src.width * scale), round(src.height * scale)), Image.LANCZOS)
    left_crop = (src.width - w) // 2
    img = src.crop((left_crop, (src.height - h) // 2, left_crop + w, (src.height - h) // 2 + h)).convert("RGBA")

    # 文字を読みやすくするため、左側を白くぼかす
    fade = Image.new("L", (w, h))
    fd = ImageDraw.Draw(fade)
    for x in range(w):
        t = max(0.0, 1 - x / 780)
        fd.line((x, 0, x, h), fill=round(238 * min(1.0, t * 1.35)))
    white = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    img = Image.composite(white, img, fade)

    draw = ImageDraw.Draw(img)
    _draw_copy(draw, copy, label, site_name, EYECATCH_ACCENT, "#FFFFFF", h, text_w=600)
    buf = io.BytesIO()
    img.convert("RGB").save(buf, "JPEG", quality=90)
    return buf.getvalue()


def _illustration_eyecatch(copy: str, label: str, illustration: str, site_name: str) -> bytes:
    bg, accent = THEMES.get(illustration, THEMES["mom_and_kids"])
    w, h = 1200, 630
    img = Image.new("RGBA", (w, h), bg)
    draw = ImageDraw.Draw(img)

    # 背景の飾り
    draw.ellipse((-120, 430, 260, 810), fill=_mix(bg, accent, 0.10))
    draw.ellipse((560, -160, 820, 100), fill=_mix(bg, accent, 0.08))
    for x, y, r in ((610, 520, 10), (90, 80, 7), (640, 120, 6)):
        draw.ellipse((x - r, y - r, x + r, y + r), fill=_mix(bg, accent, 0.35))

    ill = _illustration_png(illustration, 540)
    img.alpha_composite(ill, (w - 540 - 30, (h - 540) // 2 + 10))

    _draw_copy(draw, copy, label, site_name, accent, bg, h, text_w=600)
    buf = io.BytesIO()
    img.convert("RGB").save(buf, "JPEG", quality=90)
    return buf.getvalue()


def _draw_copy(draw, copy, label, site_name, accent, bg, h, text_w, left=70):
    """左側にラベル・キャッチコピー（マーカー付き）・サイト名を描く。"""
    label_font = _font(30)
    if label:
        lw = draw.textlength(label, font=label_font)
        draw.rounded_rectangle((left, 80, left + lw + 48, 132), radius=26, fill=accent)
        draw.text((left + 24, 88), label, font=label_font, fill="white")

    lines = [l for l in copy.replace("/", "／").split("／") if l] or [copy]
    if len(lines) == 1:
        lines = _wrap(copy, 10)
    for size in (84, 76, 68, 60, 54, 48):
        font = _font(size)
        if max(draw.textlength(l, font=font) for l in lines) <= text_w and len(lines) * size * 1.5 <= 330:
            break
    line_h = int(size * 1.5)
    top = 165 + (330 - line_h * len(lines)) // 2
    marker = _mix("#FFFFFF", "#FFE066", 0.85)
    for i, line in enumerate(lines):
        y = top + i * line_h
        tw = draw.textlength(line, font=font)
        draw.rounded_rectangle((left - 6, y + size * 0.62, left + tw + 6, y + size * 1.08), radius=8, fill=marker)
        draw.text((left, y), line, font=font, fill="#3B3330")

    small = _font(24, bold=False)
    draw.text((left, h - 75), site_name, font=small, fill=_mix("#3B3330", bg, 0.35))


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
