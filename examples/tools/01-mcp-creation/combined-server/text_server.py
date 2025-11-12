from fastmcp import FastMCP

mcp = FastMCP("Text Server")


@mcp.tool
def count_words(text: str) -> str:
    """Count words in text.

    Args:
        text: Text to analyze

    Returns:
        Word count statistics
    """
    words = text.split()
    chars = len(text)
    lines = len(text.split("\n"))

    return f"""Text Statistics:
Words: {len(words)}
Characters: {chars}
Lines: {lines}"""


@mcp.tool
def reverse_text(text: str) -> str:
    """Reverse the given text.

    Args:
        text: Text to reverse

    Returns:
        Reversed text
    """
    return text[::-1]


@mcp.tool
def to_uppercase(text: str) -> str:
    """Convert text to uppercase.

    Args:
        text: Text to convert

    Returns:
        Uppercase text
    """
    return text.upper()


if __name__ == "__main__":
    mcp.run(show_banner=False)
