---
title: "Создание плагинов"
sidebarTitle: "Начало работы"
summary: "Создайте свой первый плагин для OpenClaw за несколько минут"
read_when:
  - Вы хотите создать новый плагин для OpenClaw
  - Вам нужен быстрый старт для разработки плагинов
  - Вы добавляете новый канал, провайдера, инструмент или другую функциональность в OpenClaw
---

# Создание плагинов

Плагины расширяют возможности OpenClaw: добавляют каналы, провайдеров моделей, функции работы с речью, транскрипцию в реальном времени, голосовую связь в реальном времени, анализ медиа, генерацию изображений, генерацию видео, получение данных из веб, веб-поиск, инструменты для агентов и любую комбинацию этих функций.

Вам не нужно добавлять свой плагин в репозиторий OpenClaw. Опубликуйте его в [ClawHub](/tools/clawhub) или npm, и пользователи смогут установить его с помощью команды `openclaw plugins install <имя-пакета>`. OpenClaw сначала обращается к ClawHub, а затем автоматически переходит к npm.

## Предварительные требования

- Node >= 22 и менеджер пакетов (npm или pnpm)
- Знание TypeScript (ESM)
- Для плагинов в репозитории: клонированный репозиторий и выполнение команды `pnpm install`

## Какой тип плагина вам нужен?

<CardGroup cols={3}>
  <Card title="Плагин канала" icon="messages-square" href="/plugins/sdk-channel-plugins">
    Подключите OpenClaw к платформе обмена сообщениями (Discord, IRC и т. д.)
  </Card>
  <Card title="Плагин провайдера" icon="cpu" href="/plugins/sdk-provider-plugins">
    Добавьте провайдера модели (LLM, прокси или пользовательскую конечную точку)
  </Card>
  <Card title="Плагин инструмента / хука" icon="wrench">
    Зарегистрируйте инструменты для агентов, хуки событий или сервисы — см. ниже
  </Card>
</CardGroup>

Если плагин канала является необязательным и может не быть установлен во время начальной настройки, используйте `createOptionalChannelSetupSurface(...)` из `openclaw/plugin-sdk/channel-setup`. Это создаст адаптер настройки и мастер, которые уведомят о необходимости установки плагина и не позволят вносить реальные изменения в конфигурацию до установки плагина.

## Быстрый старт: плагин инструмента

В этом руководстве создаётся минимальный плагин, который регистрирует инструмент для агента. Для плагинов каналов и провайдеров есть отдельные руководства, ссылки на которые приведены выше.

<Steps>
  <Step title="Создайте пакет и манифест">
    <CodeGroup>
    ```json package.json
    {
      "name": "@myorg/openclaw-my-plugin",
      "version": "1.0.0",
      "type": "module",
      "openclaw": {
        "extensions": ["./index.ts"],
        "compat": {
          "pluginApi": ">=2026.3.24-beta.2",
          "minGatewayVersion": "2026.3.24-beta.2"
        },
        "build": {
          "openclawVersion": "2026.3.24-beta.2",
          "pluginSdkVersion": "2026.3.24-beta.2"
        }
      }
    }
    ```

    ```json openclaw.plugin.json
    {
      "id": "my-plugin",
      "name": "Мой плагин",
      "description": "Добавляет пользовательский инструмент в OpenClaw",
      "configSchema": {
        "type": "object",
        "additionalProperties": false
      }
    }
    ```
    </CodeGroup>

    Каждому плагину нужен манифест, даже если у него нет конфигурации. Полный схема манифеста приведена в разделе [Манифест](/plugins/manifest). Стандартные фрагменты для публикации в ClawHub находятся в `docs/snippets/plugin-publish/`.

  </Step>

  <Step title="Напишите точку входа">

    ```typescript
    // index.ts
    import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
    import { Type } from "@sinclair/typebox";

    export default definePluginEntry({
      id: "my-plugin",
      name: "Мой плагин",
      description: "Добавляет пользовательский инструмент в OpenClaw",
      register(api) {
        api.registerTool({
          name: "my_tool",
          description: "Выполнить действие",
          parameters: Type.Object({ input: Type.String() }),
          async execute(_id, params) {
            return { content: [{ type: "text", text: `Получено: ${params.input}` }] };
          },
        });
      },
    });
    ```

    `definePluginEntry` используется для плагинов, не связанных с каналами. Для каналов используйте `defineChannelPluginEntry` — см. [Плагины каналов](/plugins/sdk-channel-plugins). Полные варианты точек входа приведены в разделе [Точки входа](/plugins/sdk-entrypoints).

  </Step>

  <Step title="Протестируйте и опубликуйте">

    **Внешние плагины:** проверьте и опубликуйте с помощью ClawHub, затем установите:

    ```bash
    clawhub package publish your-org/your-plugin --dry-run
    clawhub package publish your-org/your-plugin
    openclaw plugins install clawhub:@myorg/openclaw-my-plugin
    ```

    OpenClaw также проверяет ClawHub перед npm для простых спецификаций пакетов, таких как `@myorg/openclaw-my-plugin`.

    **Плагины в репозитории:** поместите их в дерево рабочей области встроенных плагинов — они будут обнаружены автоматически.

    ```bash
    pnpm test -- <bundled-plugin-root>/my-plugin/
    ```

  </Step>
</Steps>

## Возможности плагинов

Один плагин может зарегистрировать любое количество возможностей через объект `api`:

| Возможность | Метод регистрации | Подробное руководство |
| --- | --- | --- |
| Вывод текста (LLM) | `api.registerProvider(...)` | [Плагины провайдеров](/plugins/sdk-provider-plugins) |
| Бэкенд вывода для CLI | `api.registerCliBackend(...)` | [Бэкенды CLI](/gateway/cli-backends) |
| Канал / обмен сообщениями | `api.registerChannel(...)` | [Плагины каналов](/plugins/sdk-channel-plugins) |
| Речь (TTS/STT) | `api.registerSpeechProvider(...)` | [Плагины провайдеров](/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Транскрипция в реальном времени | `api.registerRealtimeTranscriptionProvider(...)` | [Плагины провайдеров](/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Голосовая связь в реальном времени | `api.registerRealtimeVoiceProvider(...)` | [Плагины провайдеров](/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Анализ медиа | `api.registerMediaUnderstandingProvider(...)` | [Плагины провайдеров](/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Генерация изображений | `api.registerImageGenerationProvider(...)` | [Плагины провайдеров](/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Генерация музыки | `api.registerMusicGenerationProvider(...)` | [Плагины провайдеров](/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Генерация видео | `api.registerVideoGenerationProvider(...)` | [Плагины провайдеров](/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Получение данных из веб | `api.registerWebFetchProvider(...)` | [Плагины провайдеров](/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Веб-поиск | `api.registerWebSearchProvider(...)` | [Плагины провайдеров](/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Инструменты для агентов | `api.registerTool(...)` | См. ниже |
| Пользовательские команды | `api.registerCommand(...)` | [Точки входа](/plugins/sdk-entrypoints) |
| Хуки событий | `api.registerHook(...)` | [Точки входа](/plugins/sdk-entrypoints) |
| HTTP-маршруты | `api.registerHttpRoute(...)` | [Внутреннее устройство](/plugins/architecture#gateway-http-routes) |
| Подкоманды CLI | `api.registerCli(...)` | [Точки входа](/plugins/sdk-entrypoints) |

Полная информация о API регистрации приведена в разделе [Обзор SDK](/plugins/sdk-overview#registration-api).

Если ваш плагин регистрирует пользовательские методы RPC шлюза, используйте префикс,