import asyncio
import os
from pathlib import Path

from fastmcp import FastMCP
from markitdown import MarkItDown
from math_server import mcp as math_server  # type: ignore
from text_server import mcp as text_server  # type: ignore

mcp = FastMCP("Combined Multi-Server Hub")
md = MarkItDown()


@mcp.tool
def convert_document(file_path: str) -> str:
    """Convert document to Markdown format.

    Args:
        file_path: Path to document file (PDF, DOCX, XLSX, PPTX)

    Returns:
        Converted text content in Markdown format
    """
    expanded_path = os.path.expanduser(file_path)
    result = md.convert(expanded_path)
    return result.text_content


@mcp.tool
def analyze_document(file_path: str) -> str:
    """Analyze document structure and return statistics.

    Args:
        file_path: Path to document file

    Returns:
        Document statistics (word count, lines, headers)
    """
    expanded_path = os.path.expanduser(file_path)
    content = md.convert(expanded_path).text_content

    lines = content.split("\n")
    words = len(content.split())
    chars = len(content)

    return f"""Document: {Path(file_path).name}
Size: {chars} chars, {words} words
Lines: {len(lines)}"""


async def setup():
    await mcp.import_server(math_server)
    await mcp.import_server(text_server)


if __name__ == "__main__":
    asyncio.run(setup())
    mcp.run(transport="stdio", show_banner=False)
