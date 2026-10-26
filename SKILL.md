---
name: gongwen-format
description: 按 GB/T 9704—2012《党政机关公文格式》排版中文公文与正式文档，产出 LaTeX/PDF 与 DOCX。触发场景：用户要求生成通知、报告、请示、批复、函、纪要、方案、总结、汇报材料、说明书等中文正式文档；提到"公文格式""红头文件""符合国标""按党政机关公文格式排""GB/T 9704"；或要求把已有内容排成 A4、三号仿宋、版心 156×225 mm、每行 28 字、行距 28 磅的版式。
metadata:
  author: DSH user
  version: 1.0.0
  language: zh-CN
  standard: GB/T 9704-2012
---

# 公文格式排版

把内容排成符合 GB/T 9704—2012《党政机关公文格式》的中文正式文档，同时提供
LaTeX（出 PDF）与 python-docx（出 DOCX）两条路线，并附带版面自动校验。

本技能给出的是**可实测的版式参数**，不是凭记忆的描述。所有关键尺寸都在样例上量过。

---

## 一、三条纪律

1. **不得编造参数。** 版式数值只认本技能与国标给出的值；不确定就查
   `references/parameters.md`，不要凭印象填。
2. **字体替代必须说明。** 方正小标宋简体通常缺失，用华文中宋替代时，
   交付说明里要写一句"标题字为替代字体"。同理，Linux 上缺仿宋时用 Fandol 替代也要说明。
3. **实测后才交付。** 出 PDF 或 DOCX 后必须跑 `scripts/verify_layout.py`
   量一遍版面，把实测值与国标对照，通过后才算完成。

---

## 二、版式参数（照抄即可）

| 项目 | 数值 |
|---|---|
| 纸张 | A4，210 × 297 mm |
| 天头（上白边） | 37 mm ± 1 |
| 订口（左白边） | 28 mm ± 1 |
| 右白边 | 26 mm |
| 下白边 | 35 mm |
| 版心 | 156 × 225 mm |
| 每页 | 22 行 |
| 每行 | 28 字 |
| 行距 | 固定值 28 磅 |
| 正文 | 3 号仿宋（16 pt） |
| 文件标题 | 2 号小标宋（22 pt），居中 |
| 一级标题 | 3 号黑体 |
| 二级标题 | 3 号楷体 |
| 三级标题 | 3 号仿宋加粗 |
| 页码 | 4 号宋体，单页居右、双页居左，两侧一字线 |
| 首行缩进 | 2 字符 |

字号换算：三号 16 pt、二号 22 pt、四号 14 pt。完整对照见 `references/parameters.md`。

---

## 三、两条路线

### 路线 A：LaTeX → PDF

适合排版要求严格、需要精确控制的场合。

```latex
\documentclass[UTF8, fontset=none, twoside]{ctexart}
\usepackage{gongwen}          % 把 assets/gongwen.sty 放进 TEXINPUTS 或同目录

\begin{document}
\gworg{××大学教务处文件}       % 发文机关标志（红色小标宋）
\gworg{\bfseries ××大学文件}      % 需要更粗的版头时加 \bfseries（合成粗体）
\gwdocno{教字〔2026〕15 号}     % 发文字号 + 自动生成红色分隔线
\gwtitle{关于开展××工作的通知} % 标题（2 号，居中）

\gwto{各教学单位：}             % 主送机关（顶格）

\gwbody{正文段落……}
\gwhone{一、建设目标}           % 一级标题
\gwhtwo{（一）总体要求}         % 二级标题
\gwhthree{1. 具体措施}          % 三级标题

\gwattach{1. 任务分工表\\
         2. 体例说明}          % 附件说明（左空二字）
\gwsign{××大学教务处}{二〇二六年十月二十六日}  % 落款
\end{document}
```

构建：

```bash
bash scripts/build_pdf.sh examples/notice.tex
```

模板与样例见 `assets/gongwen.sty`、`examples/notice.tex`。

### 路线 B：python-docx → DOCX

适合需要后续在 Word 里继续编辑的场合。

```python
from gongwen_docx import GongwenDoc

doc = GongwenDoc()
doc.org("××大学教务处文件")
doc.docno("教字〔2026〕15 号")
doc.title("关于开展××工作的通知")
doc.to("各教学单位：")
doc.body("正文段落……")
doc.h1("一、建设目标")
doc.h2("（一）总体要求")
doc.h3("1. 具体措施")
doc.attach(["1. 任务分工表", "2. 体例说明"])
doc.sign("××大学教务处", "二〇二六年十月二十六日")
doc.save("notice.docx")
```

实现见 `scripts/gongwen_docx.py`（可直接 import，也可当脚本跑样例）。

---

## 四、校验

```bash
# 量 PDF 版面，与国标逐项对照
python scripts/verify_layout.py examples/notice.pdf

# 检查本机字体是否齐备，缺哪个、怎么替代
python scripts/check_fonts.py
```

`verify_layout.py` 会输出实测的上/下/左/右白边与版心尺寸，并标出是否落在国标容差内。
DOCX 也能量（读 `sectPr` 的页边距与字号设置）。

---

## 五、常见错误（详细版见 references/pitfalls.md）

- 红色分隔线忘记 `\noindent`，会因首行缩进溢出 32 pt
- 落款被挤到单独一页，要用 `samepage` 包住附件与落款
- 三级标题误用黑体，应为仿宋加粗（简体仿宋无真粗体，需 `FakeBold`）
- 测量版面时把 14 pt 的页脚页码算进正文，导致下白边算错
- docx 里中文字体只设 `font.name` 不生效，必须同时设 `w:eastAsia`

---

## 六、字体与跨平台

| 用途 | Windows | macOS | Linux |
|---|---|---|---|
| 正文仿宋 | FangSong / 仿宋 | STFangsong | FandolSong（TeXLive） |
| 一级标题黑体 | SimHei / 黑体 | STHeiti | FandolHei |
| 二级标题楷体 | KaiTi / 楷体 | STKaiti | FandolKai |
| 标题小标宋 | 方正小标宋（常缺） | STZhongsong | FandolSong Bold |
| 页码宋体 | SimSun / 宋体 | STSong | FandolSong |

`assets/gongwen.sty` 内置 `\IfFontExistsTF` 回退链，缺字体会自动降级并 `\typeout` 提示，
但**降级后字体形态与国标有差异，交付时要说明**。

---

## 七、参考文件

| 文件 | 内容 |
|---|---|
| `references/parameters.md` | 版式参数、字号对照、字体表、验算 |
| `references/elements.md` | 公文各要素的格式与顺序 |
| `references/pitfalls.md` | 14 条实测踩坑记录 |
| `assets/gongwen.sty` | 可复用的 LaTeX 样式包 |
| `examples/notice.tex` | 完整公文样例源码 |
