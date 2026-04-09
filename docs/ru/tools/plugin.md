 ---
summary: "Установка, настройка и управление плагинами OpenClaw"
read_when:
  - Установка или настройка плагинов
  - Понимание правил обнаружения и загрузки плагинов
  - Работа с пакетами плагинов, совместимыми с Codex/Claude
title: "Плагины"
sidebarTitle: "Установить и настроить"
---

# Плагины

Плагины расширяют возможности OpenClaw: добавляют каналы, провайдеров моделей, инструменты, навыки, функции речи, транскрипцию в реальном времени, голосовую связь в реальном времени, понимание мультимедиа, генерацию изображений, генерацию видео, получение данных из веб-источников, веб-поиск и многое другое. Некоторые плагины являются **основными** (поставляются вместе с OpenClaw), другие — **внешними** (публикуются сообществом в npm).

## Быстрый старт

<Steps>
  <Step title="Посмотреть, что загружено">
    ```bash
    openclaw plugins list
    ```
  </Step>

  <Step title="Установить плагин">
    ```bash
    # Из npm
    openclaw plugins install @openclaw/voice-call

    # Из локального каталога или архива
    openclaw plugins install ./my-plugin
    openclaw plugins install ./my-plugin.tgz
    ```

  </Step>

  <Step title="Перезапустить Gateway">
    ```bash
    openclaw gateway restart
    ```

    Затем настройте в `plugins.entries.<id>.config` в файле конфигурации.

  </Step>
</Steps>

Если вы предпочитаете управление через чат, включите `commands.plugins: true` и используйте:

```text
/plugin install clawhub:@openclaw/voice-call
/plugin show voice-call
/plugin enable voice-call
```

Путь установки использует тот же резолвер, что и CLI: локальный путь/архив, явный `clawhub:<pkg>` или спецификация пакета (сначала ClawHub, затем резервный вариант — npm).

Если конфигурация некорректна, установка обычно завершается с ошибкой и направляет вас к `openclaw doctor --fix`. Единственное исключение для восстановления — узкий путь переустановки встроенного плагина для плагинов, которые поддерживают `openclaw.install.allowInvalidConfigRecovery`.

## Типы плагинов

OpenClaw распознаёт два формата плагинов:

| Формат | Как работает | Примеры |
| ------ | ------------ | ------- |
| **Native** | `openclaw.plugin.json` + модуль среды выполнения; выполняется внутри процесса | Официальные плагины, пакеты сообщества в npm |
| **Bundle** | Макет, совместимый с Codex/Claude/Cursor; сопоставляется с функциями OpenClaw | `.codex-plugin/`, `.claude-plugin/`, `.cursor-plugin/` |

Оба отображаются в `openclaw plugins list`. Подробнее о пакетах плагинов см. в разделе [Пакеты плагинов](/plugins/bundles).

Если вы пишете нативный плагин, начните с раздела [Создание плагинов](/plugins/building-plugins) и [Обзор SDK для плагинов](/plugins/sdk-overview).

## Официальные плагины

### Устанавливаемые (npm)

| Плагин | Пакет | Документация |
| ------- | ------- | ----------- |
| Matrix | `@openclaw/matrix` | [Matrix](/channels/matrix) |
| Microsoft Teams | `@openclaw/msteams` | [Microsoft Teams](/channels/msteams) |
| Nostr | `@openclaw/nostr` | [Nostr](/channels/nostr) |
| Голосовой вызов | `@openclaw/voice-call` | [Голосовой вызов](/plugins/voice-call) |
| Zalo | `@openclaw/zalo` | [Zalo](/channels/zalo) |
| Zalo Personal | `@openclaw/zalouser` | [Zalo Personal](/plugins/zalouser) |

### Основные (поставляются с OpenClaw)

