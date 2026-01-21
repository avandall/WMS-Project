# WMS Architecture Diagrams - PNG Export Guide

## 📁 Contents

This folder contains **9 Mermaid diagram files** extracted from the main documentation:

1. **01-system-architecture.mmd** - Full system overview with all layers
2. **02-document-transaction-flow.mmd** - ACID transaction sequence
3. **03-database-schema.mmd** - Entity relationship diagram
4. **04-clean-architecture.mmd** - Layer separation and dependencies
5. **05-request-lifecycle.mmd** - Request flow with security checks
6. **06-file-structure.mmd** - Project folder organization
7. **07-import-document-flow.mmd** - Import document creation sequence
8. **08-index-performance.mmd** - Database index performance comparison
9. **09-security-architecture.mmd** - Security components mindmap

## 🎨 Export Methods

### Method 1: Automated Batch Export (Recommended) ✅

Run the PowerShell script to export all diagrams at once:

```powershell
cd diagrams
.\export-all.ps1
```

**Output**: All PNG files will be in `diagrams/png/` folder at 2400x1600px resolution.

### Method 2: Manual Export (Individual Diagrams)

Export a single diagram with custom settings:

```powershell
# Basic export
mmdc -i 01-system-architecture.mmd -o output.png

# High-resolution export (for printing)
mmdc -i 01-system-architecture.mmd -o output.png -w 2400 -H 1600 -b white

# Extra large (poster size)
mmdc -i 01-system-architecture.mmd -o output.png -w 4000 -H 3000 -b white
```

### Method 3: Online Tool (No Installation) 🌐

1. Open https://mermaid.live/
2. Copy content from any `.mmd` file
3. Paste into the editor
4. Click **"PNG"** button to download
5. Adjust size with the zoom slider before export

### Method 4: VS Code + Extension

1. Install: **Markdown Preview Mermaid Support**
2. Create a temporary `.md` file with this content:
   ````markdown
   ```mermaid
   [paste .mmd file content here]
   ```
   ````
3. Open markdown preview (`Ctrl+Shift+V`)
4. Right-click diagram → **"Copy Image"** or **"Save Image"**

## 🖨️ Printing Recommendations

### For Documents/Reports
- **Resolution**: 2400x1600px (default from export-all.ps1)
- **Paper Size**: A4 or Letter (landscape orientation)
- **DPI**: 300 DPI for professional printing
- **Format**: PNG with white background

### For Presentations
- **Resolution**: 1920x1080px (Full HD)
- **Background**: Transparent or white
- **Format**: PNG or SVG

### For Posters
- **Resolution**: 4000x3000px or larger
- **Paper Size**: A3, A2, or larger
- **DPI**: 300 DPI minimum
- **Format**: High-quality PNG or PDF

## 📐 Size Presets

```powershell
# Standard (screens)
mmdc -i diagram.mmd -o output.png -w 1920 -H 1080

# Print-ready (A4)
mmdc -i diagram.mmd -o output.png -w 2400 -H 1600

# Large format (poster)
mmdc -i diagram.mmd -o output.png -w 4000 -H 3000

# Ultra-high resolution
mmdc -i diagram.mmd -o output.png -w 6000 -H 4000
```

## 🎯 Quick Start

**Just want PNG files?** Run this:

```powershell
cd d:\Hoc\weekend\WMS\diagrams
.\export-all.ps1
```

All PNG files will be ready in the `png/` subfolder! 🎉

## 🔧 Troubleshooting

### "mmdc: command not found"

Install Mermaid CLI:
```powershell
npm install -g @mermaid-js/mermaid-cli
```

### Chromium download fails

Use manual Puppeteer installation:
```powershell
npm install -g @mermaid-js/mermaid-cli --force
```

### Export is too small/large

Adjust width (`-w`) and height (`-H`) parameters:
```powershell
mmdc -i diagram.mmd -o output.png -w [WIDTH] -H [HEIGHT]
```

### Background is transparent

Add white background:
```powershell
mmdc -i diagram.mmd -o output.png -b white
```

## 📚 Additional Resources

- **Mermaid Documentation**: https://mermaid.js.org/
- **Mermaid Live Editor**: https://mermaid.live/
- **Mermaid CLI GitHub**: https://github.com/mermaid-js/mermaid-cli

---

**Ready to export?** Run `.\export-all.ps1` now! 🚀
