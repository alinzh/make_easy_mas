from langchain.tools import tool


@tool
def web_search(query: str) -> str:
    """web-search"""
    return f"[mock] search results for: {query}"


@tool
def calc(expr: str) -> str:
    """calculator"""
    try:
        return str(eval(expr, {"__builtins__": {}}))
    except Exception as e:
        return f"calc error: {e}"
