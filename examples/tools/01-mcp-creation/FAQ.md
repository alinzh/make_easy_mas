# Вопросы и ответы: FastMCP и Model Context Protocol

Этот документ содержит вопросы и развернутые ответы для проверки понимания основ FastMCP и работы с MCP-серверами на основе примеров в этой директории.

---

## Блок 1: Основы FastMCP

### Вопрос 1: Варианты использования декоратора @mcp.tool

**Вопрос:** В файле `server.py` используется декоратор `@mcp.tool` без скобок. Какие еще варианты использования этого декоратора поддерживает FastMCP?

**Ответ:**

FastMCP поддерживает несколько вариантов использования декоратора `@mcp.tool`:

1. **Без скобок** (как в примере):
```python
@mcp.tool
def my_tool(): ...
```

2. **С пустыми скобками**:
```python
@mcp.tool()
def my_tool(): ...
```

3. **С параметрами для кастомизации**:
```python
@mcp.tool(name="custom_name")
def my_tool(): ...

@mcp.tool(tags=["production", "analytics"])
def my_tool(): ...

@mcp.tool(cache_ttl=300)  # кэширование на 5 минут
def my_tool(): ...

@mcp.tool(name="analyzer", tags=["prod"], cache_ttl=600)
def my_tool(): ...
```

Все эти варианты валидны и позволяют гибко настраивать поведение инструмента.

---

### Вопрос 2: Описание инструмента для LLM

**Вопрос:** Откуда FastMCP берет описание инструмента, которое передается языковой модели?

**Ответ:**

FastMCP автоматически извлекает описание из **docstring** функции. Docstring становится описанием инструмента, которое видит LLM.

Пример из `server.py`:

```python
@mcp.tool
def convert_document(file_path: str) -> str:
    """Convert document to Markdown format.
    
    Args:
        file_path: Path to document file (PDF, DOCX, XLSX, PPTX)
    
    Returns:
        Converted text content in Markdown format
    """
    ...
```

Модель получает:
- Название инструмента: `convert_document`
- Описание: "Convert document to Markdown format"
- Информацию об аргументах из секции `Args:`
- Информацию о возвращаемом значении из секции `Returns:`

Также можно переопределить описание через параметр декоратора:
```python
@mcp.tool(description="Custom description here")
def my_tool(): ...
```

Но приоритет всегда отдается docstring, так как она более информативна.

---

### Вопрос 3: Роль type hints в FastMCP

**Вопрос:** Зачем в `server.py` используются type hints (например, `file_path: str`)? Это только для документации?

**Ответ:**

Type hints в FastMCP выполняют критически важную роль - **автоматическую валидацию параметров**.

FastMCP автоматически генерирует JSON Schema из type hints для валидации входных данных:

```python
@mcp.tool
def process_number(value: int, name: str) -> str:
    return f"{name}: {value}"
```

Это создаст следующую схему:
```json
{
  "type": "object",
  "properties": {
    "value": {"type": "integer"},
    "name": {"type": "string"}
  },
  "required": ["value", "name"]
}
```

**Что происходит при валидации:**
- Если LLM попытается передать строку вместо числа - FastMCP вернет ошибку
- Если параметр не указан - ошибка
- Если тип не соответствует - ошибка

**Дополнительные возможности:**
```python
from typing import Optional, Literal

@mcp.tool
def advanced_tool(
    required: str,
    optional: Optional[int] = None,
    mode: Literal["fast", "accurate"] = "fast"
) -> dict:
    ...
```

Type hints обеспечивают надежность и предотвращают ошибки на этапе вызова инструмента.

---

## Блок 2: Client и архитектура

### Вопрос 4: Async context manager

**Вопрос:** Почему в `example.py` используется конструкция `async with Client(...) as client:`?

**Ответ:**

Конструкция `async with` обеспечивает **автоматическое управление жизненным циклом соединения** с MCP-сервером.

```python
async with Client(str(server_script)) as client:
    # Здесь соединение открыто
    tools_list = await client.list_tools()
    # Работаем с клиентом
# Здесь соединение автоматически закрыто
```

**Что происходит внутри:**

1. **При входе в блок (`__aenter__`):**
   - Запускается процесс сервера (если это STDIO)
   - Устанавливается соединение
   - Выполняется handshake
   - Согласуются возможности (capabilities)

2. **При выходе из блока (`__aexit__`):**
   - Корректно закрывается соединение
   - Останавливается процесс сервера
   - Освобождаются ресурсы

