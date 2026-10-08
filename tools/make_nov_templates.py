"""11月の製作 型紙セット（A4・PDF）を生成するスクリプト。

使い方: python3 tools/make_nov_templates.py
出力:   templates/2026-11-kata-gami.pdf
"""
import math
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

BRAND = "ハッピーほいく"
FONT = "IPAG"
OUT = Path(__file__).resolve().parent.parent / "templates" / "2026-11-kata-gami.pdf"

pdfmetrics.registerFont(TTFont(FONT, "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"))

PW, PH = 210, 297  # A4 (mm)
LW = 0.5  # 切り取り線の太さ (mm)


# ---------- 線のスタイル ----------
def style_cut(c, lw=LW):
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(lw)
    c.setDash()


def style_guide(c):
    c.setStrokeColorRGB(0.62, 0.62, 0.62)
    c.setLineWidth(0.3)
    c.setDash()


def style_fold(c):
    c.setStrokeColorRGB(0.25, 0.25, 0.25)
    c.setLineWidth(0.35)
    c.setDash(2, 1.5)


def text(c, x, y, s, size=3.2, gray=0.35, center=True):
    c.setFillColorRGB(gray, gray, gray)
    c.setFont(FONT, size)
    if center:
        c.drawCentredString(x, y, s)
    else:
        c.drawString(x, y, s)
    c.setFillColorRGB(1, 1, 1)


def union(c, path_fns):
    """重なった図形を1つの外形線で描く（内側の線を消す）。"""
    style_cut(c, LW * 2)
    for fn in path_fns:
        c.drawPath(fn(), stroke=1, fill=0)
    c.setFillColorRGB(1, 1, 1)
    for fn in path_fns:
        c.drawPath(fn(), stroke=0, fill=1)
    style_cut(c)


def outline(c, p):
    style_cut(c)
    c.setFillColorRGB(1, 1, 1)
    c.drawPath(p, stroke=1, fill=1)


# ---------- ページ枠 ----------
def page_frame(c, no, title, sub):
    c.setFillColorRGB(0.97, 0.55, 0.18)
    c.rect(0, PH - 9, PW, 9, stroke=0, fill=1)
    c.setFillColorRGB(1, 1, 1)
    c.setFont(FONT, 4)
    c.drawString(12, PH - 6.3, f"11月の製作 型紙セット　{no}")
    c.setFillColorRGB(0.15, 0.15, 0.15)
    c.setFont(FONT, 7)
    c.drawString(12, PH - 19, title)
    text(c, 12, PH - 25.5, sub, size=3.4, center=False)
    footer(c)


def footer(c):
    text(c, 12, 8, f"© {BRAND}　園内・ご家庭でのご利用OK／再配布・転売・型紙の二次販売は禁止です", size=2.6, center=False)
    # 印刷サイズ確認用のものさし
    style_cut(c, 0.3)
    x0, y0 = PW - 62, 9
    c.line(x0, y0, x0 + 50, y0)
    for i in range(6):
        c.line(x0 + i * 10, y0, x0 + i * 10, y0 + (2.5 if i % 5 == 0 else 1.5))
    text(c, x0 + 25, y0 - 4, "印刷チェック：この線が5cmならOK", size=2.4)


# ---------- 図形 ----------
def acorn_body(c, cx, cy, w, h):
    def f():
        p = c.beginPath()
        p.moveTo(cx - w / 2, cy)
        p.curveTo(cx - w * 0.52, cy - h * 0.7, cx - w * 0.3, cy - h, cx, cy - h)
        p.curveTo(cx + w * 0.3, cy - h, cx + w * 0.52, cy - h * 0.7, cx + w / 2, cy)
        p.curveTo(cx + w * 0.2, cy + h * 0.05, cx - w * 0.2, cy + h * 0.05, cx - w / 2, cy)
        p.close()
        return p
    return f


def acorn_cap(c, cx, cy, w, hc):
    cw = w * 1.15

    def f():
        p = c.beginPath()
        p.moveTo(cx - cw / 2, cy)
        p.curveTo(cx - cw / 2, cy + hc * 1.25, cx + cw / 2, cy + hc * 1.25, cx + cw / 2, cy)
        p.curveTo(cx + cw * 0.25, cy - hc * 0.18, cx - cw * 0.25, cy - hc * 0.18, cx - cw / 2, cy)
        p.close()
        return p

    def nub():
        p = c.beginPath()
        p.roundRect(cx - w * 0.06, cy + hc * 0.8, w * 0.12, hc * 0.45, w * 0.03)
        return p
    return f, nub


