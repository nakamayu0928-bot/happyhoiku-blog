"""アイキャッチ用のイラスト（SVG）。

記事の内容に合わせて ILLUSTRATIONS のどれかを選んで使う。
人物は person() で描くので、キャラクターの雰囲気がそろう。
"""

SKIN = "#F7D6BF"
HAIR = "#6B4A3A"
CHEEK = "#F4A7A0"
LINE = "#5A4A42"


def person(x, y, s=1.0, top="#F28C6B", bottom="#6C8EBF", hair=HAIR, hair_style="bob",
           arm_l=(-38, 55), arm_r=(38, 55), apron=None, eyes="smile", legs=True):
    """(x, y) を頭の中心として人物を描く。s は大きさ。"""
    g = [f'<g transform="translate({x},{y}) scale({s})">']
    # 体
    if legs:
        g.append(f'<path d="M-14 118 L-16 170" stroke="{bottom}" stroke-width="16" stroke-linecap="round"/>')
        g.append(f'<path d="M14 118 L16 170" stroke="{bottom}" stroke-width="16" stroke-linecap="round"/>')
        g.append(f'<ellipse cx="-18" cy="174" rx="13" ry="7" fill="{LINE}"/>')
        g.append(f'<ellipse cx="18" cy="174" rx="13" ry="7" fill="{LINE}"/>')
    g.append(f'<path d="M-30 40 Q0 30 30 40 L38 125 Q0 135 -38 125 Z" fill="{top}"/>')
    if apron:
        g.append(f'<path d="M-22 50 L22 50 L28 122 Q0 128 -28 122 Z" fill="{apron}"/>')
        g.append(f'<rect x="-12" y="78" width="24" height="16" rx="5" fill="white" opacity=".6"/>')
    # 腕
    for ax, ay in (arm_l, arm_r):
        sx = -26 if ax < 0 else 26
        g.append(f'<path d="M{sx} 50 L{ax} {ay}" stroke="{top}" stroke-width="15" stroke-linecap="round"/>')
        g.append(f'<circle cx="{ax}" cy="{ay}" r="8" fill="{SKIN}"/>')
    # 首と頭
    g.append(f'<rect x="-7" y="22" width="14" height="16" fill="{SKIN}"/>')
    if hair_style == "bob":
        g.append(f'<path d="M-34 -2 Q-36 -40 0 -42 Q36 -40 34 -2 L34 26 Q24 30 20 20 L-20 20 Q-24 30 -34 26 Z" fill="{hair}"/>')
    elif hair_style == "pony":
        g.append(f'<circle cx="30" cy="-24" r="14" fill="{hair}"/>')
    elif hair_style == "kid":
        pass
    g.append(f'<circle cx="0" cy="0" r="30" fill="{SKIN}"/>')
    if hair_style in ("bob", "pony"):
        g.append(f'<path d="M-31 -4 Q-30 -34 0 -34 Q30 -34 31 -4 Q14 -20 -6 -14 Q-20 -10 -31 -4 Z" fill="{hair}"/>')
    else:
        g.append(f'<path d="M-29 -6 Q-26 -32 0 -32 Q26 -32 29 -6 Q10 -18 -2 -16 Q-16 -14 -29 -6 Z" fill="{hair}"/>')
    # 顔
    if eyes == "smile":
        g.append(f'<path d="M-15 0 Q-10 -6 -5 0 M5 0 Q10 -6 15 0" stroke="{LINE}" stroke-width="3" fill="none" stroke-linecap="round"/>')
    elif eyes == "tired":
        g.append(f'<path d="M-15 -1 L-5 1 M5 1 L15 -1" stroke="{LINE}" stroke-width="3" stroke-linecap="round"/>')
    else:
        g.append(f'<circle cx="-10" cy="-1" r="3.2" fill="{LINE}"/><circle cx="10" cy="-1" r="3.2" fill="{LINE}"/>')
    g.append(f'<circle cx="-17" cy="9" r="5" fill="{CHEEK}" opacity=".7"/><circle cx="17" cy="9" r="5" fill="{CHEEK}" opacity=".7"/>')
    mouth = "M-5 11 Q0 15 5 11" if eyes != "tired" else "M-5 13 Q0 11 5 13"
    g.append(f'<path d="{mouth}" stroke="{LINE}" stroke-width="2.5" fill="none" stroke-linecap="round"/>')
    g.append("</g>")
    return "".join(g)