**Преимущества:**
- Гарантирует закрытие соединения даже при исключениях
- Предотвращает утечки ресурсов
- Избегает зависших процессов
- Обеспечивает чистый код

**Без context manager пришлось бы писать:**
```python
client = Client(str(server_script))
try:
    await client.connect()
    tools_list = await client.list_tools()
    # работа
finally:
    await client.close()
```

---

### Вопрос 5: Транспортные протоколы MCP

**Вопрос:** В примере используется `Client(str(server_script))` - путь к Python-файлу. Какой транспортный протокол используется в этом случае?

**Ответ:**

Используется транспорт **STDIO (Standard Input/Output)**.

**Как работает STDIO транспорт:**

1. Клиент запускает Python-скрипт как подпроцесс
2. Общение происходит через стандартные потоки:
   - `stdin` - клиент → сервер
   - `stdout` - сервер → клиент
   - `stderr` - логи и ошибки

```python
# STDIO транспорт (локальный)
async with Client("path/to/server.py") as client:
    # Запускается подпроцесс: python path/to/server.py
    ...
```

**Другие транспорты в FastMCP:**

**HTTP с Server-Sent Events:**
```python
# Удаленный сервер через HTTP
async with Client("http://localhost:8000/mcp") as client:
    ...
```

**Когда использовать каждый:**

| Транспорт | Использование |
|-----------|---------------|
| STDIO | Локальная разработка, тестирование, простые случаи |
| HTTP/SSE | Продакшен, удаленные серверы, микросервисы |

**Преимущества STDIO:**
- Простота развертывания
- Не нужна сетевая конфигурация
- Автоматический жизненный цикл

**Преимущества HTTP:**
- Масштабируемость
- Возможность удаленного доступа
- Load balancing
- Независимый запуск сервера

---

### Вопрос 6: Обнаружение возможностей сервера

**Вопрос:** Как клиент узнает, какие инструменты доступны на MCP-сервере?

**Ответ:**

Клиент использует метод **`list_tools()`** для обнаружения доступных инструментов:

```python
async with Client(str(server_script)) as client:
    # Получаем список всех инструментов
    tools_list = await client.list_tools()
    
    for tool in tools_list:
        print(f"  - {tool.name}")
        print(f"    Description: {tool.description}")
        print(f"    Schema: {tool.input_schema}")
```

**Другие методы обнаружения:**

```python
# Получить список ресурсов
resources = await client.list_resources()

# Получить список промптов
prompts = await client.list_prompts()
```

**Что возвращает `list_tools()`:**

Каждый инструмент содержит:
- `name` - имя инструмента
- `description` - описание из docstring
- `input_schema` - JSON Schema для валидации параметров

**Пример вывода:**
```python
[
    Tool(
        name="convert_document",
        description="Convert document to Markdown format...",
        input_schema={
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to document..."}
            },
            "required": ["file_path"]
        }
    ),
    Tool(
        name="analyze_document",
        description="Analyze document structure...",
        input_schema={...}
    )
]
```

Это стандартный механизм MCP-протокола для **автоматического обнаружения возможностей** (capability discovery).

---

## Блок 3: Интеграция и продвинутые концепции

### Вопрос 7: Синхронные и асинхронные инструменты

**Вопрос:** В `server.py` функции определены как синхронные (без `async`). Будут ли они работать с асинхронным клиентом?

**Ответ:**

Да, будут работать корректно. FastMCP **автоматически адаптирует синхронные функции** для работы в асинхронном контексте.

```python
# Синхронная функция (как в примере)
@mcp.tool
def convert_document(file_path: str) -> str:
    result = md.convert(file_path)  # блокирующая операция
    return result.text_content

# Асинхронная функция
@mcp.tool
async def fetch_data(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()
```

**Оба варианта поддерживаются!**

**Когда использовать async:**

1. **I/O операции:**
   - Сетевые запросы (HTTP, API)
   - Работа с базой данных
   - Чтение/запись больших файлов

2. **Множественные параллельные операции:**
```python
@mcp.tool
async def fetch_multiple_urls(urls: list[str]) -> list[str]:
    async with aiohttp.ClientSession() as session:
        tasks = [session.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return [await r.text() for r in responses]
```

**Когда синхронная функция подходит:**
- Быстрые CPU-bound операции
- Работа с библиотеками без async поддержки
- Простые преобразования данных

**Важно:** Для длительных блокирующих операций лучше использовать async, чтобы не блокировать event loop сервера.

---

