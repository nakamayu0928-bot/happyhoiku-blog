"""プレゼント用「Excelテンプレ3点セット 使い方ガイド」(PDF) を作るスクリプト。

使い方: python make_templates_guide_pdf.py [フォントのパス]
  フォントは丸ゴシック（Zen Maru Gothic）を想定。省略時は IPAゴシック を使う。
  画面イメージは img/shot_*.png（テンプレをPDF化してから切り出したもの）を使う。
出力:   keiri-templates-guide.pdf（このファイルと同じフォルダ）
"""
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

HERE = Path(__file__).parent
OUT = HERE / "keiri-templates-guide.pdf"
FONT_PATH = sys.argv[1] if len(sys.argv) > 1 else "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"
pdfmetrics.registerFont(TTFont("JP", FONT_PATH))

ORANGE = HexColor("#F28C28")
ORANGE_LIGHT = HexColor("#FFF3E6")
ORANGE_MID = HexColor("#FCE3C8")
YELLOW = HexColor("#FFF6BF")
GREEN = HexColor("#5B9A4B")
INK = HexColor("#3A3A3A")
GRAY = HexColor("#7A7A7A")
BOX = HexColor("#FAFAF7")
LINE = HexColor("#E6D9C8")

W, H = A4
MARGIN = 18 * mm
CW = W - 2 * MARGIN
HANDLE = "@mikan_keiri"


def st(name, size=10, leading=None, color=INK, **kw):
    return ParagraphStyle(name, fontName="JP", fontSize=size, leading=leading or size * 1.7,
                          textColor=color, wordWrap="CJK", **kw)


S = {
    "h1": st("h1", 18, 26, ORANGE, spaceAfter=4),
    "lead": st("lead", 10, 17, GRAY, spaceAfter=10),
    "h3": st("h3", 12, 18, INK),
    "body": st("body", 10, 17),
    "small": st("small", 8.5, 14, GRAY),
    "prompt": st("prompt", 9.5, 16.5),
    "cell": st("cell", 9, 15),
    "label": st("label", 8.5, 12, white, alignment=TA_CENTER),
}


def P(text, style="body"):
    return Paragraph(text, S[style])


def hl(text):
    t = escape(text).replace("\n", "<br/>")
    return re.sub(r"(［[^］]*］)", r'<font color="#E0701A">\1</font>', t)


def grid(rows, widths, head=True):
    t = Table([[P(c, "cell") for c in r] for r in rows], colWidths=widths)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.6, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]
    if head:
        style.append(("BACKGROUND", (0, 0), (-1, 0), ORANGE_MID))
    t.setStyle(TableStyle(style))
    return t


def box(flowables, bg=BOX):
    t = Table([[flowables]], colWidths=[CW])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.8, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("ROUNDEDCORNERS", [5, 5, 5, 5]),
    ]))
    return t


def shot(name):
    path = HERE / "img" / name
    img = Image(str(path))
    ratio = CW / img.imageWidth
    img.drawWidth, img.drawHeight = CW, img.imageHeight * ratio
    frame = Table([[img]], colWidths=[CW])
    frame.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return [frame, P("※ 画面はサンプル行が入った状態です", "small"), Spacer(1, 8)]


