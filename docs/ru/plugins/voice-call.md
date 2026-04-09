---
summary: "Плагин Voice Call: исходящие и входящие звонки через Twilio/Telnyx/Plivo (установка плагина + настройка + CLI)"
read_when:
  - Вам нужно совершить исходящий голосовой звонок из OpenClaw
  - Вы настраиваете или разрабатываете плагин для голосовых звонков
title: "Плагин Voice Call"
---

# Voice Call (плагин)

Голосовые звонки для OpenClaw посредством плагина. Поддерживает исходящие уведомления и многоэтапные диалоги с политиками обработки входящих звонков.

Поддерживаемые провайдеры:

- `twilio` (Programmable Voice + Media Streams);
- `telnyx` (Call Control v2);
- `plivo` (Voice API + XML transfer + GetInput speech);
- `mock` (разработка/без сети).

Краткая схема работы:

- Установите плагин;
- Перезапустите Gateway;
- Настройте в разделе `plugins.entries.voice-call.config`;
- Используйте `openclaw voicecall …` или инструмент `voice_call`.

## Где выполняется плагин (локально vs удалённо)

Плагин Voice Call выполняется **внутри процесса Gateway**.

Если вы используете удалённый Gateway, установите и настройте плагин на **машине, где запущен Gateway**, затем перезапустите Gateway, чтобы загрузить плагин.

## Установка

### Вариант А: установка из npm (рекомендуется)

```bash
openclaw plugins install @openclaw/voice-call
```

После этого перезапустите Gateway.

### Вариант Б: установка из локальной папки (разработка, без копирования)

```bash
PLUGIN_SRC=./path/to/local/voice-call-plugin
openclaw plugins install "$PLUGIN_SRC"
cd "$PLUGIN_SRC" && pnpm install
```

После этого перезапустите Gateway.

## Настройка

Настройте параметры в разделе `plugins.entries.voice-call.config`:

```json5
{
  plugins: {
    entries: {
      "voice-call": {
        enabled: true,
        config: {
          provider: "twilio", // или "telnyx" | "plivo" | "mock"
          fromNumber: "+15550001234",
          toNumber: "+15550005678",

          twilio: {
            accountSid: "ACxxxxxxxx",
            authToken: "...",
          },

          telnyx: {
            apiKey: "...",
            connectionId: "...",
            // Публичный ключ вебхука Telnyx из Telnyx Mission Control Portal
            // (строка в формате Base64; также может быть задан через TELNYX_PUBLIC_KEY).
            publicKey: "...",
          },

          plivo: {
            authId: "MAxxxxxxxxxxxxxxxxxxxx",
            authToken: "...",
          },

          // Сервер вебхуков
          serve: {
            port: 3334,
            path: "/voice/webhook",
          },

          // Безопасность вебхуков (рекомендуется для туннелей/прокси)
          webhookSecurity: {
            allowedHosts: ["voice.example.com"],
            trustedProxyIPs: ["100.64.0.1"],
          },

          // Публичный доступ (выберите один вариант)
          // publicUrl: "https://example.ngrok.app/voice/webhook",
          // tunnel: { provider: "ngrok" },
          // tailscale: { mode: "funnel", path: "/voice/webhook" }

          outbound: {
            defaultMode: "notify", // notify | conversation
          },

          streaming: {
            enabled: true,
            provider: "openai", // необязательно; первый зарегистрированный провайдер транскрипции в реальном времени, если не задан
            streamPath: "/voice/stream",
            providers: {
              openai: {
                apiKey: "sk-...", // необязательно, если задан OPENAI_API_KEY
                model: "gpt-4o-transcribe",
                silenceDurationMs: 800,
                vadThreshold: 0.5,
              },
            },
            preStartTimeoutMs: 5000,
            maxPendingConnections: 32,
            maxPendingConnectionsPerIp: 4,
            maxConnections: 128,
          },
        },
      },
    },
  },
}
```

Примечания:

