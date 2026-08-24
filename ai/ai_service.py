import json
import re

from sqlalchemy.orm import Session

from ai.llm_service import ask_llm_with_tools

from ai.tools import (
    get_product_stock,
    get_product_stock_tool,
    get_low_stock_products,
    get_low_stock_products_tool,
    search_company_policy,
    search_company_policy_tool
)


def is_stock_policy_comparison_question(
    user_message: str
):
    message = user_message.lower()

    comparison_keywords = [
        "minimum seviyenin altında",
        "minimum stok seviyesinin altında",
        "kritik stok",
        "stok seviyesi kritik",
        "yeniden sipariş gerekir mi",
        "yeniden sipariş gerekli mi"
    ]

    return any(
        keyword in message
        for keyword in comparison_keywords
    )


def extract_product_name(
    user_message: str
):
    messages = [
        {
            "role": "system",
            "content": """
Sen bir ürün adı çıkarma aracısısın.

Kullanıcının mesajından sadece ürün adını çıkar.

Örnek:

Kullanıcı:
"iPhone 15'in stoğu minimum seviyenin altında mı?"

Cevap:
iPhone 15

Kullanıcı:
"Bilgisayarın stoğu kritik mi?"

Cevap:
bilgisayar

Sadece ürün adını yaz.
Açıklama yapma.
"""
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    response = ask_llm_with_tools(
        messages,
        []
    )

    product_name = response.message.content.strip()

    return product_name


def extract_minimum_stock(
    policy_text: str
):
    match = re.search(
        r"minimum stok seviyesi\s+(\d+)",
        policy_text.lower()
    )

    if not match:
        return None

    return int(match.group(1))


def check_stock_policy(
    db: Session,
    user_message: str
):
    # Kullanıcının mesajından ürün adını çıkar
    product_name = extract_product_name(
        user_message
    )

    if not product_name:
        return {
            "error": "Ürün adı belirlenemedi."
        }

    # Ürünün canlı stok bilgisini DB'den al
    product = get_product_stock(
        db,
        product_name
    )

    # Ürün bulunamadıysa
    if isinstance(product, dict) and "error" in product:
        return product["error"]

    # Mevcut stok
    current_stock = product["stock"]

    # Ürün kategorisi
    category = product["category"]

    # Kategoriye göre şirket politikasını RAG'den al
    policy_question = (
        f"{category} kategorisinin minimum stok seviyesi nedir?"
    )

    policy = search_company_policy(
        policy_question
    )

    # RAG cevabından minimum stok sayısını çıkar
    minimum_stock = extract_minimum_stock(
        policy
    )

    if minimum_stock is None:
        return {
            "error": "Minimum stok seviyesi belirlenemedi."
        }

    # Gerçek iş kuralı
    is_below_minimum = (
        current_stock < minimum_stock
    )

    return {
        "product_name": product["name"],
        "category": category,
        "current_stock": current_stock,
        "minimum_stock": minimum_stock,
        "is_below_minimum": is_below_minimum
    }


def chat_with_ai(
    db: Session,
    user_message: str
):

    # =====================================================
    # STOCK POLICY COMPARISON
    # =====================================================

    if is_stock_policy_comparison_question(
        user_message
    ):
        result = check_stock_policy(
            db,
            user_message
        )

        if isinstance(result, str):
            return result

        if "error" in result:
            return result["error"]

        product_name = result["product_name"]
        current_stock = result["current_stock"]
        minimum_stock = result["minimum_stock"]
        is_below_minimum = result["is_below_minimum"]
        category = result["category"]

        if is_below_minimum:
            return (
                f"{product_name} ürününün mevcut stoğu "
                f"{current_stock} adettir. "
                f"{category} kategorisi için minimum stok "
                f"seviyesi {minimum_stock} adettir. "
                f"Bu nedenle ürün minimum stok seviyesinin "
                f"altındadır. Yeniden sipariş süreci "
                f"başlatılmalıdır."
            )

        return (
            f"{product_name} ürününün mevcut stoğu "
            f"{current_stock} adettir. "
            f"{category} kategorisi için minimum stok "
            f"seviyesi {minimum_stock} adettir. "
            f"Ürün minimum stok seviyesinin altında değildir."
        )

    # =====================================================
    # NORMAL TOOL CALLING
    # =====================================================

    messages = [
        {
            "role": "user",
            "content": user_message
        }
    ]

    # LLM'e kullanabileceği bütün tool'ları tanıt
    response = ask_llm_with_tools(
        messages,
        [
            get_product_stock_tool,
            get_low_stock_products_tool,
            search_company_policy_tool
        ]
    )

    # Debug
    print("\nTOOL ÇAĞRILARI:")

    for tool_call in response.message.tool_calls:

        print(
            "Tool:",
            tool_call.function.name
        )

        print(
            "Arguments:",
            tool_call.function.arguments
        )

    # LLM herhangi bir tool çağırmadıysa
    if not response.message.tool_calls:
        return response.message.content

    # LLM'in tool çağrısını konuşma geçmişine ekle
    messages.append(
        response.message
    )

    # =====================================================
    # MULTI TOOL CALLING
    # =====================================================

    for tool_call in response.message.tool_calls:

        tool_name = tool_call.function.name
        arguments = tool_call.function.arguments

        # -------------------------------------------------
        # PRODUCT STOCK TOOL
        # -------------------------------------------------

        if tool_name == "get_product_stock":

            try:
                arguments = json.loads(
                    json.dumps(arguments)
                )

                product_name = arguments.get(
                    "product_name"
                )

            except (TypeError, ValueError):
                return (
                    "Ürün bilgisi işlenirken "
                    "bir hata oluştu."
                )

            if not product_name:
                return "Ürün adı belirtilmedi."

            result = get_product_stock(
                db,
                product_name
            )

        # -------------------------------------------------
        # LOW STOCK TOOL
        # -------------------------------------------------

        elif tool_name == "get_low_stock_products":

            result = get_low_stock_products(
                db
            )

        # -------------------------------------------------
        # COMPANY POLICY / RAG
        # -------------------------------------------------

        elif tool_name == "search_company_policy":

            try:
                arguments = json.loads(
                    json.dumps(arguments)
                )

                question = arguments.get(
                    "question"
                )

            except (TypeError, ValueError):
                return (
                    "Politika sorusu işlenirken "
                    "bir hata oluştu."
                )

            if not question:
                return "Politika sorusu belirtilmedi."

            result = search_company_policy(
                question
            )

        # -------------------------------------------------
        # UNKNOWN TOOL
        # -------------------------------------------------

        else:
            return (
                "Bu işlem için uygun "
                "bir araç bulunamadı."
            )

        # Tool sonucunu LLM'e ekle
        messages.append({
            "role": "tool",
            "tool_name": tool_name,
            "content": json.dumps(
                result,
                ensure_ascii=False
            )
        })

    # =====================================================
    # FINAL LLM RESPONSE
    # =====================================================

    final_response = ask_llm_with_tools(
        messages,
        [
            get_product_stock_tool,
            get_low_stock_products_tool,
            search_company_policy_tool
        ]
    )

    return final_response.message.content