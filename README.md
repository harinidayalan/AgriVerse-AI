# AgriVerse AI – Intelligent Smart Farming Ecosystem

> **Tagline:** *"Empowering Farmers Through Artificial Intelligence."*

AgriVerse AI is a centralized digital farming assistant and precision agriculture ecosystem built using Python Flask, Google Gemini GenAI, FAISS Retrieval-Augmented Generation (RAG), and bilingual (English & Tamil) conversational intelligence.

---

## 🌾 Project Vision & Capabilities

- **Bilingual Agri AI Chatbot**: Conversational agronomy advisor supporting English and Tamil (தமிழ்).
- **Plant Doctor AI**: Multimodal leaf symptom inspection and disease awareness with organic management tips.
- **Soil Intelligence Lab**: Automated PDF Soil Health Card parameter extraction (pH, NPK, OC, EC) and amendments.
- **CropMatch AI**: Evidence-aware multi-criteria crop recommendations tailored to climate, soil, and season.
- **AquaSmart**: Stage-specific water management and drip irrigation guidance.
- **Scheme Navigator**: Grounded RAG assistant for PM-KISAN, PMFBY, and state government schemes with page citations.
- **AgriMarket Intelligence**: Real-time mandi commodity price indicators and historical trends.
- **Virtual Farm Twin & Risk Radar**: Digital farm simulation and environmental water/heat stress warnings.
- **Smart Farming Calendar & Budget**: Activity timelines and itemized cultivation expense calculators.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.11+, Flask 3.1+, Flask-CORS, python-dotenv, Werkzeug
- **AI / Multimodal**: Google GenAI Python SDK (`google-genai`), Gemini 2.5 Flash, text-embedding-004
- **RAG & Document Intelligence**: PyMuPDF (`fitz`), FAISS CPU vector index, NumPy
- **Database**: SQLite 3 with parameterized queries & foreign keys
- **Frontend**: HTML5, CSS3 (Forest & Emerald Theme), JavaScript (ES6+), Chart.js, FontAwesome

---

## 📂 Project Architecture

```
AgriVerse-AI/
├── app.py                     # Flask application factory, routing & error handlers
├── config.py                  # Environment settings, upload limits & path resolution
├── requirements.txt           # Python dependencies
├── .env                       # Local secrets (excluded from Git)
├── .env.example               # Template environment configuration
├── .gitignore                 # Excluded directories (venv, .env, DB, vector store)
│
├── backend/                   # Modular Python Services
│   ├── __init__.py
│   ├── database.py            # SQLite schema initialization & connection helpers
│   ├── validators.py          # Upload validation & input sanitization
│   ├── gemini_service.py      # Google GenAI SDK wrapper
│   ├── chatbot.py             # Agricultural conversational engine
│   ├── chat_history.py        # Context & session retention
│   ├── pdf_processor.py       # PyMuPDF text & page extraction
│   ├── text_chunker.py        # Overlapping text chunker
│   ├── embeddings.py          # Gemini embedding generation
│   ├── rag_engine.py          # FAISS vector similarity retrieval
│   ├── soil_analyzer.py       # Soil parameter extraction & interpretation
│   ├── crop_recommender.py    # Agronomic crop suitability matching
│   ├── image_analyzer.py      # Multimodal leaf symptom inspection
│   ├── irrigation_advisor.py  # AquaSmart water guidance
│   ├── scheme_navigator.py    # Government subsidy RAG pipeline
│   ├── market_service.py      # Mandi market intelligence
│   ├── farm_calendar.py       # Crop stage activity timeline
│   └── farm_budget.py         # Cultivation cost breakdown & analysis
│
├── templates/                 # Jinja2 HTML Templates
│   ├── base.html              # 14-item sidebar, topbar, language selector
│   ├── dashboard.html         # Main dashboard with farm metrics & twin snapshot
│   ├── chatbot.html           # Bilingual chat interface
│   ├── soil.html              # Soil lab report analyzer
│   ├── crop.html              # CropMatch recommendation engine
│   ├── disease.html           # Plant Doctor leaf scanner
│   ├── schemes.html           # Scheme Navigator RAG assistant
│   └── market.html            # AgriMarket commodity rates
│
├── static/
│   ├── css/style.css          # Forest & emerald theme stylesheet
│   └── js/app.js              # Client logic, speech recognition, health check
│
├── uploads/                   # Uploaded PDFs and images (.gitkeep)
├── vector_store/              # FAISS index storage (.gitkeep)
├── database/                  # SQLite agriverse.db (.gitkeep)
│
└── tests/                     # Automated Test Suite
    ├── __init__.py
    ├── test_app.py            # Flask startup, navigation, APIs, and DB tests
    ├── test_chatbot.py        # Chatbot tests
    ├── test_rag.py            # RAG & embedding tests
    ├── test_uploads.py        # Upload security tests
    └── test_database.py       # Database schema & query tests
```

---

## 🚀 Quickstart Guide (Windows 10/11)

### 1. Open Windows PowerShell and navigate to the project directory:
```powershell
cd C:\Users\Dell\.gemini\antigravity\scratch\AgriVerse-AI
```

### 2. Activate the Virtual Environment:
```powershell
.\venv\Scripts\Activate.ps1
```
*(If PowerShell displays an execution policy restriction, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

### 3. Verify Dependencies:
```powershell
pip install -r requirements.txt
```

### 4. Configure Gemini API Key:
Verify that your API key is in `.env`:
```ini
GEMINI_API_KEY=your_actual_key_here
GEMINI_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=text-embedding-004
```

### 5. Run Stage 1 Automated Tests:
```powershell
pytest -v tests/test_app.py
```

### 6. Launch the AgriVerse AI Server:
```powershell
python app.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**
