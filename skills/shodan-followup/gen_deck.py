# -*- coding: utf-8 -*-
"""白基調・6ページの高卒採用提案書を生成する。
使い方: python3 gen_deck.py <content.json> <output.pdf>"""
import os, sys, json
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = next((p for p in [os.path.join(HERE,"assets","ipaexg.ttf"),"/tmp/deck/ipaexg.ttf"] if os.path.exists(p)), None)
if not FONT: raise SystemExit("ipaexg.ttf not found")
for n in ("HG-R","HG-B","HG-H"): pdfmetrics.registerFont(TTFont(n, FONT))

data = json.load(open(sys.argv[1], encoding="utf-8"))
OUT  = sys.argv[2]

W, H = 960, 540
NAVY  = HexColor("#143039"); TEAL  = HexColor("#1C9DB2"); TEAL_D = HexColor("#11788A")
SOFT  = HexColor("#E9F4F6"); SOFT2 = HexColor("#F4F9FB"); INK   = HexColor("#1F2B30")
MUTE  = HexColor("#5E6C72"); WHITE = HexColor("#FFFFFF"); LINE  = HexColor("#D6E6EA")

c = canvas.Canvas(OUT, pagesize=(W, H))

# ── faux-bold ────────────────────────────────────────────────────
_ds,_cs,_rs = c.drawString, c.drawCentredString, c.drawRightString
def _o(): return 0.7 if c._fontname=="HG-H" else (0.35 if c._fontname=="HG-B" else 0)
def drawString(x,y,t,*a,**k):        _ds(x,y,t,*a,**k); o=_o(); o and _ds(x+o,y,t,*a,**k)
def drawCentredString(x,y,t,*a,**k): _cs(x,y,t,*a,**k); o=_o(); o and _cs(x+o,y,t,*a,**k)
def drawRightString(x,y,t,*a,**k):   _rs(x,y,t,*a,**k); o=_o(); o and _rs(x+o,y,t,*a,**k)
c.drawString,c.drawCentredString,c.drawRightString = drawString,drawCentredString,drawRightString

# ── テキスト折り返し ─────────────────────────────────────────────
def wrap(text, font, size, maxw):
    lines, cur = [], ""
    for ch in text:
        if ch == "\n": lines.append(cur); cur=""; continue
        if pdfmetrics.stringWidth(cur+ch, font, size) <= maxw: cur += ch
        else: lines.append(cur); cur = ch
    if cur: lines.append(cur)
    return lines

def text_height(text, font, size, maxw, leading):
    """折り返し後の総高さを返す"""
    return len(wrap(text, font, size, maxw)) * leading

def fit_size(text, font, size_max, size_min, maxw, maxh, leading_ratio=1.35):
    """maxw×maxhに収まる最大フォントサイズを返す（leading = size * ratio）"""
    for s in range(int(size_max), int(size_min)-1, -1):
        if text_height(text, font, s, maxw, s*leading_ratio) <= maxh:
            return s
    return int(size_min)

def para(x, y, text, font, size, color, maxw, leading,
         max_height=None, size_min=None):
    """テキストを描画。max_height が指定されていれば収まるようフォントを縮小する。"""
    if max_height and size_min:
        size = fit_size(text, font, size, size_min, maxw, max_height,
                        leading/size if size else 1.35)
        leading = size * (leading / (size+0.001) if size else 1.35)
        # 念のため再計算
        leading = max(leading, size * 1.25)
    c.setFont(font, size); c.setFillColor(color)
    for ln in wrap(text, font, size, maxw):
        c.drawString(x, y, ln); y -= leading
    return y

def rrect(x,y,w,h,r, fill=None, stroke=None, sw=1):
    if fill   is not None: c.setFillColor(fill)
    if stroke is not None: c.setStrokeColor(stroke); c.setLineWidth(sw)
    c.roundRect(x,y,w,h,r, stroke=1 if stroke is not None else 0,
                            fill=1 if fill is not None else 0)

