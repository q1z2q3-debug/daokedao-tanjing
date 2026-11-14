# -*- coding: utf-8 -*-
"""把《润泽说 道可道之坛经·通释》编译成单文件 HTML。
用法：python3 scripts/build_html.py （需 pandoc）
"""
import pathlib, re, subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
BOOK = ROOT / "book"
MD = BOOK / "润泽说 道可道之坛经·通释.md"
OUT = BOOK / "坛经·阅读版.html"
TMP = pathlib.Path("/tmp/tanjing_src.md")
BODY = pathlib.Path("/tmp/tanjing_body.html")

src = MD.read_text(encoding="utf-8")
src = re.sub(r"^---\n.*?\n---\n", "", src, count=1, flags=re.S)
src = src.replace("# 润泽说 道可道之坛经\n## 六祖大师法宝坛经 · 通释\n", "")
TMP.write_text(src, encoding="utf-8")

subprocess.run(["pandoc", str(TMP), "-f", "markdown+hard_line_breaks",
                "-t", "html5", "--no-highlight", "-o", str(BODY)], check=True)
body = BODY.read_text(encoding="utf-8")
body = re.sub(r"<h([234])\s*\n\s*", r"<h\1 ", body)
body = body.replace("<blockquote>", '<blockquote class="sutra">')
body = body.replace("<table>", '<table class="t">')

parts = re.findall(r'<h1 id="([^"]+)"[^>]*>(.*?)</h1>', body, flags=re.S)
nav = "\n".join('<li><a href="#%s"><i>·</i><span>%s</span></a></li>'
                % (hid, re.sub(r"<[^>]+>", "", raw).strip())
                for hid, raw in parts)

body = re.sub(r"<h1 ", '<h2 class="ch" ', body)
body = body.replace("</h1>", "</h2>")

FAVICON = ("<link rel=\"icon\" type=\"image/svg+xml\" href=\"data:image/svg+xml,"
           "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
           "%3Crect width='64' height='64' fill='%23994433'/%3E"
           "%3Ctext x='32' y='46' font-size='30' text-anchor='middle' "
           "fill='%23F7F4EE' font-family='serif'%3E%E5%9D%87%3C/text%3E%3C/svg%3E\">")

SHELL = pathlib.Path(__file__).parent.joinpath("_shell.html").read_text(encoding="utf-8")
out = SHELL.replace("__NAV__", nav).replace("__BODY__", body).replace("__FAVICON__", FAVICON)
OUT.write_text(out, encoding="utf-8")
print("ok", len(out), "chars |", len(parts), "toc items |", OUT)
