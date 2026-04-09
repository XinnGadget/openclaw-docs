---
title: "Тестирование плагинов"
sidebarTitle: "Тестирование"
summary: "Утилиты и шаблоны тестирования для плагинов OpenClaw"
read_when:
  - Вы пишете тесты для плагина
  - Вам нужны утилиты тестирования из SDK плагина
  - Вы хотите разобраться в контрактных тестах для встроенных плагинов
---

# Тестирование плагинов

Справочник по утилитам тестирования, шаблонам и правилам линтинга для плагинов OpenClaw.

<Tip>
  **Ищете примеры тестов?** В руководствах есть проработанные примеры тестов:
  [Тесты для плагинов каналов](/plugins/sdk-channel-plugins#step-6-test) и
  [Тесты для плагинов провайдеров](/plugins/sdk-provider-plugins#step-6-test).
</Tip>

## Утилиты тестирования

**Импорт:** `openclaw/plugin-sdk/testing`

Подпуть для тестирования экспортирует ограниченный набор вспомогательных функций для авторов плагинов:

```typescript
import {
  installCommonResolveTargetErrorCases,
  shouldAckReaction,
  removeAckReactionAfterReply,
} from "openclaw/plugin-sdk/testing";
```

### Доступные экспорты

| Экспорт | Назначение |
| --- | --- |
| `installCommonResolveTargetErrorCases` | Общие тестовые случаи для обработки ошибок разрешения цели |
| `shouldAckReaction` | Проверка, должен ли канал добавить реакцию подтверждения (ack reaction) |
| `removeAckReactionAfterReply` | Удаление реакции подтверждения после доставки ответа |

### Типы

Подпуть для тестирования также повторно экспортирует типы, полезные в тестовых файлах:

```typescript
import type {
  ChannelAccountSnapshot,
  ChannelGatewayContext,
  OpenClawConfig,
  PluginRuntime,
  RuntimeEnv,
  MockFn,
} from "openclaw/plugin-sdk/testing";
```

## Тестирование разрешения цели

Используйте `installCommonResolveTargetErrorCases`, чтобы добавить стандартные тестовые случаи для ошибок разрешения цели канала:

```typescript
import { describe } from "vitest";
import { installCommonResolveTargetErrorCases } from "openclaw/plugin-sdk/testing";

describe("разрешение цели для my-channel", () => {
  installCommonResolveTargetErrorCases({
    resolveTarget: ({ to, mode, allowFrom }) => {
      // Логика разрешения цели для вашего канала
      return myChannelResolveTarget({ to, mode, allowFrom });
    },
    implicitAllowFrom: ["user1", "user2"],
  });

  // Добавьте тестовые случаи, специфичные для канала
  it("должен разрешать цели @username", () => {
    // ...
  });
});
```

## Шаблоны тестирования

### Модульное тестирование плагина канала

```typescript
import { describe, it, expect, vi } from "vitest";

describe("плагин my-channel", () => {
  it("должен извлекать аккаунт из конфигурации", () => {
    const cfg = {
      channels: {
        "my-channel": {
          token: "test-token",
          allowFrom: ["user1"],
        },
      },
    };

    const account = myPlugin.setup.resolveAccount(cfg, undefined);
    expect(account.token).toBe("test-token");
  });

  it("должен проверять аккаунт без раскрытия секретов", () => {
    const cfg = {
      channels: {
        "my-channel": { token: "test-token" },
      },
    };

    const inspection = myPlugin.setup.inspectAccount(cfg, undefined);
    expect(inspection.configured).toBe(true);
    expect(inspection.tokenStatus).toBe("available");
    // Значение токена не раскрывается
    expect(inspection).not.toHaveProperty("token");
  });
});
```

### Модульное тестирование плагина провайдера

```typescript
import { describe, it, expect } from "vitest";

describe("плагин my-provider", () => {
  it("должен разрешать динамические модели", () => {
    const model = myProvider.resolveDynamicModel({
      modelId: "custom-model-v2",
      // ... контекст
    });

    expect(model.id).toBe("custom-model-v2");
    expect(model.provider).toBe("my-provider");
    expect(model.api).toBe("openai-completions");
  });

  it("должен возвращать каталог, когда ключ API доступен", async () => {
    const result = await myProvider.catalog.run({
      resolveProviderApiKey: () => ({ apiKey: "test-key" }),
      // ... контекст
    });

    expect(result?.provider?.models).toHaveLength(2);
  });
});
```

### Имитация среды выполнения плагина

Для кода, использующего `createPluginRuntimeStore`, имитируйте среду выполнения в тестах:

```typescript
import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";
import type { PluginRuntime } from "openclaw/plugin-sdk/runtime-store";

const store = createPluginRuntimeStore<PluginRuntime>("test runtime not set");

// В настройке теста
const mockRuntime = {
  agent: {
    resolveAgentDir: vi.fn().mockReturnValue("/tmp/agent"),
    // ... другие имитации
  },
  config: {
    loadConfig: vi.fn(),
    writeConfigFile: vi.fn(),
  },
  // ... другие пространства имён
} as unknown as PluginRuntime;

store.setRuntime(mockRuntime);

// После тестов
store.clearRuntime();
```

### Тестирование с заглушками для отдельных экземпляров

Предпочитайте заглушки для отдельных экземпляров изменению прототипа:

```typescript
// Предпочтительно: заглушка для отдельного экземпляра
const client = new MyChannelClient();
client.sendMessage = vi.fn().mockResolvedValue({ id: "msg-1" });

// Избегайте: изменение прототипа
// MyChannelClient.prototype.sendMessage = vi.fn();
```

## Контрактные тесты (встроенные плагины)

Встроенные плагины имеют контрактные тесты, которые проверяют право собственности на регистрацию:

```bash
pnpm test -- src/plugins/contracts/
```

Эти тесты проверяют:

- Какие плагины регистрируют какие провайдеры
- Какие плагины регистрируют какие провайдеры речи
- Корректность формы регистрации
- Соответствие контракту среды выполнения

### Запуск тестов для определённого плагина

Для конкретного плагина:

```bash
pnpm test -- <bundled-plugin-root>/my-channel/
```

Только для контрактных тестов:

```bash
pnpm test -- src/plugins/contracts/shape.contract.test.ts
pnpm test -- src/plugins/contracts/auth.contract.test.ts
pnpm test -- src/plugins/contracts/runtime.contract.test.ts
```

## Правила линтинга (встроенные плагины)

Команда `pnpm check` для встроенных плагинов применяет три правила:

1. **Отсутствие монолитных корневых импортов** — корневой "баррель" `openclaw/plugin-sdk` не допускается
2. **Отсутствие прямых импортов `src/`** — плагины не могут напрямую импортировать `../../src/`
3. **Отсутствие самоимпортов** — плагины не могут импортировать свой собственный подпуть `plugin-sdk/<name>`

Для внешних плагинов эти правила линтинга не применяются, но рекомендуется следовать тем же шаблонам.

## Конфигурация тестирования

OpenClaw использует Vitest с порогами покрытия V8. Для тестов плагинов:

```bash
# Запустить все тесты
pnpm test

# Запустить тесты для конкретного плагина
pnpm test -- <bundled-plugin-root>/my-channel/src/channel.test.ts

# Запустить с фильтром по имени теста
pnpm test -- <bundled-plugin-root>/my-channel/ -t "resolves account"

# Запустить с покрытием
pnpm test:coverage
```

Если локальные запуски вызывают нагрузку на память:

```bash
OPENCLAW_VITEST_MAX_WORKERS=1 pnpm test
```

## Связанные материалы

- [Обзор SDK](/plugins/sdk-overview) — соглашения об импорте
- [Плагины каналов SDK](/plugins/sdk-channel-plugins) — интерфейс плагина канала
- [Плагины провайдеров SDK](/plugins/sdk-provider-plugins) — хуки плагина провайдера
- [Создание плагинов](/plugins/building-plugins) — руководство по началу работы