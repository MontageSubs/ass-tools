#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================================
# Name: ass-font-extractor.py
# Version: 1.0.1
# Organization: MontageSubs (蒙太奇字幕组)
# Contributors: Meow P (小p)
# License: MIT License
# Source: https://github.com/MontageSubs/ass-tools/
#
# Description / 描述:
#    A diagnostic tool designed to extract embedded TrueType fonts (TTF) 
#    from ASS subtitle files using the SSA UUDecode algorithm.
#    ASS 内嵌字体提取诊断工具。使用 SSA UUDecode 算法从 ASS 字幕文件中
#    提取嵌入的 TTF 字体，用于验证优化后的字形。
#
# Usage / 用法:
#    python ass-font-extractor.py optimized_subtitle.ass
#
# Output / 输出:
#    The extracted font will be saved using the ASS file's FontName as the filename, in the working directory.
#    提取出的字体将保存为 ASS 文件中 FontName 指定的文件名，并保存在运行目录下。
#
# ============================================================================
import sys
import os

def ass_uudecode(encoded_str):
    data = [ord(c) - 33 for c in encoded_str if 33 <= ord(c) <= 96]
    out = bytearray()
    for i in range(0, len(data), 4):
        c = data[i:i+4]
        if len(c) < 2: break
        p = c + [0] * (4 - len(c))
        v = (p[0] << 18) | (p[1] << 12) | (p[2] << 6) | p[3]
        out.append((v >> 16) & 0xFF)
        if len(c) >= 3: out.append((v >> 8) & 0xFF)
        if len(c) >= 4: out.append(v & 0xFF)
    return out

def extract_font_agnostic(ass_path):
    if not os.path.exists(ass_path): return
    
    with open(ass_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
        lines = f.readlines()

    collecting = False
    current_font = None
    fonts = {}

    for line in lines:
        clean_line = line.strip()
        if clean_line.lower() == '[fonts]':
            collecting = True
            continue

        if collecting and clean_line.startswith('[') and clean_line.endswith(']'):
            collecting = False
            current_font = None
            continue
            
        if collecting:
            if clean_line.lower().startswith('fontname:'):
                current_font = clean_line.split(':', 1)[1].strip()
                fonts[current_font] = []
            elif current_font:
                fonts[current_font].append(clean_line)

    for name, data_list in fonts.items():
        encoded_raw = "".join(data_list).replace(" ", "")
        decoded = ass_uudecode(encoded_raw)
        
        safe_name = name.replace("/", "_").replace("\\", "_")
        
        with open(safe_name, 'wb') as f:
            f.write(decoded)
        
        print(f"File: {safe_name}")
        print(f"Decoded Size: {len(decoded)} bytes")
        if len(decoded) > 0:
            print(f"Header: {decoded[:4].hex().upper()}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        extract_font_agnostic(sys.argv[1])
