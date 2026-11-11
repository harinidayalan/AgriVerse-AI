"""
Chat History Management Module.
Persists and retrieves chat conversations and message logs in SQLite.
"""
import uuid
from backend.database import get_db_connection

class ChatHistoryManager:
    """Manages chat sessions and historical context in SQLite."""
    
    @staticmethod
    def get_or_create_conversation(conversation_id: int = None, language: str = "en", initial_title: str = "Agricultural Query") -> dict:
        """Fetch existing conversation or create a new session."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if conversation_id:
            cursor.execute("SELECT * FROM conversations WHERE id = ?", (conversation_id,))
            conv = cursor.fetchone()
            if conv:
                conn.close()
                return dict(conv)
                
        # Create new conversation
        session_id = f"agri_{uuid.uuid4().hex[:12]}"
        cursor.execute(
            "INSERT INTO conversations (session_id, title, language) VALUES (?, ?, ?)",
            (session_id, initial_title, language)
        )
        new_id = cursor.lastrowid
        conn.commit()
        
        cursor.execute("SELECT * FROM conversations WHERE id = ?", (new_id,))
        conv = cursor.fetchone()
        conn.close()
        return dict(conv)

    @staticmethod
    def add_message(conversation_id: int, sender: str, content: str, language: str = "en") -> dict:
        """Insert a message into conversation history."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (conversation_id, sender, content, language) VALUES (?, ?, ?, ?)",
            (conversation_id, sender, content, language)
        )
        msg_id = cursor.lastrowid
        
        # Update conversation timestamp and title if first message
        cursor.execute("UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (conversation_id,))
        
        if sender == "user":
            cursor.execute("SELECT count(*) as cnt FROM messages WHERE conversation_id = ? AND sender = 'user'", (conversation_id,))
            if cursor.fetchone()["cnt"] <= 1:
                short_title = content[:35] + ("..." if len(content) > 35 else "")
                cursor.execute("UPDATE conversations SET title = ? WHERE id = ?", (short_title, conversation_id))
                
        conn.commit()
        cursor.execute("SELECT * FROM messages WHERE id = ?", (msg_id,))
        msg = cursor.fetchone()
        conn.close()
        return dict(msg)

    @staticmethod
    def get_conversation_messages(conversation_id: int) -> list[dict]:
        """Fetch chronological message log for a conversation."""
        conn = get_db_connection()
        messages = conn.execute(
            "SELECT * FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC",
            (conversation_id,)
        ).fetchall()
        conn.close()
        return [dict(m) for m in messages]

    @staticmethod
    def list_recent_conversations(limit: int = 15) -> list[dict]:
        """Fetch list of most recent conversations."""
        conn = get_db_connection()
        rows = conn.execute(
            """
            SELECT c.*, COUNT(m.id) as message_count 
            FROM conversations c 
            LEFT JOIN messages m ON c.id = m.conversation_id 
            GROUP BY c.id 
            ORDER BY c.updated_at DESC 
            LIMIT ?
            """,
            (limit,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def clear_conversation(conversation_id: int) -> bool:
        """Delete messages in a conversation."""
        conn = get_db_connection()
        conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
        conn.commit()
        conn.close()
        return True
