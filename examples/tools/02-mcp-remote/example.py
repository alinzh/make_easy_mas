import asyncio
import os

from dotenv import load_dotenv
from fastmcp import Client
from fastmcp.client.transports import NpxStdioTransport
from langchain.agents import create_agent
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI

load_dotenv()

BASE_MODEL = os.getenv("BASE_MODEL") or ""
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


async def main():
    if not TAVILY_API_KEY:
        print("Error: TAVILY_API_KEY not found in environment variables")
        print("Get your API key from: https://tavily.com")
        return

    transport = NpxStdioTransport(
        package="tavily-mcp@latest",
        env_vars={"TAVILY_API_KEY": TAVILY_API_KEY},
    )

    async with Client(transport) as client:
        print("Available tools:")
        tools_list = await client.list_tools()
        for tool in tools_list:
            print(f"  - {tool.name}")

        tools = await load_mcp_tools(client.session)

        llm = ChatOpenAI(model=BASE_MODEL, temperature=0)  # type: ignore

        agent = create_agent(llm, tools)

        response = await agent.ainvoke(
            {"messages": [("user", "Last 10 news about AI")]}
        )

        print("Agent response:")
        for message in response["messages"]:
            if message.type == "ai" and hasattr(message, "content") and message.content:
                print(f"\n{message.content}")


if __name__ == "__main__":
    asyncio.run(main())
