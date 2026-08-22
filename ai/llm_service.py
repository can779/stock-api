from ollama import chat


MODEL_NAME = "llama3.2:3b"


def ask_llm(prompt: str):
    response = chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]

def ask_llm_with_tools(messages, tools):
    response = chat(
        model=MODEL_NAME,
        messages=messages,
        tools=tools
    )

    return response