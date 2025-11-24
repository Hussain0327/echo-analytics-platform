"""Tests for the Chat API endpoints.

These tests require the full app to be running with database connections.
Mark them as integration tests if running without Docker.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport
from datetime import datetime
import io

# Skip all tests in this module if DB is not available
pytestmark = pytest.mark.skipif(
    True,  # Set to False when running with Docker
    reason="Integration tests require database connection"
)

from app.main import app
from app.services.llm.conversation import ChatResponse, ConversationContext, Message


@pytest.fixture
def sample_csv():
    return b"""date,amount,customer_id
2024-01-01,100.00,C001
2024-01-02,200.00,C002
2024-01-03,300.00,C003
"""


class TestChatEndpoint:
    """Tests for POST /chat endpoint."""

    @pytest.mark.asyncio
    async def test_chat_basic(self):
        """Test basic chat request."""
        with patch('app.api.v1.chat.get_conversation_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.chat = AsyncMock(return_value=ChatResponse(
                message="Hello! I'm Echo, your data consultant.",
                session_id="test-session-123",
                timestamp=datetime.now()
            ))
            mock_get_service.return_value = mock_service

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/chat",
                    json={"message": "Hi!"}
                )

            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert data["response"] == "Hello! I'm Echo, your data consultant."
            assert "session_id" in data

    @pytest.mark.asyncio
    async def test_chat_with_session_id(self):
        """Test chat with existing session ID."""
        with patch('app.api.v1.chat.get_conversation_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.chat = AsyncMock(return_value=ChatResponse(
                message="Welcome back!",
                session_id="existing-session",
                timestamp=datetime.now()
            ))
            mock_get_service.return_value = mock_service

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/chat",
                    json={
                        "message": "Hello again",
                        "session_id": "existing-session"
                    }
                )

            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == "existing-session"

    @pytest.mark.asyncio
    async def test_chat_service_error(self):
        """Test handling of service errors."""
        with patch('app.api.v1.chat.get_conversation_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.chat = AsyncMock(
                side_effect=Exception("LLM API error")
            )
            mock_get_service.return_value = mock_service

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/chat",
                    json={"message": "Hello"}
                )

            assert response.status_code == 500
            assert "Chat service error" in response.json()["detail"]


class TestChatWithDataEndpoint:
    """Tests for POST /chat/with-data endpoint."""

    @pytest.mark.asyncio
    async def test_chat_with_data(self, sample_csv):
        """Test chat with data file."""
        with patch('app.api.v1.chat.get_conversation_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.chat = AsyncMock(return_value=ChatResponse(
                message="I see your revenue data. Total is $600.",
                session_id="data-session",
                timestamp=datetime.now()
            ))
            mock_get_service.return_value = mock_service

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/chat/with-data",
                    params={"message": "What's my total revenue?"},
                    files={"file": ("test.csv", io.BytesIO(sample_csv), "text/csv")}
                )

            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert "session_id" in data

    @pytest.mark.asyncio
    async def test_chat_with_data_non_csv(self):
        """Test rejection of non-CSV files."""
        with patch('app.api.v1.chat.get_conversation_service') as mock_get_service:
            mock_service = MagicMock()
            mock_get_service.return_value = mock_service

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/chat/with-data",
                    params={"message": "Analyze this"},
                    files={"file": ("test.txt", io.BytesIO(b"not csv"), "text/plain")}
                )

            assert response.status_code == 400
            assert "CSV" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_chat_with_data_empty_file(self):
        """Test rejection of empty files."""
        with patch('app.api.v1.chat.get_conversation_service') as mock_get_service:
            mock_service = MagicMock()
            mock_get_service.return_value = mock_service

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/chat/with-data",
                    params={"message": "Analyze this"},
                    files={"file": ("empty.csv", io.BytesIO(b""), "text/csv")}
                )

            assert response.status_code == 400
            assert "empty" in response.json()["detail"].lower()


class TestLoadDataEndpoint:
    """Tests for POST /chat/load-data endpoint."""

    @pytest.mark.asyncio
    async def test_load_data(self, sample_csv):
        """Test loading data into session."""
        with patch('app.api.v1.chat.get_conversation_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.update_data_context = MagicMock()
            mock_get_service.return_value = mock_service

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/chat/load-data",
                    params={"session_id": "load-session"},
                    files={"file": ("sales.csv", io.BytesIO(sample_csv), "text/csv")}
                )

            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == "load-session"
            assert data["rows"] == 3
            assert "date" in data["columns"]
            assert "amount" in data["columns"]


class TestHistoryEndpoint:
    """Tests for GET /chat/history/{session_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_history(self):
        """Test getting conversation history."""
        with patch('app.api.v1.chat.get_conversation_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service._sessions = {
                "history-session": ConversationContext(
                    session_id="history-session",
                    messages=[
                        Message(role="user", content="Hello"),
                        Message(role="assistant", content="Hi there!")
                    ],
                    data_summary="Some data"
                )
            }
            mock_get_service.return_value = mock_service

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/chat/history/history-session")

            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == "history-session"
            assert len(data["messages"]) == 2
            assert data["data_loaded"] is True

    @pytest.mark.asyncio
    async def test_get_history_not_found(self):
        """Test 404 for non-existent session."""
        with patch('app.api.v1.chat.get_conversation_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service._sessions = {}
            mock_get_service.return_value = mock_service

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/chat/history/nonexistent")

            assert response.status_code == 404


class TestClearSessionEndpoint:
    """Tests for DELETE /chat/session/{session_id} endpoint."""

    @pytest.mark.asyncio
    async def test_clear_session(self):
        """Test clearing a session."""
        with patch('app.api.v1.chat.get_conversation_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.clear_session = MagicMock(return_value=True)
            mock_get_service.return_value = mock_service

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.delete("/api/v1/chat/session/clear-me")

            assert response.status_code == 200
            assert "cleared" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_clear_session_not_found(self):
        """Test clearing non-existent session."""
        with patch('app.api.v1.chat.get_conversation_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.clear_session = MagicMock(return_value=False)
            mock_get_service.return_value = mock_service

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.delete("/api/v1/chat/session/not-found")

            assert response.status_code == 404


class TestListSessionsEndpoint:
    """Tests for GET /chat/sessions endpoint."""

    @pytest.mark.asyncio
    async def test_list_sessions(self):
        """Test listing all sessions."""
        with patch('app.api.v1.chat.get_conversation_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service._sessions = {
                "session-1": ConversationContext(
                    session_id="session-1",
                    messages=[Message(role="user", content="test")],
                    data_summary="data"
                ),
                "session-2": ConversationContext(
                    session_id="session-2",
                    messages=[]
                )
            }
            mock_get_service.return_value = mock_service

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/chat/sessions")

            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 2
            assert len(data["sessions"]) == 2

    @pytest.mark.asyncio
    async def test_list_sessions_empty(self):
        """Test listing when no sessions exist."""
        with patch('app.api.v1.chat.get_conversation_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service._sessions = {}
            mock_get_service.return_value = mock_service

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/chat/sessions")

            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 0
            assert data["sessions"] == []