<AccordionGroup>
  <Accordion title="Провайдеры моделей (включены по умолчанию)">
    `anthropic`, `byteplus`, `cloudflare-ai-gateway`, `github-copilot`, `google`,
    `huggingface`, `kilocode`, `kimi-coding`, `minimax`, `mistral`, `qwen`,
    `moonshot`, `nvidia`, `openai`, `opencode`, `opencode-go`, `openrouter`,
    `qianfan`, `synthetic`, `together`, `venice`,
    `vercel-ai-gateway`, `volcengine`, `xiaomi`, `zai`
  </Accordion>

  <Accordion title="Плагины памяти">
    - `memory-core` — встроенная функция поиска в памяти (по умолчанию через `plugins.slots.memory`)
    - `memory-lancedb` — долговременная память с автозапоминанием/захватом (устанавливается по требованию; задайте `plugins.slots.memory = "memory-lancedb"`)
  </Accordion>

  <Accordion title="Провайдеры речи (включены по умолчанию)">
    `elevenlabs`, `microsoft`
  </Accordion>

  <Accordion title="Прочее">
    - `browser` — встроенный плагин браузера для инструмента браузера, CLI `openclaw browser`, метода шлюза `browser.request`, среды выполнения браузера и службы управления браузером по умолчанию (включён по умолчанию; отключите перед заменой)
    - `copilot-proxy` — мост прокси-сервера VS Code Copilot (отключён по умолчанию)
  </Accordion>
</AccordionGroup>

Ищете плагины сторонних разработчиков? См. раздел [Плагины сообщества](/plugins/community).

## Конфигурация

```json5
{
  plugins: {
    enabled: true,
    allow: ["voice-call"],
    deny: ["untrusted-plugin"],
    load: { paths: ["~/Projects/oss/voice-call-extension"] },
    entries: {
      "voice-call": { enabled: true, config: { provider: "twilio" } },
    },
  },
}
```

| Поле | Описание |
| ---- | -------- |
| `enabled` | Главный переключатель (по умолчанию: `true`) |
| `allow` | Список разрешённых плагинов (необязательно) |
| `deny` | Список запрещённых плагинов (необязательно; запрет имеет приоритет) |
| `load.paths` | Дополнительные файлы/каталоги плагинов |
| `slots` | Селекторы эксклюзивных слотов (например, `memory`, `contextEngine`) |
| `entries.<id>` | Переключатели и конфигурация для каждого плагина |

Изменения конфигурации **требуют перезапуска шлюза**. Если шлюз работает с включённым отслеживанием конфигурации и перезапуском внутри процесса (путь по умолчанию для `openclaw gateway`), перезапуск обычно выполняется автоматически через некоторое время после внесения изменений в конфигурацию.

<Accordion title="Состояния плагинов: отключён, отсутствует, некорректен">
  - **Отключён**: плагин существует, но правила включения его отключили. Конфигурация сохраняется.
  - **Отсутствует**: конфигурация ссылается на идентификатор плагина, который не был обнаружен.
  - **Некорректен**: плагин существует, но его конфигурация не соответствует объявленной схеме.
</Accordion>

## Обнаружение и приоритет

OpenClaw ищет плагины в следующем порядке (используется первый найденный вариант):

<Steps>
  <Step title="Пути в конфигурации">
    `plugins.load.paths` — явные пути к файлам или каталогам.
  </Step>

  <Step title="Расширения рабочей области">
    `\<workspace\>/.openclaw/<plugin-root>/*.ts` и `\<workspace\>/.openclaw/<plugin-root>/*/index.ts`.
  </Step>

  <Step title="Глобальные расширения">
    `~/.openclaw/<plugin-root>/*.ts` и `~/.openclaw/<plugin-root>/*/index.ts`.
  </Step>

  <Step title="Встроенные плагины">
    Поставляются с OpenClaw. Многие включены по умолчанию (провайдеры моделей, функции речи). Другие требуют явного включения.
  </Step>
</Steps>

### Правила включения

- `plugins.enabled: false` отключает все плагины
- `plugins.deny` всегда имеет приоритет над `allow`
- `plugins.entries.<id>.enabled: false` отключает этот плагин
- Плагины из рабочей области **по умолчанию отключены** (их нужно явно включить)
- Встроенные плагины следуют встроенному набору по умолчанию, если не переопределены
- Эксклюзивные слоты могут принудительно включить выбранный плагин для этого слота

