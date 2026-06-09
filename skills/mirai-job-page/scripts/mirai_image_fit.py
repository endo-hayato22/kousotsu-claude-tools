#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mirai_image_fit.py — みらいジョブ求人画像 自動最適化ツール

みらいジョブの求人メイン画像枠（800×500px = 8:5, object-fit: cover）に
そのままアップしても「見切れない／ボケない」画像を一発で作る。

仕様:
  - 出力は必ず 1600×1000px（8:5の2倍 = retina対応の高画質）
  - 8:5 に近い写真        → cover（枠を埋めて中央クロップ。ロス最小）
  - 8:5 から遠い画像       → contain（全体を収めて文字を絶対に切らない）
      ・縁が単色っぽい(ロゴ/バナー) → その色でベタ塗り背景
      ・写真っぽい                  → 画像自身のぼかし背景で自然に補完
  - 透過PNGはフラット化、EXIF回転補正、低解像度は警告
  - 企業名で自動リネーム（例: 佐藤鉄工所_01.jpg ...）

使い方:
  python3 mirai_image_fit.py <入力フォルダ or 画像ファイル...> [オプション]

オプション:
  --out DIR        出力先（省略時: みらいジョブ掲載素材フォルダ）
  --prefix NAME    ファイル名の接頭辞=企業名（例: 株式会社佐藤鉄工所 →「株式会社佐藤鉄工所_画像1.jpg」）
  --tolerance F    cover採用とする8:5からの許容ズレ(割合)。既定 0.12
  --width / --height  出力サイズ。既定 1600 / 1000
