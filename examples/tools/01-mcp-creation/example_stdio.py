import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import Client
from langchain.agents import create_agent
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI

load_dotenv()

BASE_MODEL = os.getenv("BASE_MODEL") or ""


async def main():
    server_script = Path(__file__).parent / "server_stdio.py"

    async with Client(str(server_script)) as client:
        print("Available tools:")
        tools_list = await client.list_tools()
        for tool in tools_list:
            print(f"  - {tool.name}")

        tools = await load_mcp_tools(client.session)

        llm = ChatOpenAI(model=BASE_MODEL, temperature=0)  # type: ignore

        agent = create_agent(llm, tools)

        test_pdf = Path(__file__).parent.parent.parent / "data" / "test.pdf"

        response = await agent.ainvoke(
            {
                "messages": [
                    (
                        "user",
                        f"Analyze the document structure at {test_pdf} and create laconic summary of the text.",
                    )
                ]
            }
        )

        print("Agent response:")
        for message in response["messages"]:
            if message.type == "ai" and hasattr(message, "content") and message.content:
                print(f"\n{message.content}")


if __name__ == "__main__":
    asyncio.run(main())
