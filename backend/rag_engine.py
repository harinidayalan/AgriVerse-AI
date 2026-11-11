"""
FAISS Vector Database & RAG Retrieval Engine for AgriVerse AI.
Indexes chunked agricultural documents and retrieves nearest neighbors using L2 distance.
"""
import os
import pickle
from pathlib import Path
import numpy as np
import faiss
from config import Config
from backend.embeddings import EmbeddingService

class RAGEngine:
    """FAISS-backed similarity search and source attribution pipeline."""
    
    def __init__(self, embedding_service: EmbeddingService = None):
        self.embedding_service = embedding_service or EmbeddingService()
        self.dimension = 3072  # Matches gemini-embedding-001
        self.index_file = Config.VECTOR_STORE_DIR / "faiss_index.bin"
        self.meta_file = Config.VECTOR_STORE_DIR / "faiss_meta.pkl"
        self.index = None
        self.chunks = []
        self._load_or_create_index()

    def _load_or_create_index(self):
        """Load persistent FAISS index or create empty one."""
        Config.ensure_directories()
        if self.index_file.exists() and self.meta_file.exists():
            try:
                self.index = faiss.read_index(str(self.index_file))
                with open(self.meta_file, "rb") as f:
                    self.chunks = pickle.load(f)
                return
            except Exception as e:
                print(f"[RAGEngine] Rebuilding index due to load error: {e}")

        self.index = faiss.IndexFlatL2(self.dimension)
        self.chunks = []

    def save_index(self):
        """Persist FAISS index and chunk metadata to disk."""
        Config.ensure_directories()
        faiss.write_index(self.index, str(self.index_file))
        with open(self.meta_file, "wb") as f:
            pickle.dump(self.chunks, f)

    def add_chunks(self, new_chunks: list[dict]):
        """
        Embed and index a list of text chunks.
        Each chunk: {"text": str, "doc_name": str, "page": int, "doc_id": int}
        """
        if not new_chunks:
            return

        embeddings = []
        for ch in new_chunks:
            emb = self.embedding_service.get_embedding(ch["text"])
            embeddings.append(emb)

        arr = np.array(embeddings, dtype=np.float32)
        if arr.shape[1] != self.dimension:
            # Recreate index if dimension differs
            self.dimension = arr.shape[1]
            self.index = faiss.IndexFlatL2(self.dimension)
            self.chunks = []

        self.index.add(arr)
        self.chunks.extend(new_chunks)
        self.save_index()

    def query(self, question: str, top_k: int = Config.TOP_K_RESULTS) -> list[dict]:
        """Search top-K most similar text chunks for question."""
        if not self.chunks or self.index.ntotal == 0:
            return []

        q_emb = self.embedding_service.get_embedding(question)
        q_arr = np.array([q_emb], dtype=np.float32)

        actual_k = min(top_k, self.index.ntotal)
        distances, indices = self.index.search(q_arr, actual_k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.chunks) and idx >= 0:
                chunk_copy = dict(self.chunks[idx])
                chunk_copy["distance"] = float(dist)
                results.append(chunk_copy)
        return results

    def clear(self):
        """Reset the vector index."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.chunks = []
        if self.index_file.exists(): self.index_file.unlink()
        if self.meta_file.exists(): self.meta_file.unlink()
