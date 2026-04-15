---
read_when:
    - Piszesz testy dla Pluginu
    - Potrzebujesz narzędzi testowych z SDK Pluginu
    - Chcesz zrozumieć testy kontraktowe dla dołączonych pluginów
sidebarTitle: Testing
summary: Narzędzia testowe i wzorce dla pluginów OpenClaw
title: Testowanie Pluginów
x-i18n:
    generated_at: "2026-04-15T19:41:35Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2f75bd3f3b5ba34b05786e0dd96d493c36db73a1d258998bf589e27e45c0bd09
    source_path: plugins/sdk-testing.md
    workflow: 15
---

# Testowanie Pluginów

Dokumentacja narzędzi testowych, wzorców i egzekwowania reguł lintingu dla
pluginów OpenClaw.

<Tip>
  **Szukasz przykładów testów?** Przewodniki how-to zawierają gotowe przykłady testów:
  [Testy Pluginów kanałów](/pl/plugins/sdk-channel-plugins#step-6-test) oraz
  [Testy Pluginów dostawców](/pl/plugins/sdk-provider-plugins#step-6-test).
</Tip>

## Narzędzia testowe

**Import:** `openclaw/plugin-sdk/testing`

Podścieżka testowa eksportuje wąski zestaw pomocników dla autorów pluginów:

```typescript
import {
  installCommonResolveTargetErrorCases,
  shouldAckReaction,
  removeAckReactionAfterReply,
} from "openclaw/plugin-sdk/testing";
```

### Dostępne eksporty

| Export                                 | Cel                                                    |
| -------------------------------------- | ------------------------------------------------------ |
| `installCommonResolveTargetErrorCases` | Współdzielone przypadki testowe dla obsługi błędów rozwiązywania celu |
| `shouldAckReaction`                    | Sprawdza, czy kanał powinien dodać reakcję ack         |
| `removeAckReactionAfterReply`          | Usuwa reakcję ack po dostarczeniu odpowiedzi           |

### Typy

Podścieżka testowa ponownie eksportuje także typy przydatne w plikach testowych:

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

## Testowanie rozwiązywania celu

Użyj `installCommonResolveTargetErrorCases`, aby dodać standardowe przypadki błędów dla
rozwiązywania celu kanału:

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

## Wzorce testowania

### Testy jednostkowe Pluginu kanału

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

### Testy jednostkowe Pluginu dostawcy

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

### Mockowanie środowiska uruchomieniowego Pluginu

W przypadku kodu używającego `createPluginRuntimeStore` zamockuj runtime w testach:

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

### Testowanie z użyciem stubów per instancja

Preferuj stuby per instancja zamiast mutacji prototypu:

```typescript
// Preferred: per-instance stub
const client = new MyChannelClient();
client.sendMessage = vi.fn().mockResolvedValue({ id: "msg-1" });

// Avoid: prototype mutation
// MyChannelClient.prototype.sendMessage = vi.fn();
```

## Testy kontraktowe (pluginy w repozytorium)

Dołączone pluginy mają testy kontraktowe, które weryfikują własność rejestracji:

```bash
pnpm test -- src/plugins/contracts/
```

Te testy sprawdzają:

- Które pluginy rejestrują których dostawców
- Które pluginy rejestrują których dostawców mowy
- Poprawność kształtu rejestracji
- Zgodność z kontraktem runtime

### Uruchamianie testów zakresowych

Dla konkretnego pluginu:

```bash
pnpm test -- <bundled-plugin-root>/my-channel/
```

Tylko dla testów kontraktowych:

```bash
pnpm test -- src/plugins/contracts/shape.contract.test.ts
pnpm test -- src/plugins/contracts/auth.contract.test.ts
pnpm test -- src/plugins/contracts/runtime.contract.test.ts
```

## Egzekwowanie reguł lintingu (pluginy w repozytorium)

Trzy reguły są egzekwowane przez `pnpm check` dla pluginów w repozytorium:

1. **Brak monolitycznych importów z root** -- barrel root `openclaw/plugin-sdk` jest odrzucany
2. **Brak bezpośrednich importów z `src/`** -- pluginy nie mogą importować `../../src/` bezpośrednio
3. **Brak importów do siebie samych** -- pluginy nie mogą importować własnej podścieżki `plugin-sdk/<name>`

Zewnętrzne pluginy nie podlegają tym regułom lintingu, ale zaleca się stosowanie tych samych
wzorców.

## Konfiguracja testów

OpenClaw używa Vitest z progami pokrycia V8. Dla testów pluginów:

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

Jeśli lokalne uruchomienia powodują presję na pamięć:

```bash
OPENCLAW_VITEST_MAX_WORKERS=1 pnpm test
```

## Powiązane

- [Przegląd SDK](/pl/plugins/sdk-overview) -- konwencje importu
- [Pluginy kanałów SDK](/pl/plugins/sdk-channel-plugins) -- interfejs Pluginu kanału
- [Pluginy dostawców SDK](/pl/plugins/sdk-provider-plugins) -- hooki Pluginu dostawcy
- [Tworzenie Pluginów](/pl/plugins/building-plugins) -- przewodnik na początek