def draw_acorn_cap(c, cx, cy, w, hc):
    f, nub = acorn_cap(c, cx, cy, w, hc)
    union(c, [nub, f])
    c.saveState()
    c.clipPath(f(), stroke=0, fill=0)
    style_guide(c)
    step = w * 0.13
    for i in range(-12, 13):
        x = cx + i * step
        c.line(x - hc * 2, cy - hc, x + hc * 2, cy + hc * 3)
        c.line(x + hc * 2, cy - hc, x - hc * 2, cy + hc * 3)
    c.restoreState()
    outline_only(c, f())


def outline_only(c, p):
    style_cut(c)
    c.drawPath(p, stroke=1, fill=0)


def acorn_set(c, cx, top, w, h, label):
    hc = h * 0.33
    draw_acorn_cap(c, cx - w * 0.75, top - hc, w, hc)
    text(c, cx - w * 0.75, top - hc - hc * 0.6, "ぼうし", size=2.8)
    outline(c, acorn_body(c, cx + w * 0.75, top - hc * 0.3, w, h)())
    text(c, cx + w * 0.75, top - hc * 0.3 - h - 5, "からだ", size=2.8)
    if label:
        text(c, cx, top - hc * 0.3 - h - 11, label, size=3.4, gray=0.15)


def momiji(c, cx, cy, R):
    lobes = [(-15, 0.72), (38, 0.95), (90, 1.0), (142, 0.95), (195, 0.72)]
    pts = []
    stem_w = R * 0.035
    pts.append((cx + stem_w, cy - R * 0.2))
    for i, (ang, L) in enumerate(lobes):
        if i > 0:
            va = (lobes[i - 1][0] + ang) / 2
            pts.append(polar(cx, cy, R * 0.32, va))
        for da, rr in ((-13, 0.5), (-7, 0.75), (0, 1.0), (7, 0.75), (13, 0.5)):
            pts.append(polar(cx, cy, R * L * rr, ang + da))
    pts.append((cx - stem_w, cy - R * 0.2))
    pts.append((cx - stem_w, cy - R * 0.62))
    pts.append((cx + stem_w, cy - R * 0.62))
    p = c.beginPath()
    p.moveTo(*pts[0])
    for pt in pts[1:]:
        p.lineTo(*pt)
    p.close()
    outline(c, p)
    style_guide(c)
    for ang, L in lobes:
        x, y = polar(cx, cy, R * L * 0.85, ang)
        c.line(cx, cy - R * 0.1, x, y)


def icho(c, cx, by, R):
    p = c.beginPath()
    p.moveTo(cx - R * 0.03, by)
    a0, a1 = 140, 40
    x, y = polar(cx, by, R, a0)
    p.curveTo(cx - R * 0.15, by + R * 0.15, x + R * 0.1, y - R * 0.25, x, y)
    for a in range(a0, 93, -4):
        p.lineTo(*polar(cx, by, R * (1 + 0.03 * math.sin(a / 6)), a))
    p.lineTo(*polar(cx, by, R * 0.78, 90))
    for a in range(87, a1 - 1, -4):
        p.lineTo(*polar(cx, by, R * (1 + 0.03 * math.sin(a / 6)), a))
    x, y = polar(cx, by, R, a1)
    p.curveTo(x - R * 0.1, y - R * 0.25, cx + R * 0.15, by + R * 0.15, cx + R * 0.03, by)
    p.lineTo(cx + R * 0.03, by - R * 0.35)
    p.lineTo(cx - R * 0.03, by - R * 0.35)
    p.close()
    outline(c, p)
    style_guide(c)
    for a in range(50, 135, 10):
        x, y = polar(cx, by, R * 0.85, a)
        c.line(cx, by + R * 0.05, x, y)