### Вопрос 8: Кэширование результатов

**Вопрос:** Предположим, конвертация больших PDF файлов занимает много времени. Как можно кэшировать результаты между вызовами в FastMCP?

**Ответ:**

FastMCP предоставляет **встроенное кэширование** через параметр `cache_ttl`:

```python
@mcp.tool(cache_ttl=300)  # Кэш на 5 минут (300 секунд)
def convert_document(file_path: str) -> str:
    """Результат будет закэширован на 5 минут"""
    expanded_path = os.path.expanduser(file_path)
    result = md.convert(expanded_path)
    return result.text_content
```

**Как работает кэширование:**

1. Первый вызов с `file_path="/path/to/doc.pdf"`:
   - Выполняется конвертация
   - Результат сохраняется в кэш
   - Результат возвращается клиенту

2. Повторный вызов с тем же `file_path` в течение 5 минут:
   - Результат берется из кэша
   - Функция не выполняется
   - Мгновенный ответ

3. После истечения TTL:
   - Кэш инвалидируется
   - Следующий вызов выполнит функцию заново

**Другие подходы к хранению данных:**

**Context.state - для временных данных в рамках сессии:**
```python
from fastmcp import Context

@mcp.tool
def convert_with_cache(file_path: str, ctx: Context) -> str:
    # Проверяем кэш в контексте сессии
    cache_key = f"converted_{file_path}"
    
    if cache_key in ctx.state:
        return ctx.state[cache_key]
    
    # Конвертируем и сохраняем
    result = md.convert(file_path).text_content
    ctx.state[cache_key] = result
    return result
```

**Persistent storage - для долговременного хранения:**
```python
@mcp.tool
async def convert_with_persistent_cache(file_path: str, ctx: Context) -> str:
    storage = ctx.get_storage()  # Persistent storage
    
    cached = await storage.get(f"doc_{file_path}")
    if cached:
        return cached
    
    result = md.convert(file_path).text_content
    await storage.set(f"doc_{file_path}", result, ttl=3600)
    return result
```

**Сравнение подходов:**

| Метод | Область действия | Персистентность | Использование |
|-------|-----------------|----------------|---------------|
| `cache_ttl` | Все клиенты | Между запросами | Автоматическое кэширование |
| `Context.state` | Одна сессия | Пока жива сессия | Временные данные |
| Persistent storage | Все клиенты | Между перезапусками | Долговременный кэш |

**Рекомендация:** Используйте `cache_ttl` - это самый простой и эффективный способ.

---

### Вопрос 9: Управление доступностью инструментов

**Вопрос:** Как сделать так, чтобы инструмент `analyze_document` был доступен только в production-окружении?

**Ответ:**

FastMCP поддерживает **систему тегов** для гибкого управления доступностью инструментов:

```python
from fastmcp import FastMCP
import os

mcp = FastMCP("Document Converter")

@mcp.tool
def convert_document(file_path: str) -> str:
    """Доступен всегда"""
    return md.convert(file_path).text_content

@mcp.tool(tags=["production"])
def analyze_document(file_path: str) -> str:
    """Доступен только в production"""
    content = md.convert(file_path).text_content
    return f"Stats: {len(content)} chars"

@mcp.tool(tags=["development", "debug"])
def debug_document(file_path: str) -> str:
    """Доступен только в development"""
    return f"Debug info for {file_path}"

if __name__ == "__main__":
    # Получаем окружение из переменной
    env = os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        mcp.run(enabled_tags=["production"])
    else:
        mcp.run(enabled_tags=["development", "debug"])
```

**Множественные теги:**
```python
@mcp.tool(tags=["production", "analytics", "premium"])
def advanced_analytics(file_path: str) -> dict:
    """Требует все три тега"""
    ...

# Запуск с несколькими тегами
mcp.run(enabled_tags=["production", "analytics", "premium"])
```

**Динамическое управление:**
```python
import os

def get_enabled_tags() -> list[str]:
    tags = ["base"]
    
    if os.getenv("ENABLE_ANALYTICS") == "true":
        tags.append("analytics")
    
    if os.getenv("PREMIUM_MODE") == "true":
        tags.append("premium")
    
    return tags

mcp.run(enabled_tags=get_enabled_tags())
```

**Другой подход - условное определение:**
```python
import os

mcp = FastMCP("Document Converter")

# Всегда доступен
@mcp.tool
def convert_document(file_path: str) -> str:
    ...

# Условно определяем инструмент
if os.getenv("ENVIRONMENT") == "production":
    @mcp.tool
    def analyze_document(file_path: str) -> str:
        ...
```

