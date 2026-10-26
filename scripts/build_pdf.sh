#!/usr/bin/env bash
# 构建公文 PDF：xelatex 多遍，并过滤关键错误。
#
# 用法：
#   bash scripts/build_pdf.sh examples/notice.tex
#   bash scripts/build_pdf.sh examples/notice.tex 3      # 指定遍数
#
# 关于 gongwen.sty 的查找：不用 TEXINPUTS。原因是 Windows 版 kpathsea 的路径列表
# 分隔符是分号而 MSYS 给的是冒号，且含中文的路径会被解析错，导致连主文件都找不到。
# 改为把 gongwen.sty 临时复制到文档所在目录，编译完删除，简单且跨平台一致。
set -u

TEX="$1"
PASSES="${2:-2}"

if [ ! -f "$TEX" ]; then
  echo "找不到文件：$TEX" >&2
  exit 1
fi

if ! command -v xelatex >/dev/null 2>&1; then
  echo "PATH 里没有 xelatex。请安装 TeX Live，或把 xelatex 所在目录加入 PATH。" >&2
  exit 1
fi

DIR=$(dirname "$TEX")
BASE=$(basename "$TEX")
ROOT=$(cd "$(dirname "$0")/.." && pwd)
STY="$ROOT/assets/gongwen.sty"

if [ ! -f "$STY" ]; then
  echo "缺少样式包：$STY" >&2
  exit 1
fi

# 临时复制样式包，退出时清理
cp -f "$STY" "$DIR/gongwen.sty"
cleanup() { rm -f "$DIR/gongwen.sty"; }
trap cleanup EXIT INT TERM

cd "$DIR" || exit 1

for i in $(seq 1 "$PASSES"); do
  echo "[xelatex] 第 ${i}/${PASSES} 遍"
  if ! xelatex -interaction=nonstopmode -halt-on-error "$BASE" >/dev/null 2>&1; then
    echo "[失败] 第 ${i} 遍报错，日志摘录：" >&2
    grep -E '^!' "${BASE%.tex}.log" | head -20 >&2
    exit 1
  fi
done

PDF="${BASE%.tex}.pdf"
if [ -f "$PDF" ]; then
  # 字体降级提示（gongwen.sty 在缺字体时 \typeout）
  grep -o 'gongwen: .*' "${BASE%.tex}.log" 2>/dev/null | sort -u | sed 's/^/  字体 /'
  echo "[完成] $PDF"
else
  echo "[失败] 未生成 PDF" >&2
  exit 1
fi