def chip(x,y,text,fg,bg,size=11,padx=10,padh=20):
    tw = pdfmetrics.stringWidth(text,"HG-B",size)
    rrect(x,y,tw+padx*2,padh,padh/2,fill=bg)
    c.setFont("HG-B",size); c.setFillColor(fg)
    c.drawString(x+padx, y+(padh-size)/2+1, text)

def circ(cx,cy,rad,glyph,bg,fg=WHITE,gsize=18):
    c.setFillColor(bg); c.circle(cx,cy,rad,stroke=0,fill=1)
    c.setFont("HG-B",gsize); c.setFillColor(fg)
    c.drawCentredString(cx, cy-gsize/2.7, glyph)

def footer(idx):
    c.setFont("HG-R",9); c.setFillColor(MUTE)
    c.drawString(40,22,"株式会社高卒採用バンク ｜ みらいジョブ")
    c.drawRightString(W-40,22,f"{idx} / 6")

def bg(): c.setFillColor(WHITE); c.rect(0,0,W,H,fill=1,stroke=0)

g = data.get

# ═══════════════════════════════════════════════════════════════
# Slide 1: Cover
# ═══════════════════════════════════════════════════════════════
bg(); rrect(40,40,W-80,H-80,20,fill=SOFT)
c.setFont("HG-B",13); c.setFillColor(TEAL_D)
c.drawString(80, H-110, g("kicker","高卒採用 ご提案資料"))

# タイトル（2行まで・自動縮小）
title_lines = g("cover_title","").split("\n")
ty = H-185
for ln in title_lines[:2]:
    # 1行が横幅に収まるサイズを探す
    sz = 42
    for s in range(42,24,-1):
        if pdfmetrics.stringWidth(ln,"HG-H",s) <= W-200: sz=s; break
    c.setFont("HG-H",sz); c.setFillColor(NAVY); c.drawString(80,ty,ln); ty -= sz*1.3

# リード文（max 3行・収まらなければ縮小）
para(82, ty-6, g("cover_lead",""), "HG-R", 15, INK, W-220, 22,
     max_height=60, size_min=11)

c.setFont("HG-B",16); c.setFillColor(NAVY); c.drawString(80,96, g("cover_client",""))
c.setFont("HG-R",11); c.setFillColor(MUTE);  c.drawString(80,72,"株式会社高卒採用バンク ｜ みらいジョブ")
c.showPage()

# ═══════════════════════════════════════════════════════════════
# Slide 2: Issues（3カード）
# ═══════════════════════════════════════════════════════════════
bg()
chip(60, H-78, "御社の採用課題", WHITE, TEAL, size=11)
c.setFont("HG-H",28); c.setFillColor(NAVY)
c.drawString(60, H-120, g("issues_heading","いま向き合うべき採用課題"))
para(60, H-148, g("issues_lead",""), "HG-R", 13, MUTE, 840, 20,
     max_height=20, size_min=10)

issues = g("issues",[])
n_cards = min(len(issues), 3)
# カード幅を動的に計算
total_gap = 20 * (n_cards-1)
cw = (W - 120 - total_gap) // n_cards
ch_ = 255
x0 = 60; y0 = H - 195 - ch_

for i, item in enumerate(issues[:3]):
    x = x0 + i*(cw+20)
    rrect(x, y0, cw, ch_, 14, fill=SOFT, stroke=LINE, sw=1)

    # アイコン
    circ(x+38, y0+ch_-50, 21, item[0] if item else "◎", TEAL, WHITE, gsize=18)

    # タイトル（1〜2行・自動縮小）
    title = item[1] if len(item)>1 else ""
    t_sz = fit_size(title,"HG-B",16,11, cw-44, 40, 1.35)
    para(x+22, y0+ch_-88, title, "HG-B", t_sz, NAVY, cw-44, t_sz*1.35,
         max_height=40, size_min=11)

    # 説明文（残りの高さに収まるよう縮小）
    desc = item[2] if len(item)>2 else ""
    desc_top = y0+ch_-140
    desc_h   = desc_top - (y0+22)      # 下マージン22px
    para(x+22, desc_top, desc, "HG-R", 12, INK, cw-44, 18,
         max_height=desc_h, size_min=9)

