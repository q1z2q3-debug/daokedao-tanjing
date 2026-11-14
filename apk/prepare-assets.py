#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 book/坛经·阅读版.html 生成 APK 用的 assets。

做两件事：
  1. 注入本地 @font-face（不再依赖系统是否装有 Noto Serif SC）；
  2. 用系统 Noto Serif CJK 子集化出只含本书用字的 woff（400 / 700）。

产物不入库（体积大、可由本脚本重建）：
  apk/assets/book.html
  apk/assets/fonts/TanjingSerif-Regular.woff
  apk/assets/fonts/TanjingSerif-Bold.woff

用法：python3 apk/prepare-assets.py
"""
import html
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "book", "坛经·阅读版.html")
ASSETS = os.path.join(HERE, "assets")
FONTS = os.path.join(ASSETS, "fonts")

NOTO = {
    "Regular": ("/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc", 2),
    "Bold": ("/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc", 2),
}

FACE = """<style>
@font-face{font-family:"TanjingSerif";src:url("fonts/TanjingSerif-Regular.woff") format("woff");font-weight:400;font-style:normal;font-display:swap}
@font-face{font-family:"TanjingSerif";src:url("fonts/TanjingSerif-Bold.woff") format("woff");font-weight:600 900;font-style:normal;font-display:swap}
</style>"""

OLD = 'font-family:"Noto Serif SC","Songti SC","Source Han Serif SC",serif;'
NEW = 'font-family:"TanjingSerif","Noto Serif SC","Songti SC","Source Han Serif SC",serif;'


def build_html():
    s = open(SRC, encoding="utf-8").read()
    assert s.count(OLD) >= 1, "阅读版字体声明结构变了"
    s = s.replace(OLD, NEW)
    s = s.replace("</head>", FACE + "</head>", 1)
    os.makedirs(ASSETS, exist_ok=True)
    dst = os.path.join(ASSETS, "book.html")
    open(dst, "w", encoding="utf-8").write(s)
    print("book.html  %d 字节  外链剩余 %d" % (os.path.getsize(dst), s.count('href="http')))
    return s


def char_set(doc):
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", "", doc)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    t = html.unescape(t)
    base = {c for c in t if not c.isspace()}
    base |= {chr(i) for i in range(32, 127)}
    base |= set("　、。《》「」『』（）—…·：；！？〔〕【】“”‘’％＋－×＝／　〇")
    return "".join(sorted(base))


def build_fonts(chars):
    from fontTools import subset

    os.makedirs(FONTS, exist_ok=True)
    for weight, (path, index) in NOTO.items():
        opts = subset.Options()
        opts.font_number = index
        opts.hinting = False
        opts.desubroutinize = True
        opts.layout_features = ["*"]
        opts.name_IDs = ["*"]
        opts.name_languages = ["*"]
        opts.notdef_outline = True
        font = subset.load_font(path, opts)
        sub = subset.Subsetter(options=opts)
        sub.populate(text=chars)
        sub.subset(font)
        font.flavor = "woff"
        dst = os.path.join(FONTS, "TanjingSerif-%s.woff" % weight)
        font.save(dst)
        print("TanjingSerif-%s.woff  %d 字节" % (weight, os.path.getsize(dst)))


if __name__ == "__main__":
    doc = build_html()
    cs = char_set(doc)
    print("用字 %d 个" % len(cs))
    build_fonts(cs)
    print("✓ assets 就绪")
