import pytest

from conftest import SOL_ADDRESS
from gnomefinance.errors import NetworkError
from gnomefinance.web_app import create_app


@pytest.fixture
def client(service):
    app = create_app(service)
    app.config["TESTING"] = True
    return app.test_client()


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"GNOMEfinance" in response.data
    assert b"Avalanche" in response.data


def test_static_files(client):
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/style.css").status_code == 200


def test_market(client):
    data = client.get("/api/market").get_json()
    assert data["bitcoin"]["price"] == 100000.0


def test_history(client):
    assert client.get("/api/history/bitcoin?days=7").get_json()[0] == [1, 90000.0]
    assert client.get("/api/history/bitcoin?days=2").status_code == 400
    assert client.get("/api/history/bitcoin?days=x").status_code == 400


def test_holdings_crud(client):
    response = client.put("/api/holdings/bitcoin", json={"amount": "0.5"})
    assert response.get_json() == {"bitcoin": 0.5}
    assert client.get("/api/portfolio").get_json()["total_value"] == 50000
    assert client.delete("/api/holdings/bitcoin").get_json() == {}


def test_holding_validation(client):
    assert client.put("/api/holdings/bitcoin", json={"amount": -1}).status_code == 400
    assert client.put("/api/holdings/dogecoin", json={"amount": 1}).status_code == 400
    assert client.put("/api/holdings/bitcoin", data="nope").status_code == 400


def test_wallets(client):
    response = client.post("/api/wallets", json={"chain": "solana", "address": SOL_ADDRESS})
    assert response.status_code == 201
    wallet = response.get_json()

    listed = client.get("/api/wallets").get_json()
    assert listed[0]["balance"] == 3.0
    assert listed[0]["explorer_url"].endswith(SOL_ADDRESS)

    assert client.delete(f"/api/wallets/{wallet['id']}").status_code == 204
    assert client.delete(f"/api/wallets/{wallet['id']}").status_code == 400


def test_invalid_wallet(client):
    response = client.post("/api/wallets", json={"chain": "solana", "address": "bad"})
    assert response.status_code == 400
    assert "valid" in response.get_json()["error"]


def test_balance_lookup(client, chain_clients):
    assert client.get(f"/api/balance/solana/{SOL_ADDRESS}").get_json()["balance"] == 3.0
    chain_clients["solana"].error = NetworkError("down")
    assert client.get(f"/api/balance/solana/{SOL_ADDRESS}").status_code == 502
