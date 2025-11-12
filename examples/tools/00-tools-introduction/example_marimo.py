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
        # Часть 1: Основы Tool Calling для LLM-агентов

        В этой части мастер-класса мы разберем, как языковые модели могут вызывать внешние функции и взаимодействовать с окружением. Вы узнаете о механизме tool calling на фундаментальном уровне.
        """
    )
    return


@app.cell
def __(mo):
    mo.md(
        """
        ## Структурированный вывод - основа tool calling

        Прежде чем разбирать работу с инструментами, важно понять ключевую концепцию - структурированный вывод.

        По умолчанию языковая модель возвращает обычный текст, который удобен для чтения человеком, но плох для программной обработки. Структурированный вывод - это когда модель возвращает данные в строго определенном формате, например JSON.

        Именно это позволяет автоматически парсить ответ модели, извлекать нужные поля и на их основе принимать решения - например, какую функцию вызвать и с какими параметрами. Без структурированного вывода механизм tool calling просто не смог бы работать.
        """
    )
    return


@app.cell
def __(mo):
    mo.md(
        """
        ## Три этапа работы с инструментами

        Работу с инструментами можно разбить на три ключевых этапа:

        1. **Определение инструмента** - описание возможностей
        2. **Вызов инструмента** - выбор и вызов модель
        3. **Возврат результата** - обработка и передача данных обратно модели

        На каждом из этих этапов используется структурированный вывод.
        """
    )
    return


@app.cell
def __(mo):
    mo.md(
        """
        ## Этап 1: Определение инструмента

        Инструмент описывается в виде JSON-схемы с ключевыми параметрами:

        - **name** - имя инструмента
        - **description** - описание работы (зачем использовать, в каких ситуациях)
        - **input_schema** - требуемые и опциональные параметры инструмента

        LLM на этапе fine-tuning обучалась вызову инструментов по заданному протоколу. Модель "понимает", что когда она видит такое описание, она может использовать этот инструмент для решения задачи.
        """
    )
    return


@app.cell
def __(mo):
    mo.md(
        """
        Пример определения инструмента в JSON:

        ```json
        {
          "name": "get_weather",
          "description": "Получает текущую погоду для указанного города",
          "input_schema": {
            "type": "object",
            "properties": {
              "city": {
                "type": "string",
                "description": "Название города"
              },
              "units": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "Единицы измерения температуры"
              }
            },
            "required": ["city"]
          }
        }
        ```
        """
    )
    return


@app.cell
def __(mo):
    mo.md(
        """
        ## Этап 2: Вызов инструмента

        Модель возвращает JSON с названием функции и параметрами. Важно понимать: сам по себе JSON от модели не вызывает никакую функцию. Это просто структурированный текст.

        Нужен отдельный интерпретатор, который:
        1. Распарсит JSON от модели
        2. Найдет соответствующую Python-функцию
        3. Подставит параметры
        4. Выполнит функцию
        5. Вернет результат

        Хорошая новость: вам не нужно писать интерпретатор самостоятельно. Агентские фреймворки (LangChain, LangGraph, Pydantic AI) предоставляют готовый функционал.
        """
    )
    return


@app.cell
def __(mo):
    mo.md(
        """
        Пример полного цикла:

        ```python
        # 1. Модель возвращает структурированный вывод
        model_response = {
            "tool_use": {
                "id": "call_123",
                "name": "get_weather",
                "input": {"city": "Москва"}
            }
        }

        # 2. Функция-инструмент
        def get_weather(city: str) -> str:
            return f"Температура в {city}: +5°C, облачно"

        # 3. Интерпретатор вызывает функцию
        result = get_weather(**model_response["tool_use"]["input"])

        # 4. Результат отправляется обратно модели
        tool_result = {
            "tool_result": {
                "call_id": "call_123",
                "content": result
            }
        }
        ```
        """
    )
    return


@app.cell
def __(mo):
    mo.md(
        """
        ## Этап 3: Возврат результата

        Python-функция может вернуть простой текст, JSON или сложные объекты. Рекомендуется возвращать структурированные данные (JSON), так модели проще их обрабатывать.

        Модель получает результат и может:
        - Вызвать еще один инструмент
        - Вернуть окончательный ответ пользователю
        - Продолжить до достижения максимального количества итераций
        """
    )
    return


@app.cell
def __(mo):
    mo.md("## Практический пример с LangChain")
    return


@app.cell
def __(mo):
    mo.md("### Шаг 1: Импорты и настройка")
    return


@app.cell
def __():
    import os
    from pathlib import Path

    from dotenv import load_dotenv
    from langchain.agents import create_agent
    from langchain.tools import tool
    from langchain_openai import ChatOpenAI
    from markitdown import MarkItDown

    load_dotenv()

    BASE_MODEL = os.getenv("BASE_MODEL") or ""
    return BASE_MODEL, ChatOpenAI, MarkItDown, Path, create_agent, load_dotenv, os, tool


@app.cell
def __(mo):
    mo.md(
        """
        ### Шаг 2: Создание инструмента

        Используем декоратор `@tool` из LangChain. Под капотом LangChain создает JSON-описание функции с параметрами и типами, которое передается модели.
        """
    )
    return


@app.cell
def __(MarkItDown, os, tool):
    md = MarkItDown()

    @tool
    def convert_to_markdown(file_path: str) -> str:
        """Extract text information from a document file into markdown format.

        Args:
            file_path: Path to document file (PDF, DOCX, XLSX, PPTX)

        Returns:
            Converted text content in Markdown format
        """
        try:
            expanded_path = os.path.expanduser(file_path)
            result = md.convert(expanded_path)
            return result.text_content
        except Exception as e:
            return f"ошибка конвертации: {str(e)}"

    return convert_to_markdown, md


@app.cell
def __(mo):
    mo.md(
        """
        ### Шаг 3: Создание агента

        Агент получает список инструментов и может выбирать, какой из них использовать для решения задачи.
        """
    )
    return


@app.cell
def __(BASE_MODEL, ChatOpenAI, convert_to_markdown, create_agent):
    tools = [convert_to_markdown]

    llm = ChatOpenAI(model=BASE_MODEL, temperature=0)

    graph = create_agent(llm, tools)
    return graph, llm, tools


@app.cell
def __(mo):
    mo.md(
        """
        ### Шаг 4: Запуск агента

        Даем агенту задачу проанализировать документ. Агент:
        1. Видит описание инструмента `convert_to_markdown`
        2. Решает, что нужно вызвать этот инструмент
        3. Возвращает структурированный JSON с названием функции и параметрами
        4. LangChain вызывает функцию и передает результат обратно модели
        5. Модель формирует финальный ответ
        """
    )
    return


@app.cell
def __(Path, graph):
    test_pdf = Path("../../data/test.pdf")

    result = graph.invoke(
        {
            "messages": [
                (
                    "user",
                    f"Analyze the document at {test_pdf} and tell me what it contains. Create an table .md .",
                )
            ]
        }
    )

    print("Result:")
    for message in result["messages"]:
        if hasattr(message, "content") and message.content:
            print(f"{message.type}: {message.content}")
    return message, result, test_pdf


@app.cell
def __(mo):
    mo.md(
        """
        ## Ограничения текущего подхода

        При работе с инструментами напрямую (без стандартизации) возникают проблемы:

        **1. Отсутствие переиспользуемости**
        Инструмент, написанный для одной модели или фреймворка, не работает с другими без переписывания.

        **2. Нет стандарта обнаружения**
        Каждый раз нужно вручную регистрировать инструменты и описывать их в правильном формате.

        **3. Проблемы с безопасностью**
        Нет встроенных механизмов для валидации параметров, контроля доступа, аудита вызовов и изоляции между инструментами.

        **4. Сложность масштабирования**
        При росте количества инструментов сложно управлять их описаниями, обеспечивать консистентность, версионировать изменения и тестировать взаимодействия.
        """
    )
    return


@app.cell
def __(mo):
    mo.md(
        """
        ## Что дальше?

        Механизм tool calling предоставляет языковым моделям большие возможности по работе с окружением, но подход с "ручным" определением инструментов имеет серьезные ограничения.

        В следующей части мы познакомимся с **Model Context Protocol (MCP)** - открытым стандартом, который решает все перечисленные проблемы и предоставляет унифицированный способ работы с инструментами, ресурсами и промптами для LLM-агентов.

        MCP использует те же три этапа, но добавляет:
        - Стандартизированный протокол обмена сообщениями
        - Автоматическое обнаружение возможностей
        - Встроенную валидацию и безопасность
        - Возможность переиспользования инструментов между проектами
        """
    )
    return


if __name__ == "__main__":
    app.run()
