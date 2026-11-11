"""
Smart Farming Calendar & Activity Scheduler.
Manages crop stage activity schedules, reminders, and completion statuses.
"""
from backend.database import get_db_connection

class FarmCalendarService:
    """Manages crop activity timelines, reminders, and growth stages."""
    
    @staticmethod
    def get_activities(farm_profile_id: int = 1):
        conn = get_db_connection()
        rows = conn.execute(
            "SELECT * FROM calendar_activities WHERE farm_profile_id = ? ORDER BY scheduled_date ASC",
            (farm_profile_id,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def add_activity(crop_name: str, activity_name: str, stage: str, scheduled_date: str, notes: str = "", farm_profile_id: int = 1):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO calendar_activities (farm_profile_id, crop_name, activity_name, stage, scheduled_date, status, notes)
        VALUES (?, ?, ?, ?, ?, 'pending', ?)
        """, (farm_profile_id, crop_name, activity_name, stage, scheduled_date, notes))
        act_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return act_id

    @staticmethod
    def toggle_activity_status(activity_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM calendar_activities WHERE id = ?", (activity_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        new_status = "completed" if row["status"] == "pending" else "pending"
        cursor.execute("UPDATE calendar_activities SET status = ? WHERE id = ?", (new_status, activity_id))
        conn.commit()
        conn.close()
        return new_status

    @staticmethod
    def delete_activity(activity_id: int):
        conn = get_db_connection()
        conn.execute("DELETE FROM calendar_activities WHERE id = ?", (activity_id,))
        conn.commit()
        conn.close()
        return True