def _svg(body: str, bg: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500">'
            f'<circle cx="250" cy="260" r="215" fill="{bg}"/>{body}</svg>')


def _sparkle(x, y, s=1, color="#F6C453"):
    return (f'<path transform="translate({x},{y}) scale({s})" d="M0 -14 Q2 -2 14 0 Q2 2 0 14 Q-2 2 -14 0 Q-2 -2 0 -14 Z" fill="{color}"/>')


def _heart(x, y, s=1, color="#F28C9B"):
    return (f'<path transform="translate({x},{y}) scale({s})" d="M0 6 C-14 -6 -10 -18 0 -10 C10 -18 14 -6 0 6 Z" fill="{color}"/>')


def mom_and_kids() -> str:
    """ママと2人の子ども（子育てとの両立）。"""
    body = (
        '<ellipse cx="250" cy="440" rx="190" ry="16" fill="#000" opacity=".06"/>'
        + person(250, 190, 1.25, top="#F28C6B", bottom="#7A93C2", arm_l=(-52, 95), arm_r=(52, 95))
        + person(150, 300, 0.78, top="#8CC9A8", bottom="#F3B562", hair_style="kid", arm_l=(-36, 60), arm_r=(45, 12), eyes="dot")
        + person(342, 322, 0.66, top="#F6C453", bottom="#E58FA8", hair_style="pony", hair="#8A5A44", arm_l=(-41, -20), arm_r=(36, 60), eyes="dot")
        + _heart(330, 120, 1.4) + _heart(372, 150, 0.9, "#F6A6B2") + _sparkle(130, 140, 1.1)
    )
    return _svg(body, "#FFE6D8")


def tired_night() -> str:
    """夜、子どもが寝たあとにスマホで考えごと（悩み・不安）。"""
    body = (
        '<path d="M110 90 h150 v120 h-150 z" fill="#3E4C7A" rx="8"/>'
        '<path d="M110 150 h150 M185 90 v120" stroke="#FFF7EC" stroke-width="6"/>'
        '<circle cx="225" cy="120" r="16" fill="#F8E39A"/><circle cx="232" cy="114" r="14" fill="#3E4C7A"/>'
        + _sparkle(140, 115, 0.5, "#F8E39A") + _sparkle(160, 185, 0.4, "#F8E39A")
        + person(300, 220, 1.2, top="#9DB6E0", bottom="#6C7FA8", arm_l=(-20, 80), arm_r=(20, 78), eyes="tired", legs=False)
        + '<rect x="283" y="300" width="34" height="50" rx="6" fill="#4A4A5A"/><rect x="287" y="305" width="26" height="38" rx="3" fill="#BFE3F5"/>'
        '<rect x="140" y="370" width="300" height="22" rx="10" fill="#C99A72"/>'
        '<rect x="170" y="335" width="40" height="36" rx="8" fill="#FFFFFF"/><path d="M210 345 q16 4 0 18" stroke="#FFFFFF" stroke-width="6" fill="none"/>'
        '<path d="M182 325 q6 -10 0 -18 M196 325 q6 -10 0 -18" stroke="#C9C9D6" stroke-width="3" fill="none" stroke-linecap="round"/>'
    )
    return _svg(body, "#E3E8F7")


