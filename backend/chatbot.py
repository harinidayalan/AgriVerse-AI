"""
Agri AI Chatbot Service Module.
Handles conversational agronomy advice, agricultural system instructions,
context management, and bilingual (English & Tamil) responses.
"""
import re
from backend.gemini_service import GeminiService
from backend.chat_history import ChatHistoryManager

class AgriChatbot:
    """Conversational assistant for agricultural guidance in English & Tamil."""
    
    SYSTEM_INSTRUCTION = """You are AgriVerse AI, an expert agricultural assistant, agronomist, and farming companion.
Your mission is to empower farmers, farm workers, and agriculture students with practical, evidence-aware advice.

CRITICAL GUIDELINES:
1. Simplicity: Explain technical agronomic terms (e.g., NPK ratios, foliar spray, systemic fungicides, soil porosity) in plain, actionable language.
2. Language: If the user communicates in Tamil or selected Tamil language, reply in clear, culturally natural Tamil (தமிழ்). If English, reply in English.
3. Evidence & Uncertainty: Never fabricate data or promise guaranteed yields/profitability. If symptoms or conditions are ambiguous, clearly state the uncertainty and advise consulting an agricultural extension officer or local Krishi Vigyan Kendra (KVK).
4. Safety First: When discussing chemical pesticides or fertilizers, prioritize Integrated Pest Management (IPM), bio-control, and organic remedies first. Always mention safety gear and dosage precautions for synthetic agrochemicals.
5. Actionable Structure: Structure answers with:
   - Brief direct explanation
   - Practical step-by-step guidance
   - Preventive & organic management tips
   - Disclaimer regarding local agronomic verification
6. Follow-up suggestions: At the very end of your response, provide 2 to 3 concise relevant follow-up questions formatted on separate lines beginning with "-> "."""

    def __init__(self, gemini_service: GeminiService = None):
        self.gemini_service = gemini_service or GeminiService()

    def generate_response(self, user_message: str, conversation_id: int = None, language: str = "en") -> dict:
        """
        Process a user message, retain chat history, generate Gemini response,
        and persist conversation to SQLite.
        """
        user_message = user_message.strip()
        if not user_message:
            return {
                "success": False,
                "error": "Empty message received.",
                "conversation_id": conversation_id
            }

        # 1. Retrieve or create session
        conv = ChatHistoryManager.get_or_create_conversation(
            conversation_id=conversation_id,
            language=language,
            initial_title=user_message[:35]
        )
        active_conv_id = conv["id"]

        # 2. Persist user message
        ChatHistoryManager.add_message(active_conv_id, "user", user_message, language)

        # 3. Retrieve recent message history for context
        history = ChatHistoryManager.get_conversation_messages(active_conv_id)
        
        # Build multi-turn context prompt
        context_prompt = ""
        recent_turns = history[-6:-1] if len(history) > 1 else []
        if recent_turns:
            context_prompt = "Previous Conversation Context:\n"
            for msg in recent_turns:
                role = "Farmer" if msg["sender"] == "user" else "AgriVerse AI"
                context_prompt += f"{role}: {msg['content']}\n"
            context_prompt += "\n"

        prompt = f"{context_prompt}Farmer asks: {user_message}\n\nPlease provide a helpful agronomic answer in {'Tamil (தமிழ்)' if language == 'ta' else 'English'}."

        try:
            raw_response = self.gemini_service.generate_text(
                prompt=prompt,
                system_instruction=self.SYSTEM_INSTRUCTION
            )
            
            # Extract follow-up chips if present
            follow_ups = []
            cleaned_lines = []
            for line in raw_response.splitlines():
                if line.strip().startswith("-> "):
                    chip = line.strip()[3:].strip()
                    if chip:
                        follow_ups.append(chip)
                else:
                    cleaned_lines.append(line)
            
            final_response = "\n".join(cleaned_lines).strip()
            
            # Default follow-ups if model didn't format them
            if not follow_ups:
                if language == "ta":
                    follow_ups = [
                        "இதற்கான இயற்கை தடுப்பு முறைகள் என்ன?",
                        "பரிந்துரைக்கப்படும் உர அளவு என்ன?",
                        "மண்ணின் ஈரப்பதத்தை எவ்வாறு பராமரிப்பது?"
                    ]
                else:
                    follow_ups = [
                        "What are the organic prevention methods?",
                        "What is the recommended fertilizer schedule?",
                        "How to maintain soil moisture for this crop?"
                    ]

            # 4. Persist assistant response
            ChatHistoryManager.add_message(active_conv_id, "assistant", final_response, language)

            return {
                "success": True,
                "response": final_response,
                "follow_ups": follow_ups[:3],
                "conversation_id": active_conv_id,
                "language": language
            }

        except Exception as e:
            error_msg = f"Unable to reach Gemini AI at the moment: {str(e)}"
            return {
                "success": False,
                "error": error_msg,
                "conversation_id": active_conv_id
            }