def tag(text):
    t = Table([[P(text, "label")]], colWidths=[30 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GREEN),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    t.hAlign = "LEFT"
    return t


# ------------------------------------------------------------------ ページ装飾
def cover(c, doc):
    c.saveState()
    c.setFillColor(ORANGE_LIGHT)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(ORANGE)
    c.circle(W - 48 * mm, H - 62 * mm, 30 * mm, stroke=0, fill=1)
    c.setFillColor(HexColor("#F7A957"))
    c.circle(W - 40 * mm, H - 54 * mm, 9 * mm, stroke=0, fill=1)
    c.setFillColor(GREEN)
    c.ellipse(W - 52 * mm, H - 34 * mm, W - 36 * mm, H - 27 * mm, stroke=0, fill=1)

    x = MARGIN + 4 * mm
    c.setFillColor(GRAY)
    c.setFont("JP", 12)
    c.drawString(x, H - 112 * mm, "ダウンロードして、そのまま使える")
    c.setFillColor(INK)
    c.setFont("JP", 30)
    c.drawString(x, H - 129 * mm, "経理・事務の")
    c.setFillColor(ORANGE)
    c.drawString(x, H - 146 * mm, "Excelテンプレ3点セット")
    c.setFillColor(INK)
    c.setFont("JP", 12)
    c.drawString(x, H - 160 * mm, "入力するだけで、チェックと集計が自動で終わる")

    items = ["経費精算表（領収書もれ・二重申請・高額申請を自動チェック）",
             "請求・入金管理表（未入金・期日超過・手数料差引を自動表示）",
             "月次集計表（勘定科目別・取引先別に月ごとの集計を自動作成）",
             "使い方ガイド＋Claudeで自分の会社用に直すプロンプト"]
    y = H - 184 * mm
    for it in items:
        c.setFillColor(ORANGE)
        c.circle(x + 2 * mm, y + 1.3 * mm, 1.4 * mm, stroke=0, fill=1)
        c.setFillColor(INK)
        c.setFont("JP", 11)
        c.drawString(x + 6 * mm, y, it)
        y -= 9 * mm

    c.setFillColor(ORANGE)
    c.rect(0, 0, W, 22 * mm, stroke=0, fill=1)
    c.setFillColor(white)
    c.setFont("JP", 12)
    c.drawString(MARGIN, 9 * mm, f"みかん｜{HANDLE}")
    c.setFont("JP", 9)
    c.drawRightString(W - MARGIN, 9 * mm, "※ サンプルのデータ・会社名はすべて架空のものです")
    c.restoreState()


def later(c, doc):
    c.saveState()
    c.setFillColor(ORANGE)
    c.rect(0, H - 6 * mm, W, 6 * mm, stroke=0, fill=1)
    c.setFillColor(GRAY)
    c.setFont("JP", 8)
    c.drawString(MARGIN, 10 * mm, f"経理・事務のExcelテンプレ3点セット　{HANDLE}")
    c.drawRightString(W - MARGIN, 10 * mm, f"{doc.page}")
    c.restoreState()


# ------------------------------------------------------------------ 本文
story = [PageBreak()]

story += [
    P("はじめに", "h1"),
    P("毎月の経費精算・入金確認・月次の集計を、「入力するだけ」で終わらせるためのテンプレートです。"
      "関数を知らなくても使えるように、数式はすべて入れてあります。", "lead"),
    P("入っているもの", "h3"), Spacer(1, 4),
    grid([
        ["ファイル", "内容"],
        ["keiri-templates.xlsx", "Excelテンプレ本体（はじめに／経費精算／請求・入金／月次集計／設定の5シート）"],
        ["このPDF", "使い方ガイドと、Claudeで自分の会社用に直すためのプロンプト集"],
    ], [42 * mm, CW - 42 * mm]),
    Spacer(1, 14),
    P("使いはじめの3ステップ", "h3"), Spacer(1, 4),
    grid([
        ["ステップ", "やること"],
        ["① 設定を合わせる", "「設定」シートで、勘定科目・取引先・申請者・年度の開始月を自分の会社に合わせます。"
                          "ここで入れた内容が、ほかのシートの選択リストになります。"],
        ["② サンプルを消す", "「経費精算」「請求・入金」のサンプル行（内容やメモに「サンプル」とある行）の、"
                          "黄色いセルの中身を消します。行ごと削除はしないでください。"],
        ["③ 入力する", "黄色いセルに入力するだけ。チェック・状況・集計は自動で表示されます。"],
    ], [34 * mm, CW - 34 * mm]),
    Spacer(1, 14),
    P("セルの色の意味", "h3"), Spacer(1, 4),
]
legend = Table([
    [P("黄色", "cell"), P("入力するセル。自由に書きかえてOKです。", "cell")],
    [P("白", "cell"), P("自動で計算するセル。数式が入っているので、消したり上書きしたりしないでください。", "cell")],
    [P("オレンジ", "cell"), P("チェックにひっかかった行や、期日超過などの注意が必要な行です。", "cell")],
], colWidths=[24 * mm, CW - 24 * mm])
legend.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.6, LINE),
    ("BACKGROUND", (0, 0), (0, 0), YELLOW),
    ("BACKGROUND", (0, 2), (0, 2), HexColor("#FDDCB5")),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
]))
story += [legend, Spacer(1, 10),
          P("※ 行を削除・挿入すると数式がずれることがあります。行を空けたいときは、黄色いセルの中身だけを消してください。"
            "入力欄は1シート200行まで用意しています。", "small"),
          PageBreak()]