## Слоты плагинов (эксклюзивные категории)

Некоторые категории являются эксклюзивными (активен только один вариант):

```json5
{
  plugins: {
    slots: {
      memory: "memory-core", // или "none", чтобы отключить
      contextEngine: "legacy", // или идентификатор плагина
    },
  },
}
```

| Слот | Что контролирует | По умолчанию |
| ---- | --------------- | ------------ |
| `memory` | Активный плагин памяти | `memory-core` |
| `contextEngine` | Активный механизм контекста | `legacy` (встроенный) |

## Справочная информация по CLI

```bash
openclaw plugins list                       # краткий список
openclaw plugins list --enabled            # только загруженные плагины
openclaw plugins list --verbose            # подробные сведения по каждому плагину
openclaw plugins list --json               # список в машиночитаемом формате
openclaw plugins inspect <id>              # подробные сведения
openclaw plugins inspect <id> --json       # в машиночитаемом формате
openclaw plugins inspect --all             # таблица по всем плагинам
openclaw plugins info <id>                 # псевдоним для inspect
openclaw plugins doctor                    # диагностика

openclaw plugins install <package>         # установка (сначала ClawHub, затем npm)
openclaw plugins install clawhub:<pkg>     # установка только из ClawHub
openclaw plugins install <spec> --force    # перезаписать существующую установку
openclaw plugins install <path>            # установка из локального пути
openclaw plugins install -l <path>         # связать (без копирования) для разработки
openclaw plugins install <plugin> --marketplace <source>
openclaw plugins install <plugin> --marketplace https://github.com/<owner>/<repo>
openclaw plugins install <spec> --pin      # зафиксировать точную спецификацию npm
openclaw plugins install <spec> --dangerously-force-unsafe-install
openclaw plugins update <id>             # обновить один плагин
openclaw plugins update <id> --dangerously-force-unsafe-install
openclaw plugins update --all            # обновить все
openclaw plugins uninstall <id>          # удалить записи о конфигурации/установке
openclaw plugins uninstall <id> --keep-files
openclaw plugins marketplace list <source>
openclaw plugins marketplace list <source> --json

openclaw plugins enable <id>
openclaw plugins disable <id>
```

Встроенные плагины поставляются с OpenClaw. Многие из них включены по умолчанию (например, встроенные провайдеры моделей, встроенные провайдеры речи и встроенный плагин браузера). Другие встроенные плагины по-прежнему требуют выполнения `openclaw plugins enable <id>`.

`--force` перезаписывает существующий установленный плагин или пакет хуков на месте. Не поддерживается с `--link`, который использует исходный путь вместо копирования в управляемую целевую директорию установки.

`--pin` работает только с npm. Не поддерживается с `--marketplace`, поскольку при установке из маркетплейса сохраняются метаданные источника маркетплейса, а не спецификация npm.

`--dangerously-force-unsafe-install` — это аварийный механизм обхода ложных срабатываний встроенного сканера опасного кода. Позволяет продолжить установку и обновление плагинов, несмотря на обнаружение критических проблем встроенным сканером, но не обходит блокировки политик `before_install` или блокировки из-за сбоев сканирования.

Этот флаг CLI применяется только к процессам установки/обновления плагинов. Для установки зависимостей навыков, поддерживаемых шлюзом, используется соответствующий параметр переопределения `dangerouslyForceUnsafeInstall`, а `openclaw skills install` остаётся отдельным процессом загрузки/установки навыков ClawHub.

Совместимые пакеты участвуют в том же потоке операций со списком плагинов/проверкой/включением/отключением. Текущая поддержка среды выполнения включает навыки пакетов, навыки команд Claude, значения по умолчанию для Claude в `settings.json`, значения по умолчанию для Claude в `.lsp.json` и объявленные в манифесте значения по умолчанию для `lspServers`, навыки команд Cursor и совместимые каталоги хуков Codex.

