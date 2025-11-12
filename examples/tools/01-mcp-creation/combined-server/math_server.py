from fastmcp import FastMCP

mcp = FastMCP("Math Server")


@mcp.tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression safely.

    Args:
        expression: Mathematical expression (e.g., "2 + 2", "10 * 5 - 3")

    Returns:
        Result of the calculation
    """
    try:
        allowed_names = {"__builtins__": {}}
        result = eval(expression, allowed_names)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error calculating '{expression}': {str(e)}"


if __name__ == "__main__":
    mcp.run(show_banner=False)