# ① 経費精算
story += [
    tag("テンプレ①"), Spacer(1, 4),
    P("経費精算表", "h1"),
    P("申請を1行ずつ入力するだけで、見落としやすいミスに自動で印がつきます。", "lead"),
    *shot("shot_keihi.png"),
    P("自動でつくチェック", "h3"), Spacer(1, 4),
    grid([
        ["表示", "印がつく条件", "確認すること"],
        ["領収書なし", "「領収書」が「なし」になっている", "領収書の提出をお願いする。出せない理由があれば、メモを残す"],
        ["重複?", "申請日・申請者・金額がまったく同じ申請がほかにもある", "二重申請ではないか、申請者に確認する"],
        ["金額要確認", "金額が「設定」シートの基準（最初は30,000円）以上", "内容と金額が合っているか、桁の打ちまちがいがないか確認する"],
    ], [26 * mm, 62 * mm, CW - 88 * mm]),
    Spacer(1, 10),
    P("右側には<b>勘定科目別の合計と件数</b>、その下に<b>チェックがついた件数</b>と<b>承認がまだの件数</b>が自動で出ます。"
      "締め日の前に、この2つが0になっているかを見るだけで確認が終わります。"),
    Spacer(1, 6),
    P("★ 「金額要確認」の基準は、「設定」シートの「要確認とする金額」で変えられます。", "small"),
    PageBreak(),
]

# ② 請求・入金
story += [
    tag("テンプレ②"), Spacer(1, 4),
    P("請求・入金管理表", "h1"),
    P("請求を出したら左側を、入金があったら入金日と入金額を入れるだけ。「状況」が自動で変わります。", "lead"),
    *shot("shot_seikyu.png"),
    P("「状況」の見方", "h3"), Spacer(1, 4),
    grid([
        ["状況", "意味", "次にやること"],
        ["未入金", "入金額が空で、支払期日はまだ先", "期日まで待つ"],
        ["期日超過", "入金額が空のまま、支払期日を過ぎた", "取引先に確認の連絡をする"],
        ["手数料差引?", "請求額より少ないが、差額が「設定」の上限（最初は880円）以内", "取引条件で、振込手数料がどちらの負担か確認する"],
        ["一部入金", "請求額より、上限をこえて少ない入金", "残りの入金予定を確認する"],
        ["過入金", "請求額より多い入金", "二重の振込や、別の請求分ではないか確認する"],
        ["入金済", "請求額と入金額が一致", "消し込み完了"],
    ], [26 * mm, 70 * mm, CW - 96 * mm]),
    Spacer(1, 10),
    P("右側の<b>状況のまとめ</b>で、件数と金額がひと目でわかります。月末は「期日超過」が0件かどうかを確認しましょう。"),
    Spacer(1, 6),
    P("★ 「期日超過」は、ファイルを開いた日の日付で判定します。", "small"),
    PageBreak(),
]

# ③ 月次集計
story += [
    tag("テンプレ③"), Spacer(1, 4),
    P("月次集計表", "h1"),
    P("このシートは入力不要です。経費精算と請求・入金に入れた内容が、月ごとに自動で集計されます。", "lead"),
    *shot("shot_getsuji.png"),
    grid([
        ["集計", "内容"],
        ["経費（勘定科目別）", "経費精算の「申請日」の月で、勘定科目ごとに合計"],
        ["請求額（取引先別）", "請求・入金の「請求日」の月で、取引先ごとに合計"],
        ["入金額の合計", "請求・入金の「入金日」の月で合計"],
    ], [40 * mm, CW - 40 * mm]),
    Spacer(1, 10),
    P("★ 年度の始まりは「設定」シートの「年度の開始年」「年度の開始月」で変えられます（最初は2026年4月始まり）。", "small"),
    Spacer(1, 12),
    P("上司への報告コメントは、Claudeに下書きしてもらうと早いです", "h3"), Spacer(1, 4),
    box([P(hl("下の月次集計表をもとに、［10月］の経費について上司に報告するコメントを3〜4文で書いてください。\n"
              "前の月とくらべて増えた勘定科目・減った勘定科目と、その理由として考えられることを入れてください。\n"
              "数字は表にあるものだけを使い、推測の部分は「〜の可能性があります」と書いてください。\n"
              "（月次集計表の経費の部分をここに貼り付け）"), "prompt")]),
    PageBreak(),
]

