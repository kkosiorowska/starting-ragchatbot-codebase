"""API endpoint tests for the FastAPI application.

These tests run against the app built by create_test_app() in conftest.py
rather than importing backend/app.py directly, since app.py mounts static
files from ../frontend at import time which isn't available in the test
environment.
"""

import pytest

pytestmark = pytest.mark.api


class TestQueryEndpoint:
    def test_query_without_session_id_creates_session(self, client, mock_rag_system):
        response = client.post(
            "/api/query", json={"query": "What is covered in lesson 1?"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "This is a test answer."
        assert data["sources"] == ["Course A - Lesson 1"]
        assert data["session_id"] == "session_1"
        mock_rag_system.session_manager.create_session.assert_called_once()

    def test_query_with_existing_session_id_is_reused(self, client, mock_rag_system):
        response = client.post(
            "/api/query",
            json={
                "query": "What is covered in lesson 1?",
                "session_id": "existing_session",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "existing_session"
        mock_rag_system.session_manager.create_session.assert_not_called()
        mock_rag_system.query.assert_called_once_with(
            "What is covered in lesson 1?", "existing_session"
        )

    def test_query_missing_query_field_returns_422(self, client):
        response = client.post("/api/query", json={"session_id": "session_1"})

        assert response.status_code == 422

    def test_query_propagates_rag_system_error_as_500(self, client, mock_rag_system):
        mock_rag_system.query.side_effect = RuntimeError("boom")

        response = client.post("/api/query", json={"query": "trigger an error"})

        assert response.status_code == 500
        assert response.json()["detail"] == "boom"

    def test_query_response_schema(self, client):
        response = client.post("/api/query", json={"query": "hello"})

        data = response.json()
        assert set(data.keys()) == {"answer", "sources", "session_id"}
        assert isinstance(data["sources"], list)


class TestCoursesEndpoint:
    def test_get_course_stats_returns_analytics(self, client):
        response = client.get("/api/courses")

        assert response.status_code == 200
        data = response.json()
        assert data["total_courses"] == 2
        assert data["course_titles"] == ["Course A", "Course B"]

    def test_get_course_stats_propagates_error_as_500(self, client, mock_rag_system):
        mock_rag_system.get_course_analytics.side_effect = RuntimeError(
            "analytics unavailable"
        )

        response = client.get("/api/courses")

        assert response.status_code == 500
        assert response.json()["detail"] == "analytics unavailable"

    def test_get_course_stats_response_schema(self, client):
        response = client.get("/api/courses")

        data = response.json()
        assert set(data.keys()) == {"total_courses", "course_titles"}
        assert isinstance(data["course_titles"], list)


class TestRootEndpoint:
    def test_root_returns_200(self, client):
        response = client.get("/")

        assert response.status_code == 200
        assert response.json() == {"message": "Course Materials RAG System API"}
