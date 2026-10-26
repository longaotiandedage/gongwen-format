# 踩过的坑

以下均为实际排版时遇到的问题，逐条记录避免重复。

## LaTeX 侧

### 1. `ctexart` 没有 `zihao=3` 选项

写 `\documentclass[...,zihao=3]{ctexart}` 会报
`Key 'ctex/option/zihao' accepts only a fixed set of choices`。

字号必须用 `\fontsize{16pt}{28pt}\selectfont` 显式设定。
本技能的 `gongwen.sty` 已在 `\AtBeginDocument` 里设好，无需重复。

### 2. 红色分隔线会溢出 32 pt

`\rule{\textwidth}{1.5pt}` 作为独立段落时继承 `\parindent`（2 字 = 32 pt），
线宽又是整版心，正好超出一个缩进量，报 `Overfull \hbox (32.0pt too wide)`。

必须写成 `\noindent{\color{gwred}\rule{\textwidth}{1.5pt}}`。
`gongwen.sty` 的 `\gwdocno` 已处理。

### 3. `flushright` 里的 `\hspace` 会溢出

```latex
\begin{flushright}
华中科技大学教务处\hspace{2em}\par
\end{flushright}
```

右对齐段落末尾加 `\hspace`，行宽变成「文本 + 2em」，超出 `\hsize`。

改用 `\noindent\hfill 华中科技大学教务处\hspace*{2em}\par`。
`gongwen.sty` 的 `\gwsign` 已处理。

### 4. 落款会孤立成一页

正文写满时，附件说明与署名可能被挤到下一页，出现只有两行字的空白页。

用 `\begin{samepage}...\end{samepage}` 把附件与落款包住：

```latex
\begin{samepage}
\gwattach{附件：1.\ 任务分工表}
\gwattachcont{2.\ 体例说明}
\gwsign{××大学教务处}{2026年10月26日}
\end{samepage}
```

### 5. 三级标题是仿宋加粗，不是黑体加粗

初版误用 `\hei\bfseries`。国标要求 3 号仿宋加粗。

而简体仿宋**没有真粗体**，需在同一字族上做合成加粗：

```latex
\setCJKmainfont{FangSong}[BoldFont=FangSong, BoldFeatures={FakeBold=2.5}]
```

之后 `\bfseries` 得到的就是仿宋加粗，与 Word 的「加粗」表现一致。
`gongwen.sty` 已对正文主字族启用 FakeBold。

### 6. 双面模式下左右边距「互换」是正常的

用 `twoside` 时 geometry 的 `left`/`right` 在偶数页互换，实测第 2 页左 26 mm、右 28 mm。

这不是错误——订口要始终在装订边，偶数页的装订边在右侧。不要「修」它，
也不要在校验脚本里把它判为偏差。

### 7. 字体名与文件名不是一回事

`\setCJKmainfont{simfang.ttf}` 是按**文件名**加载（需 `Path` 选项），
`\setCJKmainfont{FangSong}` 是按**字体族名**加载。

跨平台脚本应按族名加载，并用 `\IfFontExistsTF` 做回退判断。
按文件名加载在别的系统上必然失败。

## DOCX 侧

### 8. 页码要手写域，奇偶页不同还要改 settings

python-docx 没有页码 API。要插入 `<w:fldSimple w:instr=" PAGE "/>`。

双面页码（单页居右、双页居左）还需要在 `settings.xml` 里加
`<w:evenAndOddHeaders/>`，再分别写 `section.footer` 与 `section.even_page_footer`，
并把 `is_linked_to_previous` 设为 `False`。

### 9. 红色分隔线用段落边框

即 `<w:pBdr><w:bottom w:val="single" w:sz="12" w:color="D40000"/>`。
注意 `w:sz` 的单位是 **1/8 磅**，12 才是 1.5 磅。

### 10. 字号单位是半磅

`<w:sz w:val="32"/>` 才是 16 pt（三号）。写 16 会变成 8 pt。

### 11. 中文字体必须同时设 `w:eastAsia`

只设 `run.font.name` 不会改变中文字形。还要：

```python
run._element.rPr.rFonts.set(qn("w:eastAsia"), "仿宋")
```

### 12. 「首行缩进 2 字符」用 `Pt(字号 × 2)`

python-docx 没有「字符」单位。`Pt(32)` 对应三号字的 2 字符。
若要严格按字符数，得写 `w:firstLineChars`，但按磅值换算结果一致。

### 13. 附件说明的缩进

首行左空 2 字；多附件时，第二行起要对齐到「1.」下方，即左空 6 字。
`attach()` 已按此实现。

## 测量与验证

### 14. 量版面别把页脚算进正文

页码是 4 号（14 pt）。若按「字号 ≥ 12 就算正文」过滤，页脚会被计入，
A4 纸下白边会从 35 mm 错算成 26 mm。

应按内容判断（形如 `— 1 —` 的纯数字行）或按 y 坐标排除页脚区域。
`verify_layout.py` 用的是内容判断。

### 15. LibreOffice 渲染会报 `missingFonts: ["Courier"]`

来自默认样式残留，中文不受影响，可忽略。

### 16. 文字包围盒比版心大

字体有上伸部与下伸部，包围盒量出来的版心通常比理论值大半毫米到一毫米。
校验容差取 ±2 mm，不要取 ±0.5 mm。