footer(2); c.showPage()

# ═══════════════════════════════════════════════════════════════
# Slide 3: Background（3行+結論バー）
# ═══════════════════════════════════════════════════════════════
bg()
chip(60, H-78, "課題が起きている背景", WHITE, TEAL, size=11)
c.setFont("HG-H",28); c.setFillColor(NAVY)
c.drawString(60, H-120, g("bg_heading","なぜ、その課題が起きているのか"))

causes = g("causes",[])
# 結論バーの高さ
bar_h = 52
bar_y = 44
# 3行に使えるY領域
rows_top = H - 140
rows_bot = bar_y + bar_h + 10
rows_h   = rows_top - rows_bot
n_causes = min(len(causes), 3)
rh       = (rows_h - 8*(n_causes-1)) // n_causes  # 行高（均等）

for i, cz in enumerate(causes[:3]):
    yv = rows_top - i*(rh+8)
    rrect(60, yv-rh, W-120, rh, 10, fill=SOFT, stroke=LINE, sw=1)
    circ(100, yv-rh/2, 16, str(i+1), TEAL, WHITE, gsize=14)
    # タイトル
    c.setFont("HG-B",15); c.setFillColor(NAVY)
    c.drawString(140, yv-rh*0.35, cz[0] if cz else "")
    # 説明（残り高さに収まるよう縮小）
    desc_y = yv - rh*0.38 - 18
    desc_h = rh*0.55
    para(140, desc_y, cz[1] if len(cz)>1 else "", "HG-R", 12, INK,
         W-220, 17, max_height=desc_h, size_min=9)

# 結論バー
rrect(60, bar_y, W-120, bar_h, 10, fill=TEAL)
para(84, bar_y+bar_h-16,
     g("bg_conclusion","つまり〜"),
     "HG-B", 13, WHITE, W-190, 17,
     max_height=bar_h-8, size_min=10)

footer(3); c.showPage()

# ═══════════════════════════════════════════════════════════════
# Slide 4: Solution（2カラム + データ帯）
# ═══════════════════════════════════════════════════════════════
bg()
chip(60, H-78, "解決方法", WHITE, TEAL, size=11)
c.setFont("HG-H",28); c.setFillColor(NAVY)
c.drawString(60, H-120, g("sol_heading","御社の求人を「届く」状態に"))

data_band_h = 68
data_band_y = 44
colw = (W - 120 - 30) // 2      # 2列
card_top = H - 148
card_h   = card_top - (data_band_y + data_band_h + 10)

for i, s in enumerate(g("solutions",[])[:2]):
    x = 60 + i*(colw+30)
    rrect(x, data_band_y+data_band_h+10, colw, card_h, 14, fill=SOFT, stroke=LINE, sw=1)
    chip(x+22, data_band_y+data_band_h+10+card_h-40, s.get("sub",""), WHITE, TEAL_D, size=10)
    # タイトル
    t_sz = fit_size(s.get("title",""),"HG-H",20,13, colw-44, 28, 1.3)
    c.setFont("HG-H",t_sz); c.setFillColor(NAVY)
    c.drawString(x+22, data_band_y+data_band_h+10+card_h-76, s.get("title",""))
    # 箇条書き
    yv = data_band_y+data_band_h+10+card_h-110
    item_h = (yv - (data_band_y+data_band_h+20)) / max(len(s.get("items",[])),1)
    for it in s.get("items",[])[:4]:
        c.setFillColor(TEAL); c.circle(x+30, yv+5, 4, stroke=0, fill=1)
        para(x+44, yv+9, it, "HG-R", 12, INK, colw-70, 17,
             max_height=max(item_h-4, 14), size_min=9)
        yv -= item_h

