#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================================
# Name: ass-drawing-subsetter.py
# Version: 1.1
# Organization: MontageSubs (蒙太奇字幕组)
# Contributors: Meow P (小p)
# License: MIT License
# Source: https://github.com/MontageSubs/ass-tools/
#
# Description / 描述:
#    This script optimizes Advanced Substation Alpha (.ass) subtitle files 
#    by extracting vector drawing commands (\p1, etc.) and converting them 
#    into a subsetted, embedded TrueType font (TTF) to significantly reduce 
#    file size and improve drawing command reuse, improving compatibility
#    on lower-performance playback devices (e.g., Android TV).
#    本脚本用于优化 ASS 字幕文件，通过提取绘图指令（\p1 等）并将其转换为
#    子集化的嵌入式 TrueType 字体 (TTF)，从而大幅减少文件体积并提高
#    绘图指令的复用率，提升在性能较弱播放设备（如 Android TV）上的兼容性。
#
# Features:
#    - Extracts unique drawing shapes to prevent redundant data.
#    - Automatically generates a minimal TTF font using FontForge.
#    - Subsets the font using FontTools to ensure the smallest file size.
#    - Encodes the font using the SSA-standard UUEncode algorithm.
#    - Replace drawing tags with lightweight font characters.
#
# 功能:
#    - 提取唯一的绘图形状，防止数据冗余。
#    - 使用 FontForge 自动生成极简 TTF 字体。
#    - 使用 FontTools 对字体进行子集化压缩，确保最小文件体积。
#    - 使用 SSA 标准的 UUEncode 算法对字体进行编码。
#    - 用轻量字体字符替换绘图标签。
#
# Dependencies / 依赖:
#    - FontForge (Python extension)
#    - FontTools (pip install fonttools)
#
# Usage / 用法:
#    python ass-drawing-subsetter.py input.ass
#
# Output / 输出:
#    The optimized file will be saved as: <input>_optimized.ass
#    优化后的文件将保存为：<原文件名>_optimized.ass
#
# Notes / 注意事项:
#    - The optimized ASS typesetting may experience size or position shifts. 
#      Users should manually inspect the output for accuracy.
#    - 转换后的 ASS 特效可能会出现大小和位置偏移，使用者需手动检查最终效果。
#
# ============================================================================
import re
import os
import sys
import io
import tempfile

MISSING_DEPS = []
try:
    import fontforge
except ImportError:
    MISSING_DEPS.append("fontforge (Python extension)")
try:
    from fontTools.subset import Subsetter, Options
    from fontTools.ttLib import TTFont
except ImportError:
    MISSING_DEPS.append("fonttools (pip install fonttools)")

if MISSING_DEPS:
    print("-" * 50)
    print("ERROR: Missing dependencies detected! | 错误: 未检测到依赖库！")
    for dep in MISSING_DEPS:
        print(f"  - {dep}")
    print("-" * 50)
    print("HOW TO FIX | 解决方法:")
    print("1. pip install fonttools")
    print("2. Ubuntu/Debian: sudo apt install python3-fontforge")
    print("   MacOS: brew install fontforge")
    print("   Windows: Use FontForge build with Python support.")
    print("-" * 50)
    sys.exit(1)

FONT_NAME = "ASSDrawSubset"
START_CHAR = 'a'

def ass_uuencode(data):
    res = []
    for i in range(0, len(data), 3):
        chunk = data[i:i+3]
        padding = 3 - len(chunk)
        if padding > 0:
            chunk += b'\x00' * padding
        v = (chunk[0] << 16) | (chunk[1] << 8) | chunk[2]
        chars = [
            chr(((v >> 18) & 0x3f) + 33),
            chr(((v >> 12) & 0x3f) + 33),
            chr(((v >> 6) & 0x3f) + 33),
            chr((v & 0x3f) + 33)
        ]
        if padding == 1:
            chars[-1] = ""
        elif padding == 2:
            chars[-1] = ""
            chars[-2] = ""
        res.extend(chars)
    return "".join(res)

