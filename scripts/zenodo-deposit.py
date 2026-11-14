#!/usr/bin/env python3
"""把《坛经》存入 Zenodo，取一个可引用的 DOI。

用法：
  export ZENODO_TOKEN=$(~/.daokedao-vault/cred zenodo)
  python3 scripts/zenodo-deposit.py --dry-run      # 建草稿、传附件，不发布
  python3 scripts/zenodo-deposit.py --publish      # DOI 立即生效，不可撤销
"""
import argparse, json, os, time, urllib.error, urllib.request
from pathlib import Path

BASE = "https://zenodo.org/api"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
ROOT = Path(__file__).resolve().parent.parent
VER = "1.2.0"

FILES = [
    ("book/润泽说 道可道之坛经·通释.md", "daokedao-tanjing-v1.2.0.md"),
    ("book/润泽说 道可道之坛经.pdf", "daokedao-tanjing-v1.2.0.pdf"),
    ("book/坛经·阅读版.html", "daokedao-tanjing-reader-v1.2.0.html"),
    ("packages/apk-1.2.0-tanjing/道可道-坛经-1.2.0.apk", "daokedao-tanjing-reader-v1.2.0.apk"),
]
META = {"metadata": {
    "title": "润泽说 道可道之坛经（v1.2.0）",
    "upload_type": "publication",
    "publication_type": "book",
    "publication_date": "2026-11-14",
    "version": VER,
    "language": "zho",
    "license": "cc-by-nc-sa-4.0",
    "creators": [{"name": "润泽"}],
    "keywords": ["坛经", "六祖", "慧能", "敦煌本", "自性", "和合之辨", "禅宗", "中国哲学"],
    "description": (
        "<p>《六祖大师法宝坛经》十品通释。全书约 4.0 万字（40,373 字），"
        "总序、凡例、十品、后记，另附三张查表附录。</p>"
        "<p>底本：敦煌本《六祖坛经》S.5475；品题依通行十品立目，立目只为便于阅读，不改动经文文字。</p>"
        "<p>体例：每品八段——原文底本、时代背景、字源溯源、逐段深解、体系联动、"
        "和合对照、跨典互参、小结。行由品内嵌两篇专释：自性五句、风幡公案。</p>"
        "<p>立宗：破执在金刚，归心在坛经；无住是体，自性是用，般若是眼，坛经是足。"
        "自性非独立恒常之实体，是般若空性在众生分上的本名。「和」为本自圆满无对待之实相，"
        "「合」为划界取舍之造作。不支持狂禅，也不支持枯禅。</p>"
        "<p>附录三表：三十六对表（敦煌本列三十三对，与名目差三，照录不补）、三科表、品目对照。</p>"
        "<p>附件：Markdown 母本、A5 成书 PDF（104 页）、单文件 HTML 阅读版、"
        "安卓离线包（零权限、断网可用、字体内置）。</p>"
    ),
    "related_identifiers": [
        {"relation": "isSupplementTo",
         "identifier": "https://github.com/q1z2q3-debug/daokedao-tanjing",
         "resource_type": "software"},
        {"relation": "isAlternateIdentifier",
         "identifier": "https://q1z2q3-debug.github.io/daokedao-tanjing/",
         "resource_type": "other"},
        {"relation": "isPartOf",
         "identifier": "https://q1z2q3-debug.github.io/runze-daokedao/",
         "resource_type": "other"},
        {"relation": "references",
         "identifier": "https://doi.org/10.5281/zenodo.24222027",
         "resource_type": "publication"},
    ],
    "notes": "许可 CC BY-NC-SA 4.0。引用请注明书名与版本号 v1.2.0。本书为「润泽说 道可道」系列禅宗读本，与《金刚经通释》互参：破执在金刚，归心在坛经。",
}}


def call(url, token, data=None, method="POST", raw=None, tries=6):
    """Zenodo 偶发 503，按退避重试。"""
    body = raw if raw is not None else (json.dumps(data).encode() if data is not None else None)
    last = None
    for i in range(tries):
        req = urllib.request.Request(url, data=body, method=method, headers={
            "Authorization": f"Bearer {token}", "User-Agent": UA,
            "Content-Type": "application/json", "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (429, 500, 502, 503, 504):
                print(f"  zenodo {e.code}，{30*(i+1)}s 后重试（{i+1}/{tries}）")
                time.sleep(30 * (i + 1))
                continue
            raise
    raise last


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--publish", action="store_true")
    a = ap.parse_args()
    token = os.environ.get("ZENODO_TOKEN") or ""
    if not token:
        raise SystemExit("缺 ZENODO_TOKEN")

    dep = call(BASE + "/deposit/depositions", token, {})
    dep_id = dep["id"]
    bucket = dep["links"]["bucket"]
    print("draft", dep_id, dep["links"]["html"])

    call(BASE + f"/deposit/depositions/{dep_id}", token, META, method="PUT")

    for path, name in FILES:
        data = (ROOT / path).read_bytes()
        for i in range(6):
            req = urllib.request.Request(f"{bucket}/{name}", data=data, method="PUT", headers={
                "Authorization": f"Bearer {token}", "User-Agent": UA,
                "Content-Type": "application/octet-stream"})
            try:
                with urllib.request.urlopen(req, timeout=900) as r:
                    j = json.load(r)
                break
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503, 504) and i < 5:
                    print(f"  up {e.code}，{30*(i+1)}s 后重试")
                    time.sleep(30 * (i + 1))
                    continue
                raise
        print("  up", j.get("key"), j.get("size"))

    if a.publish:
        pub = call(BASE + f"/deposit/depositions/{dep_id}/actions/publish", token, {}, method="POST")
        print("DOI", pub.get("doi"), pub.get("links", {}).get("doi"))
    else:
        print("草稿未发布：", dep["links"]["html"])


if __name__ == "__main__":
    main()
