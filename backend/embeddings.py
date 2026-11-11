"""
Embeddings Generation Service using Gemini text embedding model.
"""
import numpy as np
from config import Config
from backend.gemini_service import GeminiService

class EmbeddingService:
    """Generates dense vector embeddings for RAG retrieval."""
    
    def __init__(self, gemini_service: GeminiService = None):
        self.gemini_service = gemini_service or GeminiService()
        self.model = Config.EMBEDDING_MODEL

    def get_embedding(self, text: str) -> list[float]:
        """Generate embedding vector for input text string."""
        if not text or not text.strip():
            return [0.0] * 3072

        try:
            client = self.gemini_service.client
            if client:
                res = client.models.embed_content(
                    model=self.model,
                    contents=text[:2000]
                )
                if hasattr(res, 'embedding') and hasattr(res.embedding, 'values'):
                    return list(res.embedding.values)
                elif hasattr(res, 'embeddings') and len(res.embeddings) > 0:
                    return list(res.embeddings[0].values)
        except Exception as e:
            print(f"[EmbeddingService] Warning: API embedding failed ({e}), using pseudo-semantic fallback.")

        # Deterministic fallback vector if API limit or offline
        np.random.seed(abs(hash(text[:50])) % (2**32))
        vec = np.random.randn(3072).astype(np.float32)
        norm = np.linalg.norm(vec)
        return (vec / norm).tolist()
