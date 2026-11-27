# -*- coding: utf-8 -*-
"""从 book/润泽说 道可道之坛经·通释.md 生成 docs/ 静态站
（首页、卷首总序凡例、篇目、十品逐页、后记、附录、下载页、英文页、llms、sitemap、robots）。

用法：python3 scripts/build_site.py
"""
import html as H
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
BOOK = ROOT / "book"
MD = BOOK / "润泽说 道可道之坛经·通释.md"
DOCS = ROOT / "docs"

SITE = "https://q1z2q3-debug.github.io/daokedao-tanjing"
SERIES = "润泽说 道可道"
TITLE = "润泽说 道可道之坛经"
VER = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
DOI = "10.5281/zenodo.24223179"   # 存缴后回填

# 十品：(序数, 品题, slug)
PIN = [
    (1, "行由品第一", "xingyou"), (2, "般若品第二", "bore"),
    (3, "疑问品第三", "yiwen"), (4, "定慧品第四", "dinghui"),
    (5, "坐禅品第五", "zuochan"), (6, "忏悔品第六", "chanhui"),
    (7, "机缘品第七", "jiyuan"), (8, "顿渐品第八", "dunjian"),
    (9, "护法品第九", "hufa"), (10, "付嘱品第十", "fuzhu"),
]

ZONES = [("上三品", 1, 3, "立本：行由明缘起与自性，般若立见地，疑问破净土之执。"),
         ("中三品", 4, 6, "起行：定慧一体、坐禅离相、忏悔无相——见地落到日用。"),
         ("下四品", 7, 10, "勘验与交付：机缘验机、顿渐辨根、护法明道由心悟、付嘱定传法之法。")]

# 英文十篇（发稿后回填 JSON；缺省则页面提示待发）
EN_JSON = ROOT / "data" / "en-posts.json"

CSS = """
:root{--paper:#F7F4EE;--paper2:#FCFAF6;--ink:#25211D;--ink2:#3B352F;--muted:#6B6152;--line:#DCD3C4;--accent:#944433}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:"Noto Serif SC","Songti SC",Georgia,serif;font-size:16px;line-height:1.9;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none;border-bottom:1px solid rgba(148,68,51,.28)}
a:hover{border-bottom-color:var(--accent)}
.wrap{max-width:900px;margin:0 auto;padding:0 28px}
header.top{border-bottom:1px solid var(--line);position:sticky;top:0;z-index:9;background:rgba(247,244,238,.94)}
header.top .wrap{display:flex;align-items:baseline;justify-content:space-between;gap:14px;padding:14px 0;flex-wrap:wrap}
.brand{font-size:15px;letter-spacing:.12em;border:0;white-space:nowrap}
nav{display:flex;flex-wrap:wrap;column-gap:16px;row-gap:2px;justify-content:flex-end}
nav a{font-size:13px;color:var(--muted);border:0;white-space:nowrap;font-family:"Noto Sans SC",sans-serif;letter-spacing:.04em}
nav a.on,nav a:hover{color:var(--accent)}
main{padding:52px 0 40px}
.eyebrow{font-family:"Noto Sans SC",sans-serif;font-size:12px;letter-spacing:.22em;color:var(--muted)}
h1{font-size:38px;line-height:1.32;font-weight:600;margin:14px 0 8px}
h2{font-size:21px;font-weight:600;margin:48px 0 16px;padding-top:18px;border-top:1px solid var(--line)}
h3{font-size:17px;font-weight:600;margin:24px 0 8px}
p{margin:0 0 14px}
.lede{font-size:17.5px;color:#3A342C;max-width:730px}
.small{font-size:13.5px;color:var(--muted);font-family:"Noto Sans SC",sans-serif;line-height:1.8}
.list{border-top:1px solid var(--line)}
.row{display:grid;grid-template-columns:56px 1fr 150px;gap:18px;padding:18px 0;border-bottom:1px solid var(--line);align-items:start}
.row .no{font-family:"Noto Sans SC",sans-serif;font-size:12px;color:var(--muted);letter-spacing:.1em;padding-top:6px}
.row h3{margin:0 0 4px;font-size:18px}
.row .go{text-align:right;font-size:13px}
article{border-top:1px solid var(--line);padding-top:26px}
article h3{font-size:18px;letter-spacing:.04em;color:var(--accent)}
article h4{font-size:15.5px;margin:20px 0 6px}
article p{text-align:justify}
blockquote{margin:22px 0;padding:4px 0 4px 18px;border-left:2px solid var(--accent);color:#3A342C}
ul{margin:0 0 14px 18px;padding:0}
table{width:100%;border-collapse:collapse;font-size:14px;margin:14px 0}
th,td{border:1px solid var(--line);padding:9px 11px;text-align:left;vertical-align:top;line-height:1.7}
th{background:#F1EAE0;font-weight:600}
.prevnext{display:flex;justify-content:space-between;gap:16px;margin:44px 0 0;padding-top:18px;border-top:1px solid var(--line);font-size:14px}
footer{border-top:1px solid var(--line);padding:30px 0 56px;margin-top:44px}
footer .wrap{display:flex;justify-content:space-between;gap:18px;flex-wrap:wrap}
@media(max-width:720px){
 header.top .wrap{padding:12px 18px;gap:10px}.wrap{padding:0 18px}.brand{font-size:12.5px;letter-spacing:.04em}nav{column-gap:8px}nav a{font-size:11px;letter-spacing:0}
 h1{font-size:28px}main{padding-top:34px}.row{grid-template-columns:1fr;gap:4px}.row .no{display:none}.row .go{text-align:left}
 .prevnext{flex-direction:column;gap:6px}
}
"""

