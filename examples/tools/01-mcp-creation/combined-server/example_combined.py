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
    server_script = Path(__file__).parent / "server_combined.py"

    async with Client(str(server_script)) as client:
        print("Available tools from combined server:")
        tools_list = await client.list_tools()
        for tool in tools_list:
            print(f"  - {tool.name}")

        tools = await load_mcp_tools(client.session)

        llm = ChatOpenAI(model=BASE_MODEL, temperature=0)  # type: ignore

        agent = create_agent(llm, tools)

        # Пример комплексной задачи, использующей инструменты из разных групп
        test_pdf = Path(__file__).parent.parent.parent.parent / "data" / "test.pdf"

        response = await agent.ainvoke(
            {
                "messages": [
                    (
                        "user",
                        f"""Perform a multi-step analysis:
1. Get statistics about the document at {test_pdf}
2. Calculate the factorial of the word count
3. Reverse the document name

Please execute all these tasks and present the results clearly.""",
                    )
                ]
            }
        )

        print("\nAgent response:")
        for message in response["messages"]:
            if message.type == "ai" and hasattr(message, "content") and message.content:
                print(f"\n{message.content}")


if __name__ == "__main__":
    asyncio.run(main())
