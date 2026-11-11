import os
import sys
import uuid
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from config import Config
from backend.database import init_db, get_db_connection
from backend.chatbot import AgriChatbot
from backend.chat_history import ChatHistoryManager
from backend.image_analyzer import PlantDoctorAnalyzer
from backend.soil_analyzer import SoilAnalyzer
from backend.crop_recommender import CropRecommender
from backend.irrigation_advisor import IrrigationAdvisor
from backend.scheme_navigator import SchemeNavigator
from backend.market_service import MarketService
from backend.farm_calendar import FarmCalendarService
from backend.farm_budget import FarmBudgetService
from backend.gemini_service import GeminiService
from backend.validators import is_allowed_file, get_safe_filename, validate_required_fields, validate_numeric

def create_app():
    """Application factory for AgriVerse AI."""
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )
    
    # Load configuration
    app.config.from_object(Config)
    CORS(app)
    
    # Ensure database tables exist
    with app.app_context():
        init_db()

    # Initialize Services
    gemini_svc = GeminiService()
    chatbot = AgriChatbot(gemini_svc)
    image_analyzer = PlantDoctorAnalyzer(gemini_svc)
    soil_analyzer = SoilAnalyzer(gemini_svc)
    crop_recommender = CropRecommender(gemini_svc)
    irrigation_advisor = IrrigationAdvisor(gemini_svc)
    scheme_navigator = SchemeNavigator(gemini_service=gemini_svc)

    # =========================================================================
    # FRONTEND PAGE ROUTES (Unified Single-Page Application on http://localhost:5000)
    # =========================================================================
    @app.route("/")
    def index():
        return render_template("dashboard.html", active_page="dashboard", initial_view="dashboard")
        
    @app.route("/chat")
    def chat_page():
        return render_template("dashboard.html", active_page="chatbot", initial_view="chat")
        
    @app.route("/plant-doctor")
    def plant_doctor_page():
        return render_template("dashboard.html", active_page="plant-doctor", initial_view="plant-doctor")
        
    @app.route("/soil-lab")
    def soil_page():
        return render_template("dashboard.html", active_page="soil-lab", initial_view="soil-lab")
        
    @app.route("/crop-match")
    def crop_page():
        return render_template("dashboard.html", active_page="crop-match", initial_view="crop-match")

    @app.route("/aquasmart")
    def aquasmart_page():
        return render_template("dashboard.html", active_page="aquasmart", initial_view="aquasmart")
        
    @app.route("/schemes")
    def schemes_page():
        return render_template("dashboard.html", active_page="schemes", initial_view="schemes")
        
    @app.route("/market")
    def market_page():
        return render_template("dashboard.html", active_page="market", initial_view="market")

    @app.route("/farm-twin")
    def farm_twin_page():
        return render_template("dashboard.html", active_page="farm-twin", initial_view="farm-twin")

    @app.route("/calendar")
    def calendar_page():
        return render_template("dashboard.html", active_page="calendar", initial_view="calendar")

    @app.route("/budget")
    def budget_page():
        return render_template("dashboard.html", active_page="budget", initial_view="budget")

    @app.route("/settings")
    def settings_page():
        return render_template("dashboard.html", active_page="settings", initial_view="settings")

    # =========================================================================
    # SYSTEM & DASHBOARD APIs
    # =========================================================================
    @app.route("/api/health", methods=["GET"])
    def health_check():
        gemini_configured = bool(Config.GEMINI_API_KEY and not Config.GEMINI_API_KEY.startswith("your_"))
        return jsonify({
            "status": "online",
            "app_name": "AgriVerse AI",
            "tagline": "Empowering Farmers Through Artificial Intelligence",
            "version": "1.0.0",
            "environment": "development" if Config.DEBUG else "production",
            "gemini_api_configured": gemini_configured,
            "gemini_model": Config.GEMINI_MODEL,
            "database_connected": Config.DATABASE_PATH.exists()
        }), 200

    @app.route("/api/farm-profile", methods=["GET"])
    def get_farm_profile():
        try:
            conn = get_db_connection()
            profile = conn.execute("SELECT * FROM farm_profiles WHERE id = 1").fetchone()
            conn.close()
            if profile:
                return jsonify({"success": True, "profile": dict(profile)}), 200
            return jsonify({"success": False, "error": "Profile not found"}), 404
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/farm-profile/update", methods=["POST"])
    def update_farm_profile():
        data = request.get_json(silent=True) or {}
        valid, err = validate_required_fields(data, ["farm_name", "farm_size", "location", "soil_type", "primary_crop"])
        if not valid:
            return jsonify({"success": False, "error": err}), 400

        try:
            conn = get_db_connection()
            conn.execute("""
            UPDATE farm_profiles 
            SET farm_name = ?, farm_size = ?, location = ?, soil_type = ?, 
                primary_crop = ?, irrigation_type = ?, water_availability = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = 1
            """, (
                data["farm_name"], float(data["farm_size"]), data["location"],
                data["soil_type"], data["primary_crop"],
                data.get("irrigation_type", "Drip Irrigation"),
                data.get("water_availability", "Moderate")
            ))
            conn.commit()
            updated = conn.execute("SELECT * FROM farm_profiles WHERE id = 1").fetchone()
            conn.close()
            return jsonify({"success": True, "profile": dict(updated)}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/dashboard/stats", methods=["GET"])
    def get_dashboard_stats():
        try:
            conn = get_db_connection()
            doc_count = conn.execute("SELECT COUNT(*) as c FROM uploaded_documents").fetchone()["c"]
            conv_count = conn.execute("SELECT COUNT(*) as c FROM conversations").fetchone()["c"]
            activity_count = conn.execute("SELECT COUNT(*) as c FROM calendar_activities WHERE status='pending'").fetchone()["c"]
            total_expense = conn.execute("SELECT COALESCE(SUM(amount), 0) as total FROM expense_records").fetchone()["total"]
            profile = conn.execute("SELECT * FROM farm_profiles WHERE id = 1").fetchone()
            next_act = conn.execute("SELECT * FROM calendar_activities WHERE status='pending' ORDER BY scheduled_date ASC LIMIT 1").fetchone()
            conn.close()
            
            return jsonify({
                "success": True,
                "stats": {
                    "documents_analyzed": doc_count,
                    "conversations": conv_count,
                    "pending_activities": activity_count,
                    "total_cultivation_cost": total_expense,
                    "farm_size": profile["farm_size"] if profile else 4.5,
                    "primary_crop": profile["primary_crop"] if profile else "Paddy / Rice",
                    "next_activity": next_act["activity_name"] if next_act else "No pending activity"
                }
            }), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    # =========================================================================
    # AGRI AI CHATBOT APIs
    # =========================================================================
    @app.route("/api/chat", methods=["POST"])
    def chat_endpoint():
        data = request.get_json(silent=True) or {}
        valid, err = validate_required_fields(data, ["message"])
        if not valid:
            return jsonify({"success": False, "error": err}), 400

        user_message = data.get("message")
        conversation_id = data.get("conversation_id")
        language = data.get("language", "en")

        result = chatbot.generate_response(user_message, conversation_id, language)
        status_code = 200 if result.get("success") else 500
        return jsonify(result), status_code

    @app.route("/api/chat/history", methods=["GET"])
    def chat_history():
        conversation_id = request.args.get("conversation_id", type=int)
        if conversation_id:
            messages = ChatHistoryManager.get_conversation_messages(conversation_id)
            return jsonify({"success": True, "messages": messages}), 200
        conversations = ChatHistoryManager.list_recent_conversations()
        return jsonify({"success": True, "conversations": conversations}), 200

    @app.route("/api/chat/new", methods=["POST"])
    def new_chat_session():
        data = request.get_json(silent=True) or {}
        language = data.get("language", "en")
        conv = ChatHistoryManager.get_or_create_conversation(language=language)
        return jsonify({"success": True, "conversation": conv}), 200

    @app.route("/api/chat/clear", methods=["DELETE"])
    def clear_chat_history():
        data = request.get_json(silent=True) or {}
        conv_id = data.get("conversation_id")
        if not conv_id:
            return jsonify({"success": False, "error": "conversation_id required"}), 400
        ChatHistoryManager.clear_conversation(conv_id)
        return jsonify({"success": True, "message": "Conversation history cleared."}), 200

    # =========================================================================
    # PLANT DOCTOR AI APIs
    # =========================================================================
    @app.route("/api/plant-doctor/analyze", methods=["POST"])
    def analyze_plant_disease():
        if "leaf_image" not in request.files:
            return jsonify({"success": False, "error": "No leaf image uploaded."}), 400
        file = request.files["leaf_image"]
        if file.filename == "":
            return jsonify({"success": False, "error": "No file selected."}), 400

        if not is_allowed_file(file.filename, Config.ALLOWED_IMAGE_EXTENSIONS):
            return jsonify({"success": False, "error": "Invalid format. Allowed: PNG, JPG, JPEG, WEBP."}), 400

        safe_name = f"leaf_{uuid.uuid4().hex[:8]}_{get_safe_filename(file.filename)}"
        saved_path = Config.UPLOAD_FOLDER / safe_name
        file.save(saved_path)

        user_notes = request.form.get("crop_notes", "")
        language = request.form.get("language", "en")

        result = image_analyzer.analyze_leaf_image(saved_path, user_notes=user_notes, language=language)
        result["image_url"] = f"/uploads/{safe_name}"
        return jsonify(result), 200 if result.get("success") else 500

    # =========================================================================
    # SOIL INTELLIGENCE LAB APIs
    # =========================================================================
    @app.route("/api/soil-lab/upload", methods=["POST"])
    def upload_soil_report():
        if "soil_pdf" not in request.files:
            return jsonify({"success": False, "error": "No PDF report uploaded."}), 400
        file = request.files["soil_pdf"]
        if file.filename == "" or not is_allowed_file(file.filename, Config.ALLOWED_DOC_EXTENSIONS):
            return jsonify({"success": False, "error": "Please upload a valid PDF document."}), 400

        safe_name = f"soil_{uuid.uuid4().hex[:8]}_{get_safe_filename(file.filename)}"
        saved_path = Config.UPLOAD_FOLDER / safe_name
        file.save(saved_path)

        crop_name = request.form.get("crop_name", "Paddy / Rice")
        language = request.form.get("language", "en")

        extracted_params = soil_analyzer.parse_pdf_report(saved_path)
        eval_result = soil_analyzer.evaluate_and_recommend(extracted_params, crop_name=crop_name, language=language)
        eval_result["filename"] = file.filename
        return jsonify(eval_result), 200

    @app.route("/api/soil-lab/evaluate", methods=["POST"])
    def evaluate_manual_soil():
        data = request.get_json(silent=True) or {}
        crop_name = data.get("crop_name", "Paddy / Rice")
        language = data.get("language", "en")
        params = {
            "ph": float(data.get("ph", 6.8)),
            "nitrogen": float(data.get("nitrogen", 240)),
            "phosphorus": float(data.get("phosphorus", 18)),
            "potassium": float(data.get("potassium", 210)),
            "organic_carbon": float(data.get("organic_carbon", 0.55)),
            "electrical_conductivity": float(data.get("electrical_conductivity", 0.40))
        }
        eval_result = soil_analyzer.evaluate_and_recommend(params, crop_name=crop_name, language=language)
        return jsonify(eval_result), 200

    # =========================================================================
    # CROPMATCH AI APIs
    # =========================================================================
    @app.route("/api/crop-match/recommend", methods=["POST"])
    def get_crop_recommendations():
        data = request.get_json(silent=True) or {}
        valid, err = validate_required_fields(data, ["location", "soil_type", "ph", "season", "water"])
        if not valid:
            return jsonify({"success": False, "error": err}), 400

        result = crop_recommender.recommend(
            location=data["location"],
            soil_type=data["soil_type"],
            ph=float(data["ph"]),
            season=data["season"],
            water=data["water"],
            prev_crop=data.get("previous_crop", ""),
            language=data.get("language", "en")
        )
        return jsonify(result), 200 if result.get("success") else 500

    # =========================================================================
    # AQUASMART IRRIGATOR APIs
    # =========================================================================
    @app.route("/api/aquasmart/guidance", methods=["POST"])
    def get_aquasmart_guidance():
        data = request.get_json(silent=True) or {}
        valid, err = validate_required_fields(data, ["crop", "stage", "soil", "system"])
        if not valid:
            return jsonify({"success": False, "error": err}), 400

        result = irrigation_advisor.advise(
            crop=data["crop"],
            growth_stage=data["stage"],
            soil_type=data["soil"],
            irrigation_system=data["system"],
            water_source=data.get("water_source", "Borewell & Canal"),
            language=data.get("language", "en")
        )
        return jsonify(result), 200 if result.get("success") else 500

    # =========================================================================
    # SCHEME NAVIGATOR RAG APIs
    # =========================================================================
    @app.route("/api/schemes/query", methods=["POST"])
    def query_scheme_rag():
        data = request.get_json(silent=True) or {}
        valid, err = validate_required_fields(data, ["question"])
        if not valid:
            return jsonify({"success": False, "error": err}), 400

        result = scheme_navigator.query_scheme(
            question=data["question"],
            language=data.get("language", "en")
        )
        return jsonify(result), 200 if result.get("success") else 500

    @app.route("/api/schemes/upload", methods=["POST"])
    def upload_scheme_document():
        if "scheme_pdf" not in request.files:
            return jsonify({"success": False, "error": "No PDF file uploaded."}), 400
        file = request.files["scheme_pdf"]
        if file.filename == "" or not is_allowed_file(file.filename, Config.ALLOWED_DOC_EXTENSIONS):
            return jsonify({"success": False, "error": "Please upload a valid PDF scheme file."}), 400

        safe_name = f"scheme_{uuid.uuid4().hex[:8]}_{get_safe_filename(file.filename)}"
        saved_path = Config.UPLOAD_FOLDER / safe_name
        file.save(saved_path)

        chunk_count = scheme_navigator.index_pdf_document(saved_path, file.filename)
        return jsonify({
            "success": True,
            "message": f"Successfully indexed {file.filename} into FAISS vector database ({chunk_count} semantic chunks created).",
            "chunks_indexed": chunk_count
        }), 200

    # =========================================================================
    # AGRIMARKET INTELLIGENCE APIs
    # =========================================================================
    @app.route("/api/market/search", methods=["GET"])
    def search_market_prices():
        query = request.args.get("query", "")
        state = request.args.get("state", "")
        results = MarketService.search_markets(query, state)
        return jsonify({"success": True, "prices": results}), 200

    @app.route("/api/market/trend", methods=["GET"])
    def get_market_trend():
        commodity = request.args.get("commodity", "Paddy (Common)")
        data = MarketService.get_historical_chart_data(commodity)
        return jsonify({"success": True, "chart_data": data}), 200

    # =========================================================================
    # FARMING CALENDAR APIs
    # =========================================================================
    @app.route("/api/calendar", methods=["GET"])
    def get_calendar_activities():
        activities = FarmCalendarService.get_activities()
        return jsonify({"success": True, "activities": activities}), 200

    @app.route("/api/calendar/add", methods=["POST"])
    def add_calendar_activity():
        data = request.get_json(silent=True) or {}
        valid, err = validate_required_fields(data, ["crop_name", "activity_name", "stage", "scheduled_date"])
        if not valid:
            return jsonify({"success": False, "error": err}), 400

        act_id = FarmCalendarService.add_activity(
            crop_name=data["crop_name"],
            activity_name=data["activity_name"],
            stage=data["stage"],
            scheduled_date=data["scheduled_date"],
            notes=data.get("notes", "")
        )
        return jsonify({"success": True, "activity_id": act_id, "message": "Activity scheduled."}), 201

    @app.route("/api/calendar/toggle", methods=["POST"])
    def toggle_calendar_activity():
        data = request.get_json(silent=True) or {}
        act_id = data.get("activity_id")
        if not act_id:
            return jsonify({"success": False, "error": "activity_id required"}), 400

        new_status = FarmCalendarService.toggle_activity_status(int(act_id))
        if not new_status:
            return jsonify({"success": False, "error": "Activity not found"}), 404
        return jsonify({"success": True, "new_status": new_status}), 200

    @app.route("/api/calendar/delete", methods=["DELETE"])
    def delete_calendar_activity():
        data = request.get_json(silent=True) or {}
        act_id = data.get("activity_id")
        if not act_id:
            return jsonify({"success": False, "error": "activity_id required"}), 400
        FarmCalendarService.delete_activity(int(act_id))
        return jsonify({"success": True, "message": "Activity deleted."}), 200

    # =========================================================================
    # FARM BUDGET APIs
    # =========================================================================
    @app.route("/api/budget", methods=["GET"])
    def get_budget():
        budget = FarmBudgetService.get_budget_summary()
        return jsonify({"success": True, "budget": budget}), 200

    @app.route("/api/budget/add", methods=["POST"])
    def add_budget_expense():
        data = request.get_json(silent=True) or {}
        valid, err = validate_required_fields(data, ["category", "item_name", "amount"])
        if not valid:
            return jsonify({"success": False, "error": err}), 400

        exp_id = FarmBudgetService.add_expense(
            category=data["category"],
            item_name=data["item_name"],
            amount=float(data["amount"]),
            notes=data.get("notes", ""),
            expense_date=data.get("expense_date")
        )
        return jsonify({"success": True, "expense_id": exp_id, "message": "Expense saved."}), 201

    @app.route("/api/budget/delete", methods=["DELETE"])
    def delete_budget_expense():
        data = request.get_json(silent=True) or {}
        exp_id = data.get("expense_id")
        if not exp_id:
            return jsonify({"success": False, "error": "expense_id required"}), 400
        FarmBudgetService.delete_expense(int(exp_id))
        return jsonify({"success": True, "message": "Expense deleted."}), 200

    # =========================================================================
    # VIRTUAL FARM TWIN & RISK RADAR APIs
    # =========================================================================
    @app.route("/api/twin/simulate", methods=["POST"])
    def simulate_twin_scenario():
        data = request.get_json(silent=True) or {}
        scenario = data.get("scenario", "Delayed monsoon by 3 weeks")
        language = data.get("language", "en")

        conn = get_db_connection()
        profile = conn.execute("SELECT * FROM farm_profiles WHERE id = 1").fetchone()
        conn.close()

        prompt = f"""You are AgriVerse Virtual Farm Twin Simulator.
Current Farm Parameters:
- Crop: {profile['primary_crop'] if profile else 'Paddy'}
- Farm Size: {profile['farm_size'] if profile else 4.5} Acres in {profile['location'] if profile else 'Coimbatore'}
- Soil: {profile['soil_type'] if profile else 'Red Loam'}
- Irrigation: {profile['irrigation_type'] if profile else 'Drip'}

SIMULATE SCENARIO: "{scenario}"

Provide:
1. Agronomic Impact on Crop Growth & Yield Potential.
2. Soil & Moisture Stress Assessment.
3. Recommended Immediate Action & Adaptive Management.
4. Farm Risk Radar Assessment (Water Stress level, Heat vulnerability, Pest risk).

Language: {'Tamil (தமிழ்)' if language == 'ta' else 'English'}.
Clearly state this is a hypothetical simulation."""

        try:
            simulation_result = gemini_svc.generate_text(prompt)
            return jsonify({
                "success": True,
                "simulation": simulation_result,
                "scenario": scenario
            }), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    # Static uploads handler
    @app.route("/uploads/<filename>")
    def uploaded_file(filename):
        return send_from_directory(Config.UPLOAD_FOLDER, filename)

    # Error Handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found", "status": 404}), 404

    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({"error": "File size exceeds the 16MB limit.", "status": 413}), 413

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "An internal server error occurred.", "status": 500}), 500

    return app

if __name__ == "__main__":
    app = create_app()
    print("🌾 AgriVerse AI Server starting on http://localhost:5000 and http://127.0.0.1:5000 ...")
    app.run(host="0.0.0.0", port=5000, debug=True)
