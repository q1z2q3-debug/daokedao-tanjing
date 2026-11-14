# -*- coding: utf-8 -*-
"""把《润泽说 道可道之坛经·通释》编成 A5 成书 PDF。

用法：python3 scripts/build_pdf.py
产物：book/润泽说 道可道之坛经.pdf
依赖：weasyprint CLI（本机 /usr/local/bin/weasyprint）
"""
import html as H
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MD = ROOT / "book" / "润泽说 道可道之坛经·通释.md"
OUT = ROOT / "book" / "润泽说 道可道之坛经.pdf"

sys.path.insert(0, str(ROOT / "scripts"))
from build_site import split_book, PIN, ZONES, TITLE, VER  # noqa: E402

CSS = """
@page {
  size: A5;
  margin: 20mm 17mm 18mm;
  @bottom-center { content: counter(page); font-family: "Noto Serif CJK SC", serif; font-size: 8pt; color: #6B6152; }
  @top-center { content: "润泽说 道可道之坛经"; font-family: "Noto Serif CJK SC", serif; font-size: 7.6pt; color: #A79C8B; letter-spacing: .1em; }
}
@page :first { @top-center { content: "" } @bottom-center { content: "" } }
@page cover { margin: 0; @top-center { content: "" } @bottom-center { content: "" } }

html, body { margin: 0; }
body { font-family: "Noto Serif CJK SC", serif; font-size: 9.6pt; line-height: 1.85; color: #25211D; }

.cover { page: cover; height: 210mm; padding: 26mm 20mm; box-sizing: border-box;
         border: 1px solid #DCD3C4; background: #FCFAF6; }
.cover .inner { border: 1px solid #EBE4D8; height: 100%; padding: 16mm 10mm; box-sizing: border-box; text-align: center; }
.cover .series { font-size: 8.4pt; letter-spacing: .34em; color: #7C6D5C; }
.cover h1 { font-size: 34pt; letter-spacing: .16em; margin: 34mm 0 4mm; font-weight: 700; line-height: 1.1; }
.cover .sub { font-size: 10pt; letter-spacing: .1em; color: #7C6D5C; }
.cover .rule { width: 14mm; height: .6mm; background: #944433; margin: 8mm auto 7mm; }
.cover .verse { font-size: 8.6pt; color: #6B6152; line-height: 2.1; letter-spacing: .05em; }
.cover .meta { margin-top: 28mm; font-size: 8.4pt; color: #7C6D5C; letter-spacing: .1em; }

.frontis { page-break-before: always; padding: 30mm 8mm 0; text-align: center; }
.frontis .fs { font-size: 8.4pt; letter-spacing: .3em; color: #7C6D5C; }
.frontis .ft { font-size: 24pt; letter-spacing: .12em; margin: 14mm 0 3mm; font-weight: 600; }
.frontis .fu { font-size: 9.4pt; color: #6B6152; letter-spacing: .06em; }
.frontis .fr { width: 12mm; height: .5mm; background: #944433; margin: 7mm auto; }
.frontis .fn { font-size: 9.6pt; letter-spacing: .2em; }
.frontis .fm { margin-top: 16mm; font-size: 8.2pt; color: #7C6D5C; line-height: 2; }
.frontis .seal { margin: 12mm auto 0; width: 12mm; height: 12mm; border: .6mm solid #944433; color: #944433;
                 font-size: 12pt; line-height: 12mm; letter-spacing: 0; }

.toc { page-break-before: always; column-count: 2; column-gap: 9mm; }
.toc h2 { font-size: 13pt; letter-spacing: .2em; color: #944433; text-align: center; margin: 2mm 0 6mm; font-weight: 600; }
.toc .zone { font-size: 8pt; color: #7C6D5C; letter-spacing: .14em; margin: 4mm 0 1mm; break-after: avoid; }
.toc a { display: block; text-decoration: none; color: #25211D; font-size: 8.6pt; margin: 1mm 0;
        border-bottom: 1px dotted #E1D9CB; }
.toc a::after { content: target-counter(attr(href), page); float: right; color: #7C6D5C; }

h1.part { page-break-before: always; font-size: 15pt; letter-spacing: .08em; margin: 0 0 2mm; color: #944433; font-weight: 600; }
h1.part .pn { display: block; font-size: 8pt; letter-spacing: .2em; color: #A79C8B; margin-bottom: 1mm; }
h2 { font-size: 11.2pt; margin: 6mm 0 2mm; padding-top: 3mm; border-top: .3pt solid #DCD3C4; color: #25211D; font-weight: 600; letter-spacing: .04em; }
h3 { font-size: 10pt; margin: 4mm 0 1.5mm; color: #944433; font-weight: 600; }
p { margin: 0 0 1.4mm; text-align: justify; text-indent: 2em; }
p.noind { text-indent: 0; }
blockquote { margin: 3mm 0; padding: 1mm 0 1mm 4mm; border-left: .7mm solid #944433; color: #3B352F; }
blockquote p { text-indent: 0; }
ul { margin: 1mm 0 2mm 6mm; padding: 0; }
li { font-size: 9.4pt; }
table { width: 100%; border-collapse: collapse; font-size: 8.2pt; margin: 2mm 0 3mm; page-break-inside: avoid; }
th, td { border: .3pt solid #DCD3C4; padding: 1.2mm 1.6mm; text-align: left; vertical-align: top; line-height: 1.6; }
th { background: #F1EAE0; font-weight: 600; }
hr { display: none; }
figure { margin: 4mm 0; text-align: center; page-break-inside: avoid; }
figure img { max-width: 100%; border: .3pt solid #DCD3C4; }
figure figcaption { font-size: 8pt; color: #7C6D5C; margin-top: 1.5mm; }
"""


