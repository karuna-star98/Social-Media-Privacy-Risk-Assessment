import pytest
from backend.app import create_app
from backend.services.questionnaire import extreme_answers


@pytest.fixture
def app(tmp_path):
    return create_app({"DB_PATH": str(tmp_path / "t.db"), "TESTING": True, "RATE_LIMIT_PER_MIN": 10000})


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def best():
    return extreme_answers("best")


@pytest.fixture
def worst():
    return extreme_answers("worst")
