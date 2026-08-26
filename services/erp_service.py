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

        # -------------------------------------------------
        # AUTHENTICATION HATASI
        # -------------------------------------------------

        if response.status_code == 401:
            return {
                "error": "ERP API yetkilendirme hatası"
            }

        # -------------------------------------------------
        # ÜRÜN BULUNAMADI
        # -------------------------------------------------

        if response.status_code == 404:
            return {
                "error": "ERP'de ürün bulunamadı"
            }

        # -------------------------------------------------
        # DİĞER HTTP HATALARI
        # -------------------------------------------------

        if response.status_code >= 500:
            return {
                "error": "ERP sunucusunda hata oluştu"
            }

        response.raise_for_status()

        # -------------------------------------------------
        # JSON KONTROLÜ
        # -------------------------------------------------

        try:
            return response.json()

        except ValueError:
            return {
                "error": "ERP geçersiz veri döndürdü"
            }

    # -----------------------------------------------------
    # TIMEOUT
    # -----------------------------------------------------

    except httpx.TimeoutException:

        print(
            "ERP bağlantısı zaman aşımına uğradı."
        )

        return {
            "error": "ERP servisine erişim zaman aşımına uğradı"
        }

    # -----------------------------------------------------
    # BAĞLANTI HATASI
    # -----------------------------------------------------

    except httpx.ConnectError as e:

        print(
            "ERP bağlantı hatası:",
            e
        )

        return {
            "error": "ERP servisine bağlanılamadı"
        }

    # -----------------------------------------------------
    # DİĞER HTTPX HATALARI
    # -----------------------------------------------------

    except httpx.RequestError as e:

        print(
            "ERP HTTP hatası:",
            e
        )

        return {
            "error": "ERP servisiyle iletişim kurulamadı"
        }

    # -----------------------------------------------------
    # BEKLENMEYEN HATA
    # -----------------------------------------------------

    except Exception as e:

        print(
            "Beklenmeyen ERP hatası:",
            e
        )

        return {
            "error": "ERP işlemi sırasında beklenmeyen bir hata oluştu"
        }