# Claudeで直す
story += [
    P("Claudeで「自分の会社用」に直す", "h1"),
    P("会社によって、必要な列や集計の仕方はちがいます。Claudeに聞けば、数式をこわさずに直す方法を教えてくれます。"
      "<font color='#E0701A'>［ ］</font>の部分を書きかえて使ってください。", "lead"),
]
fixes = [
    ("列を追加したい",
     "このExcelテンプレの［経費精算］シートに［部門］の列を追加したいです。\n"
     "シートの列は［A:No、B:申請日、C:申請者、D:勘定科目、E:内容、F:金額、G:領収書、H:承認、I:チェック］です。\n"
     "ほかのシートの数式がずれないように、手順を1つずつ教えてください。"),
    ("部門別にも集計したい",
     "［経費精算］シートの［J列］に部門を入れるようにしました。\n"
     "［月次集計］シートに、部門別・月別の経費の合計を出す表を追加したいです。\n"
     "金額は［F列］、申請日は［B列］です。SUMIFSを使った数式と、表の作り方を教えてください。"),
    ("チェックの条件を増やしたい",
     "［経費精算］シートのチェック欄（I列）は、今はこの数式です。\n［（I6の数式をここに貼り付け）］\n"
     "これに、［勘定科目が「接待交際費」で、内容に人数が書かれていない場合］にも印をつける条件を追加したいです。\n"
     "追加した数式と、どこを変えたのかを教えてください。"),
    ("入金の消し込みを楽にしたい",
     "［請求・入金］シートの請求一覧と、銀行からダウンロードした入金明細（CSV）を照合したいです。\n"
     "入金明細には［入金日、振込名義（カナ）、金額］が入っています。\n"
     "「設定」シートの［取引先と振込名義（カナ）の対応表］を使って、どの請求の入金かを自動で探す方法を教えてください。"),
    ("印刷しやすくしたい",
     "［請求・入金］シートを、A4横1枚に収めて印刷したいです。\n"
     "入力のある行だけを印刷する方法と、毎月同じ設定で印刷する方法を教えてください。Excelのバージョンは［365］です。"),
]
for i, (t, p) in enumerate(fixes, 1):
    story += [KeepTogether([
        P(f"<font color='#5B9A4B'>●</font> {i}. {t}", "h3"), Spacer(1, 3),
        box([P(hl(p), "prompt")]), Spacer(1, 10),
    ])]
story += [
    P("★ 直す前に、必ずファイルのコピーを保存してから試してください。", "small"),
    PageBreak(),
]

# 注意＋おわりに
story += [
    P("使う前に確認してほしいこと", "h1"),
    P("テンプレは「見落とし防止」のための道具です。最後の判断は、担当者のあなたが行ってください。", "lead"),
]
checks = [
    "会社の経理規程や承認のながれと、テンプレの使い方が合っているか確認した",
    "「設定」シートの基準（要確認とする金額・手数料の上限）を、会社のルールに合わせた",
    "Claudeに表を貼るときは、取引先名・個人名・口座番号などを伏せた",
    "Claudeに作ってもらった数式は、少ないデータで試してから使った",
    "大事な合計は、電卓や別の方法でも確かめた",
    "テンプレを直す前に、ファイルのコピーを保存した",
]
t = Table([[P("□", "h3"), P(cx)] for cx in checks], colWidths=[10 * mm, CW - 10 * mm])
t.setStyle(TableStyle([
    ("LINEBELOW", (0, 0), (-1, -1), 0.6, LINE),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
]))
story += [t, Spacer(1, 22)]
story += [box([P(
    "<font size='13' color='#F28C28'>おわりに</font><br/><br/>"
    "受け取っていただき、ありがとうございます。<br/>"
    "経理や事務の仕事は「合っていて当たり前」と思われがちですが、毎日ちゃんと合わせているあなたは本当にすごいです。<br/>"
    "このテンプレで、毎月の確認作業が少しでも軽くなればうれしいです。<br/><br/>"
    f"使ってみた感想や「こう直したら便利だった」は、Xの <font color='#F28C28'>{HANDLE}</font> で教えてください。"
    "ClaudeとExcelで事務・経理がちょっと楽になるコツを、毎日発信しています。")], ORANGE_LIGHT),
    Spacer(1, 10),
    P("※ サンプルのデータ・会社名はすべて架空のものです。Claude はAnthropic社のAIアシスタントです。"
      "Excelやアプリの画面・機能の名前は、更新によって変わることがあります。", "small")]

doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                        topMargin=16 * mm, bottomMargin=18 * mm,
                        title="経理・事務のExcelテンプレ3点セット 使い方ガイド", author=HANDLE)
doc.build(story, onFirstPage=cover, onLaterPages=later)
print(OUT)
