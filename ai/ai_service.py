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

    return response.message.content.strip()


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
# TOOL ARGUMENT PARSER
# ============================================================

def parse_tool_arguments(
    arguments
):
    try:

        if isinstance(
            arguments,
            dict
        ):
            return arguments

        if isinstance(
            arguments,
            str
        ):
            return json.loads(
                arguments
            )

        return json.loads(
            json.dumps(arguments)
        )

    except (
        TypeError,
        ValueError,
        json.JSONDecodeError
    ):
        return None


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

    product_name = extract_product_name(
        user_message
    )

    if not product_name:
        return {
            "error": "Ürün adı belirlenemedi."
        }

    product = get_product_stock(
        db,
        product_name
    )

    if (
        isinstance(product, dict)
        and "error" in product
    ):
        return product

    current_stock = product["stock"]

    erp_category = product["category"]

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

    policy_question = (
        f"{policy_category} kategorisinin "
        f"minimum stok seviyesi nedir?"
    )

    policy = search_company_policy(
        policy_question
    )

    minimum_stock = extract_minimum_stock(
        policy
    )

    if minimum_stock is None:
        return {
            "error": "Minimum stok seviyesi belirlenemedi."
        }

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
# TOOL EXECUTION
# ============================================================

def execute_tool(
    db: Session,
    tool_name: str,
    arguments: dict
):

    # --------------------------------------------------------
    # PRODUCT STOCK
    # --------------------------------------------------------

    if tool_name == "get_product_stock":

        product_name = arguments.get(
            "product_name"
        )

        if not product_name:
            return "Ürün adı belirtilmedi."

        if not isinstance(
            product_name,
            str
        ):
            return "Ürün adı geçersiz."

        return get_product_stock(
            db,
            product_name
        )

    # --------------------------------------------------------
    # LOW STOCK PRODUCTS
    # --------------------------------------------------------

    if tool_name == "get_low_stock_products":

        return get_low_stock_products(
            db
        )

    # --------------------------------------------------------
    # COMPANY POLICY / RAG
    # --------------------------------------------------------

    if tool_name == "search_company_policy":

        question = arguments.get(
            "question"
        )

        if not question:
            return "Politika sorusu belirtilmedi."

        if not isinstance(
            question,
            str
        ):
            return "Politika sorusu geçersiz."

        return search_company_policy(
            question
        )

    # --------------------------------------------------------
    # ERP PRODUCT
    # --------------------------------------------------------

    if tool_name == "get_erp_product":

        product_name = arguments.get(
            "product_name"
        )

        if not product_name:
            return "ERP ürün adı belirtilmedi."

        if not isinstance(
            product_name,
            str
        ):
            return "ERP ürün adı geçersiz."

        return get_erp_product_tool_function(
            product_name
        )

    # --------------------------------------------------------
    # UNKNOWN TOOL
    # --------------------------------------------------------

    return (
        "Bu işlem için uygun "
        "bir araç bulunamadı."
    )


# ============================================================
# MAIN AI SERVICE
# ============================================================

def chat_with_ai(
    db: Session,
    user_message: str
):

    # ========================================================
    # STOCK POLICY COMPARISON
    # ========================================================

    if is_stock_policy_comparison_question(
        user_message
    ):

        result = check_stock_policy(
            db,
            user_message
        )

        if isinstance(
            result,
            str
        ):
            return result

        if "error" in result:
            return result["error"]

        product_name = result["product_name"]

        current_stock = result["current_stock"]

        minimum_stock = result["minimum_stock"]

        is_below_minimum = result[
            "is_below_minimum"
        ]

        if is_below_minimum:

            return (
                f"{product_name} ürününün mevcut stoğu "
                f"{current_stock} adettir. "
                f"{result['policy_category']} kategorisi için "
                f"minimum stok seviyesi "
                f"{minimum_stock} adettir. "
                f"Bu nedenle ürün minimum stok seviyesinin "
                f"altındadır. Yeniden sipariş süreci "
                f"başlatılmalıdır."
            )

        return (
            f"{product_name} ürününün mevcut stoğu "
            f"{current_stock} adettir. "
            f"{result['policy_category']} kategorisi için "
            f"minimum stok seviyesi "
            f"{minimum_stock} adettir. "
            f"Ürün minimum stok seviyesinin "
            f"altında değildir."
        )

    # ========================================================
    # NORMAL TOOL CALLING
    # ========================================================

    messages = [
        {
            "role": "user",
            "content": user_message
        }
    ]

    tools = [
        get_product_stock_tool,
        get_low_stock_products_tool,
        search_company_policy_tool,
        get_erp_product_tool
    ]

    response = ask_llm_with_tools(
        messages,
        tools
    )

    print(
        "\nTOOL ÇAĞRILARI:"
    )

    for tool_call in response.message.tool_calls:

        print(
            "Tool:",
            tool_call.function.name
        )

        print(
            "Arguments:",
            tool_call.function.arguments
        )

    if not response.message.tool_calls:
        return response.message.content

    messages.append(
        response.message
    )

    # ========================================================
    # TOOL CALLING
    # ========================================================

    for tool_call in response.message.tool_calls:

        tool_name = tool_call.function.name

        arguments = parse_tool_arguments(
            tool_call.function.arguments
        )

        if arguments is None:
            return (
                f"{tool_name} için "
                "geçersiz tool parametreleri alındı."
            )

        result = execute_tool(
            db,
            tool_name,
            arguments
        )

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
        tools
    )

    return final_response.message.content