def teacher() -> str:
    """エプロン姿の保育士と子ども（保育の仕事）。"""
    body = (
        '<ellipse cx="250" cy="440" rx="180" ry="14" fill="#000" opacity=".06"/>'
        + person(220, 185, 1.25, top="#F3E3C3", bottom="#7A93C2", apron="#F28C6B", arm_l=(-50, 92), arm_r=(60, 70))
        + person(330, 318, 0.7, top="#8CC9A8", bottom="#5B8FD1", hair_style="kid", arm_l=(-50, -62), arm_r=(36, 60), eyes="dot")
        + '<rect x="96" y="380" width="44" height="44" rx="6" fill="#F6C453"/><text x="118" y="412" font-size="28" text-anchor="middle" fill="white" font-family="sans-serif" font-weight="bold">A</text>'
        '<rect x="146" y="396" width="34" height="28" rx="6" fill="#5B8FD1"/><path d="M118 340 l22 36 h-44 z" fill="#E58FA8"/>'
        + _sparkle(400, 180, 1.0) + _heart(110, 150, 1.2)
    )
    return _svg(body, "#E5F4EA")


def checklist() -> str:
    """チェックリストを持つ女性（比較・選び方・ノウハウ）。"""
    body = (
        '<ellipse cx="250" cy="440" rx="180" ry="14" fill="#000" opacity=".06"/>'
        '<rect x="285" y="120" width="130" height="170" rx="12" fill="#FFFFFF" stroke="#D9CFC4" stroke-width="4"/>'
        '<rect x="325" y="108" width="50" height="20" rx="6" fill="#B9A89A"/>'
        + "".join(
            f'<rect x="305" y="{150 + i * 40}" width="20" height="20" rx="4" fill="none" stroke="#5B8FD1" stroke-width="3"/>'
            f'<path d="M309 {160 + i * 40} l5 6 l10 -12" stroke="#F28C6B" stroke-width="4" fill="none" stroke-linecap="round"/>'
            f'<rect x="335" y="{156 + i * 40}" width="{60 - i * 10}" height="8" rx="4" fill="#E3DCD3"/>'
            for i in range(3)
        )
        + person(195, 200, 1.25, top="#5B8FD1", bottom="#6B5B53", hair_style="pony", arm_l=(-40, 95), arm_r=(80, 40))
        + _sparkle(430, 100, 1.0) + _sparkle(110, 140, 0.7, "#8CC9A8")
    )
    return _svg(body, "#E6EEF9")


def step_forward() -> str:
    """前に一歩ふみ出す女性（前向き・背中を押す）。"""
    body = (
        '<circle cx="380" cy="130" r="44" fill="#FFD27A"/>'
        + "".join(f'<path d="M380 130 L{380 + 70 * c} {130 + 70 * s}" stroke="#FFD27A" stroke-width="6" stroke-linecap="round" opacity=".7"/>'
                  for c, s in ((1, 0), (0.7, 0.7), (0, 1), (-0.7, 0.7), (-1, 0), (0.7, -0.7), (0, -1), (-0.7, -0.7)))
        + '<clipPath id="c"><circle cx="250" cy="260" r="215"/></clipPath>'
        '<path clip-path="url(#c)" d="M20 420 Q250 360 480 420 L480 480 L20 480 Z" fill="#BFE3C8"/>'
        + person(230, 190, 1.25, top="#F28C6B", bottom="#7A93C2", arm_l=(-60, 40), arm_r=(48, 100), eyes="smile")
        + "".join(f'<g transform="translate({x},{y})"><circle r="9" fill="{c}"/><circle r="4" fill="#FFF3C4"/></g>'
                  for x, y, c in ((90, 410, "#F6A6B2"), (130, 400, "#F6C453"), (380, 405, "#F6A6B2"), (420, 412, "#9DB6E0")))
        + _sparkle(120, 140, 1.1) + _sparkle(330, 250, 0.7)
    )
    return _svg(body, "#FFF1D6")


ILLUSTRATIONS = {
    "mom_and_kids": mom_and_kids,
    "tired_night": tired_night,
    "teacher": teacher,
    "checklist": checklist,
    "step_forward": step_forward,
}
