import asyncio
import os

from dotenv import load_dotenv
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
from langchain.agents import create_agent
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI

load_dotenv()

BASE_MODEL = os.getenv("BASE_MODEL") or ""


async def main():
    transport = StdioTransport(command="uvx", args=["mcp-server-fetch"])

    async with Client(transport) as client:
        print("Available tools:")
        tools_list = await client.list_tools()
        for tool in tools_list:
            print(f"  - {tool.name}")

        tools = await load_mcp_tools(client.session)

        llm = ChatOpenAI(model=BASE_MODEL, temperature=0)  # type: ignore

        agent = create_agent(llm, tools)

        response = await agent.ainvoke(
            {
                "messages": [
                    (
                        "user",
                        "Fetch the content from https://docs.langchain.com/oss/python/langgraph/overview and summarize key points",
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
