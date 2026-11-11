"""
PDF Document Processor for AgriVerse AI.
Extracts clean, normalized text and metadata from PDF files using PyMuPDF.
"""
from pathlib import Path

class PDFProcessor:
    """Extracts text and page structure from agricultural PDF documents."""
    
    @staticmethod
    def extract_text_by_pages(pdf_path: str | Path) -> list[dict]:
        """Extract text page by page with page numbering."""
        import fitz
        doc = fitz.open(str(pdf_path))
        pages_content = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").strip()
            if text:
                pages_content.append({
                    "page": page_num + 1,
                    "text": text
                })
        doc.close()
        return pages_content
