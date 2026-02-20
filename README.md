# ASS Tools

**中文 | [English](./README.en.md)**

ASS Tools 是由 蒙太奇字幕组 (MontageSubs) 开发的高级 SubStation Alpha (.ass) 字幕处理工具集合。

本仓库专注于处理 ASS 字幕中的复杂特效与资源优化，例如将矢量绘图指令（Drawing Tags）转换为子集化嵌入字体，以显著减小文件体积并提升渲染兼容性。

## 文件结构

```
ass-tools/
├── scripts/
│   └── python/              # Python 脚本
│       ├── ass-drawing-subsetter.py
│       └── ass-font-extractor.py
├── LICENSE                  # MIT 许可协议
└── README.md                # 中文说明
└── README.en.md             # 英文说明
```

## 脚本说明

### [`ass-drawing-subsetter.py`](scripts/python/ass-drawing-subsetter.py)

**功能**

将 ASS 文件中的矢量绘图指令（`\p1` 等）提取并转换为子集化的内嵌 TrueType 字体 (TTF)。

- **体积压缩**：将重复、庞大的绘图数据替换为极小的字体字符，显著减小文件体积。
- **子集化**：利用 FontTools 仅保留必要的字形，确保生成的字体文件实现极致压缩。
- **自动处理**：自动进行 SSA 标准的 UUEncode 编码并注入到字幕文件的 `[Fonts]` 段落中。

**用法**
```bash
$ python ass-drawing-subsetter.py input.ass
```
*注：优化后的文件将保存为 `<文件名>_optimized.ass`。*

### [`ass-font-extractor.py`](scripts/python/ass-font-extractor.py)

**功能**

ASS 内嵌字体提取与诊断工具。使用 SSA UUDecode 算法从字幕文件中还原 TTF 字体。

- **验证工具**：用于检查 `ass-drawing-subsetter` 生成的字体是否正确。
- **通用提取**：支持从任何符合标准的 ASS 文件中提取并还原已嵌入的字体文件。

**用法**
```bash
$ python ass-font-extractor.py optimized_subtitle.ass
```

## 环境依赖
- **Python 3.x**
- **FontForge** (需包含 Python 扩展)
- **FontTools** (`pip install fonttools`)

## 社群

欢迎加入我们的交流群，讨论字幕技术、反馈建议或参与制作：

- **Telegram**：[蒙太奇字幕组电报群](https://t.me/+HCWwtDjbTBNlM2M5)
- **IRC**：[#MontageSubs](https://web.libera.chat/#MontageSubs)（与 Telegram 互联）

## 许可协议

本仓库的源代码与文档遵循 [MIT 许可协议](./LICENSE) 授权。

---

<div align="center">

**蒙太奇字幕组 (MontageSubs)**  
“用爱发电 ❤️ Powered by Love”

</div>
