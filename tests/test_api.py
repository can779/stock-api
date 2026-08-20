from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Stock API çalışıyor!"
    }

def test_login():
    response = client.post(
        "/auth/login",
        json={
            "email": "can@example.com",
            "password": "123456"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_get_products_authenticated():
    login_response = client.post(
        "/auth/login",
        json={
            "email": "can@example.com",
            "password": "123456"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/products",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200