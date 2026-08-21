from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def get_auth_headers():
    response = client.post(
        "/auth/login",
        json={
            "email": "can@example.com",
            "password": "123456"
        }
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


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
    headers = get_auth_headers()

    response = client.get(
        "/products",
        headers=headers
    )

    assert response.status_code == 200


def test_products_pagination():
    headers = get_auth_headers()

    response = client.get(
        "/products?page=1&limit=2",
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) <= 2


def test_products_filtering():
    headers = get_auth_headers()

    response = client.get(
        "/products?category=Telefon",
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    for product in data:
        assert product["category"] == "Telefon"


def test_products_search():
    headers = get_auth_headers()

    response = client.get(
        "/products?search=iphone",
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    for product in data:
        assert "iphone" in product["name"].lower()


def test_products_sort_price_asc():
    headers = get_auth_headers()

    response = client.get(
        "/products?sort=price_asc",
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    prices = [product["price"] for product in data]

    assert prices == sorted(prices)


def test_products_sort_price_desc():
    headers = get_auth_headers()

    response = client.get(
        "/products?sort=price_desc",
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    prices = [product["price"] for product in data]

    assert prices == sorted(prices, reverse=True)


def test_products_combined_filters():
    headers = get_auth_headers()

    response = client.get(
        "/products"
        "?page=1"
        "&limit=3"
        "&category=Telefon"
        "&search=iphone"
        "&sort=price_asc",
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) <= 3

    for product in data:
        assert product["category"] == "Telefon"
        assert "iphone" in product["name"].lower()

    prices = [product["price"] for product in data]

    assert prices == sorted(prices)