import os

from langchain_openai import ChatOpenAI


def make_openrouter_llm(model: str, temperature: float = 0.0) -> ChatOpenAI:
    return ChatOpenAI(
        model=model,
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ.get("OPENROUTER_API_KEY"),
        temperature=temperature,
    )