`openclaw plugins inspect <id>` также отображает обнаруженные возможности пакета, а также поддерживаемые или неподдерживаемые записи серверов MCP и LSP для плагинов на основе пакетов.

Источниками маркетплейса могут быть: имя известного маркетплейса Claude из `~/.claude/plugins/known_marketplaces.json`, корневой каталог локального маркетплейса или путь к `marketplace.json`, сокращённая запись GitHub вроде `owner/repo`, URL репозитория GitHub или URL git. Для удалённых маркетплейсов записи плагинов должны находиться внутри клонированного репозитория маркетплейса и использовать только относительные пути.

См. [справочную информацию по CLI `openclaw plugins`](/cli/plugins) для получения полных сведений.

## Обзор API плагинов

Нативные плагины экспортируют объект входа, который предоставляет `register(api)`. Более старые плагины могут по-прежнему использовать `activate(api)` в качестве устаревшего псевдонима, но новые плагины должны использовать `register`.

```typescript
export default definePluginEntry({
  id: "my-plugin",
  name: "Мой плагин",
  register(api) {
    api.registerProvider({
      /* ... */
    });
    api.registerTool({
      /* ... */
    });
    api.registerChannel({
      /* ... */
    });
  },
});
```

OpenClaw загружает объект входа и вызывает `register(api)` во время активации плагина. Загрузчик по-прежнему поддерживает `activate(api)` для старых плагинов, но встроенные плагины и новые внешние плагины должны рассматривать `register` как публичный контракт.

Распространённые методы регистрации:

| Метод | Что регистрирует |
| --------------------------------------- | --------------------------- |
| `registerProvider` | Провайдер моделей (LLM) |
| `registerChannel` | Канал чата |
| `registerTool` | Инструмент агента |
| `registerHook` / `on(...)` | Хуки жизненного цикла |
| `registerSpeechProvider` | Преобразование текста в речь / STT |
| `registerRealtimeTranscriptionProvider` | Потоковая STT |
| `registerRealtimeVoiceProvider` | Дуплексная голосовая связь в реальном времени |
| `registerMediaUnderstandingProvider` | Анализ изображений/аудио |
| `registerImageGenerationProvider` | Генерация изображений |
| `registerMusicGenerationProvider` | Генерация музыки |
| `registerVideoGenerationProvider` | Генерация видео |
| `registerWebFetchProvider` | Провайдер получения/парсинга веб-данных |
| `registerWebSearchProvider` | Веб-поиск |
| `registerHttpRoute` | HTTP-конечная точка |
| `registerCommand` / `registerCli` | Команды CLI |
| `registerContextEngine` | Механизм контекста |
| `registerService` | Фоновая служба |

Поведение защиты хуков для типизированных хуков жизненного цикла:

- `before_tool_call`: `{ block: true }` — терминальное состояние; обработчики с более низким приоритетом пропускаются.
- `before_tool_call`: `{ block: false }` — операция без действий, не отменяет ранее установленный блок.
- `before_install`: `{ block: true }` — терминальное состояние; обработчики с более низким приоритетом пропускаются.
- `before_install`: `{ block: false }` — операция без действий, не отменяет ранее установленный блок.
- `message_sending`: `{ cancel: true }` — терминальное состояние; обработчики с более низким приоритетом пропускаются.
- `message_sending`: `{ cancel: false }` — операция без действий, не отменяет ранее установленную отмену.

Для полного описания поведения типизированных хуков см. раздел [Обзор SDK](/plugins/sdk-overview#hook-decision-semantics).

## Связанные разделы

- [Создание плагинов](/plugins/building-plugins) — создайте собственный плагин
- [Пакеты плагинов](/plugins/bundles) — совместимость с пакетами Codex/Claude/Cursor
- [Манифест плагина](/plugins/manifest) — схема манифеста
- [Регистрация инструментов](/plugins/building-plugins#registering-agent-tools) — добавление инструментов агента в плагин
- [Внутреннее устройство плагинов](/plugins/architecture) — модель возможностей и конвейер загрузки
- [Плагины сообщества](/plugins/community) — списки плагинов сторонних разработчиков