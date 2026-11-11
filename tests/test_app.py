import os
import pytest
from app import create_app
from backend.database import get_db_connection

@pytest.fixture
def client():
    """Create and configure a test client for the application."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_check_endpoint(client):
    """Test the /api/health endpoint returns online status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "online"
    assert data["app_name"] == "AgriVerse AI"
    assert "gemini_model" in data
    assert data["gemini_api_configured"] is True

def test_all_14_navigation_pages(client):
    """Test all primary navigation pages render 200 OK without errors."""
    routes = [
        "/",
        "/chat",
        "/plant-doctor",
        "/soil-lab",
        "/crop-match",
        "/aquasmart",
        "/schemes",
        "/market",
        "/farm-twin",
        "/calendar",
        "/budget",
        "/settings"
    ]
    for route in routes:
        response = client.get(route)
        assert response.status_code == 200, f"Route {route} returned {response.status_code}"

def test_farm_profile_and_update_api(client):
    """Test fetching and updating the Virtual Farm Twin profile."""
    # Get profile
    res_get = client.get("/api/farm-profile")
    assert res_get.status_code == 200
    assert res_get.get_json()["success"] is True

    # Update profile
    payload = {
        "farm_name": "Sunrise Organic Farm",
        "farm_size": 5.2,
        "location": "Coimbatore, Tamil Nadu",
        "soil_type": "Red Loamy Soil",
        "primary_crop": "Paddy (CO-51)",
        "irrigation_type": "Drip Irrigation",
        "water_availability": "Moderate"
    }
    res_up = client.post("/api/farm-profile/update", json=payload)
    assert res_up.status_code == 200
    data = res_up.get_json()
    assert data["success"] is True
    assert data["profile"]["farm_name"] == "Sunrise Organic Farm"
    assert data["profile"]["farm_size"] == 5.2

def test_calendar_activity_lifecycle(client):
    """Test adding, listing, toggling, and deleting a calendar activity."""
    # 1. Add activity
    payload = {
        "crop_name": "Paddy",
        "activity_name": "Test Pheromone Trap Installation",
        "stage": "Panicle Initiation",
        "scheduled_date": "2026-11-20",
        "notes": "5 traps per acre"
    }
    res_add = client.post("/api/calendar/add", json=payload)
    assert res_add.status_code == 201
    act_id = res_add.get_json()["activity_id"]

    # 2. Verify in list
    res_list = client.get("/api/calendar")
    assert res_list.status_code == 200
    activities = res_list.get_json()["activities"]
    assert any(a["id"] == act_id for a in activities)

    # 3. Toggle status
    res_tog = client.post("/api/calendar/toggle", json={"activity_id": act_id})
    assert res_tog.status_code == 200
    assert res_tog.get_json()["new_status"] == "completed"

    # 4. Delete activity
    res_del = client.delete("/api/calendar/delete", json={"activity_id": act_id})
    assert res_del.status_code == 200

def test_budget_expense_lifecycle(client):
    """Test adding, fetching breakdown, and deleting an expense."""
    payload = {
        "category": "Seeds",
        "item_name": "Certified Paddy CO-51 Seeds",
        "amount": 3200,
        "notes": "Purchased from TNAU"
    }
    res_add = client.post("/api/budget/add", json=payload)
    assert res_add.status_code == 201
    exp_id = res_add.get_json()["expense_id"]

    # Fetch budget summary
    res_get = client.get("/api/budget")
    assert res_get.status_code == 200
    budget = res_get.get_json()["budget"]
    assert budget["total_expenses"] > 0
    assert "Seeds" in budget["category_breakdown"]

    # Delete
    res_del = client.delete("/api/budget/delete", json={"expense_id": exp_id})
    assert res_del.status_code == 200

def test_market_intelligence_apis(client):
    """Test APMC price searching and historical trend chart data."""
    res_search = client.get("/api/market/search?query=Paddy")
    assert res_search.status_code == 200
    prices = res_search.get_json()["prices"]
    assert len(prices) >= 1
    assert "Paddy" in prices[0]["commodity"]

    res_trend = client.get("/api/market/trend?commodity=Paddy+(Common)")
    assert res_trend.status_code == 200
    chart = res_trend.get_json()["chart_data"]
    assert len(chart["prices"]) == 6

def test_crop_match_api(client, mocker):
    """Test CropMatch AI recommendation endpoint with mocked Gemini response."""
    mocker.patch(
        "backend.gemini_service.GeminiService.generate_text",
        return_value="Recommended: Paddy CO-51, Blackgram VBN-8. Suitable for red loam."
    )
    payload = {
        "location": "Coimbatore",
        "soil_type": "Red Loam",
        "ph": 6.8,
        "season": "Kharif",
        "water": "Moderate"
    }
    res = client.post("/api/crop-match/recommend", json=payload)
    assert res.status_code == 200
    assert res.get_json()["success"] is True

def test_aquasmart_api(client, mocker):
    """Test AquaSmart irrigation guidance endpoint."""
    mocker.patch(
        "backend.gemini_service.GeminiService.generate_text",
        return_value="Maintain soil moisture at 70%. Run drip for 2.5 hours daily."
    )
    payload = {
        "crop": "Paddy / Rice",
        "stage": "Tillering",
        "soil": "Red Loam",
        "system": "Drip Irrigation"
    }
    res = client.post("/api/aquasmart/guidance", json=payload)
    assert res.status_code == 200
    assert res.get_json()["success"] is True

def test_soil_manual_evaluate_api(client, mocker):
    """Test Soil Intelligence Lab manual parameter evaluation."""
    mocker.patch(
        "backend.gemini_service.GeminiService.generate_text",
        return_value="Soil is optimal. Apply 5t FYM and 50kg Azospirillum."
    )
    payload = {
        "ph": 6.8,
        "nitrogen": 240,
        "phosphorus": 18,
        "potassium": 210,
        "organic_carbon": 0.6,
        "electrical_conductivity": 0.4
    }
    res = client.post("/api/soil-lab/evaluate", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["metrics"]["ph"]["value"] == 6.8

def test_twin_simulation_api(client, mocker):
    """Test Virtual Farm Twin hypothetical scenario simulation."""
    mocker.patch(
        "backend.gemini_service.GeminiService.generate_text",
        return_value="Impact: Delaying monsoon reduces tillering by 15%. Remedial action: Foliar spray of 1% potassium nitrate."
    )
    payload = {"scenario": "Monsoon delayed by 3 weeks"}
    res = client.post("/api/twin/simulate", json=payload)
    assert res.status_code == 200
    assert res.get_json()["success"] is True
