---
title: "Обзор Plugin SDK"
sidebarTitle: "Обзор SDK"
summary: "Карта импортов, справочная информация по API регистрации и архитектура SDK"
read_when:
  - Вам нужно узнать, какой подпуть SDK следует импортировать
  - Вы хотите получить справочную информацию по всем методам регистрации в OpenClawPluginApi
  - Вы ищете конкретный экспорт SDK
---

# Обзор Plugin SDK

Plugin SDK — это типизированный контракт между плагинами и ядром системы. На этой странице представлена справочная информация о том, **что импортировать** и **что можно регистрировать**.

<Tip>
  **Ищете руководство по работе?**
  - Первый плагин? Начните с [Начало работы](/plugins/building-plugins)
  - Плагин для канала? Смотрите [Плагины для каналов](/plugins/sdk-channel-plugins)
  - Плагин для провайдера? Смотрите [Плагины для провайдеров](/plugins/sdk-provider-plugins)
</Tip>

## Правила импорта

Всегда импортируйте из конкретного подпути:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
```

Каждый подпуть представляет собой небольшой автономный модуль. Это позволяет ускорить запуск и избежать проблем с циклическими зависимостями. Для вспомогательных инструментов, специфичных для канала (entry/build), предпочтительно использовать `openclaw/plugin-sdk/channel-core`. Подпуть `openclaw/plugin-sdk/core` предназначен для более общих функций и вспомогательных инструментов, таких как `buildChannelConfigSchema`.

Не добавляйте и не используйте зависимости от именованных провайдеров, таких как `openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`, `openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp` или вспомогательных инструментов, привязанных к каналу. Встроенные плагины должны объединять общие подпути SDK внутри своих файлов `api.ts` или `runtime-api.ts`. Ядро должно либо использовать эти локальные для плагина файлы, либо добавлять узкий общий контракт SDK, если это действительно необходимо для работы с несколькими каналами.

Сгенерированная карта экспорта по-прежнему содержит небольшой набор вспомогательных инструментов для встроенных плагинов, таких как `plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`, `plugin-sdk/zalo-setup` и `plugin-sdk/matrix*`. Эти подпути существуют только для обслуживания и обеспечения совместимости встроенных плагинов; они намеренно не включены в общую таблицу ниже и не рекомендуются для импорта в новые сторонние плагины.

## Справочник по подпутям

Наиболее часто используемые подпути, сгруппированные по назначению. Полный список из более чем 200 подпутей находится в файле `scripts/lib/plugin-sdk-entrypoints.json`.

Зарезервированные вспомогательные подпути для встроенных плагинов по-прежнему присутствуют в этом сгенерированном списке. Рассматривайте их как детали реализации или поверхности совместимости, если только в документации явно не указано, что они являются общедоступными.

### Вход в плагин

| Подпуть | Ключевые экспорты |
| --- | --- |
| `plugin-sdk/plugin-entry` | `definePluginEntry` |
| `plugin-sdk/core` | `defineChannelPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase`, `defineSetupPluginEntry`, `buildChannelConfigSchema` |
| `plugin-sdk/config-schema` | `OpenClawSchema` |
| `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry` |

<AccordionGroup>
  <Accordion title="Подпути для каналов">
    | Подпуть | Ключевые экспорты |
    | --- | --- |
    | `plugin-sdk/channel-core` | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
    | `plugin-sdk/config-schema` | Корневой экспорт схемы Zod для `openclaw.json` (`OpenClawSchema`) |
    | `plugin-sdk/channel-setup` | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, а также `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
    | `plugin-sdk/setup` | Общие вспомогательные инструменты для мастера настройки, подсказки для списка разрешений, построители статуса настройки |
    | `plugin-sdk/setup-runtime` | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
    | `plugin-sdk/setup-adapter-runtime` | `createEnvPatchedAccountSetupAdapter` |
    | `plugin-sdk/setup-tools` | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
    | `plugin-sdk/account-core` | Вспомогательные инструменты для конфигурации с несколькими учётными записями/управления действиями, вспомогательные инструменты для резервной учётной записи по умолчанию |
    | `plugin-sdk/account-id` | `DEFAULT_ACCOUNT_ID`, вспомогательные инструменты для нормализации идентификатора учётной записи |
    | `plugin-sdk/account-resolution` | Вспомогательные инструменты для поиска учётной записи и резервного варианта по умолчанию |
    | `plugin-sdk/account-helpers` | Узкие вспомогательные инструменты для списка учётных записей/действий с учётными записями |
    | `plugin-sdk/channel-pairing` | `createChannelPairingController` |
    | `plugin-sdk/channel-reply-pipeline` | `createChannelReplyPipeline` |
    | `plugin-sdk/channel-config-helpers` | `createHybridChannelConfigAdapter` |
    | `plugin-sdk/channel-config-schema` | Типы схемы конфигурации канала |
    | `plugin-sdk/telegram-command-config` | Вспомогательные инструменты для нормализации/проверки пользовательских команд Telegram с резервным контрактом |
    | `plugin-sdk/channel-policy` | `resolveChannelGroupRequireMention` |
    | `plugin-sdk/channel-lifecycle` | `createAccountStatusSink` |
    | `plugin-sdk/inbound-envelope` | Общие вспомогательные инструменты для входящих маршрутов и построения конвертов |
    | `plugin-sdk/inbound-reply-dispatch` | Общие вспомогательные инструменты для записи и отправки входящих сообщений |
    | `plugin-sdk/messaging-targets` | Вспомогательные инструменты для анализа и сопоставления целевых объектов |
    | `plugin-sdk/outbound-media` | Общие вспомогательные инструменты для загрузки исходящих медиафайлов |
    | `plugin-sdk/outbound-runtime` | Вспомогательные инструменты для идентификации исходящих сообщений и делегирования отправки |
    | `plugin-sdk/thread-bindings-runtime` | Вспомогательные инструменты для жизненного цикла привязки потоков и адаптеров |
    | `plugin-sdk/agent-media-payload` | Устаревший инструмент для построения полезной нагрузки медиафайлов агента |
    | `plugin-sdk/conversation-runtime` | Привязка разговоров/потоков, сопоставление и настройка привязок |
    | `plugin-sdk/runtime-config-snapshot` | Вспомогательный инструмент для снимка конфигурации во время выполнения |
    | `plugin-sdk/runtime-group-policy` | Вспомогательные инструменты для разрешения групповых политик во время выполнения |
    | `plugin-sdk/channel-status` | Общие вспомогательные инструменты для снимков и сводок статуса канала |
    | `plugin-sdk/channel-config-primitives` | Узкие примитивы схемы конфигурации канала |
    | `plugin-sdk/channel-config-writes` | Вспомогательные инструменты для авторизации записи конфигурации канала |
    | `plugin-sdk/channel-plugin-common` | Общие предварительные экспорты для плагина канала |
    | `plugin-sdk/allowlist-config-edit` | Вспомогательные инструменты для редактирования/чтения конфигурации списка разрешений |
    | `plugin-sdk/group-access` | Общие вспомогательные инструменты для принятия решений о групповом доступе |
    | `plugin-sdk/direct-dm` | Общие вспомогательные инструменты для аутентификации и защиты прямых DM |
    | `plugin-sdk/interactive-runtime` | Вспомогательные инструменты для нормализации/сокращения полезной нагрузки интерактивных ответов |
    | `plugin-sdk/channel-inbound` | Вспомогательные инструменты для подавления повторных срабатываний, сопоставления упоминаний, политик упоминаний и построения конвертов |
    | `plugin-sdk/channel-send-result` | Типы результатов ответа |
    | `plugin-sdk/channel-actions` | `createMessageToolButtonsSchema`, `createMessageToolCardSchema` |
    | `plugin-sdk/channel-targets` | Вспомогательные инструменты для анализа и сопоставления целевых объектов |
    | `plugin-sdk/channel-contract` | Типы контрактов канала |
    | `plugin-sdk/channel-feedback` | Настройка обратной связи/реакций |
    | `plugin-sdk/