**Рекомендация:** Используйте теги - это более гибкий и декларативный подход.

---

## Блок 4: Практическое применение

### Вопрос 11: Когда использовать Resources вместо Tools

**Вопрос:** В текущем примере используются только tools. В каких случаях лучше использовать resources?

**Ответ:**

**Resources** и **Tools** решают разные задачи:

**Tools** - для выполнения **действий**:
- Изменение данных
- Вызов внешних API
- Выполнение вычислений
- Преобразование данных

**Resources** - для предоставления **данных**:
- Чтение файлов
- Доступ к конфигурации
- Запросы к БД
- Статический контент

**Пример текущего tool:**
```python
@mcp.tool
def convert_document(file_path: str) -> str:
    """Выполняет действие - конвертацию"""
    return md.convert(file_path).text_content
```

**Как это можно реализовать через resource:**
```python
@mcp.resource("document://content/{file_path}")
def get_document_content(file_path: str) -> str:
    """Предоставляет доступ к содержимому документа"""
    return md.convert(file_path).text_content

# Клиент обращается к ресурсу:
# content = await client.read_resource("document://content/test.pdf")
```

**Практические примеры Resources:**

**1. Конфигурационные данные:**
```python
@mcp.resource("config://settings")
def get_settings() -> dict:
    return {
        "max_file_size": 10_000_000,
        "supported_formats": ["pdf", "docx", "xlsx"],
        "cache_ttl": 300
    }
```

**2. Список доступных документов:**
```python
@mcp.resource("documents://list")
def list_documents() -> list[str]:
    docs_dir = Path("./documents")
    return [str(f) for f in docs_dir.glob("*.pdf")]
```

**3. Метаданные документа:**
```python
@mcp.resource("document://metadata/{file_path}")
def get_metadata(file_path: str) -> dict:
    stat = os.stat(file_path)
    return {
        "size": stat.st_size,
        "modified": stat.st_mtime,
        "name": Path(file_path).name
    }
```

**4. Динамический контент с параметрами:**
```python
@mcp.resource("logs://{service}/{date}")
def get_logs(service: str, date: str) -> str:
    log_file = f"/var/log/{service}/{date}.log"
    return Path(log_file).read_text()
```

**Когда использовать Resources:**
- Модель нуждается в контекстных данных для ответа
- Данные читаются часто, но меняются редко
- Нужно предоставить доступ к файловой системе или БД
- Данные имеют древовидную структуру (URI схема)

**Когда использовать Tools:**
- Нужно выполнить операцию с побочными эффектами
- Требуется параметризованная логика
- Операция может завершиться ошибкой
- Результат зависит от внешних факторов

**Можно комбинировать:**
```python
# Resource - для чтения
@mcp.resource("document://{file_path}")
def read_document(file_path: str) -> str:
    return Path(file_path).read_text()

# Tool - для анализа
@mcp.tool
def analyze_document(file_path: str) -> dict:
    content = Path(file_path).read_text()
    return {"words": len(content.split()), "lines": len(content.split("\n"))}
```

---

### Вопрос 12: Структурированный вывод с Pydantic

**Вопрос:** Как улучшить инструмент `analyze_document`, чтобы он возвращал структурированные данные вместо форматированной строки?

**Ответ:**

Текущая реализация возвращает строку:
```python
@mcp.tool
def analyze_document(file_path: str) -> str:
    # ...
    return f"""Document: {Path(file_path).name}
Size: {chars} chars, {words} words
Lines: {len(lines)}"""
```

**Проблемы:**
- Клиент должен парсить строку
- Нет гарантий структуры
- Сложно извлекать отдельные значения
- LLM тратит токены на парсинг

**Решение 1: Использовать словарь (простой способ)**
```python
@mcp.tool
def analyze_document(file_path: str) -> dict:
    """Analyze document structure and return statistics.
    
    Args:
        file_path: Path to document file
    
    Returns:
        Dictionary with document statistics
    """
    expanded_path = os.path.expanduser(file_path)
    content = md.convert(expanded_path).text_content
    
    lines = content.split("\n")
    words = content.split()
    
    return {
        "name": Path(file_path).name,
        "size_chars": len(content),
        "size_words": len(words),
        "lines_count": len(lines),
        "has_content": bool(content.strip())
    }
```

