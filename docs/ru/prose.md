---
summary: "OpenProse: рабочие процессы .prose, слэш-команды и состояние в OpenClaw"
read_when:
  - Вы хотите запустить или написать рабочие процессы .prose
  - Вы хотите включить плагин OpenProse
  - Вам нужно разобраться в хранении состояния
title: "OpenProse"
---

# OpenProse

OpenProse — это переносимый формат рабочих процессов с приоритетом Markdown для организации сессий ИИ. В OpenClaw он поставляется в виде плагина, который устанавливает набор навыков OpenProse, а также слэш-команду `/prose`. Программы размещаются в файлах `.prose` и могут запускать несколько суб-агентов с явным управлением потоком выполнения.

Официальный сайт: [https://www.prose.md](https://www.prose.md)

## Что можно делать

- Исследования с участием нескольких агентов и синтез данных с явным параллелизмом.
- Повторяемые рабочие процессы с контролем утверждений (рецензирование кода, сортировка инцидентов, конвейеры контента).
- Переиспользуемые программы `.prose`, которые можно запускать на всех поддерживаемых средах выполнения агентов.

## Установка и включение

Встроенные плагины по умолчанию отключены. Чтобы включить OpenProse, выполните:

```bash
openclaw plugins enable open-prose
```

После включения плагина перезапустите Gateway.

Для локальной установки: `openclaw plugins install ./path/to/local/open-prose-plugin`

Связанные документы: [Плагины](/tools/plugin), [Манифест плагина](/plugins/manifest), [Навыки](/tools/skills).

## Слэш-команда

OpenProse регистрирует `/prose` как команду навыков, вызываемую пользователем. Она направляет к инструкциям виртуальной машины OpenProse и использует инструменты OpenClaw "под капотом".

Распространённые команды:

```
/prose help
/prose run <file.prose>
/prose run <handle/slug>
/prose run <https://example.com/file.prose>
/prose compile <file.prose>
/prose examples
/prose update
```

## Пример: простой файл `.prose`

```prose
# Исследование и синтез с двумя агентами, работающими параллельно.

input topic: "What should we research?"

agent researcher:
  model: sonnet
  prompt: "You research thoroughly and cite sources."

agent writer:
  model: opus
  prompt: "You write a concise summary."

parallel:
  findings = session: researcher
    prompt: "Research {topic}."
  draft = session: writer
    prompt: "Summarize {topic}."

session "Merge the findings + draft into a final answer."
context: { findings, draft }
```

## Расположение файлов

OpenProse хранит состояние в каталоге `.prose/` в вашем рабочем пространстве:

```
.prose/
├── .env
├── runs/
│   └── {YYYYMMDD}-{HHMMSS}-{random}/
│       ├── program.prose
│       ├── state.md
│       ├── bindings/
│       └── agents/
└── agents/
```

Постоянные агенты на уровне пользователя находятся по адресу:

```
~/.prose/agents/
```

## Режимы состояния

OpenProse поддерживает несколько бэкендов состояния:

- **filesystem** (по умолчанию): `.prose/runs/...`
- **in-context**: временное, для небольших программ
- **sqlite** (экспериментальный): требуется бинарный файл `sqlite3`
- **postgres** (экспериментальный): требуется `psql` и строка подключения

Примечания:

- sqlite и postgres — опциональные и экспериментальные.
- учётные данные postgres попадают в журналы суб-агентов; используйте выделенную БД с минимальными привилегиями.

## Удалённые программы

`/prose run <handle/slug>` преобразуется в `https://p.prose.md/<handle>/<slug>`.
Прямые URL-адреса загружаются как есть. При этом используется инструмент `web_fetch` (или `exec` для POST).

## Сопоставление с средой выполнения OpenClaw

Программы OpenProse сопоставляются с примитивами OpenClaw:

| Концепция OpenProse | Инструмент OpenClaw |
| ------------------------- | ---------------- |
| Spawn session / Task tool | `sessions_spawn` |
| Чтение/запись файла | `read` / `write` |
| Получение данных из веб | `web_fetch` |

Если ваш список разрешённых инструментов блокирует эти инструменты, программы OpenProse не будут работать. См. [Конфигурация навыков](/tools/skills-config).

## Безопасность и утверждения

Относитесь к файлам `.prose` как к коду. Проверяйте их перед запуском. Используйте списки разрешённых инструментов OpenClaw и шлюзы утверждений, чтобы контролировать побочные эффекты.

Для детерминированных рабочих процессов с контролем утверждений сравните с [Lobster](/tools/lobster).