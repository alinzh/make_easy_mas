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
        # Часть 2: Создание собственного MCP-сервера

        В этом примере мы создадим собственный MCP-сервер с использованием FastMCP и подключим его к агенту через STDIO транспорт.

        MCP решает проблемы обычного tool calling через стандартизацию и переиспользуемость.
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
    from pathlib import Path

    from dotenv import load_dotenv
    from fastmcp import Client
    from langchain.agents import create_agent
    from langchain_mcp_adapters.tools import load_mcp_tools
    from langchain_openai import ChatOpenAI

    load_dotenv()

    BASE_MODEL = os.getenv("BASE_MODEL") or ""
    return (
        BASE_MODEL,
        ChatOpenAI,
        Client,
        Path,
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
        ## Шаг 2: Структура MCP-сервера

        Наш сервер находится в файле `server_stdio.py`. Он использует FastMCP и предоставляет два инструмента:

        - `convert_document` - конвертирует документы в markdown
        - `analyze_document` - возвращает статистику о документе

        Сервер запускается как отдельный процесс и общается через STDIO транспорт.
        """
    )
    return


@app.cell
def __(mo):
    mo.md(
        """
        ## Шаг 3: Подключение к серверу

        Создаем клиент, который подключается к нашему серверу через STDIO.
        Сервер автоматически предоставляет список своих инструментов через `tools/list`.
        """
    )
    return


@app.cell
def __(BASE_MODEL, ChatOpenAI, Client, Path, create_agent, load_mcp_tools):
    async def main():
        server_script = Path("server_stdio.py")

        async with Client(str(server_script)) as client:
            print("Available tools:")
            tools_list = await client.list_tools()
            for tool in tools_list:
                print(f"  - {tool.name}")

            tools = await load_mcp_tools(client.session)

            llm = ChatOpenAI(model=BASE_MODEL, temperature=0)

            agent = create_agent(llm, tools)

            test_pdf = Path("../../data/test.pdf")

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
                if (
                    message.type == "ai"
                    and hasattr(message, "content")
                    and message.content
                ):
                    print(f"\n{message.content}")

    return (main,)


@app.cell
def __(mo):
    mo.md(
        """
        ## Шаг 4: Запуск примера

        Выполним асинхронную функцию main для взаимодействия с сервером.
        """
    )
    return


@app.cell
def __(asyncio, main):
    asyncio.run(main())
    return


@app.cell
def __(mo):
    mo.md(
        """
        ## Преимущества MCP

        По сравнению с обычным tool calling, MCP предоставляет:

        - **Стандартизацию**: один сервер работает с любыми совместимыми клиентами
        - **Автоматическое обнаружение**: клиент узнает о возможностях через `tools/list`
        - **Переиспользуемость**: сервер можно использовать в разных проектах без изменений
        - **Изоляцию**: сервер работает в отдельном процессе
        - **Масштабируемость**: легко добавлять новые инструменты и развертывать удаленно
        """
    )
    return


if __name__ == "__main__":
    app.run()