# データ帯
rrect(60, data_band_y, W-120, data_band_h, 10, fill=SOFT2, stroke=LINE, sw=1)
data_list = g("data",[])
sec_w = (W-120) // max(len(data_list),1)
for i,(n,l) in enumerate(data_list[:4]):
    x = 90 + i*sec_w
    n_sz = fit_size(n,"HG-H",20,12, sec_w-20, 28, 1.2)
    c.setFont("HG-H",n_sz); c.setFillColor(TEAL_D); c.drawString(x, data_band_y+data_band_h-18, n)
    l_sz = fit_size(l,"HG-R",11,8,  sec_w-20, 16, 1.2)
    c.setFont("HG-R",l_sz); c.setFillColor(MUTE);   c.drawString(x, data_band_y+10, l)

footer(4); c.showPage()

# ═══════════════════════════════════════════════════════════════
# Slide 5: Plan（着地プランのみ）
# ═══════════════════════════════════════════════════════════════
bg()
chip(60, H-78, "サービス内容・料金", WHITE, TEAL, size=11)
c.setFont("HG-H",28); c.setFillColor(NAVY)
c.drawString(60, H-120, g("plan_heading","御社へのご提案プラン"))

p = g("plan",{})
note_h = 36
lx, lw = 60, 360
card_top_y = H - 140
card_bot_y = note_h + 24
ph = card_top_y - card_bot_y

rrect(lx, card_bot_y, lw, ph, 16, fill=TEAL_D)

# レイアウト（上から固定領域で積み上げ）
CHIP_H   = 24; CHIP_PAD = 14   # チップ
GAP1     = 10                   # チップ→価格
PRICE_SZ = 40                   # 価格フォントサイズ
UNIT_SZ  = 11
GAP2     = 10                   # 価格→説明
BADGE_H  = 30; BADGE_PAD = 14  # バッジ
MARGIN   = 18                   # 上下マージン

# チップ（上から MARGIN）
chip_y = card_bot_y + ph - MARGIN - CHIP_H
chip(lx+24, chip_y, p.get("name","ご提案プラン"), TEAL_D, WHITE, size=10, padh=CHIP_H)

# バッジ（下から MARGIN）
badge_y = card_bot_y + MARGIN
if p.get("badge"):
    bw = min(pdfmetrics.stringWidth(p["badge"],"HG-B",12)+32, lw-48)
    rrect(lx+24, badge_y, bw, BADGE_H, 15, fill=WHITE)
    c.setFont("HG-B",12); c.setFillColor(TEAL_D)
    c.drawString(lx+40, badge_y+9, p["badge"])

# 説明（バッジ上から chip下まで中間領域）
desc_avail_top  = chip_y - GAP1 - 4
desc_avail_bot  = badge_y + BADGE_H + 8
desc_h_available = max(desc_avail_top - desc_avail_bot, 10)

# 説明テキストを中間領域に収まるサイズで描画
d_sz = fit_size(p.get("desc",""), "HG-R", 12, 8, lw-52, desc_h_available, 1.45)
d_lead = d_sz * 1.45
# 説明を縦中央に近い位置から開始
d_lines = wrap(p.get("desc",""), "HG-R", d_sz, lw-52)
d_total = len(d_lines) * d_lead
d_start = desc_avail_top - max(0, (desc_h_available - d_total)/2 - d_lead*0.3)
para(lx+24, d_start, p.get("desc",""), "HG-R", d_sz, SOFT, lw-52, d_lead,
     max_height=desc_h_available, size_min=8)

# 価格（説明の上）
price_y = chip_y - GAP1 - PRICE_SZ
c.setFont("HG-H", PRICE_SZ); c.setFillColor(WHITE)
c.drawString(lx+24, price_y, p.get("price",""))
# 単位：価格の右横に（右端に収まる場合）、収まらなければ非表示
unit_str = p.get("unit","")
pw2 = pdfmetrics.stringWidth(p.get("price",""), "HG-H", PRICE_SZ)
unit_w = pdfmetrics.stringWidth(unit_str, "HG-R", UNIT_SZ)
if lx+24+pw2+6+unit_w <= lx+lw-16:
    c.setFont("HG-R", UNIT_SZ); c.setFillColor(SOFT)
    c.drawString(lx+24+pw2+6, price_y+4, unit_str)