**Решение 2: Pydantic модель (рекомендуется)**
```python
from pydantic import BaseModel, Field

class DocumentStatistics(BaseModel):
    """Статистика документа"""
    name: str = Field(description="Имя файла")
    size_chars: int = Field(description="Количество символов")
    size_words: int = Field(description="Количество слов")
    lines_count: int = Field(description="Количество строк")
    has_content: bool = Field(description="Есть ли содержимое")
    avg_word_length: float = Field(description="Средняя длина слова")

@mcp.tool(output_schema=DocumentStatistics)
def analyze_document(file_path: str) -> DocumentStatistics:
    """Analyze document structure and return statistics.
    
    Args:
        file_path: Path to document file
    
    Returns:
        Structured document statistics
    """
    expanded_path = os.path.expanduser(file_path)
    content = md.convert(expanded_path).text_content
    
    lines = content.split("\n")
    words = content.split()
    
    avg_length = sum(len(w) for w in words) / len(words) if words else 0
    
    return DocumentStatistics(
        name=Path(file_path).name,
        size_chars=len(content),
        size_words=len(words),
        lines_count=len(lines),
        has_content=bool(content.strip()),
        avg_word_length=round(avg_length, 2)
    )
```

**Преимущества Pydantic:**

1. **Валидация типов:**
```python
# Это вызовет ошибку на этапе возврата
return DocumentStatistics(
    name="doc.pdf",
    size_chars="not a number"  # ❌ Ошибка: ожидается int
)
```

2. **Автоматическая генерация JSON Schema:**
FastMCP автоматически добавит схему в описание инструмента для LLM.

3. **Документирование полей:**
```python
class DetailedStats(BaseModel):
    name: str = Field(description="Имя файла", examples=["document.pdf"])
    size: int = Field(description="Размер в байтах", ge=0)  # >= 0
    created: datetime = Field(description="Дата создания")
```

4. **Вложенные структуры:**
```python
class PageStats(BaseModel):
    number: int
    word_count: int

class DocumentStatistics(BaseModel):
    name: str
    total_pages: int
    pages: list[PageStats]  # Вложенная структура
```

5. **Сериализация:**
```python
stats = analyze_document("test.pdf")
# Легко преобразуется в JSON
json_str = stats.model_dump_json()
dict_data = stats.model_dump()
```

**Сравнение подходов:**

| Подход | Простота | Валидация | Документация | Рекомендуется |
|--------|----------|-----------|--------------|---------------|
| Строка | ⭐⭐⭐ | ❌ | ❌ | Для простых случаев |
| Dict | ⭐⭐ | ❌ | ⚠️ | Для прототипов |
| Pydantic | ⭐ | ✅ | ✅ | Для продакшена |

**Рекомендация:** Используйте Pydantic для всех инструментов, возвращающих сложные данные.

---

## Дополнительные вопросы

### Вопрос 13: Интеграция с LangChain

**Вопрос:** Что делает функция `load_mcp_tools(client.session)` в примере `example.py`?

**Ответ:**

Функция `load_mcp_tools()` из пакета `langchain_mcp_adapters` преобразует MCP-инструменты в формат **LangChain Tools**, что позволяет использовать любые MCP-серверы с LangChain агентами.

**Как это работает:**

```python
from langchain_mcp_adapters.tools import load_mcp_tools
from fastmcp import Client

async with Client(str(server_script)) as client:
    # 1. Клиент подключается к MCP-серверу
    
    # 2. load_mcp_tools преобразует MCP tools → LangChain tools
    tools = await load_mcp_tools(client.session)
    
    # 3. Теперь tools можно использовать с LangChain
    llm = ChatOpenAI(model="gpt-4")
    agent = create_agent(llm, tools)
    
    # 4. Агент вызывает инструменты через MCP-протокол
    response = await agent.ainvoke({"messages": [("user", "Convert test.pdf")]})
```

**Что происходит внутри:**

1. **Обнаружение инструментов:**
   - `load_mcp_tools` вызывает `client.list_tools()`
   - Получает список всех доступных MCP-инструментов

2. **Преобразование:**
   ```python
   # MCP Tool
   {
       "name": "convert_document",
       "description": "Convert document to Markdown",
       "input_schema": {...}
   }
   
   # Становится LangChain Tool
   class ConvertDocumentTool(BaseTool):
       name = "convert_document"
       description = "Convert document to Markdown"
       args_schema = PydanticSchemaFromMCP(...)
       
       def _run(self, file_path: str) -> str:
           return mcp_client.call_tool("convert_document", {"file_path": file_path})
   ```