FIG_CUP = f'<figure style="margin:26px 0;text-align:center"><img src="{SITE}/figures/cup.png" alt="三才五蕴太极空杯：色为杯底，受想行识为四壁" style="max-width:100%;border:1px solid #DCD3C4"><figcaption class="small" style="margin-top:8px">图一　三才五蕴太极空杯：色为杯底，受、想、行、识为四壁；聚则器现，散则器消。</figcaption></figure>'
FIG_FF = f'<figure style="margin:26px 0;text-align:center"><img src="{SITE}/figures/fengfan.svg" alt="风幡阴阳太和：幡阴风阳，心是太和" style="max-width:100%;border:1px solid #DCD3C4;background:#FCFAF6"><figcaption class="small" style="margin-top:8px">图二　风幡阴阳太和：幡为阴（有形显相），风为阳（无形动能），心是太和，非阴非阳而统摄阴阳。</figcaption></figure>'

NAV = [("/", "首页", "home"), ("/book.html", "全书", "book"), ("/chapters/", "十品", "chapters"),
       ("/english/", "英文", "english"), ("/afterword.html", "后记", "afterword"), ("/downloads/", "下载", "downloads")]


def head(title, desc, path, jsonld=None, act="home"):
    ld = ""
    if jsonld:
        ld = '<script type="application/ld+json">%s</script>' % json.dumps(jsonld, ensure_ascii=False, separators=(",", ":"))
    nav = "".join(f'<a href="{SITE}{p}" class="{"on" if a == act else ""}">{n}</a>' for p, n, a in NAV)
    return f"""<!DOCTYPE html>
<html lang="zh-Hans">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{H.escape(title)}</title>
<meta name="description" content="{H.escape(desc)}">
<link rel="canonical" href="{SITE}{path}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SERIES}">
<meta property="og:title" content="{H.escape(title)}">
<meta property="og:description" content="{H.escape(desc)}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:image" content="{SITE}/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{H.escape(title)}">
<meta name="twitter:description" content="{H.escape(desc)}">
<meta name="twitter:image" content="{SITE}/og.png">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="author" content="润泽">
<link rel="icon" type="image/svg+xml" href="{SITE}/favicon.svg">
<link rel="stylesheet" href="https://miaoda.feishu.cn/fonts/css2?family=Noto+Serif+SC:wght@400;500;600;700&family=Noto+Sans+SC:wght@300;400;500&display=swap">
<style>{CSS}</style>
{ld}
</head>
<body>
<header class="top"><div class="wrap">
<a class="brand" href="{SITE}/"><b>润泽说</b> · 道可道</a>
<nav>{nav}</nav>
</div></header>
"""


