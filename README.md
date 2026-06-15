# GPT Image 2 Polza MCP Server

MCP-сервер для генерации и редактирования изображений моделью **GPT Image 2**
через API-провайдера [Polza](https://polza.ai).

- Провайдер: `Polza`
- Model ID: `openai/gpt-5.4-image-2`
- Model tier: `gpt-image-2`
- Поддержка генерации, редактирования и референсных изображений
- Сохранение полноразмерных файлов на диск
- Возврат превью и структурированных метаданных через MCP

Для работы нужен только `POLZA_AI_API_KEY`. Отдельный ключ OpenAI не требуется.

## Инструменты MCP

- `generate_image` — создаёт или редактирует изображения с помощью GPT Image 2.
- `fetch_generation` — получает результат уже запущенной генерации по `gen_...` ID.
- `upload_file` — загружает референс в Polza Storage.
- `show_output_stats` — показывает статистику локальной папки с результатами.
- `maintenance` — обслуживает локальный кэш и базу метаданных.

## Требования

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- Аккаунт Polza и `POLZA_AI_API_KEY`
- Любой MCP-клиент: Claude Code, Claude Desktop, Cursor, VS Code или другой

## Быстрая установка

Клонируйте репозиторий:

```bash
git clone https://github.com/ivankhokholkov/gpt-image-2-polza-mcp.git
cd gpt-image-2-polza-mcp
uv sync
```

Создайте `.mcp.json`:

```json
{
  "mcpServers": {
    "gpt-image-2-polza": {
      "command": "uv",
      "args": [
        "run",
        "gpt-image-2-polza-mcp-server"
      ],
      "cwd": "/absolute/path/to/gpt-image-2-polza-mcp",
      "env": {
        "POLZA_AI_API_KEY": "your-polza-api-key",
        "POLZA_BASE_URL": "https://polza.ai/api",
        "IMAGE_OUTPUT_DIR": "/absolute/path/to/gpt-image-2-output"
      }
    }
  }
}
```

Перезапустите MCP-клиент после добавления конфигурации.

## Использование

Обычная генерация:

```text
Создай рекламный кадр флакона духов на чёрном камне,
кинематографический свет, формат 16:9, разрешение 4K.
Используй gpt-image-2.
```

Основные параметры `generate_image`:

| Параметр | Описание |
|---|---|
| `prompt` | Текстовое описание изображения или инструкция по редактированию |
| `mode` | `generate`, `edit` или автоматическое определение |
| `model_tier` | `gpt-image-2`; используется по умолчанию |
| `resolution` | `1k`, `2k`, `4k` или `high` |
| `aspect_ratio` | Например, `1:1`, `16:9`, `9:16`, `4:5` |
| `input_image_path_1` | Путь к основному референсу или редактируемому изображению |
| `input_image_path_2` | Второй референс |
| `input_image_path_3` | Третий референс |
| `output_path` | Конкретный файл или папка для результата |
| `force_new_generation` | Принудительно запустить новую генерацию вместо использования кэша |

## Восстановление после таймаута

Генерация может продолжаться на стороне Polza после таймаута MCP-клиента. Не
запускайте тот же запрос повторно сразу: это может создать и оплатить ещё одну
генерацию.

Получите `gen_...` ID в истории генераций Polza и вызовите:

```text
fetch_generation(
  media_id="gen_2158267363095220225",
  output_path="/absolute/path/to/result.png"
)
```

## Переменные окружения

| Переменная | Обязательно | Описание |
|---|---|---|
| `POLZA_AI_API_KEY` | Да | API-ключ аккаунта Polza |
| `POLZA_BASE_URL` | Нет | Базовый URL API; по умолчанию `https://polza.ai/api` |
| `IMAGE_OUTPUT_DIR` | Нет | Папка результатов; по умолчанию `~/gpt-image-2-images` |
| `GPT_IMAGE_MODEL` | Нет | Model tier; по умолчанию `gpt-image-2` |
| `POLZA_POLL_INTERVAL_SECONDS` | Нет | Интервал проверки статуса генерации |
| `POLZA_POLL_TIMEOUT_SECONDS` | Нет | Максимальное время ожидания результата |
| `POLZA_EXTERNAL_USER_ID` | Нет | Внешний ID пользователя для Polza |
| `RETURN_FULL_IMAGE` | Нет | Возвращать полное изображение вместо превью |

## Локальный запуск

```bash
cp .env.example .env
uv sync
uv run gpt-image-2-polza-mcp-server
```

Минимальный `.env`:

```env
POLZA_AI_API_KEY=your-polza-api-key
POLZA_BASE_URL=https://polza.ai/api
GPT_IMAGE_MODEL=gpt-image-2
IMAGE_OUTPUT_DIR=/absolute/path/to/gpt-image-2-output
```

## API Polza

Сервер использует:

- `POST /v1/media` — запуск генерации
- `GET /v1/media/{id}` — получение статуса и результата
- `POST /v1/storage/upload` — загрузка референсов
- `GET /v1/storage/files/{id}` — метаданные файла
- `DELETE /v1/storage/files/{id}` — удаление файла

## Лицензия

MIT. См. [LICENSE](LICENSE).
