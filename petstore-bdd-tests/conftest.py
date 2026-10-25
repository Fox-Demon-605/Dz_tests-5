from uuid import uuid4

import pytest
import requests


def pytest_addoption(parser):
    parser.addoption(
        "--base-url",
        action="store",
        default="http://localhost:8080/api/v3",
        help="Базовый URL Swagger Petstore API",
    )


@pytest.fixture
def base_url(request):
    return request.config.getoption("--base-url").rstrip("/")


@pytest.fixture
def api_session(base_url):
    session = requests.Session()

    try:
        # Даём понятную ошибку, если Petstore ещё не запущен.
        response = session.get(f"{base_url}/openapi.json", timeout=10)
        response.raise_for_status()
    except requests.RequestException as error:
        session.close()
        pytest.fail(
            f"Petstore недоступен по адресу {base_url}. "
            f"Проверь запуск Docker-контейнера. Ошибка: {error}"
        )

    yield session
    session.close()


@pytest.fixture
def context():
    return {
        "response": None,
        "pet": None,
        "order": None,
        "user": None,
    }


@pytest.fixture
def unique_id():
    # Положительный ID; вероятность пересечения между запусками мала.
    return uuid4().int % 1_000_000_000 + 1