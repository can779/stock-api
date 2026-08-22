import json

from sqlalchemy.orm import Session

from ai.llm_service import ask_llm_with_tools
from ai.tools import (
    get_product_stock,
    get_product_stock_tool
)


def chat_with_ai(
    db: Session,
    user_message: str
):
    messages = [
        {
            "role": "user",
            "content": user_message
        }
    ]

    response = ask_llm_with_tools(
        messages,
        [get_product_stock_tool]
    )

    # LLM doğrudan cevap verdiyse
    if not response.message.tool_calls:
        return response.message.content

    # Şimdilik ilk tool çağrısını ele alıyoruz
    tool_call = response.message.tool_calls[0]

    tool_name = tool_call.function.name
    arguments = tool_call.function.arguments

    # Tanımadığımız bir tool gelirse
    if tool_name != "get_product_stock":
        return "Bu işlem için uygun bir araç bulunamadı."

    try:
        arguments = json.loads(
            json.dumps(arguments)
        )

        product_name = arguments.get("product_name")

    except (TypeError, ValueError):
        return "Ürün bilgisi işlenirken bir hata oluştu."

    if not product_name:
        return "Ürün adı belirtilmedi."

    result = get_product_stock(
        db,
        product_name
    )

    # Ürün bulunamadı
    if isinstance(result, dict) and "error" in result:
        return result["error"]

    messages.append(response.message)

    messages.append({
        "role": "tool",
        "tool_name": "get_product_stock",
        "content": json.dumps(
            result,
            ensure_ascii=False
        )
    })

    final_response = ask_llm_with_tools(
        messages,
        [get_product_stock_tool]
    )

    return final_response.message.content