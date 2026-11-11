"""
CropMatch AI - Multi-Criteria Agronomic Crop Recommendation Engine.
Matches soil type, pH, seasonal climate, water availability, and crop rotation
to generate evidence-aware crop options.
"""
from backend.gemini_service import GeminiService

class CropRecommender:
    """Recommends suitable crops based on agronomic parameters."""
    
    def __init__(self, gemini_service: GeminiService = None):
        self.gemini_service = gemini_service or GeminiService()

    def recommend(self, location: str, soil_type: str, ph: float, season: str, water: str, prev_crop: str = "", language: str = "en") -> dict:
        """Generate crop recommendation report using Gemini."""
        prompt = f"""You are AgriVerse CropMatch AI, an expert agricultural scientist.
Recommend 3 to 4 the most suitable crops for a farmer with these conditions:
- Farm Location: {location}
- Soil Type: {soil_type}
- Soil pH: {ph}
- Farming Season: {season}
- Water Availability: {water}
- Previous Crop Harvested: {prev_crop or 'None'}

For EACH recommended crop, provide:
1. Crop Name & Recommended Variety (e.g. CO-51, IR-64, Groundnut TMV-13, Blackgram VBN-8).
2. Key Reasons for Recommendation.
3. Soil & pH Suitability Explanation.
4. Water & Irrigation Requirements.
5. Crop Rotation Advantage (especially considering previous crop: {prev_crop}).
6. Key Agronomic Limitations / Risks to Monitor.

Language: Reply in {'Tamil (தமிழ்)' if language == 'ta' else 'English'}.
Maintain evidence-awareness: Do not guarantee yields or profitability."""

        try:
            advice = self.gemini_service.generate_text(prompt)
            return {
                "success": True,
                "recommendations": advice,
                "parameters": {
                    "location": location,
                    "soil_type": soil_type,
                    "ph": ph,
                    "season": season,
                    "water": water,
                    "previous_crop": prev_crop
                },
                "language": language
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"CropMatch recommendation failed: {str(e)}"
            }
