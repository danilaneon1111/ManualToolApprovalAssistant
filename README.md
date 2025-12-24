# Manual Tool Approval Assistant (LangChain)

Тема: **Модель с интерактивным управлением вызовами API и функциями**  
Идея: модель может **предложить** вызов инструмента (function/tool), но решение о запуске принимает оператор (в CLI — пользователь).

## Использованные компоненты LangChain
- LLM через LangChain: `ChatOpenAI`
- PromptTemplate: `ChatPromptTemplate`
- Chain: `ManualToolApprovalChain` (Prompt -> LLM(bind_tools) + цикл подтверждения)
- Tools / Function calling: `@tool`, `bind_tools`
- Memory: `ConversationBufferMemory`

## Установка и запуск (локально)
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# заполни OPENAI_API_KEY
python -m app.main
```

## Примеры (5 тестов)
1) Пустой ввод: просто нажать Enter  
2) Вопрос без инструментов: `Объясни разницу между symmetric и asymmetric encryption`  
3) Время: `Скажи текущее время UTC` -> approve y  
4) Вычисление: `Посчитай 123*(45+6)` -> approve n (модель должна попытаться без инструмента)  
5) Некорректное выражение: `Посчитай __import__('os').system('ls')` -> tool вернёт ошибку

## Flow обработки запроса (текстовая схема)
1. Пользователь вводит запрос
2. Модель отвечает текстом или предлагает tool call
3. CLI печатает предложенный tool + args и спрашивает `Run tool? (y/n)`
4. При `y` выполняется tool и результат возвращается модели как `ToolMessage`
5. При `n` возвращается `ToolMessage` со строкой `TOOL_DENIED by operator`
6. Модель формирует финальный ответ


## Cost / лимиты (вариант: бедны студент)
- По умолчанию используется `gpt-4o-mini` (дешёвый вариант).
- В `.env` стоит ограничение `MAX_OUTPUT_TOKENS=256` — это резко снижает стоимость и риск «улететь» по токенам.
- Если ответы слишком короткие — увеличь до 400–600, но для демо обычно хватает 256.
- Логи usage можно включать/выключать через `LOG_USAGE`.
