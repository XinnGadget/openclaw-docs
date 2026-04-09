---
summary: "Настройка DeepSeek (аутентификация + выбор модели)"
read_when:
  - Вы хотите использовать DeepSeek с OpenClaw
  - Вам нужна переменная окружения с API-ключом или выбор аутентификации через CLI
---

# DeepSeek

[DeepSeek](https://www.deepseek.com) предоставляет мощные ИИ-модели с API, совместимым с OpenAI.

- Поставщик: `deepseek`
- Аутентификация: `DEEPSEEK_API_KEY`
- API: совместим с OpenAI
- Базовый URL: `https://api.deepseek.com`

## Быстрый старт

Задайте API-ключ (рекомендуется сохранить его для Gateway):

```bash
openclaw onboard --auth-choice deepseek-api-key
```

Это запросит ваш API-ключ и установит `deepseek/deepseek-chat` в качестве модели по умолчанию.

## Пример неинтерактивного запуска

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice deepseek-api-key \
  --deepseek-api-key "$DEEPSEEK_API_KEY" \
  --skip-health \
  --accept-risk
```

## Примечание об окружении

Если Gateway работает как демон (launchd/systemd), убедитесь, что `DEEPSEEK_API_KEY` доступен для этого процесса (например, в `~/.openclaw/.env` или через `env.shellEnv`).

## Встроенный каталог

| Ссылка на модель | Название | Ввод | Контекст | Максимальный объём вывода | Примечания |
| --- | --- | --- | --- | --- | --- |
| `deepseek/deepseek-chat` | DeepSeek Chat | текст | 131 072 | 8 192 | Модель по умолчанию; DeepSeek V3.2 без функции размышления |
| `deepseek/deepseek-reasoner` | DeepSeek Reasoner | текст | 131 072 | 65 536 | Поверхность V3.2 с поддержкой рассуждений |

Обе встроенные модели в настоящее время заявляют о совместимости с потоковой обработкой данных в исходном коде.

Получите свой API-ключ на [platform.deepseek.com](https://platform.deepseek.com/api_keys).