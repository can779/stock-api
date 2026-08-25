import os
import httpx

from dotenv import load_dotenv


load_dotenv()


ERP_API_URL = os.getenv(
    "ERP_API_URL",
    "http://127.0.0.1:8000"
)

ERP_API_KEY = os.getenv(
    "ERP_API_KEY"
)


def get_erp_product(
    product_name: str
):
    url = (
        f"{ERP_API_URL}/mock-erp/products/"
        f"{product_name}"
    )

    headers = {
        "X-API-Key": ERP_API_KEY
    }

    try:
        response = httpx.get(
            url,
            headers=headers,
            timeout=5
        )

        if response.status_code == 401:
            return {
                "error": "ERP API yetkilendirme hatası"
            }

        if response.status_code == 404:
            return {
                "error": "ERP'de ürün bulunamadı"
            }

        response.raise_for_status()

        return response.json()

    except httpx.RequestError as e:

        print(
            "ERP bağlantı hatası:",
            e
        )

        return {
            "error": "ERP servisine ulaşılamadı"
        }