# 润泽说 道可道之坛经 · 通释

> 十品圆满，封面、扉页与附图二（v1.2.1）。站点十八页、A5 成书 PDF 一百零四页、安卓离线包零权限，DOI 已存缴。

《六祖大师法宝坛经》通释。底本用敦煌本（S.5475），体例与同系列《金刚经》《心经》一致。

**破执在金刚，归心在坛经。**

## 全书宗旨

《金刚经》讲「无住以破执」，《坛经》讲「自性以成真」。无住是体，自性是用；般若是眼，坛经是足。

全书贯穿四维：三才五蕴太极空杯模型（勘破五蕴缘起）／阴阳太和（统摄动静、风幡、有无）／和合之辨（分「本然之和」与「造作之合」）／《金刚经》般若范式（校准全部见地）。

## 已完成篇目

| 篇目 | 内容 |
|---|---|
| 总序 | 立旨 · 核心宗旨 · 七大定规 · 全书总纲 |
| 凡例 | 底本 · 体例 · 五组名相定义 · 校注符号 · 义理校准 |
| 行由品第一 | 求法因缘 · 神秀慧能两偈 · 三更传法 · 辞衣南行 · 风幡勘验。内嵌两篇核心专释：**自性五句**、**风幡公案** |
| 般若品第二 | 摩诃般若 · 自性真空 · 真如起念 · 无念之行 · 无相颂 |
| 疑问品第三 | 自性净土 · 十万八千之喻 · 色身为城 · 在家亦得 · 无相颂 |
| 定慧品第四 | 定慧一体 · 灯与光喻 · 无念为宗、无相为体、无住为本 |
| 坐禅品第五 | 破看心看净 · 外离相为禅，内不乱为定 |
| 忏悔品第六 | 五分法身香 · 无相忏悔 · 四弘誓愿 · 无相三归依 · 一体三身自性佛 |
| 机缘品第七 | 非关文字 · 转经 · 三身四智 · 破空相 · 破断常 · 青原南岳二支 |
| 顿渐品第八 | 法无顿渐，人有利钝 · 破住心观静 · 行昌公案 |
| 护法品第九 | 道由心悟 · 烦恼即菩提 · 实性 · 辨外道不生不灭 |
| 付嘱品第十 | 三科 · 三十六对 · 真假动静偈 · 末后一偈 |
| 后记 | 成书现状 · 底本说明 · 和合判定说明 |
| 附录一 | 三十六对表（敦煌本列三十三对，与名目差三，照录不补；分七组） |
| 附录二 | 三科表（五蕴 · 十二入 · 十八界） |
| 附录三 | 品目对照（敦煌本十品 ↔ 宗宝本；护法品第九＝宣诏品第九） |

## 体例（每品八段）

原文底本｜时代背景｜字源溯源｜逐段深解｜体系联动｜和合对照｜跨典互参｜小结

## 库内结构

```
daokedao-tanjing/
├── book/
│   ├── 润泽说 道可道之坛经·通释.md   ← 母本
│   └── 坛经·阅读版.html              ← 单文件阅读版
├── book/
│   ├── figures/                      ← 附图源（图一 PNG、图二 SVG）
│   └── 润泽说 道可道之坛经.pdf        ← A5 成书版（104 页）
├── docs/                             ← Pages 站点（18 页）
│   ├── index.html  preface.html  chapters/  afterword.html  appendix.html
│   ├── downloads/  english/  book.html
│   ├── llms.txt  sitemap.xml  robots.txt  favicon.svg  figures/
├── apk/                              ← 离线阅读壳（aapt2 + d8 + apksigner）
├── packages/apk-1.2.0-tanjing/       ← APK 与校验值归档
├── data/en-posts.json                ← 英文发稿清单（/english/ 读取）
├── scripts/
│   ├── build_html.py  _shell.html    ← 母本 → 单文件阅读版
│   ├── build_site.py                 ← 十品逐页站点
│   ├── build_pdf.py                  ← A5 成书 PDF（weasyprint）
│   ├── zenodo-deposit.py             ← 存缴取 DOI
│   └── setup-toolchain.sh            ← 重建 Android 工具链
├── LICENSE  README.md  CHANGELOG.md  VERSION  CITATION.cff  .gitignore
```

## 重建

```bash
python3 scripts/build_html.py            # 母本 → 阅读版（需 pandoc）
python3 scripts/build_site.py            # 18 页站点 → docs/
python3 scripts/build_pdf.py             # A5 成书 PDF（需 weasyprint）
bash scripts/setup-toolchain.sh          # 首次：重建 Android 工具链
python3 apk/prepare-assets.py && bash apk/build.sh   # 离线 APK
```

## 在线阅读

- 站点：<https://q1z2q3-debug.github.io/daokedao-tanjing/>（18 页，逐品独立）
- 目录：<https://q1z2q3-debug.github.io/daokedao-tanjing/chapters/>
- 全书一页：<https://q1z2q3-debug.github.io/daokedao-tanjing/book.html>
- 下载：<https://q1z2q3-debug.github.io/daokedao-tanjing/downloads/>
- 英文页：<https://q1z2q3-debug.github.io/daokedao-tanjing/english/>（十品十篇，已发）

## 引用与存档

- DOI：<https://doi.org/10.5281/zenodo.24223179>（Zenodo，含 md／PDF／HTML／APK 四件）
- 引用格式见 `CITATION.cff`。

## 同系列

| 篇目 | 仓库 |
|---|---|
| 金刚经 · 三十二分通释 | [daokedao-jingang](https://github.com/q1z2q3-debug/daokedao-jingang) |
| 心经 · 通释 | [daokedao-xinjing](https://github.com/q1z2q3-debug/daokedao-xinjing) |
| 周易 · 六十四卦通释 | [daokedao-yijing](https://github.com/q1z2q3-debug/daokedao-yijing) |
| 道德经 · 通释 | [runze-daodejing](https://github.com/q1z2q3-debug/runze-daodejing) |

## 许可

[CC BY-NC-SA 4.0](LICENSE)：署名、非商业性使用、相同方式共享。

## 商业使用

本书公开层为 CC BY-NC-SA 4.0；商业训练、商业分发与第三方素材边界见 [`NOTICE.md`](NOTICE.md)。
