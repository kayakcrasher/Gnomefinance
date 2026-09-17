import pytest

from gnomefinance.web_app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_homepage_loads(client):
    response = client.get("/")

    assert response.status_code == 200


def test_prices_route_exists(client):
    response = client.get("/api/prices")

    assert response.status_code in (200, 500)


def test_portfolio_route_exists(client):
    response = client.get("/api/portfolio")

    assert response.status_code in (200, 500)


def test_history_route_exists(client):
    response = client.get("/api/history/bitcoin")

    assert response.status_code in (200, 500)