# 右カラム：含まれるもの
rx = lx+lw+36; rw = W-60-rx
c.setFont("HG-B",15); c.setFillColor(NAVY)
c.drawString(rx, card_top_y-16, "プランに含まれるもの")
included = p.get("included",[])
n_inc = min(len(included), 4)
inc_h = ph / max(n_inc, 1)
yv = card_top_y-52
for inc in included[:4]:
    c.setFillColor(TEAL); c.circle(rx+8, yv-4, 5, stroke=0, fill=1)
    # 項目名
    t_sz = fit_size(inc[0],"HG-B",13,9, rw-30, 18, 1.3)
    c.setFont("HG-B",t_sz); c.setFillColor(NAVY); c.drawString(rx+26, yv-8, inc[0])
    # 説明（残り高さに収まるよう縮小）
    desc_avail = inc_h - 30
    para(rx+26, yv-26, inc[1] if len(inc)>1 else "", "HG-R", 11, INK,
         rw-30, 15, max_height=max(desc_avail,12), size_min=8)
    yv -= inc_h

# 注記
para(60, note_h+18, p.get("plan_note",""), "HG-B", 11, INK, W-120, 16,
     max_height=note_h, size_min=9)
footer(5); c.showPage()

# ═══════════════════════════════════════════════════════════════
# Slide 6: Closing + Steps
# ═══════════════════════════════════════════════════════════════
bg()
chip(60, H-78, "次のステップ", WHITE, TEAL, size=11)
c.setFont("HG-H",28); c.setFillColor(NAVY)
c.drawString(60, H-120, g("close_heading","次のステップ"))
para(60, H-150, g("close_lead",""), "HG-R", 13, MUTE, 840, 20,
     max_height=20, size_min=10)

case = g("close_case","")
case_h = 62
case_y = None
if case:
    steps_h = 130
    steps_y = 40
    case_y  = steps_y + steps_h + 10
    rrect(60, case_y, W-120, case_h, 10, fill=SOFT, stroke=LINE, sw=1)
    c.setFont("HG-B",12); c.setFillColor(TEAL_D); c.drawString(84, case_y+case_h-16, "実績")
    para(144, case_y+case_h-14, case, "HG-R", 11.5, INK, W-250, 16,
         max_height=case_h-10, size_min=9)
else:
    # 実績なし→ステップを中央寄りに大きく配置
    steps_h = 180
    steps_y = (H - 170 - 180) // 2  # 縦中央あたりに配置

# 3ステップカード
steps = g("steps",[])
n_steps = min(len(steps), 3)
sw_ = (W - 120 - 20*(n_steps-1)) // n_steps
for i, st in enumerate(steps[:3]):
    x = 60 + i*(sw_+20)
    rrect(x, steps_y, sw_, steps_h, 12, fill=SOFT, stroke=LINE, sw=1)
    # STEP番号
    c.setFont("HG-H",13); c.setFillColor(TEAL_D)
    c.drawString(x+18, steps_y+steps_h-28, st[0] if st else "")
    # 見出し
    h_sz = fit_size(st[1] if len(st)>1 else "","HG-B",14,10, sw_-36, 22, 1.3)
    c.setFont("HG-B",h_sz); c.setFillColor(NAVY)
    c.drawString(x+18, steps_y+steps_h-52, st[1] if len(st)>1 else "")
    # 説明
    para(x+18, steps_y+steps_h-74, st[2] if len(st)>2 else "",
         "HG-R", 10.5, INK, sw_-36, 15,
         max_height=steps_h-80, size_min=8)

footer(6); c.showPage()

c.save()
print("OK:", OUT)