3. **Адаптация вызовов:**
   - LangChain агент вызывает инструмент
   - Адаптер преобразует вызов в MCP-запрос
   - Отправляет через `client.session`
   - Возвращает результат агенту

**Преимущества:**
- Один раз написанный MCP-сервер работает с любыми LangChain агентами
- Не нужно переписывать инструменты для LangChain
- Можно комбинировать MCP-инструменты с нативными LangChain tools
- Поддержка всех возможностей MCP (кэширование, валидация и т.д.)

---

### Вопрос 14: Обработка падения сервера

**Вопрос:** Что произойдет, если MCP-сервер упадет во время работы клиента? Как это обработать?

**Ответ:**

При использовании `async with` клиент автоматически обработает ошибки соединения:

```python
try:
    async with Client(server_path) as client:
        # Работа с клиентом
        result = await client.call_tool("convert_document", {"file_path": "test.pdf"})
except ConnectionError as e:
    print(f"Сервер недоступен: {e}")
except TimeoutError as e:
    print(f"Таймаут соединения: {e}")
except Exception as e:
    print(f"Ошибка: {e}")
```

**Стратегии обработки:**

**1. Retry с экспоненциальным backoff:**
```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def call_mcp_with_retry(server_path: str, tool_name: str, args: dict):
    async with Client(server_path) as client:
        return await client.call_tool(tool_name, args)

# Использование
try:
    result = await call_mcp_with_retry(
        "server.py",
        "convert_document",
        {"file_path": "test.pdf"}
    )
except Exception as e:
    print(f"Все попытки исчерпаны: {e}")
```

**2. Fallback механизм:**
```python
async def call_with_fallback(primary_server: str, fallback_server: str):
    try:
        async with Client(primary_server) as client:
            return await client.call_tool("convert_document", {"file_path": "test.pdf"})
    except Exception as e:
        print(f"Первичный сервер недоступен, используем fallback: {e}")
        async with Client(fallback_server) as client:
            return await client.call_tool("convert_document", {"file_path": "test.pdf"})
```

**3. Health check:**
```python
async def check_server_health(server_path: str) -> bool:
    try:
        async with Client(server_path) as client:
            tools = await client.list_tools()
            return len(tools) > 0
    except:
        return False

# Использование
if await check_server_health("server.py"):
    async with Client("server.py") as client:
        # Работа с сервером
        ...
else:
    print("Сервер недоступен")
```

**Для продакшена рекомендуется:**

1. **Использовать HTTP транспорт** вместо STDIO:
```python
# Сервер под управлением systemd/docker/kubernetes
async with Client("http://mcp-server:8000/mcp") as client:
    ...
```

2. **Настроить автоперезапуск:**
```yaml
# docker-compose.yml
services:
  mcp-server:
    image: mcp-server:latest
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

3. **Мониторинг:**
```python
import logging

logging.basicConfig(level=logging.INFO)

async with Client(server_path) as client:
    logging.info("Connected to MCP server")
    try:
        result = await client.call_tool(...)
        logging.info(f"Tool executed successfully: {result}")
    except Exception as e:
        logging.error(f"Tool execution failed: {e}", exc_info=True)
```

4. **Circuit breaker:**
```python
from pybreaker import CircuitBreaker

breaker = CircuitBreaker(fail_max=5, timeout_duration=60)

@breaker
async def call_mcp_tool(server_path: str, tool_name: str, args: dict):
    async with Client(server_path) as client:
        return await client.call_tool(tool_name, args)

# После 5 неудачных попыток circuit breaker откроется
# и не будет пытаться вызывать сервер в течение 60 секунд
```

---

## Практические задания

После изучения материала попробуйте:

1. **Добавить новый tool** в `server.py` для подсчета количества слов в документе
2. **Создать resource** для предоставления списка поддерживаемых форматов документов
3. **Реализовать structured output** с Pydantic для `analyze_document`
4. **Добавить кэширование** для `convert_document` с TTL 5 минут
5. **Использовать теги** для разделения инструментов по окружениям (dev/prod)
6. **Обработать ошибки** с помощью структурированных ответов
7. **Создать асинхронный tool** для параллельной обработки нескольких документов

---

## Полезные ссылки

- [FastMCP документация](https://gofastmcp.com)
- [MCP спецификация](https://modelcontextprotocol.io)
- [Примеры MCP-серверов](https://github.com/modelcontextprotocol/servers)
- [LangChain MCP Adapters](https://github.com/langchain-ai/langchain-mcp)
