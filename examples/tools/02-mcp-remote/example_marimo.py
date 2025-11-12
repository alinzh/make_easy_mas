import marimo

__generated_with = "0.9.30"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo

    return (mo,)


@app.cell
def __(mo):
    mo.md(
        """
        # Часть 3: Использование готовых MCP-серверов

        В этом примере мы используем готовый сервер `mcp-server-fetch` из официального репозитория Model Context Protocol.

        Вместо написания собственного кода для работы с веб-страницами, мы просто устанавливаем пакет и подключаем его.
        """
    )
    return


@app.cell
def __(mo):
    mo.md("## Шаг 1: Импорты и настройка")
    return


@app.cell
def __():
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
    return (
        BASE_MODEL,
        ChatOpenAI,
        Client,
        StdioTransport,
        asyncio,
        create_agent,
        load_dotenv,
        load_mcp_tools,
        os,
    )


@app.cell
def __(mo):
    mo.md(
        """
        ## Шаг 2: О сервере mcp-server-fetch

        Этот сервер из [официального репозитория MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch) предоставляет:

        - Загрузку веб-страниц через инструмент `fetch`
        - Конвертацию HTML в markdown для удобной обработки моделями
        - Параметры для контроля размера и чтения контента по частям

        Установка: `uvx mcp-server-fetch` (или через npm/pip)
        """
    )
    return


@app.cell
def __(mo):
    mo.md(
        """
        ## Шаг 3: Подключение готового сервера

        Создаем транспорт, который запускает сервер через `uvx`.
        Процесс подключения идентичен собственным серверам.
        """
    )
    return


@app.cell
def __(
    BASE_MODEL,
    ChatOpenAI,
    Client,
    StdioTransport,
    create_agent,
    load_mcp_tools,
):
    async def main():
        transport = StdioTransport(command="uvx", args=["mcp-server-fetch"])

        async with Client(transport) as client:
            print("Available tools:")
            tools_list = await client.list_tools()
            for tool in tools_list:
                print(f"  - {tool.name}")

            tools = await load_mcp_tools(client.session)

            llm = ChatOpenAI(model=BASE_MODEL, temperature=0)

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
                if (
                    message.type == "ai"
                    and hasattr(message, "content")
                    and message.content
                ):
                    print(f"\n{message.content}")

    return (main,)


@app.cell
def __(mo):
    mo.md("## Шаг 4: Запуск")
    return


@app.cell
def __(asyncio, main):
    asyncio.run(main())
    return


@app.cell
def __(mo):
    mo.md(
        """
        ## Экосистема MCP и открытость

        MCP построен на принципах open source. Существуют репозитории с готовыми серверами:

        - [Docker Hub MCP](https://hub.docker.com/mcp/explore)
        - [Glama MCP Servers](https://glama.ai/mcp/servers)
        - Научные инструменты: [academia_mcp](https://github.com/IlyaGusev/academia_mcp)

        Вы можете:
        - Использовать готовые решения других разработчиков
        - Публиковать свои серверы для сообщества
        - Контрибутить в существующие проекты

        Открытость MCP означает возможность изучать/модифицировать любой сервер.
        """
    )
    return


if __name__ == "__main__":
    app.run()
