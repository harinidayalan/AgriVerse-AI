"""
AquaSmart - Smart Irrigation & Water Management Advisor.
Calculates crop water requirements, critical moisture stress stages,
and drip irrigation schedules.
"""
from backend.gemini_service import GeminiService

class IrrigationAdvisor:
    """Smart water management and irrigation advisor."""
    
    def __init__(self, gemini_service: GeminiService = None):
        self.gemini_service = gemini_service or GeminiService()

    def advise(self, crop: str, growth_stage: str, soil_type: str, irrigation_system: str, water_source: str, language: str = "en") -> dict:
        prompt = f"""You are AgriVerse AquaSmart Advisor.
Provide precise irrigation and water conservation advice for:
- Crop: {crop}
- Growth Stage: {growth_stage}
- Soil Type: {soil_type}
- Irrigation System: {irrigation_system}
- Water Source Availability: {water_source}

Include:
1. Stage-Specific Water Requirement (liters/day or depth in cm).
2. Critical Growth Stages where water stress causes severe yield loss.
3. Irrigation Schedule & Duration (e.g., drip running hours per day).
4. Water Conservation & Soil Moisture Retention Tips (mulching, fertigation).
5. Warning signs of over-watering vs water stress.

Language: {'Tamil (தமிழ்)' if language == 'ta' else 'English'}."""

        try:
            advice = self.gemini_service.generate_text(prompt)
            return {
                "success": True,
                "guidance": advice,
                "crop": crop,
                "stage": growth_stage,
                "system": irrigation_system,
                "language": language
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"AquaSmart advisor error: {str(e)}"
            }
