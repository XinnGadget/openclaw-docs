---
summary: "Хабы, которые содержат ссылки на всю документацию OpenClaw"
read_when:
  - Вам нужна полная карта документации
title: "Хабы документации"
---

# Хабы документации

<Note>
Если вы новичок в OpenClaw, начните с [Начало работы](/start/getting-started).
</Note>

Используйте эти хабы, чтобы найти все страницы, включая углублённые материалы и справочную документацию, которые не отображаются в левом меню.

## Начните отсюда

- [Индекс](/)
- [Начало работы](/start/getting-started)
- [Ознакомление](/start/onboarding)
- [Ознакомление (CLI)](/start/wizard)
- [Настройка](/start/setup)
- [Панель управления (локальный шлюз)](http://127.0.0.1:18789/)
- [Помощь](/help)
- [Каталог документации](/start/docs-directory)
- [Конфигурация](/gateway/configuration)
- [Примеры конфигурации](/gateway/configuration-examples)
- [Помощник OpenClaw](/start/openclaw)
- [Демонстрация возможностей](/start/showcase)
- [Лоре (контекст проекта)](/start/lore)

## Установка и обновления

- [Docker](/install/docker)
- [Nix](/install/nix)
- [Обновление и откат](/install/updating)
- [Рабочий процесс Bun (экспериментальный)](/install/bun)

## Основные концепции

- [Архитектура](/concepts/architecture)
- [Функции](/concepts/features)
- [Сетевой хаб](/network)
- [Среда выполнения агента](/concepts/agent)
- [Рабочее пространство агента](/concepts/agent-workspace)
- [Память](/concepts/memory)
- [Цикл агента](/concepts/agent-loop)
- [Потоковая передача и разбиение на фрагменты](/concepts/streaming)
- [Маршрутизация между несколькими агентами](/concepts/multi-agent)
- [Компактификация](/concepts/compaction)
- [Сессии](/concepts/session)
- [Удаление сессий](/concepts/session-pruning)
- [Инструменты для сессий](/concepts/session-tool)
- [Очередь](/concepts/queue)
- [Команды со слешем](/tools/slash-commands)
- [Адаптеры RPC](/reference/rpc)
- [Схемы TypeBox](/concepts/typebox)
- [Обработка часовых поясов](/concepts/timezone)
- [Присутствие (presence)](/concepts/presence)
- [Обнаружение и транспорты](/gateway/discovery)
- [Bonjour](/gateway/bonjour)
- [Маршрутизация каналов](/channels/channel-routing)
- [Группы](/channels/groups)
- [Сообщения в группах](/channels/group-messages)
- [Отказоустойчивость моделей](/concepts/model-failover)
- [OAuth](/concepts/oauth)

## Поставщики и входящий трафик

- [Хаб чат-каналов](/channels)
- [Хаб поставщиков моделей](/providers/models)
- [WhatsApp](/channels/whatsapp)
- [Telegram](/channels/telegram)
- [Slack](/channels/slack)
- [Discord](/channels/discord)
- [Mattermost](/channels/mattermost)
- [Signal](/channels/signal)
- [BlueBubbles (iMessage)](/channels/bluebubbles)
- [QQ Bot](/channels/qqbot)
- [iMessage (устаревший)](/channels/imessage)
- [Разбор местоположения](/channels/location)
- [WebChat](/web/webchat)
- [Вебхуки](/automation/cron-jobs#webhooks)
- [Gmail Pub/Sub](/automation/cron-jobs#gmail-pubsub-integration)

## Шлюз и операции

- [Руководство по работе со шлюзом](/gateway)
- [Сетевая модель](/gateway/network-model)
- [Сопряжение шлюзов](/gateway/pairing)
- [Блокировка шлюза](/gateway/gateway-lock)
- [Фоновый процесс](/gateway/background-process)
- [Состояние системы](/gateway/health)
- [Heartbeat (проверка работоспособности)](/gateway/heartbeat)
- [Doctor (инструмент диагностики)](/gateway/doctor)
- [Логирование](/gateway/logging)
- [Песочница](/gateway/sandboxing)
- [Панель управления](/web/dashboard)
- [Интерфейс управления](/web/control-ui)
- [Удалённый доступ](/gateway/remote)
- [README для удалённого шлюза](/gateway/remote-gateway-readme)
- [Tailscale](/gateway/tailscale)
- [Безопасность](/gateway/security)
- [Устранение неполадок](/gateway/troubleshooting)

## Инструменты и автоматизация

- [Интерфейс инструментов](/tools)
- [OpenProse](/prose)
- [Справочник по CLI](/cli)
- [Инструмент Exec](/tools/exec)
- [Инструмент PDF](/tools/pdf)
- [Режим с повышенными правами](/tools/elevated)
- [Cron-задачи](/automation/cron-jobs)
- [Автоматизация и задачи](/automation)
- [Мышление и подробный вывод](/tools/thinking)
- [Модели](/concepts/models)
- [Суб-агенты](/tools/subagents)
- [CLI для отправки сообщений агента](/tools/agent-send)
- [Терминальный UI](/web/tui)
- [Управление браузером](/tools/browser)
- [Браузер (устранение неполадок в Linux)](/tools/browser-linux-troubleshooting)
- [Опросы](/cli/message)

## Узлы, медиа, голос

- [Обзор узлов](/nodes)
- [Камера](/nodes/camera)
- [Изображения](/nodes/images)
- [Аудио](/nodes/audio)
- [Команда местоположения](/nodes/location-command)
- [Пробуждение по голосу](/nodes/voicewake)
- [Режим разговора](/nodes/talk)

## Платформы

- [Обзор платформ](/platforms)
- [macOS](/platforms/macos)
- [iOS](/platforms/ios)
- [Android](/platforms/android)
- [Windows (WSL2)](/platforms/windows)
- [Linux](/platforms/linux)
- [Веб-интерфейсы](/web)

## Приложение-компаньон для macOS (расширенные возможности)

- [Настройка разработки для macOS](/platforms/mac/dev-setup)
- [Строка меню macOS](/platforms/mac/menu-bar)
- [Пробуждение по голосу в macOS](/platforms/mac/voicewake)
- [Наложение голоса в macOS](/platforms/mac/voice-overlay)
- [WebChat в macOS](/platforms/mac/webchat)
- [Canvas в macOS](/platforms/mac/canvas)
- [Дочерний процесс в macOS](/platforms/mac/child-process)
- [Состояние системы в macOS](/platforms/mac/health)
- [Иконка в macOS](/platforms/mac/icon)
- [Логирование в macOS](/platforms/mac/logging)
- [Разрешения в macOS](/platforms/mac/permissions)
- [Удалённый доступ в macOS](/platforms/mac/remote)
- [Подписание в macOS](/platforms/mac/signing)
- [Шлюз в macOS (launchd)](/platforms/mac/bundled-gateway)
- [XPC в macOS](/platforms/mac/xpc)
- [Навыки в macOS](/platforms/mac/skills)
- [Peekaboo в macOS](/platforms/mac/peekaboo)

## Расширения и плагины

- [Обзор плагинов](/tools/plugin)
- [Создание плагинов](/plugins/building-plugins)
- [Манифест плагина](/plugins/manifest)
- [Инструменты агента](/plugins/building-plugins#registering-agent-tools)
- [Пакеты плагинов](/plugins/bundles)
- [Плагины сообщества](/plugins/community)
- [Кулинарная книга возможностей](/tools/capability-cookbook)
- [Плагин голосовых вызовов](/plugins/voice-call)
- [Плагин пользователя Zalo](/plugins/zalouser)

## Рабочее пространство и шаблоны

- [Навыки](/tools/skills)
- [ClawHub](/tools/clawhub)
- [Конфигурация навыков](/tools/skills-config)
- [AGENTS по умолчанию](/reference/AGENTS.default)
- [Шаблоны: AGENTS](/reference/templates/AGENTS)
- [Шаблоны: BOOTSTRAP](/reference/templates/BOOTSTRAP)
- [Шаблоны: HEARTBEAT](/reference/templates/HEARTBEAT)
- [Шаблоны: IDENTITY](/reference/templates/IDENTITY)
- [Шаблоны: SOUL](/reference/templates/SOUL)
- [Шаблоны: TOOLS](/reference/templates/TOOLS)
- [Шаблоны: USER](/reference/templates/USER)

## Проект

- [Благодарности](/reference/credits)

## Тестирование и выпуск

- [Тестирование](/reference/test