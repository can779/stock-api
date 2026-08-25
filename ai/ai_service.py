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
    search_company_policy_tool,
    get_erp_product_tool,
    get_erp_product_tool_function
)

from services.category_mapping_service import (
    get_policy_category
)


# ============================================================
# STOCK POLICY QUESTION DETECTION
# ============================================================

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


# ============================================================
# PRODUCT NAME EXTRACTION
# ============================================================

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


# ============================================================
# MINIMUM STOCK EXTRACTION
# ============================================================

def extract_minimum_stock(
    policy_text: str
):
    match = re.search(
        r"minimum stok seviyesi\s+(\d+)",
        policy_text.lower()
    )

    if not match:
        return None

    return int(
        match.group(1)
    )


# ============================================================
# BUSINESS RULE
# ============================================================

def compare_stock_with_policy(
    current_stock: int,
    minimum_stock: int
):
    return current_stock < minimum_stock


# ============================================================
# STOCK POLICY CHECK
# ============================================================

def check_stock_policy(
    db: Session,
    user_message: str
):
    # --------------------------------------------------------
    # Ürün adını bul
    # --------------------------------------------------------

    product_name = extract_product_name(
        user_message
    )

    if not product_name:
        return {
            "error": "Ürün adı belirlenemedi."
        }

    # --------------------------------------------------------
    # Ürünün mevcut stok bilgisini DB'den al
    # --------------------------------------------------------

    product = get_product_stock(
        db,
        product_name
    )

    if isinstance(product, dict) and "error" in product:
        return product

    current_stock = product["stock"]

    erp_category = product["category"]

    # --------------------------------------------------------
    # ERP kategorisini politika kategorisine çevir
    # --------------------------------------------------------

    policy_category = get_policy_category(
        product["name"]
    )

    if policy_category is None:
        return {
            "error": (
                f"{product['name']} ürünü için "
                "şirket politikasında kategori "
                "eşleşmesi bulunamadı."
            )
        }

    # --------------------------------------------------------
    # RAG'e politika sorusu gönder
    # --------------------------------------------------------

    policy_question = (
        f"{policy_category} kategorisinin "
        f"minimum stok seviyesi nedir?"
    )

    policy = search_company_policy(
        policy_question
    )

    # --------------------------------------------------------
    # RAG sonucundan minimum stok çıkar
    # --------------------------------------------------------

    minimum_stock = extract_minimum_stock(
        policy
    )

    if minimum_stock is None:
        return {
            "error": "Minimum stok seviyesi belirlenemedi."
        }

    # --------------------------------------------------------
    # BUSINESS RULE
    # --------------------------------------------------------

    is_below_minimum = compare_stock_with_policy(
        current_stock,
        minimum_stock
    )

    return {
        "product_name": product["name"],
        "erp_category": erp_category,
        "policy_category": policy_category,
        "current_stock": current_stock,
        "minimum_stock": minimum_stock,
        "is_below_minimum": is_below_minimum
    }


# ============================================================
# MAIN AI SERVICE
# ============================================================

def chat_with_ai(
    db: Session,
    user_message: str
):

    # ========================================================
    # NORMAL TOOL CALLING
    # ========================================================

    messages = [
        {
            "role": "user",
            "content": user_message
        }
    ]

    # --------------------------------------------------------
    # LLM'e bütün tool'ları tanıt
    # --------------------------------------------------------

    response = ask_llm_with_tools(
        messages,
        [
            get_product_stock_tool,
            get_low_stock_products_tool,
            search_company_policy_tool,
            get_erp_product_tool
        ]
    )

    # --------------------------------------------------------
    # DEBUG
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Tool çağrılmadıysa direkt cevap
    # --------------------------------------------------------

    if not response.message.tool_calls:
        return response.message.content

    # --------------------------------------------------------
    # LLM mesajını geçmişe ekle
    # --------------------------------------------------------

    messages.append(
        response.message
    )

    # ========================================================
    # MULTI TOOL CALLING
    # ========================================================

    for tool_call in response.message.tool_calls:

        tool_name = tool_call.function.name

        arguments = tool_call.function.arguments

        # ====================================================
        # PRODUCT STOCK
        # ====================================================

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

        # ====================================================
        # LOW STOCK PRODUCTS
        # ====================================================

        elif tool_name == "get_low_stock_products":

            result = get_low_stock_products(
                db
            )

        # ====================================================
        # COMPANY POLICY / RAG
        # ====================================================

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

        # ====================================================
        # ERP PRODUCT
        # ====================================================

        elif tool_name == "get_erp_product":

            try:
                arguments = json.loads(
                    json.dumps(arguments)
                )

                product_name = arguments.get(
                    "product_name"
                )

            except (TypeError, ValueError):

                return (
                    "ERP ürün bilgisi işlenirken "
                    "bir hata oluştu."
                )

            if not product_name:
                return "ERP ürün adı belirtilmedi."

            result = get_erp_product_tool_function(
                product_name
            )

        # ====================================================
        # UNKNOWN TOOL
        # ====================================================

        else:

            return (
                "Bu işlem için uygun "
                "bir araç bulunamadı."
            )

        # ----------------------------------------------------
        # Tool sonucunu konuşma geçmişine ekle
        # ----------------------------------------------------

        messages.append({
            "role": "tool",
            "tool_name": tool_name,
            "content": json.dumps(
                result,
                ensure_ascii=False
            )
        })

    # ========================================================
    # FINAL LLM RESPONSE
    # ========================================================

    final_response = ask_llm_with_tools(
        messages,
        [
            get_product_stock_tool,
            get_low_stock_products_tool,
            search_company_policy_tool,
            get_erp_product_tool
        ]
    )

    return final_response.message.content