def polar(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def kinoko_cap(c, cx, by, w, h):
    p = c.beginPath()
    p.moveTo(cx - w / 2, by)
    p.curveTo(cx - w / 2, by + h * 1.3, cx + w / 2, by + h * 1.3, cx + w / 2, by)
    p.curveTo(cx + w * 0.3, by - h * 0.14, cx - w * 0.3, by - h * 0.14, cx - w / 2, by)
    p.close()
    outline(c, p)


def kinoko_stem(c, cx, ty, w, h):
    p = c.beginPath()
    p.moveTo(cx - w * 0.38, ty)
    p.curveTo(cx - w * 0.42, ty - h * 0.5, cx - w * 0.56, ty - h * 0.85, cx - w / 2, ty - h)
    p.curveTo(cx - w * 0.2, ty - h * 1.06, cx + w * 0.2, ty - h * 1.06, cx + w / 2, ty - h)
    p.curveTo(cx + w * 0.56, ty - h * 0.85, cx + w * 0.42, ty - h * 0.5, cx + w * 0.38, ty)
    p.curveTo(cx + w * 0.15, ty + h * 0.04, cx - w * 0.15, ty + h * 0.04, cx - w * 0.38, ty)
    p.close()
    outline(c, p)


def imo(c, cx, cy, L, T, bend):
    top, bot = [], []
    n = 60
    for i in range(n + 1):
        t = -1 + 2 * i / n
        x = cx + t * L / 2
        yc = cy + bend * (1 - t * t)
        th = T / 2 * (max(0.0, 1 - abs(t) ** 2.2)) ** 0.65
        top.append((x, yc + th))
        bot.append((x, yc - th))
    p = c.beginPath()
    p.moveTo(cx - L / 2 - L * 0.05, cy - T * 0.05)
    for pt in top:
        p.lineTo(*pt)
    p.lineTo(cx + L / 2 + L * 0.06, cy + T * 0.04)
    for pt in reversed(bot):
        p.lineTo(*pt)
    p.close()
    outline(c, p)
    style_guide(c)
    for t, s in ((-0.45, 1), (-0.1, -1), (0.3, 1), (0.6, -1)):
        x = cx + t * L / 2
        yc = cy + bend * (1 - t * t) + s * T * 0.18
        c.arc(x - T * 0.08, yc - T * 0.04, x + T * 0.08, yc + T * 0.04, 0, 180 if s > 0 else -180)


def minomushi(c, cx, top, w, h):
    p = c.beginPath()
    p.moveTo(cx, top)
    p.curveTo(cx + w * 0.35, top, cx + w / 2, top - h * 0.45, cx + w / 2, top - h * 0.68)
    p.curveTo(cx + w / 2, top - h * 1.02, cx - w / 2, top - h * 1.02, cx - w / 2, top - h * 0.68)
    p.curveTo(cx - w / 2, top - h * 0.45, cx - w * 0.35, top, cx, top)
    p.close()
    outline(c, p)
    style_fold(c)
    c.line(cx, top, cx, top + 14)
    text(c, cx + 2, top + 9, "毛糸", size=2.6, center=False)
    style_guide(c)
    for k in range(1, 6):
        y = top - h * k / 6.5
        c.line(cx - w * 0.3, y, cx + w * 0.3, y - 3)


def face(c, cx, cy, r):
    p = c.beginPath()
    p.circle(cx, cy, r)
    outline(c, p)
    style_guide(c)
    for dx in (-r * 0.35, r * 0.35):
        e = c.beginPath()
        e.circle(cx + dx, cy + r * 0.1, r * 0.09)
        c.drawPath(e, stroke=1, fill=0)
    c.arc(cx - r * 0.25, cy - r * 0.45, cx + r * 0.25, cy - r * 0.05, 200, 140)


def risu_ear(c, cx, by, w, h):
    def path(s):
        p = c.beginPath()
        p.moveTo(cx - w / 2 * s, by)
        p.curveTo(cx - w / 2 * s, by + h * 0.6 * s, cx - w * 0.12 * s, by + h * s, cx, by + h * s)
        p.curveTo(cx + w * 0.12 * s, by + h * s, cx + w / 2 * s, by + h * 0.6 * s, cx + w / 2 * s, by)
        p.curveTo(cx + w * 0.2 * s, by - h * 0.08, cx - w * 0.2 * s, by - h * 0.08, cx - w / 2 * s, by)
        p.close()
        return p
    outline(c, path(1))
    style_guide(c)
    c.drawPath(path(0.6), stroke=1, fill=0)
    style_fold(c)
    c.line(cx - w * 0.45, by + 4, cx + w * 0.45, by + 4)


def risu_tail(c, x0, y0, s):
    def P(x, y):
        return x0 + x * s, y0 + y * s
    p = c.beginPath()
    p.moveTo(*P(0.25, 0.0))
    p.curveTo(*P(-0.1, 0.35), *P(-0.12, 0.9), *P(0.22, 1.2))
    p.curveTo(*P(0.45, 1.47), *P(0.97, 1.45), *P(1.0, 1.12))
    p.curveTo(*P(1.03, 0.9), *P(0.85, 0.82), *P(0.72, 0.9))
    p.curveTo(*P(0.82, 1.03), *P(0.66, 1.16), *P(0.50, 1.07))
    p.curveTo(*P(0.40, 1.0), *P(0.52, 0.6), *P(0.74, 0.22))
    p.curveTo(*P(0.80, 0.12), *P(0.76, 0.0), *P(0.66, 0.0))
    p.close()
    outline(c, p)
    style_guide(c)
    for (ax, ay), (bx, by) in (((0.12, 0.45), (0.22, 0.5)), ((0.1, 0.85), (0.2, 0.9)),
                                ((0.55, 1.3), (0.6, 1.24))):
        c.line(*P(ax, ay), *P(bx, by))
    style_fold(c)
    c.line(*P(0.23, 0.06), *P(0.7, 0.06))


def kame(c, cx, cy, s):
    def ell(x, y, rx, ry):
        return lambda: _ellipse(c, x, y, rx, ry)
    parts = [
        ell(cx - 0.62 * s, cy - 0.45 * s, 0.18 * s, 0.13 * s),
        ell(cx + 0.55 * s, cy - 0.45 * s, 0.18 * s, 0.13 * s),
        ell(cx + 0.95 * s, cy + 0.05 * s, 0.25 * s, 0.2 * s),
        ell(cx - 0.95 * s, cy - 0.1 * s, 0.15 * s, 0.06 * s),
        ell(cx, cy, 0.8 * s, 0.55 * s),
    ]
    union(c, parts)
    style_guide(c)
    hexagon(c, cx, cy, 0.25 * s)
    for a in range(30, 360, 60):
        x, y = polar(cx, cy, 0.25 * s, a)
        x2, y2 = polar(cx, cy, 0.55 * s, a)
        c.line(x, y, x2, y2 * 0.85 + cy * 0.15)
    e = c.beginPath()
    e.circle(cx + 1.02 * s, cy + 0.1 * s, 0.035 * s)
    c.drawPath(e, stroke=1, fill=0)


def _ellipse(c, x, y, rx, ry):
    p = c.beginPath()
    p.ellipse(x - rx, y - ry, rx * 2, ry * 2)
    return p


def hexagon(c, cx, cy, r):
    p = c.beginPath()
    for i, a in enumerate(range(30, 391, 60)):
        x, y = polar(cx, cy, r, a)
        (p.moveTo if i == 0 else p.lineTo)(x, y)
    c.drawPath(p, stroke=1, fill=0)


def ume(c, cx, cy, R):
    def petal(a):
        def f():
            x, y = polar(cx, cy, R * 0.55, a)
            p = c.beginPath()
            p.circle(x, y, R * 0.45)
            return p
        return f
    union(c, [petal(90 + 72 * i) for i in range(5)])
    style_guide(c)
    p = c.beginPath()
    p.circle(cx, cy, R * 0.22)
    c.drawPath(p, stroke=1, fill=0)
    for i in range(5):
        c.line(cx, cy, *polar(cx, cy, R * 0.4, 90 + 36 + 72 * i))


def ogi(c, cx, cy, R):
    p = c.beginPath()
    p.moveTo(cx, cy)
    p.lineTo(*polar(cx, cy, R, 150))
    p.arcTo(cx - R, cy - R, cx + R, cy + R, 150, -120)
    p.close()
    outline(c, p)
    style_guide(c)
    p2 = c.beginPath()
    p2.circle(cx, cy, R * 0.04)
    c.drawPath(p2, stroke=1, fill=0)
    for a in range(45, 140, 15):
        c.line(*polar(cx, cy, R * 0.1, a), *polar(cx, cy, R, a))
    c.arc(cx - R * 0.45, cy - R * 0.45, cx + R * 0.45, cy + R * 0.45, 30, 120)


# ---------- ページ ----------
def p_cover(c):
    c.setFillColorRGB(0.99, 0.95, 0.88)
    c.rect(0, 0, PW, PH, stroke=0, fill=1)
    c.setFillColorRGB(0.97, 0.55, 0.18)
    c.rect(0, PH - 70, PW, 70, stroke=0, fill=1)
    c.setFillColorRGB(1, 1, 1)
    c.setFont(FONT, 6)
    c.drawCentredString(PW / 2, PH - 28, "どんぐり・落ち葉・きのこ・七五三・勤労感謝の日")
    c.setFont(FONT, 13)
    c.drawCentredString(PW / 2, PH - 48, "11月の製作 型紙セット")
    c.setFont(FONT, 4.5)
    c.drawCentredString(PW / 2, PH - 60, "0〜5歳児　A4・9枚")

    y = PH - 90
    c.setFillColorRGB(0.15, 0.15, 0.15)
    c.setFont(FONT, 5.5)
    c.drawString(20, y, "もくじ")
    rows = [
        ("P2", "どんぐり（大・中・小）", "②シールのどんぐり／⑧りすの持たせ用"),
        ("P3", "もみじ・いちょう", "①手形もみじ／⑥落ち葉コラージュの飾り"),
        ("P4", "きのこ（大・小）", "⑤ちぎり絵のきのこ"),
        ("P5", "さつまいも（大・小）", "③たんぽスタンプの焼き芋"),
        ("P6", "みのむし", "④くしゃくしゃみのむし"),
        ("P7", "りすの耳・しっぽ", "⑧紙皿のりす"),
        ("P8", "千歳飴袋（展開図）", "⑦七五三の千歳飴袋"),
        ("P9", "千歳飴袋の飾り（亀・梅・扇）", "⑦七五三の千歳飴袋"),
        ("P10", "フォトフレーム・メッセージカード", "⑨勤労感謝の日のプレゼント"),
    ]
    y -= 10
    for pg, name, use in rows:
        c.setFont(FONT, 4)
        c.setFillColorRGB(0.97, 0.55, 0.18)
        c.drawString(22, y, pg)
        c.setFillColorRGB(0.15, 0.15, 0.15)
        c.drawString(36, y, name)
        text(c, 112, y, use, size=3.3, center=False)
        y -= 8.5

    y -= 6
    c.setFillColorRGB(0.15, 0.15, 0.15)
    c.setFont(FONT, 5.5)
    c.drawString(20, y, "使い方")
    y -= 10
    style_cut(c)
    c.line(22, y + 1, 40, y + 1)
    text(c, 45, y, "実線 … 切り取り線", size=3.6, gray=0.15, center=False)
    style_fold(c)
    c.line(110, y + 1, 128, y + 1)
    text(c, 133, y, "点線 … 折り線・のりしろ", size=3.6, gray=0.15, center=False)
    y -= 8
    style_guide(c)
    c.line(22, y + 1, 40, y + 1)
    text(c, 45, y, "グレーの線 … 模様（描き込み・色ぬりの目安）", size=3.6, gray=0.15, center=False)
    y -= 12
    for line in [
        "・印刷は「実際のサイズ（100%）」で。各ページ右下のものさしが5cmになればOKです。",
        "・色画用紙や色上質紙に直接印刷すると、色ぬりなしでそのまま使えます。",
        "・何度も使う型は、厚紙に貼って切り抜くと、なぞり書き用の型紙になります。",
        "・子どもの年齢に合わせて、保育者が事前に切っておく・子どもが切るを選んでください。",
    ]:
        text(c, 22, y, line, size=3.4, gray=0.2, center=False)
        y -= 7
    footer(c)


def p_donguri(c):
    page_frame(c, "P2", "どんぐり（大・中・小）", "ぼうしとからだは別々に切って貼り合わせます。丸シールを貼る台紙にも。")
    acorn_set(c, 105, 255, 60, 75, "どんぐり（大）")
    acorn_set(c, 50, 150, 36, 46, "どんぐり（中）")
    acorn_set(c, 155, 150, 36, 46, "どんぐり（中）")
    acorn_set(c, 60, 72, 26, 33, "どんぐり（小）")
    acorn_set(c, 155, 72, 26, 33, "どんぐり（小）")


def p_leaves(c):
    page_frame(c, "P3", "もみじ・いちょう", "手形もみじの木のまわりに飾ったり、落ち葉コラージュに足したりできます。")
    momiji(c, 60, 205, 42)
    momiji(c, 150, 210, 32)
    momiji(c, 160, 150, 20)
    icho(c, 55, 110, 48)
    icho(c, 140, 95, 34)
    icho(c, 165, 45, 22)
    icho(c, 105, 40, 22)


def p_kinoko(c):
    page_frame(c, "P4", "きのこ（大・小）", "かさにちぎった折り紙を貼り、白い丸シールで水玉模様をつけます。")
    kinoko_cap(c, 105, 200, 140, 62)
    text(c, 105, 191, "かさ（大）", size=3)
    kinoko_stem(c, 60, 165, 50, 60)
    text(c, 60, 98, "え（大）", size=3)
    kinoko_cap(c, 140, 135, 80, 36)
    text(c, 140, 127, "かさ（小）", size=3)
    kinoko_stem(c, 140, 108, 30, 36)
    text(c, 140, 66, "え（小）", size=3)
    kinoko_stem(c, 60, 82, 30, 36)
    text(c, 60, 40, "え（小）", size=3)


def p_imo(c):
    page_frame(c, "P5", "さつまいも（大・小）", "紫の画用紙に印刷して、まん中にたんぽで黄色をポンポン。")
    imo(c, 105, 220, 170, 62, 8)
    imo(c, 70, 140, 110, 42, 6)
    imo(c, 150, 95, 90, 34, 5)
    imo(c, 70, 60, 90, 34, -5)


def p_mino(c):
    page_frame(c, "P6", "みのむし", "台紙に両面テープを貼り、丸めたお花紙をくっつけます。顔は下の方に貼ります。")
    for cx, top, w, h in ((45, 245, 62, 120), (110, 245, 50, 96), (165, 245, 40, 78)):
        minomushi(c, cx, top, w, h)
    for i, (cx, r) in enumerate(((35, 15), (70, 15), (110, 12), (140, 12), (172, 10))):
        face(c, cx, 75, r)
    text(c, 105, 52, "顔（大・中・小）", size=3)


def p_risu(c):
    page_frame(c, "P7", "りすの耳・しっぽ", "紙皿（直径18cm程度）を顔にして、耳としっぽを貼ります。点線はのりしろです。")
    risu_ear(c, 45, 215, 34, 42)
    risu_ear(c, 95, 215, 34, 42)
    text(c, 70, 205, "耳 ×2", size=3)
    risu_tail(c, 100, 50, 100)
    text(c, 155, 44, "しっぽ", size=3)
    acorn_set(c, 45, 160, 26, 33, "持たせるどんぐり")
    acorn_set(c, 45, 95, 26, 33, "")


def p_chitose_bag(c):
    page_frame(c, "P8", "千歳飴袋（展開図）", "まん中の点線で山折りし、のりしろを貼って袋にします。A4の画用紙に印刷してください。")
    x0, y0, bw, bh, g = 10, 25, 90, 235, 9
    # 前・後ろ
    style_cut(c)
    p = c.beginPath()
    p.moveTo(x0, y0)
    p.lineTo(x0, y0 + bh)
    p.lineTo(x0 + bw * 2, y0 + bh)
    p.lineTo(x0 + bw * 2 + g, y0 + bh - g)
    p.lineTo(x0 + bw * 2 + g, y0 + g)
    p.lineTo(x0 + bw * 2, y0)
    p.lineTo(x0 + bw + g * 0.0, y0)
    p.lineTo(x0 + bw, y0)
    p.close()
    c.drawPath(p, stroke=1, fill=0)
    # 底ののりしろ（後ろ側）
    p2 = c.beginPath()
    p2.moveTo(x0 + bw, y0)
    p2.lineTo(x0 + bw + g, y0 - g + 0.01)
    p2.lineTo(x0 + bw * 2 - g, y0 - g + 0.01)
    p2.lineTo(x0 + bw * 2, y0)
    c.drawPath(p2, stroke=1, fill=0)
    style_fold(c)
    c.line(x0 + bw, y0, x0 + bw, y0 + bh)
    c.line(x0 + bw * 2, y0, x0 + bw * 2, y0 + bh)
    c.line(x0 + bw, y0, x0 + bw * 2, y0)
    text(c, x0 + bw * 2 + g / 2, y0 + bh / 2, "", size=2.6)
    c.saveState()
    c.translate(x0 + bw * 2 + g / 2 + 1, y0 + bh / 2)
    c.rotate(90)
    text(c, 0, 0, "のりしろ", size=2.8)
    c.restoreState()
    text(c, x0 + bw * 1.5, y0 - g + 2.5, "のりしろ", size=2.8)
    text(c, x0 + bw / 2, y0 + bh - 12, "おもて", size=3.4)
    text(c, x0 + bw * 1.5, y0 + bh - 12, "うら", size=3.4)
    # おもての飾りガイド
    style_guide(c)
    c.rect(x0 + 12, y0 + 30, bw - 24, bh - 70, stroke=1, fill=0)
    c.setFillColorRGB(0.8, 0.8, 0.8)
    c.setFont(FONT, 12)
    for i, ch in enumerate("ちとせあめ"):
        c.drawCentredString(x0 + bw / 2, y0 + bh - 45 - i * 18, ch)
    text(c, x0 + bw / 2, y0 + 18, "和柄の折り紙や亀・梅の飾りを貼りましょう", size=2.6)


def p_chitose_deco(c):
    page_frame(c, "P9", "千歳飴袋の飾り（亀・梅・扇）", "千歳飴袋のおもてに貼る飾りです。色をぬってから切り取ります。")
    kame(c, 70, 215, 40)
    ogi(c, 150, 185, 45)
    ume(c, 40, 130, 20)
    ume(c, 95, 135, 15)
    ume(c, 140, 120, 12)
    ume(c, 175, 125, 12)
    kame(c, 60, 60, 26)
    ogi(c, 145, 45, 32)


def p_frame(c):
    page_frame(c, "P10", "フォトフレーム・メッセージカード", "厚紙に印刷し、グレーの部分を切り抜きます。まわりにどんぐりや落ち葉を貼りましょう。")
    fx, fy, fw, fh = 40, 115, 130, 150
    style_cut(c)
    c.roundRect(fx, fy, fw, fh, 6, stroke=1, fill=0)
    wx, wy, ww, wh = fx + 22, fy + 28, fw - 44, fh - 50
    c.setFillColorRGB(0.88, 0.88, 0.88)
    c.rect(wx, wy, ww, wh, stroke=1, fill=1)
    text(c, fx + fw / 2, wy + wh / 2 + 3, "ここを切り抜く", size=3.4, gray=0.4)
    text(c, fx + fw / 2, wy + wh / 2 - 3, "（写真は L判 の大きさ）", size=2.8, gray=0.45)
    text(c, fx + fw / 2, fy + 12, "いつもありがとう", size=6, gray=0.25)
    # メッセージカード
    cx, cy, cw, ch = 40, 25, 130, 75
    style_cut(c)
    c.roundRect(cx, cy, cw, ch, 4, stroke=1, fill=0)
    style_fold(c)
    c.line(cx + cw / 2, cy, cx + cw / 2, cy + ch)
    text(c, cx + cw * 0.25, cy + ch - 18, "いつも", size=5, gray=0.25)
    text(c, cx + cw * 0.25, cy + ch - 28, "ありがとう", size=5, gray=0.25)
    momiji_small = (cx + cw * 0.25, cy + 22)
    momiji(c, *momiji_small, 11)
    style_guide(c)
    for i in range(4):
        y = cy + ch - 16 - i * 12
        c.line(cx + cw / 2 + 8, y, cx + cw - 8, y)
    text(c, cx + cw - 22, cy + 8, "より", size=3.4, gray=0.3)
    text(c, cx + cw / 2, cy - 5, "メッセージカード（点線で半分に折ります）", size=2.8)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT), pagesize=A4)
    c.setTitle("11月の製作 型紙セット")
    c.setAuthor(BRAND)
    for fn in (p_cover, p_donguri, p_leaves, p_kinoko, p_imo, p_mino, p_risu,
               p_chitose_bag, p_chitose_deco, p_frame):
        c.saveState()
        c.scale(mm, mm)
        fn(c)
        c.restoreState()
        c.showPage()
    c.save()
    print(OUT)


if __name__ == "__main__":
    main()
