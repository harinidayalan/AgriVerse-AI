"""
Scheme Navigator - Agricultural Government Scheme Document Intelligence.
Full RAG implementation using PyMuPDF, text chunking, FAISS, and Gemini grounded responses.
"""
from pathlib import Path
from backend.rag_engine import RAGEngine
from backend.pdf_processor import PDFProcessor
from backend.text_chunker import TextChunker
from backend.gemini_service import GeminiService
from backend.database import get_db_connection

class SchemeNavigator:
    """Answers queries regarding PM-KISAN, PMFBY, and state agricultural schemes using RAG."""
    
    # Pre-seeded core agricultural schemes documentation
    DEFAULT_SCHEMES_KNOWLEDGE = [
        {
            "doc_name": "PM-KISAN Operational Guidelines",
            "page": 1,
            "text": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) is a Central Sector scheme with 100% funding from Government of India. Under the scheme an income support of ₹6,000 per year in three equal installments of ₹2,000 each is provided to all landholding farmer families across the country."
        },
        {
            "doc_name": "PM-KISAN Operational Guidelines",
            "page": 2,
            "text": "Eligibility and Exclusions for PM-KISAN: All landholder farmer families having cultivable landholding in their names are eligible. Excluded categories include institutional landholders, farmer families holding constitutional posts, former and present Ministers, MPs, MLAs, and individuals who paid income tax in last assessment year. Mandatory requirements: Aadhaar seeded bank account and land ownership records (Patta/Chitta)."
        },
        {
            "doc_name": "PMFBY Guidelines (Crop Insurance)",
            "page": 1,
            "text": "Pradhan Mantri Fasal Bima Yojana (PMFBY) aims at supporting sustainable production in agriculture sector. Premium rates payable by farmers: Maximum 2.0% of Sum Insured for all Kharif food and oilseed crops; 1.5% for all Rabi food and oilseed crops; and 5% for annual commercial/horticultural crops. The remaining premium is shared equally between Central and State Governments."
        },
        {
            "doc_name": "PMFBY Guidelines (Crop Insurance)",
            "page": 2,
            "text": "PMFBY Coverage of Risks: Comprehensive risk insurance covers localized calamities (hailstorm, landslide, inundation, cloud burst), post-harvest losses within 14 days of harvesting, and mid-season adversity due to floods or drought. Claims are directly credited to farmer bank accounts via National Crop Insurance Portal (NCIP)."
        },
        {
            "doc_name": "PMKSY (Per Drop More Crop - Drip & Sprinkler)",
            "page": 1,
            "text": "Pradhan Mantri Krishi Sinchayee Yojana (PMKSY) - Per Drop More Crop promotes micro-irrigation systems. Financial assistance: 55% subsidy for Small and Marginal farmers (holding up to 2 hectares), and 45% subsidy for Other farmers. In states like Tamil Nadu, state top-up subsidy brings total assistance up to 100% for small/marginal farmers and 75% for other farmers."
        },
        {
            "doc_name": "SMAM Agricultural Mechanization Scheme",
            "page": 1,
            "text": "Sub-Mission on Agricultural Mechanization (SMAM) provides financial assistance of 40% to 50% for procurement of agricultural machinery and equipment (tractors, power tillers, rotavators, laser land levelers, multi-crop threshers) for individual farmers. Special priority is given to SC, ST, and women farmers."
        }
    ]

    def __init__(self, rag_engine: RAGEngine = None, gemini_service: GeminiService = None):
        self.rag_engine = rag_engine or RAGEngine()
        self.gemini_service = gemini_service or GeminiService()
        self._ensure_default_knowledge()

    def _ensure_default_knowledge(self):
        """Seed default scheme knowledge if vector store is empty."""
        if self.rag_engine.index.ntotal == 0:
            print("[SchemeNavigator] Seeding official government scheme knowledge base...")
            self.rag_engine.add_chunks(self.DEFAULT_SCHEMES_KNOWLEDGE)

    def index_pdf_document(self, pdf_path: str | Path, original_filename: str) -> int:
        """Process, chunk, and index an uploaded scheme PDF."""
        pages = PDFProcessor.extract_text_by_pages(pdf_path)
        if not pages:
            return 0

        chunker = TextChunker()
        chunks = chunker.chunk_pages(pages)

        # Attach document name to each chunk
        formatted_chunks = []
        for ch in chunks:
            formatted_chunks.append({
                "doc_name": original_filename,
                "page": ch["page"],
                "text": ch["text"]
            })

        self.rag_engine.add_chunks(formatted_chunks)

        # Update uploaded documents in SQLite
        conn = get_db_connection()
        conn.execute("""
        INSERT INTO uploaded_documents (filename, original_name, file_type, file_size, doc_category, chunk_count)
        VALUES (?, ?, 'pdf', ?, 'scheme', ?)
        """, (Path(pdf_path).name, original_filename, Path(pdf_path).stat().st_size, len(formatted_chunks)))
        conn.commit()
        conn.close()

        return len(formatted_chunks)

    def query_scheme(self, question: str, language: str = "en") -> dict:
        """
        Grounded RAG question answering based on retrieved scheme chunks.
        """
        relevant_chunks = self.rag_engine.query(question, top_k=4)

        if not relevant_chunks:
            return {
                "success": False,
                "answer": "No relevant scheme documents found in the database. Please upload a government scheme PDF.",
                "citations": []
            }

        # Format context with explicit source citations
        context_text = ""
        citations = []
        for i, ch in enumerate(relevant_chunks):
            doc = ch.get("doc_name", "Scheme Document")
            page = ch.get("page", 1)
            citations.append({"document": doc, "page": page, "text_snippet": ch["text"][:150]})
            context_text += f"\n[Source {i+1}: {doc}, Page {page}]\n{ch['text']}\n"

        prompt = f"""You are AgriVerse Scheme Navigator, a specialist in Indian agricultural government schemes and subsidies.
Answer the farmer's question STRICTLY based on the provided official document excerpts below.

OFFICIAL SCHEME EXCERPTS:
{context_text}

FARMER'S QUESTION:
{question}

INSTRUCTIONS:
1. Grounding: Rely ONLY on the facts mentioned in the excerpts. If the excerpts do not contain the answer, say "This information is not specified in the uploaded scheme document."
2. Explain clearly: Eligibility criteria, financial benefits, mandatory documents, and application steps.
3. Citations: Reference the source document name and page number for key claims.
4. Language: Answer in {'Tamil (தமிழ்)' if language == 'ta' else 'English'}."""

        try:
            answer = self.gemini_service.generate_text(prompt)
            return {
                "success": True,
                "answer": answer,
                "citations": citations,
                "language": language
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"RAG query failed: {str(e)}",
                "citations": citations
            }
