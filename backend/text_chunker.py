"""
Text Chunker for Document Intelligence and RAG Pipeline.
"""
from config import Config

class TextChunker:
    """Splits document text into overlapping semantic chunks."""
    
    def __init__(self, chunk_size: int = Config.CHUNK_SIZE, overlap: int = Config.CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_pages(self, pages: list[dict], doc_id: int = None) -> list[dict]:
        """Produce indexed chunks from list of page dicts."""
        chunks = []
        chunk_id = 1
        for page in pages:
            text = page["text"]
            page_no = page["page"]
            start = 0
            while start < len(text):
                end = min(start + self.chunk_size, len(text))
                chunk_text = text[start:end].strip()
                if chunk_text:
                    chunks.append({
                        "chunk_id": chunk_id,
                        "doc_id": doc_id,
                        "page": page_no,
                        "text": chunk_text
                    })
                    chunk_id += 1
                start += (self.chunk_size - self.overlap)
        return chunks
