# core/pdf_fonts.py
from pathlib import Path
from xhtml2pdf.default import DEFAULT_FONT
import xhtml2pdf.pisa as pisa

FONT_DIR = Path(__file__).resolve().parent.parent / 'static' / 'fonts'

def link_callback(uri, rel):
    """
    Convert font URIs to local filesystem paths for xhtml2pdf.
    """
    # Map CSS font references to actual files
    if 'NotoNaskhArabic' in uri:
        return str(FONT_DIR / 'NotoNaskhArabic-Regular.ttf')
    return uri