"""
import argparse
import os
import sys
from PIL import Image, ImageOps, ImageFilter, ImageEnhance

IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tif", ".tiff", ".heic"}

# 既定の出力先（みらいジョブ掲載素材フォルダ）。--out で変更可。
# 各メンバー自身のホーム配下に出力する（組織配布のため絶対パス直書きしない）。
DEFAULT_OUT_DIR = os.path.expanduser("~/Downloads/営業資料/claude提案資料/みらいジョブ掲載素材")


def gather_inputs(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            for name in sorted(os.listdir(p)):
                fp = os.path.join(p, name)
                if os.path.isfile(fp) and os.path.splitext(name)[1].lower() in IMG_EXTS:
                    files.append(fp)
        elif os.path.isfile(p) and os.path.splitext(p)[1].lower() in IMG_EXTS:
            files.append(p)
    return files


def border_color_and_uniformity(rgb):
    """画像の縁の平均色と、縁のばらつき(平均絶対偏差)を返す。"""
    w, h = rgb.size
    px = rgb.load()
    samples = []
    step_x = max(1, w // 60)
    step_y = max(1, h // 60)
    for x in range(0, w, step_x):
        samples.append(px[x, 0])
        samples.append(px[x, h - 1])
    for y in range(0, h, step_y):
        samples.append(px[0, y])
        samples.append(px[w - 1, y])
    n = len(samples)
    avg = tuple(sum(s[i] for s in samples) // n for i in range(3))
    mad = sum(sum(abs(s[i] - avg[i]) for i in range(3)) for s in samples) / (n * 3)
    return avg, mad


def blurred_background(rgb, tw, th):
    base = ImageOps.fit(rgb, (tw, th), Image.LANCZOS, centering=(0.5, 0.5))
    return base.filter(ImageFilter.GaussianBlur(radius=40))


def sharpen_lowres(img, factor):
    """低解像度を拡大した画像の見栄えを上げる：シャープ化＋わずかな彩度/コントラスト補正。
    ★リサイズはしない（呼び出し側で既に最終サイズにしてある）。サイズを変えると貼り付け時に
    はみ出して切れる原因になる。元に無いディテールは作れないが補間のボケを打ち消す。
    img は RGB または RGBA。アルファはシャープ化対象から除外する。"""
    alpha = None
    if img.mode == "RGBA":
        alpha = img.split()[-1]
        base = img.convert("RGB")
    else:
        base = img.convert("RGB")

    # アンシャープマスクで輪郭を立てる（拡大率が大きいほど強め）
    percent = 110 if factor < 1.8 else (150 if factor < 2.6 else 180)
    base = base.filter(ImageFilter.UnsharpMask(radius=2.2, percent=percent, threshold=2))
    # ほんの少しだけコントラスト・彩度を補ってぼやけ感を打ち消す
    base = ImageEnhance.Contrast(base).enhance(1.04)
    base = ImageEnhance.Color(base).enhance(1.05)

    if alpha is not None:
        base = base.convert("RGBA")
        base.putalpha(alpha)
    return base


def flatten(img, bg=(255, 255, 255)):
    """透過を背景色でフラット化して RGB を返す。"""
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        rgba = img.convert("RGBA")
        canvas = Image.new("RGB", rgba.size, bg)
        canvas.paste(rgba, mask=rgba.split()[-1])
        return canvas
    return img.convert("RGB")


def process_one(path, tw, th, tolerance, fit="contain"):
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)  # 回転補正
    ow, oh = img.size
    ar = ow / oh
    target = tw / th
    has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)

    deviation = abs(ar - target) / target
    # fit=contain: 常に全体表示（一切クロップしない）
    # fit=cover  : 常に切抜
    # fit=auto   : 8:5に近ければ切抜、遠ければ全体表示
    use_cover = (fit == "cover") or (fit == "auto" and deviation <= tolerance)

    # 低解像度判定（このあと拡大が必要か）
    cover_scale = max(tw / ow, th / oh)
    contain_scale = min(tw / ow, th / oh)
    lowres = (cover_scale if use_cover else contain_scale) > 1.2

    if use_cover:
        mode = "cover"
        out = ImageOps.fit(flatten(img), (tw, th), Image.LANCZOS, centering=(0.5, 0.5))
        if lowres:  # 最終サイズにしてからシャープ化（リサイズしない）
            out = sharpen_lowres(out, cover_scale)
        loss = 1 - (tw * th) / ((ow * cover_scale) * (oh * cover_scale))
        detail = f"中央クロップ {loss*100:.0f}%カット"
        upscale = cover_scale
    else:
        # 全体を収める（文字を切らない）
        avg, mad = border_color_and_uniformity(flatten(img))
        scale = contain_scale
        nw, nh = max(1, round(ow * scale)), max(1, round(oh * scale))
        if mad < 18:  # 縁が単色 → ロゴ/バナー
            mode = "pad_solid"
            bg = Image.new("RGB", (tw, th), avg)
            detail = f"余白={avg} で全体表示(文字保護)"
        else:  # 写真 → ぼかし背景
            mode = "pad_blur"
            bg = blurred_background(flatten(img), tw, th)
            detail = "ぼかし背景で全体表示(文字保護)"
        # 前景（低解像度なら高画質化してから配置。透過は元のアルファを尊重）
        fg = img.convert("RGBA") if has_alpha else flatten(img).convert("RGBA")
        fg = fg.resize((nw, nh), Image.LANCZOS)  # 全体が収まる最終サイズ
        if lowres:
            fg = sharpen_lowres(fg, scale)  # サイズは変えずシャープ化のみ
        out = bg.convert("RGB")
        out.paste(fg, ((tw - nw) // 2, (th - nh) // 2), fg.split()[-1] if has_alpha else fg)
        upscale = scale

    warn = ""
    if lowres:
        warn = f"🔧高画質化を自動適用(元{ow}×{oh}/{upscale:.1f}倍)"
        if upscale > 2.6:
            warn += " ※元が特に小さく限界あり・差し替え推奨"

    return out, {
        "src": os.path.basename(path),
        "orig": f"{ow}×{oh}",
        "ar": f"{ar:.2f}",
        "mode": mode,
        "detail": detail,
        "warn": warn,
    }


def main():
    ap = argparse.ArgumentParser(description="みらいジョブ求人画像 自動最適化（8:5 / 1600×1000）")
    ap.add_argument("inputs", nargs="+", help="入力フォルダ or 画像ファイル")
    ap.add_argument("--out", default=None)
    ap.add_argument("--prefix", default=None)
    ap.add_argument("--tolerance", type=float, default=0.18)
    ap.add_argument("--fit", choices=["contain", "cover", "auto"], default="contain",
                    help="contain=常に全体表示(既定) / cover=常に切抜 / auto=8:5に近ければ切抜")
    ap.add_argument("--width", type=int, default=1600)
    ap.add_argument("--height", type=int, default=1000)
    args = ap.parse_args()

    files = gather_inputs(args.inputs)
    if not files:
        print("画像が見つかりませんでした。", file=sys.stderr)
        sys.exit(1)

    first = args.inputs[0]
    base_dir = first if os.path.isdir(first) else os.path.dirname(first)
    out_dir = args.out or DEFAULT_OUT_DIR
    os.makedirs(out_dir, exist_ok=True)
    prefix = args.prefix or os.path.basename(os.path.normpath(base_dir)) or "image"

    print(f"出力先: {out_dir}")
    print(f"出力サイズ: {args.width}×{args.height} (8:5) / 接頭辞: {prefix}")
    print(f"対象: {len(files)}枚\n")

    reports = []
    for i, f in enumerate(files, 1):
        try:
            out_img, rep = process_one(f, args.width, args.height, args.tolerance, args.fit)
        except Exception as e:
            print(f"  [{i:02d}] {os.path.basename(f)} → エラー: {e}")
            continue
        out_name = f"{prefix}_画像{i}.jpg"
        out_path = os.path.join(out_dir, out_name)
        out_img.save(out_path, "JPEG", quality=90, optimize=True)
        rep["out"] = out_name
        reports.append(rep)
        label = {"cover": "切抜", "pad_solid": "全体(単色余白)", "pad_blur": "全体(ぼかし)"}[rep["mode"]]
        print(f"  [{i:02d}] {rep['src']} ({rep['orig']}, 比{rep['ar']}) "
              f"→ {out_name} | {label}: {rep['detail']} {rep['warn']}")

    warns = [r for r in reports if r["warn"]]
    severe = [r for r in reports if "差し替え推奨" in r["warn"]]
    print(f"\n完了: {len(reports)}枚を最適化。", end="")
    if warns:
        print(f" うち{len(warns)}枚は低解像度のため自動で高画質化を適用。", end="")
        if severe:
            print(f"（{len(severe)}枚は元が特に小さく限界あり→可能なら差し替え推奨）")
        else:
            print("")
    else:
        print(" 全て問題なし。")
    print("→ これらをそのままみらいジョブ編集ページにアップすれば見切れません。")
    print(f"RESULT_DIR:{out_dir}")  # ドラッグ&ドロップアプリ用（出力先を機械可読で出力）


if __name__ == "__main__":
    main()
