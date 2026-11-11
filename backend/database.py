import sqlite3
import os
from pathlib import Path
from config import Config

def get_db_connection():
    """Establish and return a connection to the SQLite database."""
    Config.ensure_directories()
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Enables dict-like column access
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Initialize all required SQLite tables if they do not exist."""
    Config.ensure_directories()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Users / Profiles
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        location TEXT,
        preferred_language TEXT DEFAULT 'en',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # Insert default demo farmer profile if not present
    cursor.execute("SELECT id FROM users WHERE id = 1")
    if not cursor.fetchone():
        cursor.execute("""
        INSERT INTO users (id, name, phone, location, preferred_language)
        VALUES (1, 'Ramesh Kumar', '+91 98765 43210', 'Coimbatore, Tamil Nadu', 'en')
        """)

    # 2. Conversations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        language TEXT DEFAULT 'en',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 3. Chat Messages
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id INTEGER NOT NULL,
        sender TEXT NOT NULL, -- 'user' or 'assistant'
        content TEXT NOT NULL,
        language TEXT DEFAULT 'en',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
    );
    """)

    # 4. Uploaded Documents (PDFs, Images, Reports)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS uploaded_documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        original_name TEXT NOT NULL,
        file_type TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        doc_category TEXT DEFAULT 'general', -- 'scheme', 'soil', 'leaf'
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        chunk_count INTEGER DEFAULT 0,
        status TEXT DEFAULT 'processed'
    );
    """)

    # 5. Virtual Farm Twin Profiles
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS farm_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        farm_name TEXT NOT NULL,
        farm_size REAL NOT NULL, -- in acres
        location TEXT NOT NULL,
        soil_type TEXT NOT NULL,
        primary_crop TEXT NOT NULL,
        irrigation_type TEXT NOT NULL,
        water_availability TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # Insert default demo farm profile if not present
    cursor.execute("SELECT id FROM farm_profiles WHERE id = 1")
    if not cursor.fetchone():
        cursor.execute("""
        INSERT INTO farm_profiles (id, user_id, farm_name, farm_size, location, soil_type, primary_crop, irrigation_type, water_availability)
        VALUES (1, 1, 'Green Valley Farm', 4.5, 'Coimbatore, Tamil Nadu', 'Red Loamy Soil', 'Paddy / Rice', 'Drip Irrigation', 'Borewell & Canal')
        """)

    # 6. Soil Intelligence Reports
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS soil_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER,
        sample_name TEXT DEFAULT 'Sample 1',
        ph REAL,
        nitrogen REAL,
        phosphorus REAL,
        potassium REAL,
        organic_carbon REAL,
        electrical_conductivity REAL,
        soil_texture TEXT,
        summary TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (document_id) REFERENCES uploaded_documents(id) ON DELETE SET NULL
    );
    """)

    # 7. Farm Budget & Expense Records
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expense_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farm_profile_id INTEGER DEFAULT 1,
        category TEXT NOT NULL, -- 'Seeds', 'Fertilizers', 'Labour', 'Irrigation', 'Equipment', 'Transportation', 'Other'
        item_name TEXT NOT NULL,
        amount REAL NOT NULL,
        notes TEXT,
        expense_date DATE DEFAULT (DATE('now')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (farm_profile_id) REFERENCES farm_profiles(id) ON DELETE CASCADE
    );
    """)

    # Seed initial demo budget expenses if empty
    cursor.execute("SELECT count(*) as count FROM expense_records")
    if cursor.fetchone()["count"] == 0:
        cursor.execute("""
        INSERT INTO expense_records (farm_profile_id, category, item_name, amount, notes, expense_date)
        VALUES 
        (1, 'Seeds', 'Certified Paddy Seeds (CO-51)', 4500, '3 bags of 25kg each', DATE('now', '-20 days')),
        (1, 'Fertilizers', 'Organic Compost & Bio-fertilizer', 6200, 'Neem cake and Trichoderma', DATE('now', '-15 days')),
        (1, 'Labour', 'Land preparation & Sowing labour', 8500, '5 laborers for 2 days', DATE('now', '-10 days')),
        (1, 'Irrigation', 'Drip pipe repairs & filter cleaning', 2100, 'Maintenance work', DATE('now', '-5 days')),
        (1, 'Equipment', 'Tractor rental for plowing', 5400, '6 hours total plowing', DATE('now', '-2 days'))
        """)

    # 8. Farming Calendar Activities
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS calendar_activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farm_profile_id INTEGER DEFAULT 1,
        crop_name TEXT NOT NULL,
        activity_name TEXT NOT NULL,
        stage TEXT NOT NULL,
        scheduled_date DATE NOT NULL,
        status TEXT DEFAULT 'pending', -- 'pending', 'completed'
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (farm_profile_id) REFERENCES farm_profiles(id) ON DELETE CASCADE
    );
    """)

    # Seed initial calendar activities if empty
    cursor.execute("SELECT count(*) as count FROM calendar_activities")
    if cursor.fetchone()["count"] == 0:
        cursor.execute("""
        INSERT INTO calendar_activities (farm_profile_id, crop_name, activity_name, stage, scheduled_date, status, notes)
        VALUES
        (1, 'Paddy / Rice', 'Basal Fertilizer Application', 'Vegetative Stage', DATE('now', '+2 days'), 'pending', 'Apply recommended organic compost + bio-fertilizers'),
        (1, 'Paddy / Rice', 'First Weeding & Water Level Check', 'Tillering Stage', DATE('now', '+7 days'), 'pending', 'Maintain 2-3 cm shallow standing water'),
        (1, 'Paddy / Rice', 'Pest Monitoring (Stem Borer inspection)', 'Panicle Initiation', DATE('now', '+15 days'), 'pending', 'Set up pheromone traps in the field')
        """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("AgriVerse AI database initialized successfully.")
