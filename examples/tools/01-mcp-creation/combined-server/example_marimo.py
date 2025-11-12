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
        # Комбинирование нескольких MCP-серверов

        FastMCP позволяет объединять несколько независимых серверов в один через метод `import_server()`.

        Это позволяет строить модульные системы, где каждый сервер отвечает за свою область, но все они доступны через единую точку входа.
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
        ## Шаг 2: Структура комбинированного сервера

        У нас есть три файла:

        - `math_server.py` - инструменты для математики (calculate, factorial)
        - `text_server.py` - инструменты для текста (count_words, reverse_text, to_uppercase)
        - `server_combined.py` - главный сервер, который импортирует оба через `mcp.import_server()`

        Каждый сервер независим и может использоваться отдельно, но в комбинированном они работают вместе.
        """
    )
    return


@app.cell
def __(mo):
    mo.md(
        """
        ## Шаг 3: Как работает import_server()

        В `server_combined.py` есть функция setup():

        ```python
        async def setup():
            await mcp.import_server(math_server)
            await mcp.import_server(text_server)
        ```

        Эта функция берет все инструменты из импортированных серверов и переносит их в главный сервер.
        """
    )
    return


@app.cell
def __(mo):
    mo.md(
        """
        ## Шаг 4: Подключение и использование

        Для агента все инструменты выглядят как единый набор возможностей.
        """
    )
    return


@app.cell
def __(BASE_MODEL, ChatOpenAI, Client, Path, create_agent, load_mcp_tools):
    async def main():
        server_script = Path("server_combined.py")

        async with Client(str(server_script)) as client:
            print("Available tools from combined server:")
            tools_list = await client.list_tools()
            for tool in tools_list:
                print(f"  - {tool.name}")

            tools = await load_mcp_tools(client.session)

            llm = ChatOpenAI(model=BASE_MODEL, temperature=0)

            agent = create_agent(llm, tools)

            test_pdf = Path("../../../data/test.pdf")

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
                if (
                    message.type == "ai"
                    and hasattr(message, "content")
                    and message.content
                ):
                    print(f"\n{message.content}")

    return (main,)


@app.cell
def __(mo):
    mo.md("## Шаг 5: Запуск")
    return


@app.cell
def __(asyncio, main):
    asyncio.run(main())
    return


@app.cell
def __(mo):
    mo.md(
        """
        ## Преимущества модульной архитектуры

        - **Переиспользуемость**: базовые серверы можно использовать в разных проектах
        - **Тестируемость**: каждый сервер тестируется отдельно
        - **Поддерживаемость**: изменения в одном сервере не затрагивают другие
        - **Гибкость**: можно комбинировать серверы в разных конфигурациях

        Такой подход позволяет строить библиотеку переиспользуемых компонентов.
        """
    )
    return


if __name__ == "__main__":
    app.run()