def inline(t):
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
    return t


def md2block(src):
    """md → PDF 用的块级 html（## → h2，### → h3，含表格与图位）。"""
    src = (src.replace("<!-- FIG:cup -->", "__FIGCUP__")
               .replace("<!-- FIG:fengfan -->", "__FIGFF__"))
    out, bufq, bufl, buft = [], [], [], []

    def flush():
        nonlocal bufq, bufl, buft
        if bufq:
            out.append("<blockquote>" + "".join(f"<p>{x}</p>" for x in bufq) + "</blockquote>")
            bufq = []
        if bufl:
            out.append("<ul>" + "".join(f"<li>{x}</li>" for x in bufl) + "</ul>")
            bufl = []
        if buft:
            raw = [r for r in buft if not re.match(r"^\|?[\s:|-]+\|$", r)]
            cells = [[inline(H.escape(c.strip())) for c in r.strip().strip("|").split("|")] for r in raw]
            th = "".join(f"<th>{c}</th>" for c in cells[0])
            tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in cells[1:])
            out.append(f"<table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>")
            buft = []

    for raw in src.split("\n"):
        line = raw.rstrip()
        if not line.strip():
            flush(); continue
        if line.strip() == "__FIGCUP__":
            flush()
            out.append('<figure><img src="figures/图1-三才五蕴太极空杯.png" style="width:88%">'
                       '<figcaption>图一　三才五蕴太极空杯：色为杯底，受想行识为四壁；聚则器现，散则器消。</figcaption></figure>')
            continue
        if line.strip() == "__FIGFF__":
            flush()
            out.append('<figure><img src="figures/图2-风幡阴阳太和.svg" style="width:90%">'
                       '<figcaption>图二　风幡阴阳太和：幡为阴（有形显相），风为阳（无形动能），心是太和。</figcaption></figure>')
            continue
        if line.strip().startswith("|"):
            if bufq or bufl: flush()
            buft.append(line.strip()); continue
        flush()
        if line.startswith("## "):
            out.append(f"<h2>{inline(H.escape(line[3:]))}</h2>"); continue
        if line.startswith("### "):
            out.append(f"<h3>{inline(H.escape(line[4:]))}</h3>"); continue
        if line.strip() in ("---", ">", "***", "<!-- FRONTIS -->", "<!-- /FRONTIS -->"):
            continue
        if line.startswith(">"):
            t = line[1:].lstrip()
            if t: bufq.append(inline(H.escape(t)))
            continue
        if line.startswith("- "):
            bufl.append(inline(H.escape(line[2:])))
            continue
        if line.startswith("<div") or line.startswith("  <div") or line.startswith("</div"):
            continue
        out.append(f"<p>{inline(H.escape(line))}</p>")
    flush()
    return "".join(out)