def foot():
    doi = f'　·　<a href="https://doi.org/{DOI}">DOI</a>' if not DOI.endswith("00000000") else ""
    return f"""<footer><div class="wrap">
<div class="small">{SERIES}之坛经　·　v{VER}　·　CC BY-NC-SA 4.0<br><a href="{SITE}/llms.txt">llms.txt</a>　·　<a href="{SITE}/sitemap.xml">sitemap</a></div>
<div class="small"><a href="https://github.com/q1z2q3-debug/daokedao-tanjing">GitHub</a>{doi}　·　<a href="https://q1z2q3-debug.github.io/runze-daokedao/">系列总站</a></div>
</div></footer>
</body></html>
"""


def inline(t):
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
    return t


def md2html(src):
    """轻量 md → html：段落、li、blockquote、表格、h3/h4。"""
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
            rows = [[inline(H.escape(c.strip())) for c in r.strip().strip("|").split("|")] for r in raw]
            th = "".join(f"<th>{c}</th>" for c in rows[0])
            tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows[1:])
            out.append(f"<table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>")
            buft = []

    for raw in src.split("\n"):
        line = raw.rstrip()
        if not line.strip():
            flush(); continue
        if line.strip().startswith("|"):
            if bufq or bufl: flush()
            buft.append(line.strip()); continue
        else:
            flush()
        if line.startswith("#### ") or line.startswith("### "):
            t = line.split(" ", 1)[1]
            out.append(f"<h4>{inline(H.escape(t))}</h4>"); continue
        if line.startswith("## "):
            out.append(f"<h3>{inline(H.escape(line[3:]))}</h3>"); continue
        if line.strip() in ("---", ">", "***"):
            continue
        if line.startswith(">"):
            if bufl: flush()
            t = line[1:].lstrip()
            if t: bufq.append(inline(H.escape(t)))
            continue
        if line.startswith("- "):
            if bufq: flush()
            bufl.append(inline(H.escape(line[2:])))
            continue
        out.append(f"<p>{inline(H.escape(line))}</p>")
    flush()
    return "".join(out)


def split_book():
    """切出卷首（总序＋凡例）、十品、后记、附录。"""
    src = MD.read_text(encoding="utf-8")
    blocks, cur, title = [], [], None

    def push():
        if title is not None:
            blocks.append((title, "\n".join(cur)))

    for ln in src.split("\n"):
        m = re.match(r"^# (.+品第[一二三四五六七八九十]+|总序|凡例|后记|附录)$", ln.strip())
        if m:
            push()
            title = m.group(1)
            cur = []
        else:
            cur.append(ln)
    push()
    front = [b for b in blocks if b[0] in ("总序", "凡例")]
    pin = [b for b in blocks if "品第" in b[0]]
    after = next((b for b in blocks if b[0] == "后记"), ("后记", ""))
    app = next((b for b in blocks if b[0] == "附录"), ("附录", ""))
    return front, pin, after, app


def cn2int(s):
    CN = "一二三四五六七八九十"
    if s == "十": return 10
    if "十" in s:
        a, _, b = s.partition("十")
        return (CN.index(a) + 1 if a else 1) * 10 + (CN.index(b) + 1 if b else 0)
    return CN.index(s) + 1


