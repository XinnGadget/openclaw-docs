---
read_when:
    - Ви пишете тести для Plugin.
    - Вам потрібні утиліти тестування з Plugin SDK.
    - Ви хочете зрозуміти контрактні тести для вбудованих плагінів.
sidebarTitle: Testing
summary: Утиліти та шаблони тестування для Plugin OpenClaw
title: Тестування Plugin
x-i18n:
    generated_at: "2026-04-15T16:36:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2f75bd3f3b5ba34b05786e0dd96d493c36db73a1d258998bf589e27e45c0bd09
    source_path: plugins/sdk-testing.md
    workflow: 15
---

# Тестування Plugin

Довідник з утиліт тестування, шаблонів і перевірок lint для plugin OpenClaw.

<Tip>
  **Шукаєте приклади тестів?** Практичні посібники містять готові приклади тестів:
  [Тести channel plugin](/uk/plugins/sdk-channel-plugins#step-6-test) і
  [Тести provider plugin](/uk/plugins/sdk-provider-plugins#step-6-test).
</Tip>

## Утиліти тестування

**Імпорт:** `openclaw/plugin-sdk/testing`

Підшлях testing експортує вузький набір допоміжних засобів для авторів plugin:

```typescript
import {
  installCommonResolveTargetErrorCases,
  shouldAckReaction,
  removeAckReactionAfterReply,
} from "openclaw/plugin-sdk/testing";
```

### Доступні експорти

| Export                                 | Purpose                                          |
| -------------------------------------- | ------------------------------------------------ |
| `installCommonResolveTargetErrorCases` | Спільні тести для обробки помилок визначення цілі |
| `shouldAckReaction`                    | Перевіряє, чи має канал додавати ack-реакцію     |
| `removeAckReactionAfterReply`          | Видаляє ack-реакцію після доставки відповіді     |

### Типи

Підшлях testing також повторно експортує типи, корисні у файлах тестів:

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

## Тестування визначення цілі

Використовуйте `installCommonResolveTargetErrorCases`, щоб додати стандартні випадки помилок для
визначення цілі каналу:

```typescript
import { describe } from "vitest";
import { installCommonResolveTargetErrorCases } from "openclaw/plugin-sdk/testing";

describe("my-channel target resolution", () => {
  installCommonResolveTargetErrorCases({
    resolveTarget: ({ to, mode, allowFrom }) => {
      // Your channel's target resolution logic
      return myChannelResolveTarget({ to, mode, allowFrom });
    },
    implicitAllowFrom: ["user1", "user2"],
  });

  // Add channel-specific test cases
  it("should resolve @username targets", () => {
    // ...
  });
});
```

## Шаблони тестування

### Модульне тестування channel plugin

```typescript
import { describe, it, expect, vi } from "vitest";

describe("my-channel plugin", () => {
  it("should resolve account from config", () => {
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

  it("should inspect account without materializing secrets", () => {
    const cfg = {
      channels: {
        "my-channel": { token: "test-token" },
      },
    };

    const inspection = myPlugin.setup.inspectAccount(cfg, undefined);
    expect(inspection.configured).toBe(true);
    expect(inspection.tokenStatus).toBe("available");
    // No token value exposed
    expect(inspection).not.toHaveProperty("token");
  });
});
```

### Модульне тестування provider plugin

```typescript
import { describe, it, expect } from "vitest";

describe("my-provider plugin", () => {
  it("should resolve dynamic models", () => {
    const model = myProvider.resolveDynamicModel({
      modelId: "custom-model-v2",
      // ... context
    });

    expect(model.id).toBe("custom-model-v2");
    expect(model.provider).toBe("my-provider");
    expect(model.api).toBe("openai-completions");
  });

  it("should return catalog when API key is available", async () => {
    const result = await myProvider.catalog.run({
      resolveProviderApiKey: () => ({ apiKey: "test-key" }),
      // ... context
    });

    expect(result?.provider?.models).toHaveLength(2);
  });
});
```

### Імітація runtime Plugin

Для коду, який використовує `createPluginRuntimeStore`, імітуйте runtime у тестах:

```typescript
import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";
import type { PluginRuntime } from "openclaw/plugin-sdk/runtime-store";

const store = createPluginRuntimeStore<PluginRuntime>({
  pluginId: "test-plugin",
  errorMessage: "test runtime not set",
});

// In test setup
const mockRuntime = {
  agent: {
    resolveAgentDir: vi.fn().mockReturnValue("/tmp/agent"),
    // ... other mocks
  },
  config: {
    loadConfig: vi.fn(),
    writeConfigFile: vi.fn(),
  },
  // ... other namespaces
} as unknown as PluginRuntime;

store.setRuntime(mockRuntime);

// After tests
store.clearRuntime();
```

### Тестування зі stub для окремих екземплярів

Надавайте перевагу stub для окремих екземплярів замість мутації prototype:

```typescript
// Preferred: per-instance stub
const client = new MyChannelClient();
client.sendMessage = vi.fn().mockResolvedValue({ id: "msg-1" });

// Avoid: prototype mutation
// MyChannelClient.prototype.sendMessage = vi.fn();
```

## Контрактні тести (plugin у репозиторії)

Вбудовані plugin мають контрактні тести, які перевіряють відповідальність за реєстрацію:

```bash
pnpm test -- src/plugins/contracts/
```

Ці тести перевіряють:

- Які plugin реєструють які providers
- Які plugin реєструють які speech providers
- Коректність форми реєстрації
- Відповідність runtime-контракту

### Запуск вибіркових тестів

Для конкретного plugin:

```bash
pnpm test -- <bundled-plugin-root>/my-channel/
```

Лише для контрактних тестів:

```bash
pnpm test -- src/plugins/contracts/shape.contract.test.ts
pnpm test -- src/plugins/contracts/auth.contract.test.ts
pnpm test -- src/plugins/contracts/runtime.contract.test.ts
```

## Перевірки lint (plugin у репозиторії)

`pnpm check` примусово застосовує три правила для plugin у репозиторії:

1. **Без монолітних імпортів із кореня** -- кореневий barrel `openclaw/plugin-sdk` заборонено
2. **Без прямих імпортів `src/`** -- plugin не можуть напряму імпортувати `../../src/`
3. **Без самоімпортів** -- plugin не можуть імпортувати власний підшлях `plugin-sdk/<name>`

Зовнішні plugin не підпадають під ці правила lint, але дотримуватися тих самих
шаблонів рекомендується.

## Конфігурація тестування

OpenClaw використовує Vitest із порогами покриття V8. Для тестів plugin:

```bash
# Run all tests
pnpm test

# Run specific plugin tests
pnpm test -- <bundled-plugin-root>/my-channel/src/channel.test.ts

# Run with a specific test name filter
pnpm test -- <bundled-plugin-root>/my-channel/ -t "resolves account"

# Run with coverage
pnpm test:coverage
```

Якщо локальні запуски спричиняють тиск на пам’ять:

```bash
OPENCLAW_VITEST_MAX_WORKERS=1 pnpm test
```

## Пов’язане

- [Огляд SDK](/uk/plugins/sdk-overview) -- правила імпорту
- [SDK Channel Plugins](/uk/plugins/sdk-channel-plugins) -- інтерфейс channel plugin
- [SDK Provider Plugins](/uk/plugins/sdk-provider-plugins) -- хуки provider plugin
- [Створення plugin](/uk/plugins/building-plugins) -- посібник для початку роботи
