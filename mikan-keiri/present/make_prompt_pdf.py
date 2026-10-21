"""プレゼント用「Claude×Excel プロンプト20選」(PDF) を作るスクリプト。

使い方: python make_prompt_pdf.py [フォントのパス]
  フォントは丸ゴシック（Zen Maru Gothic）を想定。省略時は IPAゴシック を使う。
出力:   claude-excel-prompts.pdf（このファイルと同じフォルダ）
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
    CondPageBreak, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

OUT = Path(__file__).with_name("claude-excel-prompts.pdf")
FONT_PATH = sys.argv[1] if len(sys.argv) > 1 else "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"
pdfmetrics.registerFont(TTFont("JP", FONT_PATH))

ORANGE = HexColor("#F28C28")
ORANGE_LIGHT = HexColor("#FFF3E6")
ORANGE_MID = HexColor("#FCE3C8")
GREEN = HexColor("#5B9A4B")
INK = HexColor("#3A3A3A")
GRAY = HexColor("#7A7A7A")
BOX = HexColor("#FAFAF7")
LINE = HexColor("#E6D9C8")

W, H = A4
MARGIN = 18 * mm
HANDLE = "@mikan_keiri"


def st(name, size=10, leading=None, color=INK, **kw):
    return ParagraphStyle(name, fontName="JP", fontSize=size, leading=leading or size * 1.7,
                          textColor=color, wordWrap="CJK", **kw)


S = {
    "h1": st("h1", 18, 26, ORANGE, spaceAfter=4),
    "lead": st("lead", 10, 17, GRAY, spaceAfter=10),
    "h2": st("h2", 13, 20, white),
    "h3": st("h3", 12, 18, INK),
    "body": st("body", 10, 17),
    "small": st("small", 8.5, 14, GRAY),
    "prompt": st("prompt", 9.5, 16.5),
    "label": st("label", 8.5, 12, white, alignment=TA_CENTER),
    "cell": st("cell", 9, 15),
    "cellh": st("cellh", 9, 15, INK),
}


def P(text, style="body"):
    return Paragraph(text, S[style])


def hl(text):
    """［ ］の部分をオレンジ色にする。"""
    t = escape(text).replace("\n", "<br/>")
    return re.sub(r"(［[^］]*］)", r'<font color="#E0701A">\1</font>', t)


def section(title):
    t = Table([[P(title, "h2")]], colWidths=[W - 2 * MARGIN])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), ORANGE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
    ]))
    return [CondPageBreak(70 * mm), Spacer(1, 4), t, Spacer(1, 8)]


def prompt_card(no, title, scene, prompt, practice=None, point=None):
    num = Table([[P(f"No.{no}", "label")]], colWidths=[16 * mm])
    num.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GREEN),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    head = Table([[num, P(title, "h3")]], colWidths=[19 * mm, W - 2 * MARGIN - 19 * mm])
    head.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))
    box = Table([[P(hl(prompt), "prompt")]], colWidths=[W - 2 * MARGIN])
    box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BOX),
        ("BOX", (0, 0), (-1, -1), 0.8, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("ROUNDEDCORNERS", [5, 5, 5, 5]),
    ]))
    parts = [head, P(f"使う場面：{scene}", "small"), Spacer(1, 3), box]
    extra = []
    if practice:
        extra.append(f'<font color="#5B9A4B">■ 練習</font> {practice}')
    if point:
        extra.append(f'<font color="#E0701A">★ ポイント</font> {point}')
    for e in extra:
        parts += [Spacer(1, 3), P(e, "small")]
    return [KeepTogether(parts), Spacer(1, 12)]


def grid(rows, widths, head=True):
    data = [[P(c, "cellh" if (head and i == 0) else "cell") for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths)
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


# ------------------------------------------------------------------ ページ装飾
def cover(c, doc):
    c.saveState()
    c.setFillColor(ORANGE_LIGHT)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    # みかんの丸
    c.setFillColor(ORANGE)
    c.circle(W - 48 * mm, H - 62 * mm, 30 * mm, stroke=0, fill=1)
    c.setFillColor(HexColor("#F7A957"))
    c.circle(W - 40 * mm, H - 54 * mm, 9 * mm, stroke=0, fill=1)
    c.setFillColor(GREEN)
    c.ellipse(W - 52 * mm, H - 34 * mm, W - 36 * mm, H - 27 * mm, stroke=0, fill=1)

    c.setFillColor(GRAY)
    c.setFont("JP", 12)
    c.drawString(MARGIN + 4 * mm, H - 112 * mm, "経理・事務のための")
    c.setFillColor(INK)
    c.setFont("JP", 34)
    c.drawString(MARGIN + 4 * mm, H - 130 * mm, "Claude × Excel")
    c.setFillColor(ORANGE)
    c.setFont("JP", 30)
    c.drawString(MARGIN + 4 * mm, H - 148 * mm, "プロンプト20選")
    c.setFillColor(INK)
    c.setFont("JP", 12)
    c.drawString(MARGIN + 4 * mm, H - 162 * mm, "コピペして［ ］を書きかえるだけ。練習用Excelシートつき")

    items = ["回答の質を上げる「裏スイッチ」早見表", "場面別プロンプト20選（数式・エラー・照合・マクロ）",
             "練習用Excelシート（ダミーデータ）", "安全に使うためのチェックリスト"]
    y = H - 186 * mm
    for it in items:
        c.setFillColor(ORANGE)
        c.circle(MARGIN + 6 * mm, y + 1.3 * mm, 1.4 * mm, stroke=0, fill=1)
        c.setFillColor(INK)
        c.setFont("JP", 11)
        c.drawString(MARGIN + 10 * mm, y, it)
        y -= 9 * mm

    c.setFillColor(ORANGE)
    c.rect(0, 0, W, 22 * mm, stroke=0, fill=1)
    c.setFillColor(white)
    c.setFont("JP", 12)
    c.drawString(MARGIN, 9 * mm, f"みかん｜{HANDLE}")
    c.setFont("JP", 9)
    c.drawRightString(W - MARGIN, 9 * mm, "※ データはすべて架空のダミーです")
    c.restoreState()


def later(c, doc):
    c.saveState()
    c.setFillColor(ORANGE)
    c.rect(0, H - 6 * mm, W, 6 * mm, stroke=0, fill=1)
    c.setFillColor(GRAY)
    c.setFont("JP", 8)
    c.drawString(MARGIN, 10 * mm, f"Claude × Excel プロンプト20選　{HANDLE}")
    c.drawRightString(W - MARGIN, 10 * mm, f"{doc.page}")
    c.restoreState()


# ------------------------------------------------------------------ 本文
story = [PageBreak()]

# はじめに
story += [
    P("はじめに", "h1"),
    P("このプロンプト集は、経理・一般事務の仕事でClaudeとExcelを組み合わせて、"
      "「関数がわからなくて手が止まる時間」を減らすためのものです。", "lead"),
    P("使い方は3ステップ", "h3"), Spacer(1, 4),
    grid([
        ["ステップ", "やること"],
        ["① コピー", "使いたいプロンプトをコピーして、Claudeの入力欄に貼り付けます。"],
        ["② 書きかえ", "<font color='#E0701A'>［ ］</font>の部分を、自分の表や状況に合わせて書きかえます。"
                      "列の場所（A列・C列など）とExcelのバージョンは、とくに大事です。"],
        ["③ 表を渡す", "表の一部をコピーして貼り付けるか、Excelファイルを添付します。"
                      "まずは練習用シートのダミーデータで試してみてください。"],
    ], [28 * mm, W - 2 * MARGIN - 28 * mm]),
    Spacer(1, 14),
    P("練習用シートについて", "h3"), Spacer(1, 4),
    P("同梱の「claude-excel-practice.xlsx」には、売上表・経費精算・取引先リストなどのダミーデータが入っています。"
      "表記ゆれ・二重申請・入金額のズレなど、実務でよくある「ミス」をわざと入れてあります。"
      "<font color='#5B9A4B'>■ 練習</font> と書かれたプロンプトは、このシートでそのまま試せます。"),
    Spacer(1, 10),
    P("ご注意", "h3"), Spacer(1, 4),
    P("・実際の業務データを使うときは、会社のルールを確認してください。取引先名・個人名・口座番号などは伏せてから使いましょう。<br/>"
      "・Claudeの答えがいつも正しいとは限りません。数式は少ないデータで試し、大事な数字は別の方法でも確かめてください。<br/>"
      "・アプリの画面や設定の名前は、更新によって変わることがあります。"),
    PageBreak(),
]

# 裏スイッチ早見表
story += [
    P("回答の質を上げる「裏スイッチ」早見表", "h1"),
    P("隠しコマンドはありません。でも、頼み方を少し変えるだけで、返ってくる答えがはっきり変わります。", "lead"),
    grid([
        ["スイッチ", "頼み方の例", "効く理由"],
        ["① 先に質問させる", "「答える前に、わからない点があれば質問して」", "足りない情報を推測で埋めずに、聞き返してくれる"],
        ["② 立場と状況を伝える", "「経理担当です。Excelは365。月末の締め作業で使います」",
         "バージョンで使える関数がちがうので、自分の環境に合う方法が返ってくる"],
        ["③ 見本の表を貼る", "「こんな表です（ダミーの3〜5行）」", "列の並びがわかるので、そのまま使える数式になる"],
        ["④ 見直しをさせる", "「出した数式に間違いがないか確認してから答えて」", "見落としが減る"],
        ["⑤ じっくり考えるモード", "アプリの「拡張思考（Extended thinking）」をオンにする",
         "答える前に時間をかけて考えるので、複雑な集計やマクロで差が出る"],
    ], [34 * mm, 66 * mm, W - 2 * MARGIN - 100 * mm]),
    Spacer(1, 16),
    P("ビフォー・アフター", "h3"), Spacer(1, 4),
    grid([
        ["", "聞き方"],
        ["<font color='#B04040'>× ビフォー</font>", "売上を集計する数式教えて"],
        ["<font color='#5B9A4B'>○ アフター</font>",
         "Excel365を使っています。A列が日付、C列が取引先、G列が金額の表です。"
         "月ごとの金額の合計を出す数式を教えてください。"
         "ほかの月にもコピーして使える形にしてください。わからない点があれば、先に質問してください。"],
    ], [28 * mm, W - 2 * MARGIN - 28 * mm]),
    Spacer(1, 10),
    P("アフターの聞き方には「バージョン」「表の形」「目的」「使い方」「質問していいよ」の5つが入っています。"
      "この5つを意識するだけで、ほとんどの質問の答えがよくなります。"),
    PageBreak(),
]

# プロンプト20選
cards = [
    ("A　数式をつくる", [
        ("月別の合計を出す", "売上表や経費表から、月ごとの合計を出したいとき",
         "Excel［365］を使っています。\n［A列が日付、C列が取引先、G列が金額］の表があります（データは［5行目〜28行目］）。\n"
         "［2026年9月］の金額の合計を出す数式を作ってください。\n"
         "ほかの月にもコピーして使えるように、月は別のセルで指定できる形にしてください。\n"
         "わからない点があれば、答える前に質問してください。",
         "「売上表」シートの黄色いセル（練習①）", "「コピーして使える形に」と添えると、使い回しやすい数式になります。"),
        ("条件ごとに合計する（取引先別・科目別）", "取引先ごと・勘定科目ごとに金額をまとめたいとき",
         "Excel［365］です。下の表で、［取引先］ごとの［金額］の合計を出したいです。\n"
         "集計表は［J列に取引先名、K列に合計］の形で作ります。\n"
         "K列に入れる数式と、その数式の意味を1つずつ説明してください。\n（表をここに貼り付け）",
         "「売上表」の練習②、「経費精算」の練習③", None),
        ("別の表から値を取り出す", "商品コードから単価を、取引先IDから名前を引っぱってきたいとき",
         "Excel［365］です。\n［売上表］の［D列：商品コード］をもとに、［商品マスタ］シートから［単価］を取り出したいです。\n"
         "商品マスタは［A列：商品コード、B列：商品名、C列：単価］です。\n"
         "VLOOKUP・XLOOKUP・INDEXとMATCHのどれを使うのがよいか、理由も含めて教えてください。",
         "「売上表」と「商品マスタ」（売上表のF列に答えの一例が入っています）",
         "XLOOKUPはMicrosoft 365やExcel 2021以降で使える関数です。バージョンを伝えると、使える関数で答えてくれます。"),
        ("日付から「年月」「曜日」「月末」を出す", "日付の列から、集計やチェックに使う情報を作りたいとき",
         "Excel［365］です。［A列］に日付が入っています。\n"
         "① 「2026年9月」のように年月だけを表示する\n② 曜日を「月」「火」のように表示する\n③ その月の月末の日付を出す\n"
         "の3つの数式を作ってください。表示形式を変えるだけでできるものは、その方法も教えてください。",
         "「売上表」のA列", None),
        ("消費税・端数の計算", "税込金額や消費税額を、決まった端数処理で出したいとき",
         "Excel［365］です。［税抜金額がE列］に入っています。\n"
         "消費税［10％］の金額を［1円未満切り捨て］で計算する数式と、税込金額を出す数式を作ってください。\n"
         "切り捨て・四捨五入・切り上げで使う関数のちがいも、かんたんに説明してください。",
         None, "端数処理のルールは会社や取引先で決まっていることが多いので、先に確認しておきましょう。"),
    ]),
    ("B　エラー・ミスを解決する", [
        ("エラーの原因を聞く（#N/A など）", "数式がエラーになって、どこが悪いのかわからないとき",
         "この数式で［#N/A］エラーが出ます。原因として考えられることを、可能性が高い順に教えてください。\n"
         "それぞれの確かめ方と直し方もお願いします。\n数式：［=VLOOKUP(D5,商品マスタ!A:C,3,FALSE)］\n"
         "探している値：［A-102］\n（表の一部をここに貼り付け）",
         "「商品マスタ」のコードを1つ書きかえて、わざとエラーを出してから聞いてみましょう",
         "「数式」「エラーの種類」「データ」の3つをセットで渡すと、原因が早く見つかります。"),
        ("数式の意味を説明してもらう", "前の担当者が作った数式が読めないとき",
         "前の担当者が作ったこの数式の意味がわかりません。\n［=IFERROR(INDEX(C:C,MATCH(D5,A:A,0)),\"\")］\n"
         "① 何をしている数式か、ひとことで\n② 部分ごとの意味\n③ 気をつけること（壊れやすい点）\n"
         "の順で、Excel初心者にもわかるように説明してください。",
         None, "引き継ぎ資料にそのまま使えるので、答えはメモしておくと便利です。"),
        ("合計が合わない原因をさがす", "SUMの合計と電卓の合計がずれるとき",
         "SUMで合計を出していますが、電卓で計算した合計と［1］ずれます。\n"
         "考えられる原因と、表の中から原因のセルを見つける方法を教えてください。\n（表をここに貼り付け）",
         "「売上表」の数量合計（ピンクのセルに原因があります）",
         "よくある原因は「文字として入った数字」「非表示の行」「範囲の指定もれ」の3つです。"),
        ("循環参照・計算されないときの確認", "警告が出る、数字が更新されないとき",
         "Excelで［「循環参照」の警告が出ます／数式を入れても結果が更新されません］。\n"
         "原因として考えられることと、確認する手順を、画面のどこを見ればいいかも含めて教えてください。\n"
         "Excelのバージョンは［365］です。", None, None),
    ]),
    ("C　データを整える", [
        ("表記ゆれをそろえる", "同じ取引先がちがう名前で何件も登録されているとき",
         "下の取引先リストには、同じ会社がちがう書き方で入っています（株式会社／(株)、全角／半角、空白など）。\n"
         "① 同じ会社だと思われるものをグループにまとめる\n② 統一した名前の案を出す\n③ 判断に迷うものは理由つきで別に挙げる\n"
         "の順でお願いします。\n（リストをここに貼り付け）",
         "「取引先リスト」（電話番号もヒントになります）", None),
        ("全角・半角・空白を数式で整える", "毎月同じ整形作業をくり返しているとき",
         "Excel［365］です。［B列］の取引先名について、\n・半角カナを全角にする\n・英数字を半角にそろえる\n"
         "・前後や途中の余計な空白を消す\nをまとめて行う数式を作ってください。\n使う関数と、その順番にする理由も教えてください。",
         "「取引先リスト」のE列（黄色いセル）", None),
        ("重複を見つける", "同じデータが二重に入っていないか確認したいとき",
         "Excel［365］です。［取引先リスト］で、［電話番号］が同じ行に印をつけたいです。\n"
         "① 重複している行がわかる数式\n② 条件付き書式で色をつける方法\nの両方を教えてください。"
         "削除はせず、まず目で確認したいです。",
         "「取引先リスト」", "いきなり削除せず、「印をつけて確認」から始めると安全です。"),
        ("CSVを正しく読み込む", "システムから出したCSVをExcelで開くと形がくずれるとき",
         "システムから出したCSVをExcelで開くと、［先頭の0が消える／日付が文字になる／文字化けする］ことがあります。\n"
         "原因と、毎月同じ手順で正しく読み込む方法を、手順書の形で教えてください。\nExcelのバージョンは［365］です。",
         None, None),
    ]),
    ("D　チェック・照合", [
        ("請求と入金を照合する", "月末の入金確認・消し込みのとき",
         "請求一覧と入金一覧を照合してください。\n・入金がない請求\n・金額が合わない請求（差額も）\n"
         "・どの請求か判断できない入金\nを表にまとめてください。振込名義はカタカナ表記です。\n"
         "差額が振込手数料の可能性があるものは、その旨を書いてください。\n（請求一覧と入金一覧をここに貼り付け）",
         "「請求と入金」シート",
         "最終的な判断は、通帳や取引先への確認で行いましょう。AIの結果は「下書き」として使うのが安全です。"),
        ("経費精算をチェックする", "申請をまとめて確認するとき",
         "経費精算の一覧をチェックしてください。\n・同じ日・同じ人・同じ金額の申請（二重申請の可能性）\n"
         "・領収書が「なし」の申請\n・内容と勘定科目が合っていないもの\nを、行番号と理由つきで挙げてください。\n（表をここに貼り付け）",
         "「経費精算」シート", None),
        ("いつもとちがう数字を見つける", "桁のまちがいや、不自然な金額を見つけたいとき",
         "この一覧の中で、金額が不自然なものを探してください。\n"
         "同じ勘定科目のほかの金額とくらべて、大きくはずれているものを理由つきで挙げてください。\n"
         "あわせて、同じチェックをExcelで自動でできる方法（数式や条件付き書式）も教えてください。",
         "「経費精算」（ピンクのセルの金額）", None),
    ]),
    ("E　自動化・手順書", [
        ("マクロ（VBA）を作ってもらう", "毎月同じ手作業をくり返しているとき",
         "Excel［365］で、次の作業を自動化するマクロ（VBA）を作ってください。\n"
         "作業：［「売上表」シートのデータを、月ごとに別のシートに分ける］\n条件：\n・元のデータは消さない\n"
         "・実行前に確認メッセージを出す\n・コードの各行にコメント（説明）をつける\n"
         "マクロの登録方法と、実行のしかたも教えてください。",
         "「売上表」シート", "初めて動かすときは、必ずファイルのコピーで試しましょう。"),
        ("毎月の作業を手順書にする", "引き継ぎや、休むときのために作業を残したいとき",
         "私が毎月やっている［月末の売上集計］の作業を、下に箇条書きで書きます。\n"
         "これを、新しく来た人でもできる手順書にしてください。\n・番号つきの手順\n・まちがえやすいポイント\n"
         "・終わったあとのチェック項目\nを入れてください。\n（作業メモをここに貼り付け）",
         None, "箇条書きはメモ程度でOK。「わからない点は質問して」と足すと、抜けている手順を聞き返してくれます。"),
    ]),
    ("F　報告・説明", [
        ("集計結果から報告コメントを書く", "上司への月次報告をまとめるとき",
         "下の［月別売上］の集計結果をもとに、上司に報告するコメントを3〜4文で書いてください。\n"
         "前の月とくらべて増えた点・減った点と、その理由として考えられることを入れてください。\n"
         "数字は表にあるものだけを使い、推測の部分は「〜の可能性があります」と書いてください。\n（集計表をここに貼り付け）",
         "「売上表」の練習①で出した月別の合計", "「表にある数字だけを使って」と書くと、ないはずの数字が出てくるのを防げます。"),
        ("関数を新人さんに教える", "後輩に教える資料を作りたいとき",
         "新人さんに［SUMIFS関数］を教えます。\n・ひとことで言うと何をする関数か\n・身近なたとえ\n"
         "・練習用の小さな表と答え\nをつけて、5分で説明できる資料にしてください。",
         None, None),
    ]),
]

story += [P("場面別プロンプト20選", "h1"),
          P("<font color='#E0701A'>［ ］</font>の部分を書きかえて使ってください。", "lead")]
n = 0
for sec, items in cards:
    story += section(sec)
    for item in items:
        n += 1
        story += prompt_card(n, *item)
assert n == 20, n

# チェックリスト
story += [
    PageBreak(),
    P("安全に使うためのチェックリスト", "h1"),
    P("便利だからこそ、ここだけは守りましょう。", "lead"),
]
checks = [
    "会社でAIを使ってよいか、使える範囲のルールを確認した",
    "取引先名・個人名・口座番号などは伏せた（「A社」「Bさん」などに置きかえる）",
    "貼り付けるデータは、必要な列・行だけにしぼった",
    "作ってもらった数式を、少ないデータで試してから全体に使った",
    "合計などの大事な数字は、電卓やピボットテーブルなど別の方法でも確かめた",
    "マクロは、ファイルのコピーで試してから使った",
    "最後の判断（支払い・計上・報告）は、自分で行った",
]
rows = [[P("□", "h3"), P(cx, "body")] for cx in checks]
t = Table(rows, colWidths=[10 * mm, W - 2 * MARGIN - 10 * mm])
t.setStyle(TableStyle([
    ("LINEBELOW", (0, 0), (-1, -1), 0.6, LINE),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
]))
story += [t, Spacer(1, 24)]

# おわりに
end = Table([[P(
    "<font size='13' color='#F28C28'>おわりに</font><br/><br/>"
    "最後まで読んでいただき、ありがとうございます。<br/>"
    "経理や事務の仕事は「合っていて当たり前」と思われがちですが、毎日ちゃんと合わせているあなたは本当にすごいです。<br/>"
    "Claudeは、そんなあなたの横にいる「なんでも聞ける先輩」のような存在です。"
    "まずは1つ、明日の仕事で試してみてください。<br/><br/>"
    f"使ってみた感想や「こんな使い方もできたよ」は、Xの <font color='#F28C28'>{HANDLE}</font> で教えてもらえるとうれしいです。"
    "事務・経理がちょっと楽になるコツを、毎日発信しています。", "body")]], colWidths=[W - 2 * MARGIN])
end.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), ORANGE_LIGHT),
    ("LEFTPADDING", (0, 0), (-1, -1), 14),
    ("RIGHTPADDING", (0, 0), (-1, -1), 14),
    ("TOPPADDING", (0, 0), (-1, -1), 12),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
    ("ROUNDEDCORNERS", [8, 8, 8, 8]),
]))
story += [end, Spacer(1, 10),
          P("※ 本資料のデータ・会社名はすべて架空のものです。Claude はAnthropic社のAIアシスタントです。"
            "アプリの画面や機能の名前は、更新によって変わることがあります。", "small")]

doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                        topMargin=16 * mm, bottomMargin=18 * mm,
                        title="経理・事務のための Claude×Excel プロンプト20選", author=HANDLE)
doc.build(story, onFirstPage=cover, onLaterPages=later)
print(OUT)