class ASSDrawingSubsetter:
    def __init__(self, input_ass):
        self.input_ass = input_ass
        self.drawing_to_char = {} 
        self.drawings = []        
        self.content = ""

    def load_and_extract(self):
        if not os.path.exists(self.input_ass):
            print(f"Error: File '{self.input_ass}' not found. | 错误: 找不到文件 '{self.input_ass}'。")
            sys.exit(1)

        with open(self.input_ass, 'r', encoding='utf-8-sig', errors='ignore') as f:
            self.content = f.read()
        
        pattern = r'(\{[^}]*?\\p[1-9][^}]*\})(.*?)(\{\\p0\})'
        matches = re.findall(pattern, self.content, re.DOTALL | re.IGNORECASE)
        
        seen = {}
        for start_tag, drawing_data, end_tag in matches:
            clean_d = " ".join(drawing_data.split()).strip()
            if clean_d and clean_d not in seen:
                char = chr(ord(START_CHAR) + len(seen))
                seen[clean_d] = char
                self.drawings.append(clean_d)
        
        self.drawing_to_char = seen
        print(f"Extracted {len(self.drawings)} unique shapes. | 提取到 {len(self.drawings)} 个唯一形状。")

    def create_subset_ttf(self):
        # Font metrics: em square = 1024 units, full square from y=0 to y=1024
        EM     = 1024    # units per em
        TARGET = 820     # max glyph extent (leaves ~10% margin on each side)
        MARGIN = (EM - TARGET) / 2  # ~102 units of padding per side

        font = fontforge.font()
        font.fontname   = FONT_NAME
        font.familyname = FONT_NAME
        font.fullname   = FONT_NAME
        font.em         = EM
        # Put the entire em square above the baseline so y ∈ [0, EM]
        font.ascent  = EM
        font.descent = 0

        with tempfile.TemporaryDirectory() as tmp_dir:
            for path_data, char_val in self.drawing_to_char.items():
                cp   = ord(char_val)
                char = font.createChar(cp)

                svg_path = path_data.replace('b', 'C').replace('m', 'M').replace('l', 'L')
                svg_file = os.path.join(tmp_dir, f"{cp}.svg")
                with open(svg_file, 'w') as f:
                    f.write(
                        f'<svg xmlns="http://www.w3.org/2000/svg">'
                        f'<path d="{svg_path}"/></svg>'
                    )

                char.importOutlines(svg_file)

                bbox    = char.boundingBox()   # (xmin, ymin, xmax, ymax)
                glyph_w = bbox[2] - bbox[0]
                glyph_h = bbox[3] - bbox[1]

                if glyph_w <= 0 or glyph_h <= 0:
                    char.width = EM
                    continue

                # ── Step 1: move bounding-box origin to (0, 0) ──────────────
                char.transform([1, 0, 0, 1, -bbox[0], -bbox[1]])

                # ── Step 2: uniform scale so the LARGER side == TARGET ──────
                #    This preserves aspect ratio and guarantees neither
                #    dimension overflows the em square.
                scale = TARGET / max(glyph_w, glyph_h)
                char.transform([scale, 0, 0, scale, 0, 0])

                # ── Step 3: center inside the em square ──────────────────────
                scaled_w = glyph_w * scale
                scaled_h = glyph_h * scale
                offset_x = MARGIN + (TARGET - scaled_w) / 2   # horizontal center
                offset_y = MARGIN + (TARGET - scaled_h) / 2   # vertical center
                char.transform([1, 0, 0, 1, offset_x, offset_y])

                char.width = EM
            
            font.selection.all()
            font.correctDirection()
            temp_ttf = os.path.join(tmp_dir, "raw.ttf")
            font.generate(temp_ttf)
            
            with TTFont(temp_ttf) as tt_font:
                options = Options()
                options.subset_names = False 
                subsetter = Subsetter(options=options)
                subsetter.populate(text="".join(self.drawing_to_char.values()))
                subsetter.subset(tt_font)
                out_io = io.BytesIO()
                tt_font.save(out_io)
                return out_io.getvalue()

    def rewrite_ass(self, ttf_data):
        def replace_callback(match):
            start_tag = match.group(1)
            drawing_data = match.group(2)
            clean_d = " ".join(drawing_data.split()).strip()
            char = self.drawing_to_char.get(clean_d)

            if char:
                new_start_tag = re.sub(r'\\p[1-9]', r'\\fn%s\\p0' % FONT_NAME, start_tag, flags=re.I)
                return f"{new_start_tag}{char}"
            return match.group(0)

        final_text = re.sub(r'(\{[^}]*?\\p[1-9][^}]*\})(.*?)(\{\\p0\})', 
                            replace_callback, self.content, flags=re.DOTALL | re.IGNORECASE)

        final_text = re.sub(r'\n\[Fonts\].*', '', final_text, flags=re.DOTALL).strip()
        
        encoded = ass_uuencode(ttf_data)
        font_block = f"\n\n[Fonts]\nfontname: {FONT_NAME}_0.ttf\n"
        for i in range(0, len(encoded), 80):
            font_block += encoded[i:i+80] + "\n"
        
        return final_text + font_block

    def run(self, output_path):
        self.load_and_extract()
        if not self.drawings:
            print("No drawing tags found. | 未发现绘图标签。")
            return
        
        print("Generating subsetted font... | 正在生成子集化字体...")
        ttf_data = self.create_subset_ttf()
        
        print("Rewriting dialogue lines... | 正在重写 Dialogue 行...")
        final_ass = self.rewrite_ass(ttf_data)
        
        with open(output_path, 'w', encoding='utf-8-sig') as f:
            f.write(final_ass)
        print(f"Optimization complete! | 处理完成！")
        print(f"Output saved to: {output_path} | 文件保存至: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ass-drawing-subsetter.py <input.ass>")
        print("用法: python ass-drawing-subsetter.py <输入文件.ass>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = input_file.replace(".ass", "_optimized.ass")
    
    subsetter = ASSDrawingSubsetter(input_file)
    subsetter.run(output_file)
    