def build():
    front, pin, after, app = split_book()
    DOCS.mkdir(exist_ok=True)
    (DOCS / "chapters").mkdir(exist_ok=True)
    (DOCS / "downloads").mkdir(exist_ok=True)
    (DOCS / "english").mkdir(exist_ok=True)

    fen = {}
    for name, body in pin:
        m = re.match(r"^.+品第([一二三四五六七八九十]+)$", name)
        if m:
            fen[cn2int(m.group(1))] = (name, body)

    recs = [dict(i=i, name=t, slug=s, body=fen.get(i, ("", ""))[1],
                 wc=len(re.sub(r"\s", "", fen.get(i, ("", ""))[1])))
            for i, t, s in PIN]

    # ---- 十品逐页 ----
    for k, r in enumerate(recs):
        fn = f"{r['i']:02d}-{r['slug']}.html"
        prev = nxt = ""
        if k > 0:
            p = recs[k - 1]
            prev = f'<a href="{SITE}/chapters/{p["i"]:02d}-{p["slug"]}.html">← {p["name"]}</a>'
        if k < len(recs) - 1:
            nx = recs[k + 1]
            nxt = f'<a href="{SITE}/chapters/{nx["i"]:02d}-{nx["slug"]}.html">{nx["name"]} →</a>'
        zone = next(z[0] for z in ZONES if z[1] <= r["i"] <= z[2])
        peidu = ('<p class="small">并读：《金刚经》第十分「应无所住而生其心」· 第十八分「三心不可得」→ '
                 '<a href="https://q1z2q3-debug.github.io/daokedao-liuzu/duibi.html" rel="noopener">专题并读页</a></p>'
                 if r["i"] == 1 else "")
        desc = f"《坛经》{r['name']}：原文底本、时代背景、字源溯源、逐段深解、体系联动、和合对照、跨典互参、小结。{r['wc']} 字。"
        ld = {"@context": "https://schema.org", "@type": "Article",
              "headline": f"{r['name']}｜{TITLE}", "url": f"{SITE}/chapters/{fn}",
              "inLanguage": "zh-Hans", "wordCount": r["wc"],
              "author": {"@type": "Person", "name": "润泽"},
              "isPartOf": {"@type": "Book", "@id": f"{SITE}/book.html#book"}}
        raw = r["body"].replace("<!-- FIG:cup -->", "__FIGCUP__").replace("<!-- FIG:fengfan -->", "__FIGFF__")
        body_html = md2html(raw)
        body_html = body_html.replace("<p>__FIGCUP__</p>", FIG_CUP).replace("<p>__FIGFF__</p>", FIG_FF)
        (DOCS / "chapters" / fn).write_text(
            head(f"{r['name']}｜{TITLE}", desc, f"/chapters/{fn}", ld, act="chapters") +
            f"""<main><div class="wrap">
<p class="eyebrow">{zone}　·　第 {r['i']} 品　·　{r['wc']} 字</p>
<h1>{H.escape(r['name'])}</h1>
<p class="small">底本：敦煌本《六祖坛经》S.5475　·　品题依通行十品立目　·　<a href="{SITE}/book.html">全书阅读版</a>　·　<a href="{SITE}/chapters/">十品</a></p>
{peidu}<article>{body_html}</article>
<div class="prevnext">{prev}<a href="{SITE}/chapters/">十品</a>{nxt}</div>
</div></main>""" + foot(), encoding="utf-8")

    # ---- 卷首：总序＋凡例 ----
    pre_html = "".join(f"<h3>{H.escape(n)}</h3>{md2html(b)}" for n, b in front)
    (DOCS / "preface.html").write_text(
        head(f"卷首 · 总序与凡例｜{TITLE}",
             "《坛经》通释的立旨、核心宗旨、七大定规、全书总纲与凡例：底本、体例、名相、校注符号、配图、义理校准、三参、行文。",
             "/preface.html", None, act="home") +
        f"""<main><div class="wrap">
<p class="eyebrow">卷首</p>
<h1>总序与凡例</h1>
<p class="lede">破执在金刚，归心在坛经。无住是体，自性是用；般若是眼，坛经是足。</p>
<article>{pre_html}</article>
<div class="prevnext"><a href="{SITE}/chapters/">十品</a><a href="{SITE}/book.html">全书 →</a></div>
</div></main>""" + foot(), encoding="utf-8")

    # ---- 篇目 ----
    secs = []
    for zname, a, b, zdesc in ZONES:
        grp = [r for r in recs if a <= r["i"] <= b]
        secs.append(f"<h2>{zname}　<span class='small'>{len(grp)} 品</span></h2><p class='small'>{zdesc}</p><div class='list'>")
        for r in grp:
            secs.append(f"""<div class="row"><div class="no">{r['i']:02d}</div>
<div><h3><a href="{SITE}/chapters/{r['i']:02d}-{r['slug']}.html">{r['name']}</a></h3>
<p class="small" style="margin:0;">{r['wc']} 字　·　八段体例</p></div>
<div class="go"><a href="{SITE}/chapters/{r['i']:02d}-{r['slug']}.html">读这一品</a></div></div>""")
        secs.append("</div>")
    idx_ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": f"{TITLE} · 十品",
              "url": f"{SITE}/chapters/", "inLanguage": "zh-Hans",
              "isPartOf": {"@type": "Book", "@id": f"{SITE}/book.html#book"},
              "hasPart": [{"@type": "Article", "name": r["name"], "url": f"{SITE}/chapters/{r['i']:02d}-{r['slug']}.html"} for r in recs]}
    (DOCS / "chapters" / "index.html").write_text(
        head(f"十品｜{TITLE}", "《坛经》十品全目：上三品立本、中三品起行、下四品勘验与交付。一品一页，可单独引用。",
             "/chapters/", idx_ld, act="chapters") +
        f"""<main><div class="wrap">
<p class="eyebrow">坛经 · 十品</p>
<h1>一品一页，十品</h1>
<p class="lede">敦煌本原不分品，本书依通行十品立目，只为便于阅读，不改动经文文字。每品八段同构：原文底本、时代背景、字源溯源、逐段深解、体系联动、和合对照、跨典互参、小结。</p>
<p class="small">全书 4.0 万字　·　<a href="{SITE}/book.html">全书阅读版</a>　·　<a href="{SITE}/preface.html">卷首凡例</a>　·　<a href="{SITE}/appendix.html">附录三表</a></p>
{''.join(secs)}
</div></main>""" + foot(), encoding="utf-8")

    # ---- 后记 / 附录 ----
    (DOCS / "afterword.html").write_text(
        head(f"后记｜{TITLE}", "成书现状、底本说明、和合判定说明——十品读完之后，这本书怎么用。",
             "/afterword.html", None, act="afterword") +
        f"""<main><div class="wrap">
<p class="eyebrow">后记</p>
<h1>成书说明</h1>
<article>{md2html(after[1])}</article>
<div class="prevnext"><a href="{SITE}/chapters/">十品</a><a href="{SITE}/appendix.html">附录 →</a></div>
</div></main>""" + foot(), encoding="utf-8")

    (DOCS / "appendix.html").write_text(
        head(f"附录｜{TITLE}", "三十六对表（敦煌本原数）、三科表、品目对照——只作查表，不作释义。",
             "/appendix.html", None, act="afterword") +
        f"""<main><div class="wrap">
<p class="eyebrow">附录 · 三表</p>
<h1>附录</h1>
<p class="lede">三张表都不释义：三十六对逐条归位、三科拆开列清、品题与通行本对齐。敦煌本列三十三对，与「三十六对」之名差三，差数留在表后，不补。</p>
<article>{md2html(app[1])}</article>
<div class="prevnext"><a href="{SITE}/afterword.html">← 后记</a><a href="{SITE}/downloads/">下载</a></div>
</div></main>""" + foot(), encoding="utf-8")

    # ---- 首页 ----
    total = sum(r["wc"] for r in recs)
    home_ld = {"@context": "https://schema.org", "@type": "Book", "@id": f"{SITE}/book.html#book",
               "name": TITLE, "alternateName": ["道可道之坛经", "六祖坛经通释"],
               "author": {"@type": "Person", "name": "润泽"},
               "inLanguage": "zh-Hans", "version": VER,
               "license": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
               "description": "《六祖大师法宝坛经》十品通释，以敦煌本 S.5475 为底本，八段体例，附三张查表附录。"}
    if not DOI.endswith("00000000"):
        home_ld["sameAs"] = "https://doi.org/" + DOI
    (DOCS / "index.html").write_text(
        head(TITLE, "《六祖坛经》十品通释：敦煌本底本，八段体例，自性五句与风幡公案两篇专释。全书 4.0 万字。",
             "/", home_ld, act="home") +
        f"""<main><div class="wrap">
<p class="eyebrow">{SERIES}</p>
<h1>道可道之坛经</h1>
<p class="lede">破执在金刚，归心在坛经。无住是体，自性是用；般若是眼，坛经是足。全书约 4.0 万字（{total:,} 字正文），十品三十六节。</p>
<p class="small">v{VER}　·　十品 + 总序 + 凡例 + 后记 + 附录三表　·　CC BY-NC-SA 4.0{('　·　<a href="https://doi.org/%s">DOI %s</a>' % (DOI, DOI)) if not DOI.endswith('00000000') else ''}</p>

<h2>怎么读</h2>
<div class="list">
<div class="row"><div class="no">01</div><div><h3><a href="{SITE}/book.html">全书一页 · 阅读版</a></h3>
<p class="small" style="margin:0;">单文件自包含，封面扉页齐全，断网可读</p></div>
<div class="go"><a href="{SITE}/book.html">打开</a></div></div>
<div class="row"><div class="no">02</div><div><h3><a href="{SITE}/chapters/">十品 · 一品一页</a></h3>
<p class="small" style="margin:0;">上三品立本、中三品起行、下四品勘验与交付</p></div>
<div class="go"><a href="{SITE}/chapters/">十品</a></div></div>
<div class="row"><div class="no">03</div><div><h3><a href="{SITE}/downloads/">下载 · PDF 与安卓包</a></h3>
<p class="small" style="margin:0;">A5 成书 PDF 与离线 APK，手机断网可读</p></div>
<div class="go"><a href="{SITE}/downloads/">下载</a></div></div>
<div class="row"><div class="no">04</div><div><h3><a href="{SITE}/appendix.html">附录 · 三张查表</a></h3>
<p class="small" style="margin:0;">三十六对表（敦煌本原数）、三科表、品目对照</p></div>
<div class="go"><a href="{SITE}/appendix.html">附录</a></div></div>
<div class="row"><div class="no">05</div><div><h3><a href="{SITE}/english/">英文十篇 · 一品一篇</a></h3>
<p class="small" style="margin:0;">十品各一篇英文短论，canonical 指回中文品页</p></div>
<div class="go"><a href="{SITE}/english/">英文</a></div></div><div class="row"><div class="no">06</div><div><h3><a href="https://q1z2q3-debug.github.io/daokedao-liuzu/duibi.html" rel="noopener">并读 · 金刚经两分</a></h3>
<p class="small" style="margin:0;">第十分〈庄严净土〉、第十八分〈一体同观〉原文，与自性五句、风幡公案逐句对照</p></div>
<div class="go"><a href="https://q1z2q3-debug.github.io/daokedao-liuzu/duibi.html" rel="noopener">并读</a></div></div>
</div>

<h2>这本书主张什么</h2>
<p>「自性」不是一个独立恒常的实体，是般若空性在众生分上的本名。自性五句（何期自性本自清净／本不生灭／本自具足／本无动摇／能生万法）说的不是五个属性，是同一件事的五个面：本自具足，所以不必外求；本无动摇，所以风幡之争勘不出胜负。</p>
<p>「和合之辨」是全书判定尺：<b>和</b>是本自圆满、无边界、无对待的实相；<b>合</b>是因缘构框、划分边界、二元对立、取舍抓取的造作。凡把一体割为两边、另立一个可抓取的目标（包括把「空」「静」「次第」「顿」做成可抓取之物）者，皆判为合。</p>
<p>不支持狂禅，也不支持枯禅：自性具足是性体本圆，不代表无需去蔽；无念不是压念断念，是念起而不黏。</p>

<h2>体例：一品八段</h2>
<p>原文底本、时代背景、字源溯源、逐段深解、体系联动、和合对照、跨典互参、小结。行由品内嵌两篇专释：自性五句、风幡公案。底层模型为「三才五蕴太极空杯」，以阴阳太和统摄动静，并与老庄、易传、金刚般若互参。</p>
<p class="small">底本：敦煌本《六祖坛经》S.5475；品题依通行十品立目，不改动经文文字。参考 <a href="{SITE}/preface.html">卷首·总序与凡例</a>。</p>
</div></main>""" + foot(), encoding="utf-8")

    # ---- 下载页 ----
    pdf = next(iter(sorted((BOOK).glob("*.pdf"))), None)
    apk = next(iter(sorted((ROOT / "packages").glob("**/*.apk"))), None) if (ROOT / "packages").exists() else None
    pdf_row = ""
    if pdf:
        mb = pdf.stat().st_size / 1e6
        pdf_row = f"""<div class="row"><div class="no">PDF</div><div><h3><a href="{SITE}/downloads/{pdf.name}">成书 PDF · A5</a></h3>
<p class="small" style="margin:0;">{mb:.1f} MB，可直接印制</p></div><div class="go"><a href="{SITE}/downloads/{pdf.name}">下载</a></div></div>"""
    apk_row = ""
    if apk:
        mb = apk.stat().st_size / 1e6
        apk_row = f"""<div class="row"><div class="no">APK</div><div><h3><a href="{SITE}/downloads/{apk.name}">安卓离线包 v{VER}</a></h3>
<p class="small" style="margin:0;">{mb:.1f} MB，包名 com.daokedao.tanjing，零权限，字体已内置</p></div><div class="go"><a href="{SITE}/downloads/{apk.name}">下载</a></div></div>"""
    (DOCS / "downloads" / "index.html").write_text(
        head(f"下载｜{TITLE}", "《坛经》通释 A5 成书 PDF 与离线安卓包 APK，零权限、断网可用。",
             "/downloads/", None, act="downloads") +
        f"""<main><div class="wrap">
<p class="eyebrow">下载</p>
<h1>四种副本</h1>
<p class="lede">同一部书，四种拿法：成书 PDF 供印，APK 供手机断网读，阅读版在浏览器里一页到底，母本给要改字的人。</p>
<div class="list">{pdf_row}{apk_row}
<div class="row"><div class="no">HTML</div><div><h3><a href="{SITE}/book.html">单文件阅读版</a></h3>
<p class="small" style="margin:0;">自包含、无外链，含封面扉页与两张附图</p></div><div class="go"><a href="{SITE}/book.html">打开</a></div></div>
<div class="row"><div class="no">MD</div><div><h3><a href="https://github.com/q1z2q3-debug/daokedao-tanjing/blob/main/book/{MD.name}">母本 Markdown</a></h3>
<p class="small" style="margin:0;">供引用、校订、再排版</p></div><div class="go"><a href="https://github.com/q1z2q3-debug/daokedao-tanjing/blob/main/book/{MD.name}">GitHub</a></div></div>
</div>
<p class="small">APK 与 PDF 的 SHA-256 见 <a href="https://github.com/q1z2q3-debug/daokedao-tanjing/tree/main/packages">packages/</a>；签发证书与《道德经》《易传》《心经》《庄子》《金刚经》同一把。</p>
</div></main>""" + foot(), encoding="utf-8")

    # ---- 英文页 ----
    en = json.loads(EN_JSON.read_text(encoding="utf-8")) if EN_JSON.exists() else {}
    if en:
        en_rows = "".join(f"""<div class="row"><div class="no">{i:02d}</div>
<div><h3><a href="{en[str(i)]['url']}" rel="noopener">Chapter {i} · {H.escape(en[str(i)]['name'])}</a></h3>
<p class="small" style="margin:0;">canonical <a href="{SITE}/chapters/{i:02d}-{recs[i-1]['slug']}.html">第 {i} 品</a></p></div>
<div class="go"><a href="{en[str(i)]['url']}" rel="noopener">dev.to</a></div></div>""" for i in sorted(int(k) for k in en))
        en_count = len(en)
    else:
        en_rows = '<p class="small">十篇英文稿整理中，发完即在此列。</p>'
        en_count = 0
    (DOCS / "english" / "index.html").write_text(
        head(f"英文稿｜{TITLE}", "《坛经》十品的英文短论，一品一篇，canonical 一律指回中文品页。",
             "/english/", None, act="english") +
        f"""<main><div class="wrap">
<p class="eyebrow">English · dev.to</p>
<h1>十品，一品一篇英文</h1>
<p class="lede">每一品写成一篇英文短论：起于一句经文，中间只做一处字源或名相的分层，落在一个可自测的问题上。canonical 一律指回本分的中文页——同一个论点，两个入口都能核。</p>
<p class="small">已发 {en_count} 篇 / 10　·　账号 <a href="https://dev.to/q1z2q3debug" rel="noopener">q1z2q3debug</a>　·　总目 <a href="{SITE}/chapters/">十品</a>　·　书站总索引 <a href="https://q1z2q3-debug.github.io/runze-daokedao/devto/">全系列英文稿</a></p>
<div class="list">{en_rows}</div>
</div></main>""" + foot(), encoding="utf-8")

    # ---- 机器可读 ----
    (DOCS / "llms.txt").write_text(f"""# {TITLE}

> 润泽（润泽博士）《道可道》系列读本。以敦煌本《六祖坛经》S.5475 为底本，十品通释，八段体例，附三张查表附录。全书约 4.0 万字。

## 读本
- 全书一页（阅读版，单文件）：{SITE}/book.html
- 十品（一品一页）：{SITE}/chapters/
- 卷首·总序与凡例：{SITE}/preface.html
- 后记：{SITE}/afterword.html
- 附录（三十六对表、三科表、品目对照）：{SITE}/appendix.html
- 英文十篇：{SITE}/english/
- 下载（PDF / APK / Markdown 母本）：{SITE}/downloads/
- 仓库：https://github.com/q1z2q3-debug/daokedao-tanjing
""" + (f"- DOI：https://doi.org/{DOI}\n" if not DOI.endswith("00000000") else "") + f"""
## 十品
""" + "\n".join(f"- {r['name']}：{SITE}/chapters/{r['i']:02d}-{r['slug']}.html（{r['wc']} 字）" for r in recs) + f"""

## 事实
- 底本：敦煌本《六祖坛经》S.5475；品题依通行十品立目，不改动经文文字。
- 体例：原文底本／时代背景／字源溯源／逐段深解／体系联动／和合对照／跨典互参／小结。
- 两篇专释：行由品内嵌「自性五句」「风幡公案」。
- 判定尺：「和」为本自圆满无对待之实相，「合」为划界取舍之造作。
- 关键辨析：自性非独立实体；无念非压念；不支持狂禅与枯禅。
- 附录：三十六对敦煌本列三十三对，与名目差三，照录不补。
- 许可：CC BY-NC-SA 4.0。

## 引用
润泽. {TITLE}：v{VER}. 2026. {('https://doi.org/' + DOI) if not DOI.endswith('00000000') else SITE}
""", encoding="utf-8")

    (DOCS / "robots.txt").write_text("User-agent: *\nAllow: /\n\n" +
                                     "".join(f"User-agent: {b}\nAllow: /\n" for b in
                                             ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "PerplexityBot", "Google-Extended", "CCBot", "Bytespider"]) +
                                     f"\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")

    urls = ["/", "/book.html", "/preface.html", "/chapters/", "/english/", "/afterword.html", "/appendix.html", "/downloads/"] + \
           [f"/chapters/{r['i']:02d}-{r['slug']}.html" for r in recs]
    (DOCS / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
                                      "".join(f"<url><loc>{SITE}{u}</loc><lastmod>2026-11-14</lastmod></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")

    (DOCS / "favicon.svg").write_text("""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" fill="#F7F4EE"/><rect x="6" y="6" width="52" height="52" fill="none" stroke="#944433" stroke-width="2"/>
<text x="32" y="43" text-anchor="middle" font-family="serif" font-size="30" fill="#25211D">坛</text></svg>""", encoding="utf-8")

    # 阅读版 → book.html
    reader = next(iter(sorted(BOOK.glob("*阅读版.html"))), None)
    if reader:
        (DOCS / "book.html").write_text(reader.read_text(encoding="utf-8"), encoding="utf-8")

    # 下载副本
    if pdf:
        (DOCS / "downloads" / pdf.name).write_bytes(pdf.read_bytes())
    if apk:
        (DOCS / "downloads" / apk.name).write_bytes(apk.read_bytes())

    print(f"built {len(list(DOCS.rglob('*.html')))} html pages, {len(recs)} pin, sitemap {len(urls)}")


if __name__ == "__main__":
    build()
