#!/usr/bin/env python3
"""
Smart File → Markdown Converter
Routes each file type to the best conversion method for quality + token efficiency.

Decision tree:
  PDF  → pymupdf (text-based) or pymupdf+OCR (scanned)
  DOCX/XLSX/PPTX/HTML → markitdown
  Images → pymupdf OCR (if tesseract) or markitdown fallback
  Audio → markitdown (transcribe)

Usage: python smart_convert.py <file_path> [output_dir]
"""

import sys
import os
import re
import subprocess
from pathlib import Path
from datetime import datetime

# ── Configuration ──────────────────────────────────────────────
TEXT_DENSITY_THRESHOLD = 50   # chars/page — below this → treat as scanned
OCR_DPI = 300                  # DPI for OCR rendering
OCR_LANG = "eng+tha"          # English + Thai

# ── Helpers ────────────────────────────────────────────────────

def _get_tesseract_path():
    """Find tesseract.exe on Windows."""
    candidates = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    # Try PATH
    result = subprocess.run(["where", "tesseract"], capture_output=True, text=True, shell=True)
    if result.returncode == 0:
        return result.stdout.strip().split("\n")[0]
    return None

def _install_deps():
    """Ensure required packages are installed."""
    deps = {
        "pymupdf": "pymupdf",
        "markitdown": "markitdown[all]",
        "pytesseract": "pytesseract",
        "PIL": "Pillow",
    }
    for module, package in deps.items():
        try:
            __import__(module)
        except ImportError:
            subprocess.run(["uv", "pip", "install", package], check=True, capture_output=True)

def _detect_scanned_pdf(doc) -> bool:
    """Check if a PDF is scanned (image-based) by sampling first 3 pages."""
    total_chars = 0
    pages_checked = min(3, doc.page_count)
    for i in range(pages_checked):
        total_chars += len(doc[i].get_text().strip())
    avg_chars = total_chars / pages_checked
    return avg_chars < TEXT_DENSITY_THRESHOLD, avg_chars

# ── Converters ─────────────────────────────────────────────────

def _convert_pdf_pymupdf(file_path: str, output_path: str) -> dict:
    """Convert PDF with pymupdf — clean Thai, no cid artifacts."""
    import pymupdf
    doc = pymupdf.open(file_path)
    total_pages = doc.page_count

    is_scanned, avg_chars = _detect_scanned_pdf(doc)

    lines = []
    lines.append(f"# Converted from: {os.path.basename(file_path)}")
    lines.append(f"# Pages: {total_pages} | Method: {'OCR (scanned)' if is_scanned else 'pymupdf (text-based)'}")
    lines.append(f"# Converted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    tesseract_path = _get_tesseract_path()

    for i in range(total_pages):
        page = doc[i]
        page_num = i + 1

        if is_scanned:
            if tesseract_path:
                # OCR route: render page to image, then OCR
                import pytesseract
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
                pix = page.get_pixmap(dpi=OCR_DPI)
                from PIL import Image
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text = pytesseract.image_to_string(img, lang=OCR_LANG)
            else:
                # No tesseract — fall back to pymupdf text + mark warning
                text = page.get_text()
                if len(text.strip()) < 10:
                    text = "[OCR not available — install tesseract for scanned PDFs]"
        else:
            text = page.get_text()

        if text.strip():
            lines.append(f"## Page {page_num}")
            lines.append("")
            lines.append(text.strip())
            lines.append("")

    doc.close()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return {
        "method": "pymupdf-ocr" if is_scanned else "pymupdf",
        "pages": total_pages,
        "is_scanned": is_scanned,
        "avg_chars_per_page": round(avg_chars, 1),
        "output_chars": sum(len(l) for l in lines),
        "output_path": output_path,
    }

def _convert_markitdown(file_path: str, output_path: str) -> dict:
    """Convert with markitdown — best for Office docs, HTML."""
    from markitdown import MarkItDown
    md = MarkItDown()
    result = md.convert(file_path)
    text = result.text_content

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    return {
        "method": "markitdown",
        "pages": None,
        "is_scanned": False,
        "avg_chars_per_page": None,
        "output_chars": len(text),
        "output_path": output_path,
    }

def _convert_image_ocr(file_path: str, output_path: str) -> dict:
    """Convert image with OCR (tesseract) or markitdown fallback."""
    tesseract_path = _get_tesseract_path()

    if tesseract_path:
        import pytesseract
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        from PIL import Image
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img, lang=OCR_LANG)

        lines = [
            f"# OCR from: {os.path.basename(file_path)}",
            f"# Method: pytesseract ({OCR_LANG})",
            f"# Converted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            text.strip() if text.strip() else "[No text detected in image]",
        ]
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return {
            "method": "pytesseract",
            "pages": None,
            "is_scanned": True,
            "avg_chars_per_page": None,
            "output_chars": len(text),
            "output_path": output_path,
        }
    else:
        # Fallback to markitdown (EXIF + description)
        return _convert_markitdown(file_path, output_path)

# ── Router ─────────────────────────────────────────────────────

def smart_convert(file_path: str, output_dir: str = None) -> dict:
    """
    Route file to the best converter and return summary dict.
    """
    file_path = os.path.abspath(file_path)
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}

    ext = os.path.splitext(file_path)[1].lower()
    base = os.path.splitext(os.path.basename(file_path))[0]

    if output_dir is None:
        output_dir = os.path.dirname(file_path)
    output_path = os.path.join(output_dir, f"{base}.md")

    # Ensure deps
    _install_deps()

    # Route
    if ext == ".pdf":
        result = _convert_pdf_pymupdf(file_path, output_path)
    elif ext in (".docx", ".pptx", ".xlsx", ".html", ".htm"):
        result = _convert_markitdown(file_path, output_path)
    elif ext in (".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"):
        result = _convert_image_ocr(file_path, output_path)
    elif ext in (".mp3", ".wav", ".m4a", ".ogg"):
        result = _convert_markitdown(file_path, output_path)
    elif ext == ".zip":
        result = _convert_markitdown(file_path, output_path)
    else:
        return {"error": f"Unsupported format: {ext}", "hint": "Use for: PDF, DOCX, PPTX, XLSX, HTML, images, audio, ZIP"}

    # Add source info
    result["source"] = file_path
    result["source_size_kb"] = round(os.path.getsize(file_path) / 1024, 1)

    return result

# ── CLI ────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python smart_convert.py <file_path> [output_dir]")
        sys.exit(1)

    file_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    import json
    result = smart_convert(file_path, output_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
