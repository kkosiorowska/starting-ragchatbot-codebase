"""Shared pytest fixtures for the backend test suite."""

import sys
from pathlib import Path
from typing import List, Optional
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from models import Course, CourseChunk, Lesson  # noqa: E402

# ---------------------------------------------------------------------------
# Sample domain data
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_lesson() -> Lesson:
    return Lesson(
        lesson_number=1, title="Introduction", lesson_link="https://example.com/lesson1"
    )


@pytest.fixture
def sample_course(sample_lesson: Lesson) -> Course:
    return Course(
        title="Course A",
        course_link="https://example.com/course-a",
        instructor="Jane Doe",
        lessons=[sample_lesson],
    )


@pytest.fixture
def sample_course_chunk() -> CourseChunk:
    return CourseChunk(
        content="This lesson covers the basics of the topic.",
        course_title="Course A",
        lesson_number=1,
        chunk_index=0,
    )


# ---------------------------------------------------------------------------
# Mocked RAG system
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_rag_system():
    """A MagicMock standing in for RAGSystem, pre-wired with sane defaults."""
    mock = MagicMock()
    mock.session_manager.create_session.return_value = "session_1"
    mock.query.return_value = ("This is a test answer.", ["Course A - Lesson 1"])
    mock.get_course_analytics.return_value = {
        "total_courses": 2,
        "course_titles": ["Course A", "Course B"],
    }
    return mock


# ---------------------------------------------------------------------------
# Test FastAPI app
# ---------------------------------------------------------------------------
#
# backend/app.py mounts StaticFiles(directory="../frontend") at import time,
# which fails in the test environment since that directory isn't guaranteed
# to exist. To avoid that import-time failure, the API routes are redefined
# here on a standalone app that depends on an injected rag_system instead of
# importing backend/app.py directly.


class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    session_id: str


class CourseStats(BaseModel):
    total_courses: int
    course_titles: List[str]


def create_test_app(rag_system) -> FastAPI:
    """Build a FastAPI app exposing the same /api routes as backend/app.py,
    backed by the given rag_system, without mounting any static files."""
    app = FastAPI(title="Course Materials RAG System - Test")

    @app.post("/api/query", response_model=QueryResponse)
    async def query_documents(request: QueryRequest):
        try:
            session_id = request.session_id
            if not session_id:
                session_id = rag_system.session_manager.create_session()

            answer, sources = rag_system.query(request.query, session_id)

            return QueryResponse(answer=answer, sources=sources, session_id=session_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/courses", response_model=CourseStats)
    async def get_course_stats():
        try:
            analytics = rag_system.get_course_analytics()
            return CourseStats(
                total_courses=analytics["total_courses"],
                course_titles=analytics["course_titles"],
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/")
    async def root():
        return {"message": "Course Materials RAG System API"}

    return app


@pytest.fixture
def test_app(mock_rag_system) -> FastAPI:
    return create_test_app(mock_rag_system)


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app)
