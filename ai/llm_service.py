from ollama import chat


MODEL_NAME = "llama3.2:3b"


SYSTEM_PROMPT = """
Sen bir kurumsal ERP stok asistanısın.

Görevin, kullanıcı sorularını doğru tool'u kullanarak cevaplamaktır.

Tool kullanım kuralları:

1. Bir ürünün mevcut stok miktarı soruluyorsa:
   get_product_stock tool'unu kullan.

2. Stok miktarı 10 veya daha az olan ürünlerin listesi isteniyorsa:
   get_low_stock_products tool'unu kullan.

3. Şirketin stok politikası, minimum stok seviyesi,
   yeniden sipariş koşulları veya prosedürleri soruluyorsa:
   search_company_policy tool'unu kullan.

4. Kullanıcı bir ürünün mevcut stok miktarının,
   şirket politikasındaki minimum stok seviyesinin altında
   olup olmadığını soruyorsa:

   Önce get_product_stock ile ürünün mevcut stok miktarını
   ve kategorisini öğren.

   Daha sonra ürünün kategorisini kullanarak
   search_company_policy ile o kategoriye ait minimum
   stok seviyesini öğren.

   Daha sonra mevcut stok ile minimum stok seviyesini
   karşılaştır.

5. get_low_stock_products tool'u şirket politikasındaki
   minimum stok seviyesini belirlemek için kullanılmaz.

6. Mevcut stok miktarı ile minimum stok seviyesini
   birbirine karıştırma.

7. Cevap verirken yalnızca tool ve dokümanlardan elde edilen
   bilgileri kullan.

8. Kullanıcıya Türkçe ve açık cevap ver.
"""


def ask_llm(prompt: str):

    response = chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


def ask_llm_with_tools(messages, tools):

    messages_with_system = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        *messages
    ]

    response = chat(
        model=MODEL_NAME,
        messages=messages_with_system,
        tools=tools
    )

    return response