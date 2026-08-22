from llm_service import ask_llm


response = ask_llm(
    "Sen bir stok yönetim asistanısın. "
    "Stok yönetiminin ne olduğunu 2 cümleyle açıkla."
)

print(response)