- Для Twilio/Telnyx требуется **публично доступный** URL вебхука.
- Для Plivo требуется **публично доступный** URL вебхука.
- `mock` — локальный провайдер для разработки (без сетевых вызовов).
- Если в старых настройках всё ещё используются `provider: "log"`, `twilio.from` или устаревшие ключи `streaming.*` для OpenAI, выполните `openclaw doctor --fix`, чтобы переписать их.
- Для Telnyx требуется `telnyx.publicKey` (или `TELNYX_PUBLIC_KEY`), если только `skipSignatureVerification` не имеет значение `true`.
- `skipSignatureVerification` предназначен только для локального тестирования.
- Если вы используете бесплатный тариф ngrok, задайте `publicUrl` как точный URL ngrok; проверка подписи всегда выполняется.
- `tunnel.allowNgrokFreeTierLoopbackBypass: true` позволяет использовать вебхуки Twilio с недействительными подписями **только** при `tunnel.provider="ngrok"` и `serve.bind` в режиме loopback (локальный агент ngrok). Используйте только для локальной разработки.
- URLs бесплатного тарифа ngrok могут меняться или добавлять промежуточные страницы; если `publicUrl` изменится, подписи Twilio не пройдут проверку. Для продакшена предпочтительнее использовать стабильный домен или Tailscale funnel.
- Настройки безопасности потоковой передачи по умолчанию:
  - `streaming.preStartTimeoutMs` закрывает сокеты, которые никогда не отправляют допустимый кадр `start`.
- `streaming.maxPendingConnections` ограничивает общее количество неаутентифицированных сокетов до начала передачи.
- `streaming.maxPendingConnectionsPerIp` ограничивает количество неаутентифицированных сокетов до начала передачи для каждого исходного IP-адреса.
- `streaming.maxConnections` ограничивает общее количество открытых сокетов для потоковой передачи медиа (ожидание + активное состояние).
- Во время выполнения система по-прежнему принимает устаревшие ключи для голосовых звонков, но для их преобразования следует использовать `openclaw doctor --fix`, а временный механизм совместимости является временным.

## Потоковая транскрипция

Параметр `streaming` выбирает провайдера транскрипции в реальном времени для аудио звонков в режиме реального времени.

Текущее поведение во время выполнения:

- `streaming.provider` необязателен. Если он не задан, Voice Call использует первого зарегистрированного провайдера транскрипции в реальном времени.
- В настоящее время встроенный провайдер — OpenAI, зарегистрированный с помощью встроенного плагина `openai`.
- Исходная конфигурация провайдера хранится в разделе `streaming.providers.<providerId>`.
- Если `streaming.provider` указывает на незарегистрированный провайдер или вообще не зарегистрирован ни один провайдер транскрипции в реальном времени, Voice Call выводит предупреждение и пропускает потоковую передачу медиа, вместо того чтобы отключать весь плагин.

Настройки потоковой транскрипции OpenAI по умолчанию:

- Ключ API: `streaming.providers.openai.apiKey` или `OPENAI_API_KEY`;
- модель: `gpt-4o-transcribe`;
- `silenceDurationMs`: `800`;
- `vadThreshold`: `0.5`.

Пример:

```json5
{
  plugins: {
    entries: {
      "voice-call": {
        config: {
          streaming: {
            enabled: true,
            provider: "openai",
            streamPath: "/voice/stream",
            providers: {
              openai: {
                apiKey: "sk-...", // необязательно, если задан OPENAI_API_KEY
                model: "gpt-4o-transcribe",
                silenceDurationMs: 800,
                vadThreshold: 0.5,
              },
            },
          },
        },
      },
    },
  },
}
```

Устаревшие ключи автоматически переносятся с помощью `openclaw doctor --fix`:

- `streaming.sttProvider` → `streaming.provider`;
- `streaming.openaiApiKey` → `streaming.providers.openai.apiKey`;
- `streaming.sttModel` → `streaming.providers.openai.model`;
- `streaming.silenceDurationMs` → `streaming.providers.openai.silenceDurationMs`;
- `streaming.vadThreshold` → `streaming.providers.openai.vadThreshold`.

## Очиститель устаревших звонков

Используйте `staleCallReaperSeconds`, чтобы завершать звонки, которые никогда не получают терминальный вебхук (например, звонки в режиме уведомления, которые никогда не завершаются). По умолчанию значение равно `0` (отключено).

Рекомендуемые диапазоны:

- **Продакшен