import pytest
from app import create_app
from backend.chatbot import AgriChatbot
from backend.chat_history import ChatHistoryManager

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_chat_endpoint_valid_response(client, mocker):
    """Test /api/chat returns structured AI response."""
    # Mock GeminiService generate_text to avoid spending live tokens in unit tests
    mocker.patch(
        "backend.gemini_service.GeminiService.generate_text",
        return_value="To manage stem borer, set up pheromone traps and spray Neem oil (5ml/L).\n-> What are the organic options?\n-> What is the chemical remedy?"
    )
    
    response = client.post("/api/chat", json={
        "message": "How to control yellow stem borer in paddy?",
        "language": "en"
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "stem borer" in data["response"]
    assert len(data["follow_ups"]) >= 2
    assert "conversation_id" in data

def test_chat_empty_message_validation(client):
    """Test /api/chat with missing or empty message returns 400."""
    response = client.post("/api/chat", json={"message": ""})
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False

def test_chat_tamil_language_support(client, mocker):
    """Test /api/chat handles Tamil language prompt."""
    mocker.patch(
        "backend.gemini_service.GeminiService.generate_text",
        return_value="நெல் தண்டு துளைப்பான் பூச்சியை கட்டுப்படுத்த வேப்ப எண்ணெய் தெளிக்கவும்."
    )
    
    response = client.post("/api/chat", json={
        "message": "நெல் பயிரில் பூச்சி கட்டுப்பாடு",
        "language": "ta"
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["language"] == "ta"

def test_chat_history_and_clear_endpoints(client, mocker):
    """Test creating, fetching, and clearing conversation history."""
    mocker.patch(
        "backend.gemini_service.GeminiService.generate_text",
        return_value="Sample agricultural advice."
    )
    
    # 1. Send first message
    res = client.post("/api/chat", json={"message": "Soil preparation for wheat"})
    conv_id = res.get_json()["conversation_id"]
    
    # 2. Fetch history for this conversation
    res_hist = client.get(f"/api/chat/history?conversation_id={conv_id}")
    assert res_hist.status_code == 200
    messages = res_hist.get_json()["messages"]
    assert len(messages) >= 2  # user + assistant
    
    # 3. Clear conversation
    res_clear = client.delete("/api/chat/clear", json={"conversation_id": conv_id})
    assert res_clear.status_code == 200
    
    # 4. Verify cleared
    res_hist_after = client.get(f"/api/chat/history?conversation_id={conv_id}")
    assert len(res_hist_after.get_json()["messages"]) == 0
