# ASS Tools

**[中文](./README.md) | English**

ASS Tools is a collection of utilities for processing and optimizing Advanced Substation Alpha (.ass) subtitle files.

Developed and maintained by **MontageSubs**, this toolkit focuses on advanced subtitle effects, specifically optimizing vector drawing tags and managing embedded resources.

## File Structure

```
ass-tools/
├── scripts/
│   └── python/              # Python Scripts
│       ├── ass-drawing-subsetter.py
│       └── ass-font-extractor.py
├── LICENSE                  # MIT License
└── README.md                # Chinese Documentation
└── README.en.md             # English Documentation
```

## Scripts

### [`ass-drawing-subsetter.py`](scripts/python/ass-drawing-subsetter.py)

**Description**

Extracts vector drawing commands (`\p1`, etc.) from an ASS file and converts them into a subsetted, embedded TrueType font (TTF).

- **Size Optimization**: Replaces heavy and redundant drawing tags with lightweight font character calls.
- **Subsetting**: Uses FontTools to ensure the smallest possible font file size by including only required glyphs.
- **Automation**: Handles SSA-standard UUEncoding and updates the `[Fonts]` section automatically.

**Usage**
```bash
# Requirements: pip install fonttools & FontForge (with Python support)
python scripts/python/ass-drawing-subsetter.py input.ass
```
*Note: The optimized file will be saved as `<filename>_optimized.ass`.*

### [`ass-font-extractor.py`](scripts/python/ass-font-extractor.py)

**Description**

A diagnostic tool designed to extract and decode embedded TrueType fonts (TTF) from ASS files using the SSA UUDecode algorithm.

- **Validation**: Useful for verifying glyphs after optimization.
- **General Extraction**: Decodes and restores any font embedded in the `[Fonts]` section.

**Usage**
```bash
python scripts/python/ass-font-extractor.py optimized_subtitle.ass
```

## Dependencies
- **Python 3.x**
- **FontForge** (with Python extension)
- **FontTools** (`pip install fonttools`)

## Community

Join our discussion groups for subtitle tech support, feedback, or collaboration:

- **Telegram**: [MontageSubs](https://t.me/+HCWwtDjbTBNlM2M5)
- **IRC**: [#MontageSubs](https://web.libera.chat/#MontageSubs) (Synced with Telegram)

## License

Source code and documentation are licensed under the [MIT License](./LICENSE).

---

<div align="center">

**MontageSubs (蒙太奇字幕组)**  
“Powered by Love ❤️ 用爱发电”

</div>
