"""
Farm Budget AI - Agricultural Expense Calculator and Breakdown Analyzer.
"""
from backend.database import get_db_connection

class FarmBudgetService:
    """Calculates expense totals, category breakdowns, and cost allocations."""
    
    @staticmethod
    def get_budget_summary(farm_profile_id: int = 1) -> dict:
        conn = get_db_connection()
        records = conn.execute(
            "SELECT * FROM expense_records WHERE farm_profile_id = ? ORDER BY expense_date DESC",
            (farm_profile_id,)
        ).fetchall()
        
        breakdown = conn.execute(
            "SELECT category, SUM(amount) as cat_total FROM expense_records WHERE farm_profile_id = ? GROUP BY category",
            (farm_profile_id,)
        ).fetchall()

        # Fetch farm size for cost per acre calculation
        profile = conn.execute("SELECT farm_size FROM farm_profiles WHERE id = ?", (farm_profile_id,)).fetchone()
        farm_size = profile["farm_size"] if profile and profile["farm_size"] else 1.0

        conn.close()
        
        items = [dict(r) for r in records]
        cat_map = {row["category"]: float(row["cat_total"]) for row in breakdown}
        total = sum(cat_map.values())
        cost_per_acre = round(total / farm_size, 2)
        
        return {
            "total_expenses": total,
            "cost_per_acre": cost_per_acre,
            "farm_size": farm_size,
            "category_breakdown": cat_map,
            "records": items
        }

    @staticmethod
    def add_expense(category: str, item_name: str, amount: float, notes: str = "", expense_date: str = None, farm_profile_id: int = 1):
        conn = get_db_connection()
        cursor = conn.cursor()
        if expense_date:
            cursor.execute("""
            INSERT INTO expense_records (farm_profile_id, category, item_name, amount, notes, expense_date)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (farm_profile_id, category, item_name, amount, notes, expense_date))
        else:
            cursor.execute("""
            INSERT INTO expense_records (farm_profile_id, category, item_name, amount, notes)
            VALUES (?, ?, ?, ?, ?)
            """, (farm_profile_id, category, item_name, amount, notes))
            
        exp_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return exp_id

    @staticmethod
    def delete_expense(expense_id: int):
        conn = get_db_connection()
        conn.execute("DELETE FROM expense_records WHERE id = ?", (expense_id,))
        conn.commit()
        conn.close()
        return True
