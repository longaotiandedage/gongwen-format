#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""检查本机是否具备公文排版所需的中文字体，缺哪个、回退到哪个。

用法：
    python scripts/check_fonts.py

Windows 读注册表字体表，macOS / Linux 走 fc-list。
退出码 0 表示首选字体齐全，1 表示有回退。
"""
import platform
import subprocess
import sys

# 每个用途按优先级列出候选字体名（与 gongwen.sty 的回退链一致）
# 同时列英文族名与中文族名，因为注册表里两种都可能出现
ROLES = [
    ("正文（仿宋）", ["FangSong", "仿宋", "STFangsong", "华文仿宋",
                     "FandolSong", "Noto Serif CJK SC"]),
    ("一级标题（黑体）", ["SimHei", "黑体", "STHeiti", "AdobeHeitiStd-Regular",
                         "FandolHei", "Noto Sans CJK SC"]),
    ("二级标题（楷体）", ["KaiTi", "楷体", "STKaiti", "华文楷体", "FandolKai"]),
    ("页码（宋体）", ["SimSun", "宋体", "STSong", "华文宋体", "FandolSong",
                     "Noto Serif CJK SC"]),
    ("标题（小标宋）", ["FZXiaoBiaoSong-B05S", "方正小标宋简体",
                       "华文中宋", "STZhongsong", "STSong", "华文宋体",
                       "FandolSong"]),
]


def fonts_windows():
    import winreg

    names = set()
    for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        try:
            key = winreg.OpenKey(
                root,
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts")
        except OSError:
            continue
        i = 0
        while True:
            try:
                value_name, _, _ = winreg.EnumValue(key, i)
            except OSError:
                break
            # 形如 "仿宋 (TrueType)"、"SimSun & NSimSun (TrueType)"
            base = value_name.split(" (")[0]
            for part in base.split("&"):
                part = part.strip()
                if part:
                    names.add(part)
            i += 1
    return names


def fonts_posix():
    try:
        out = subprocess.run(["fc-list", ":", "family"],
                             capture_output=True, text=True, timeout=30).stdout
    except (OSError, subprocess.SubprocessError):
        return set()
    names = set()
    for line in out.splitlines():
        for part in line.split(","):
            part = part.strip()
            if part:
                names.add(part)
    return names


def probe(name, available):
    """字体名匹配：优先精确匹配，其次取最短的包含匹配。

    取最短是为了避免 "SimSun" 匹配到 "SimSun-ExtB" 这类扩展字形变体。
    """
    low = name.lower()

    exact = [a for a in available if a.lower() == low]
    if exact:
        return exact[0]

    subs = [a for a in available if low in a.lower() or a.lower() in low]
    if not subs:
        return None
    return min(subs, key=len)


def main():
    sysname = platform.system()
    print(f"系统：{sysname} {platform.release()}")

    if sysname == "Windows":
        available = fonts_windows()
        src = "注册表字体表"
    else:
        available = fonts_posix()
        src = "fc-list"

    if not available:
        print("未能枚举字体，请确认系统字体目录可读。", file=sys.stderr)
        return 2
    print(f"字来源：{src}（共 {len(available)} 个字体族）\n")

    has_fallback = False
    for role, candidates in ROLES:
        hit = None
        hit_name = None
        for i, cand in enumerate(candidates):
            got = probe(cand, available)
            if got:
                hit, hit_name = cand, got
                break
        if hit is None:
            print(f"{role:<16} 缺失        建议安装：{candidates[0]}")
            has_fallback = True
            continue
        if hit == candidates[0]:
            print(f"{role:<16} 首选可用    {hit_name}")
        else:
            print(f"{role:<16} 回退        {hit_name}（首选 {candidates[0]} 缺失）")
            has_fallback = True

    print()
    if has_fallback:
        print("存在回退。gongwen.sty 会自动降级并在编译日志里提示，")
        print("但降级后字形与国标有差异，交付时要说明。")
        return 1
    print("首选字体齐全，可直接按国标排版。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