def cn2int(s):
    CN = "一二三四五六七八九十"
    if s == "十": return 10
    if "十" in s:
        a, _, b = s.partition("十")
        return (CN.index(a) + 1 if a else 1) * 10 + (CN.index(b) + 1 if b else 0)
    return CN.index(s) + 1


def build():
    front, pin, after, app = split_book()
    fen = {}
    for name, body in pin:
        m = re.match(r"^.+品第([一二三四五六七八九十]+)$", name)
        if m:
            fen[cn2int(m.group(1))] = (name, body)

    pre_src = "\n".join(b for _, b in front)
    pre_src = re.sub(r"^### ", "## ", pre_src, flags=re.M)

    parts = []
    for i, name, slug in PIN:
        nm, body = fen.get(i, (name, ""))
        parts.append(f'<h1 class="part" id="pin{i}"><span class="pn">第 {i} 品</span>{H.escape(nm)}</h1>' + md2block(body))

    after_html = f'<h1 class="part" id="after"><span class="pn">后记</span>成书说明</h1>' + md2block(after[1])
    app_html = '<h1 class="part" id="app"><span class="pn">附录</span>三张查表</h1>' + md2block(app[1])
    pre_html = f'<h1 class="part" id="pre"><span class="pn">卷首</span>总序与凡例</h1>' + md2block(pre_src)

    toc = ['<div class="toc"><h2>目 录</h2>',
           '<div class="zone">卷首</div><a href="#pre">总序与凡例</a>']
    for zname, a, b, _ in ZONES:
        toc.append(f'<div class="zone">{zname}</div>')
        for i, name, slug in PIN:
            if a <= i <= b:
                toc.append(f'<a href="#pin{i}">{name}</a>')
    toc += ['<div class="zone">附</div><a href="#after">后记：成书说明</a>',
            '<a href="#app">附录：三十六对表 · 三科表 · 品目对照</a>', "</div>"]
    toc = "\n".join(toc)

    html = f"""<!DOCTYPE html><html lang="zh-Hans"><head><meta charset="utf-8">
<title>{TITLE}</title><style>{CSS}</style></head><body>
<div class="cover"><div class="inner">
<div class="series">润泽说　道可道</div>
<h1>坛经</h1>
<div class="sub">《六祖大师法宝坛经》十品通释</div>
<div class="rule"></div>
<div class="verse">菩提本无树，明镜亦非台。<br>本来无一物，何处惹尘埃。</div>
<div class="meta">润泽　著　·　v{VER}　·　CC BY-NC-SA 4.0</div>
</div></div>
<div class="frontis">
<div class="fs">润 泽 说 · 道 可 道</div>
<div class="ft">六祖坛经</div>
<div class="fu">六祖大师法宝坛经 · 通释</div>
<div class="fr"></div>
<div class="fn">润　泽　著</div>
<div class="fm">底本　敦煌本《六祖坛经》S.5475<br>体例　十品 · 每品八段<br>参证　三才五蕴太极空杯 · 阴阳太和 · 和合之辨<br>版本　v{VER} · 二〇二六年十一月</div>
<div class="seal">坛</div>
</div>
{toc}
{pre_html}
{''.join(parts)}
{after_html}
{app_html}
</body></html>"""

    tmp = ROOT / "book" / "_print.html"
    tmp.write_text(html, encoding="utf-8")
    subprocess.run(["weasyprint", "--base-url", str(ROOT / "book"), str(tmp), str(OUT)], check=True)
    tmp.unlink(missing_ok=True)
    import fitz
    doc = fitz.open(str(OUT))
    print(f"built {OUT.name} {OUT.stat().st_size/1e6:.2f} MB, {doc.page_count} pages")


if __name__ == "__main__":
    build()
