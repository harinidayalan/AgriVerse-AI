"""
Plant Doctor AI - Multimodal Image Analyzer for Leaf Health & Disease Symptoms.
Utilizes Google Gemini multimodal vision capabilities to inspect crop foliage photographs.
"""
from pathlib import Path
from PIL import Image
from backend.gemini_service import GeminiService
from config import Config

class PlantDoctorAnalyzer:
    """Analyzes crop leaf images with Google Gemini vision model."""
    
    SYSTEM_INSTRUCTION = """You are AgriVerse Plant Doctor AI, an expert botanical pathologist and agronomy specialist.
Your objective is to inspect leaf photographs submitted by farmers and provide evidence-aware diagnostic guidance.

CRITICAL INSTRUCTIONS:
1. Uncertainty & Limitations: You CANNOT confirm a plant disease diagnosis definitively from an image alone. You must clearly state visible symptoms and probable causes, and recommend lab testing or physical inspection by an agricultural officer for confirmation.
2. Structure your assessment clearly:
   - Visible Foliar Symptoms: Describe lesion shapes, chlorosis, necrosis, curling, discoloration, or pustules.
   - Possible Causes: List top 2-3 suspected pathogens (fungal, bacterial, viral) or physiological stressors (nitrogen deficiency, water stress, sunburn).
   - Eco-friendly / Organic Remedies: Recommend neem cake, Trichoderma viride, Pseudomonas fluorescens, Jeevamrutham, or pruning.
   - Integrated Pest/Chemical Management: Mention conventional options only if severe, with mandatory safety dosage precautions.
   - Preventive Agronomic Practices: Crop rotation, spacing, drainage, resistant varieties.
3. Language: Keep explanations simple, supportive, and accessible for farmers. If user asks in Tamil or selected Tamil language, reply in Tamil."""

    def __init__(self, gemini_service: GeminiService = None):
        self.gemini_service = gemini_service or GeminiService()

    def analyze_leaf_image(self, image_path: str | Path, user_notes: str = "", language: str = "en") -> dict:
        """
        Inspect leaf image using Gemini multimodal vision.
        """
        img_path = Path(image_path)
        if not img_path.exists():
            return {"success": False, "error": "Image file not found."}

        try:
            pil_image = Image.open(img_path)
            # Convert to RGB if PNG with alpha or palette
            if pil_image.mode not in ("RGB", "L"):
                pil_image = pil_image.convert("RGB")

            prompt = (
                f"Examine this agricultural leaf photograph carefully. "
                f"Farmer's notes / Crop name: {user_notes if user_notes else 'Unspecified crop'}. "
                f"Please provide your diagnostic inspection in {'Tamil (தமிழ்)' if language == 'ta' else 'English'}."
            )

            client = self.gemini_service.client
            if not client:
                return {
                    "success": False,
                    "error": "Gemini API client not initialized. Check your GEMINI_API_KEY in .env."
                }

            # Try primary model then fallbacks
            models_to_try = [
                Config.GEMINI_MODEL,
                "gemini-3.5-flash-lite",
                "gemini-3.1-flash-lite",
                "gemini-3.8-flash"
            ]

            from google.genai import types
            config = types.GenerateContentConfig(
                system_instruction=self.SYSTEM_INSTRUCTION,
                temperature=0.3
            )

            response = None
            last_err = None
            for model in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=model,
                        contents=[pil_image, prompt],
                        config=config
                    )
                    if response and response.text:
                        break
                except Exception as e:
                    last_err = e
                    continue

            if not response or not response.text:
                raise RuntimeError(f"All vision models failed. Last error: {last_err}")

            return {
                "success": True,
                "analysis": response.text.strip(),
                "image_filename": img_path.name,
                "language": language,
                "disclaimer": "AI image analysis provides symptom awareness, not a certified laboratory diagnosis. Consult your local KVK for critical outbreaks."
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to analyze image: {str(e)}"
            }
