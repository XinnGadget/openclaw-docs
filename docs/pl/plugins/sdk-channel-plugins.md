---
read_when:
    - Tworzysz nowy plugin kanału wiadomości
    - Chcesz połączyć OpenClaw z platformą komunikacyjną
    - Musisz zrozumieć powierzchnię adaptera ChannelPlugin
sidebarTitle: Channel Plugins
summary: Przewodnik krok po kroku po tworzeniu pluginu kanału wiadomości dla OpenClaw
title: Tworzenie pluginów kanałów
x-i18n:
    generated_at: "2026-04-06T03:09:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: 66b52c10945a8243d803af3bf7e1ea0051869ee92eda2af5718d9bb24fbb8552
    source_path: plugins/sdk-channel-plugins.md
    workflow: 15
---

# Tworzenie pluginów kanałów

Ten przewodnik pokazuje, jak zbudować plugin kanału, który łączy OpenClaw z
platformą komunikacyjną. Na końcu będziesz mieć działający kanał z
zabezpieczeniami DM, parowaniem, wątkowaniem odpowiedzi i wiadomościami wychodzącymi.

<Info>
  Jeśli nie zbudowano jeszcze żadnego pluginu OpenClaw, najpierw przeczytaj
  [Pierwsze kroki](/pl/plugins/building-plugins), aby poznać podstawową strukturę
  pakietu i konfigurację manifestu.
</Info>

## Jak działają pluginy kanałów

Pluginy kanałów nie potrzebują własnych narzędzi do wysyłania/edycji/reakcji. OpenClaw utrzymuje jedno
wspólne narzędzie `message` w rdzeniu. Twój plugin odpowiada za:

- **Config** — rozpoznawanie kont i kreator konfiguracji
- **Security** — politykę DM i listy dozwolonych
- **Pairing** — przepływ zatwierdzania DM
- **Session grammar** — sposób, w jaki identyfikatory rozmów specyficzne dla dostawcy mapują się na czaty bazowe, identyfikatory wątków i fallbacki rodziców
- **Outbound** — wysyłanie tekstu, multimediów i ankiet na platformę
- **Threading** — sposób wątkowania odpowiedzi

Rdzeń zarządza wspólnym narzędziem wiadomości, połączeniem promptów, zewnętrznym kształtem klucza sesji,
ogólnym księgowaniem `:thread:` i dystrybucją.

Jeśli Twoja platforma przechowuje dodatkowy zakres wewnątrz identyfikatorów rozmów, zachowaj
to parsowanie w pluginie za pomocą `messaging.resolveSessionConversation(...)`. To jest
kanoniczny hook do mapowania `rawId` na bazowy identyfikator rozmowy, opcjonalny identyfikator wątku,
jawny `baseConversationId` i dowolne `parentConversationCandidates`.
Gdy zwracasz `parentConversationCandidates`, zachowuj ich kolejność od
najwęższego rodzica do najszerszej/bazowej rozmowy.

Dołączone pluginy, które potrzebują tego samego parsowania przed uruchomieniem rejestru kanałów,
mogą także udostępniać plik najwyższego poziomu `session-key-api.ts` z odpowiadającym
eksportem `resolveSessionConversation(...)`. Rdzeń używa tej bezpiecznej dla bootstrapu powierzchni
tylko wtedy, gdy rejestr pluginów runtime nie jest jeszcze dostępny.

`messaging.resolveParentConversationCandidates(...)` pozostaje dostępne jako
starszy fallback zgodności, gdy plugin potrzebuje fallbacków rodziców tylko na
szczycie ogólnego/surowego identyfikatora. Jeśli istnieją oba hooki, rdzeń najpierw używa
`resolveSessionConversation(...).parentConversationCandidates` i dopiero
przechodzi awaryjnie do `resolveParentConversationCandidates(...)`, gdy kanoniczny hook
je pomija.

## Zatwierdzenia i capabilities kanału

Większość pluginów kanałów nie potrzebuje kodu specyficznego dla zatwierdzeń.

- Rdzeń zarządza `/approve` w tym samym czacie, współdzielonymi payloadami przycisków zatwierdzania i ogólnym dostarczaniem awaryjnym.
- Preferuj pojedynczy obiekt `approvalCapability` na pluginie kanału, gdy kanał wymaga zachowania specyficznego dla zatwierdzeń.
- `approvalCapability.authorizeActorAction` i `approvalCapability.getActionAvailabilityState` to kanoniczna powierzchnia uwierzytelniania zatwierdzeń.
- Jeśli kanał udostępnia natywne zatwierdzenia exec, zaimplementuj `approvalCapability.getActionAvailabilityState`, nawet gdy natywny transport znajduje się w całości pod `approvalCapability.native`. Rdzeń używa tego hooka dostępności do rozróżnienia `enabled` i `disabled`, określenia, czy kanał inicjujący obsługuje natywne zatwierdzenia, oraz uwzględnienia kanału we wskazówkach awaryjnych dla klienta natywnego.
- Użyj `outbound.shouldSuppressLocalPayloadPrompt` lub `outbound.beforeDeliverPayload` dla zachowań cyklu życia payloadu specyficznych dla kanału, takich jak ukrywanie zduplikowanych lokalnych promptów zatwierdzenia lub wysyłanie wskaźników pisania przed dostarczeniem.
- Używaj `approvalCapability.delivery` tylko dla natywnego routingu zatwierdzeń lub tłumienia fallbacku.
- Używaj `approvalCapability.render` tylko wtedy, gdy kanał naprawdę potrzebuje niestandardowych payloadów zatwierdzeń zamiast współdzielonego renderer.
- Użyj `approvalCapability.describeExecApprovalSetup`, gdy kanał chce, aby odpowiedź dla ścieżki wyłączonej wyjaśniała dokładne klucze config potrzebne do włączenia natywnych zatwierdzeń exec. Hook otrzymuje `{ channel, channelLabel, accountId }`; kanały z nazwanymi kontami powinny renderować ścieżki o zakresie konta, takie jak `channels.<channel>.accounts.<id>.execApprovals.*`, zamiast domyślnych ustawień najwyższego poziomu.
- Jeśli kanał może wywnioskować stabilne tożsamości DM podobne do właściciela z istniejącej konfiguracji, użyj `createResolvedApproverActionAuthAdapter` z `openclaw/plugin-sdk/approval-runtime`, aby ograniczyć `/approve` w tym samym czacie bez dodawania logiki specyficznej dla zatwierdzeń do rdzenia.
- Jeśli kanał potrzebuje natywnego dostarczania zatwierdzeń, utrzymuj kod kanału skupiony na normalizacji celu i hookach transportowych. Użyj `createChannelExecApprovalProfile`, `createChannelNativeOriginTargetResolver`, `createChannelApproverDmTargetResolver`, `createApproverRestrictedNativeApprovalCapability` i `createChannelNativeApprovalRuntime` z `openclaw/plugin-sdk/approval-runtime`, aby rdzeń zarządzał filtrowaniem żądań, routingiem, deduplikacją, wygaśnięciem i subskrypcją gateway.
- Kanały natywnych zatwierdzeń muszą przekazywać przez te helpery zarówno `accountId`, jak i `approvalKind`. `accountId` utrzymuje politykę zatwierdzeń wielokontowych w zakresie właściwego konta bota, a `approvalKind` zachowuje zachowanie zatwierdzeń exec vs plugin dostępne dla kanału bez zakodowanych na stałe gałęzi w rdzeniu.
- Zachowuj rodzaj dostarczonego identyfikatora zatwierdzenia end-to-end. Klienci natywni nie powinni
  zgadywać ani przepisywać routingu zatwierdzeń exec vs plugin na podstawie stanu lokalnego kanału.
- Różne rodzaje zatwierdzeń mogą celowo ujawniać różne powierzchnie natywne.
  Aktualne dołączone przykłady:
  - Slack zachowuje natywny routing zatwierdzeń dostępny zarówno dla identyfikatorów exec, jak i plugin.
  - Matrix zachowuje natywny routing DM/kanału tylko dla zatwierdzeń exec i pozostawia
    zatwierdzenia plugin na współdzielonej ścieżce `/approve` w tym samym czacie.
- `createApproverRestrictedNativeApprovalAdapter` nadal istnieje jako opakowanie zgodności, ale nowy kod powinien preferować builder capability i ujawniać `approvalCapability` w pluginie.

Dla gorących punktów wejścia kanału preferuj węższe subścieżki runtime, gdy potrzebujesz tylko jednej części tej rodziny:

- `openclaw/plugin-sdk/approval-auth-runtime`
- `openclaw/plugin-sdk/approval-client-runtime`
- `openclaw/plugin-sdk/approval-delivery-runtime`
- `openclaw/plugin-sdk/approval-native-runtime`
- `openclaw/plugin-sdk/approval-reply-runtime`

Podobnie preferuj `openclaw/plugin-sdk/setup-runtime`,
`openclaw/plugin-sdk/setup-adapter-runtime`,
`openclaw/plugin-sdk/reply-runtime`,
`openclaw/plugin-sdk/reply-dispatch-runtime`,
`openclaw/plugin-sdk/reply-reference` i
`openclaw/plugin-sdk/reply-chunking`, gdy nie potrzebujesz szerszej
zbiorczej powierzchni.

Konkretnie dla konfiguracji:

- `openclaw/plugin-sdk/setup-runtime` obejmuje bezpieczne dla runtime helpery konfiguracji:
  bezpieczne dla importu adaptery łatania konfiguracji (`createPatchedAccountSetupAdapter`,
  `createEnvPatchedAccountSetupAdapter`,
  `createSetupInputPresenceValidator`), dane wyjściowe notatek wyszukiwania,
  `promptResolvedAllowFrom`, `splitSetupEntries` oraz delegowane
  buildery proxy konfiguracji
- `openclaw/plugin-sdk/setup-adapter-runtime` to wąska, świadoma env powierzchnia
  adaptera dla `createEnvPatchedAccountSetupAdapter`
- `openclaw/plugin-sdk/channel-setup` obejmuje buildery konfiguracji z opcjonalną instalacją
  oraz kilka bezpiecznych dla konfiguracji prymitywów:
  `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`,
  `createOptionalChannelSetupWizard`, `DEFAULT_ACCOUNT_ID`,
  `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled` oraz
  `splitSetupEntries`
- używaj szerszej powierzchni `openclaw/plugin-sdk/setup` tylko wtedy, gdy potrzebujesz także
  cięższych współdzielonych helperów konfiguracji/config, takich jak
  `moveSingleAccountChannelSectionToDefaultAccount(...)`

Jeśli Twój kanał chce jedynie reklamować „najpierw zainstaluj ten plugin” w powierzchniach konfiguracji, preferuj `createOptionalChannelSetupSurface(...)`. Wygenerowane
adapter/wizard domyślnie odmawiają zapisu config i finalizacji, a także ponownie wykorzystują
ten sam komunikat wymagający instalacji w walidacji, finalizacji i treści z linkiem do dokumentacji.

Dla innych gorących ścieżek kanału preferuj wąskie helpery zamiast szerszych starszych powierzchni:

- `openclaw/plugin-sdk/account-core`,
  `openclaw/plugin-sdk/account-id`,
  `openclaw/plugin-sdk/account-resolution` oraz
  `openclaw/plugin-sdk/account-helpers` dla konfiguracji wielokontowej i
  fallbacku do konta domyślnego
- `openclaw/plugin-sdk/inbound-envelope` oraz
  `openclaw/plugin-sdk/inbound-reply-dispatch` dla routingu/koperty wejściowej i
  połączenia record-and-dispatch
- `openclaw/plugin-sdk/messaging-targets` dla parsowania/dopasowania celów
- `openclaw/plugin-sdk/outbound-media` oraz
  `openclaw/plugin-sdk/outbound-runtime` dla ładowania multimediów i delegatów tożsamości/wysyłki wychodzącej
- `openclaw/plugin-sdk/thread-bindings-runtime` dla cyklu życia powiązań wątków
  i rejestracji adapterów
- `openclaw/plugin-sdk/agent-media-payload` tylko wtedy, gdy nadal wymagany jest starszy układ pól payloadu agenta/multimediów
- `openclaw/plugin-sdk/telegram-command-config` dla normalizacji niestandardowych poleceń Telegrama, walidacji duplikatów/konfliktów i kontraktu config poleceń stabilnego względem fallbacku

Kanały tylko z auth zwykle mogą zatrzymać się na ścieżce domyślnej: rdzeń obsługuje zatwierdzenia, a plugin po prostu ujawnia capabilities outbound/auth. Kanały z natywnymi zatwierdzeniami, takie jak Matrix, Slack, Telegram i niestandardowe transporty czatu, powinny używać współdzielonych natywnych helperów zamiast tworzyć własny cykl życia zatwierdzeń.

## Przewodnik krok po kroku

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="Pakiet i manifest">
    Utwórz standardowe pliki pluginu. Pole `channel` w `package.json`
    sprawia, że jest to plugin kanału. Pełny opis powierzchni metadanych pakietu
    znajdziesz w [Konfiguracja pluginu i Config](/pl/plugins/sdk-setup#openclawchannel):

    <CodeGroup>
    ```json package.json
    {
      "name": "@myorg/openclaw-acme-chat",
      "version": "1.0.0",
      "type": "module",
      "openclaw": {
        "extensions": ["./index.ts"],
        "setupEntry": "./setup-entry.ts",
        "channel": {
          "id": "acme-chat",
          "label": "Acme Chat",
          "blurb": "Connect OpenClaw to Acme Chat."
        }
      }
    }
    ```

    ```json openclaw.plugin.json
    {
      "id": "acme-chat",
      "kind": "channel",
      "channels": ["acme-chat"],
      "name": "Acme Chat",
      "description": "Acme Chat channel plugin",
      "configSchema": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "acme-chat": {
            "type": "object",
            "properties": {
              "token": { "type": "string" },
              "allowFrom": {
                "type": "array",
                "items": { "type": "string" }
              }
            }
          }
        }
      }
    }
    ```
    </CodeGroup>

  </Step>

  <Step title="Zbuduj obiekt pluginu kanału">
    Interfejs `ChannelPlugin` ma wiele opcjonalnych powierzchni adapterów. Zacznij od
    minimum — `id` i `setup` — i dodawaj adaptery według potrzeb.

    Utwórz `src/channel.ts`:

    ```typescript src/channel.ts
    import {
      createChatChannelPlugin,
      createChannelPluginBase,
    } from "openclaw/plugin-sdk/channel-core";
    import type { OpenClawConfig } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatApi } from "./client.js"; // your platform API client

    type ResolvedAccount = {
      accountId: string | null;
      token: string;
      allowFrom: string[];
      dmPolicy: string | undefined;
    };

    function resolveAccount(
      cfg: OpenClawConfig,
      accountId?: string | null,
    ): ResolvedAccount {
      const section = (cfg.channels as Record<string, any>)?.["acme-chat"];
      const token = section?.token;
      if (!token) throw new Error("acme-chat: token is required");
      return {
        accountId: accountId ?? null,
        token,
        allowFrom: section?.allowFrom ?? [],
        dmPolicy: section?.dmSecurity,
      };
    }

    export const acmeChatPlugin = createChatChannelPlugin<ResolvedAccount>({
      base: createChannelPluginBase({
        id: "acme-chat",
        setup: {
          resolveAccount,
          inspectAccount(cfg, accountId) {
            const section =
              (cfg.channels as Record<string, any>)?.["acme-chat"];
            return {
              enabled: Boolean(section?.token),
              configured: Boolean(section?.token),
              tokenStatus: section?.token ? "available" : "missing",
            };
          },
        },
      }),

      // DM security: who can message the bot
      security: {
        dm: {
          channelKey: "acme-chat",
          resolvePolicy: (account) => account.dmPolicy,
          resolveAllowFrom: (account) => account.allowFrom,
          defaultPolicy: "allowlist",
        },
      },

      // Pairing: approval flow for new DM contacts
      pairing: {
        text: {
          idLabel: "Acme Chat username",
          message: "Send this code to verify your identity:",
          notify: async ({ target, code }) => {
            await acmeChatApi.sendDm(target, `Pairing code: ${code}`);
          },
        },
      },

      // Threading: how replies are delivered
      threading: { topLevelReplyToMode: "reply" },

      // Outbound: send messages to the platform
      outbound: {
        attachedResults: {
          sendText: async (params) => {
            const result = await acmeChatApi.sendMessage(
              params.to,
              params.text,
            );
            return { messageId: result.id };
          },
        },
        base: {
          sendMedia: async (params) => {
            await acmeChatApi.sendFile(params.to, params.filePath);
          },
        },
      },
    });
    ```

    <Accordion title="Co daje createChatChannelPlugin">
      Zamiast ręcznie implementować niskopoziomowe interfejsy adapterów,
      przekazujesz deklaratywne opcje, a builder składa je razem:

      | Option | Co łączy |
      | --- | --- |
      | `security.dm` | Rozpoznawanie zabezpieczeń DM o określonym zakresie na podstawie pól config |
      | `pairing.text` | Tekstowy przepływ parowania DM z wymianą kodu |
      | `threading` | Rozpoznawanie trybu reply-to (stały, zależny od konta lub niestandardowy) |
      | `outbound.attachedResults` | Funkcje wysyłające, które zwracają metadane wyniku (identyfikatory wiadomości) |

      Możesz też przekazać surowe obiekty adapterów zamiast opcji deklaratywnych,
      jeśli potrzebujesz pełnej kontroli.
    </Accordion>

  </Step>

  <Step title="Podłącz punkt wejścia">
    Utwórz `index.ts`:

    ```typescript index.ts
    import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatPlugin } from "./src/channel.js";

    export default defineChannelPluginEntry({
      id: "acme-chat",
      name: "Acme Chat",
      description: "Acme Chat channel plugin",
      plugin: acmeChatPlugin,
      registerCliMetadata(api) {
        api.registerCli(
          ({ program }) => {
            program
              .command("acme-chat")
              .description("Acme Chat management");
          },
          {
            descriptors: [
              {
                name: "acme-chat",
                description: "Acme Chat management",
                hasSubcommands: false,
              },
            ],
          },
        );
      },
      registerFull(api) {
        api.registerGatewayMethod(/* ... */);
      },
    });
    ```

    Umieszczaj deskryptory CLI należące do kanału w `registerCliMetadata(...)`, aby OpenClaw
    mógł pokazywać je w pomocy głównej bez aktywowania pełnego runtime kanału,
    podczas gdy zwykłe pełne ładowania nadal pobiorą te same deskryptory do rzeczywistej rejestracji poleceń. Zachowaj `registerFull(...)` dla pracy tylko w runtime.
    Jeśli `registerFull(...)` rejestruje metody Gateway RPC, użyj
    prefiksu specyficznego dla pluginu. Przestrzenie nazw administratora rdzenia (`config.*`,
    `exec.approvals.*`, `wizard.*`, `update.*`) pozostają zarezerwowane i zawsze
    wskazują na `operator.admin`.
    `defineChannelPluginEntry` automatycznie obsługuje podział trybów rejestracji. Zobacz
    [Punkty wejścia](/pl/plugins/sdk-entrypoints#definechannelpluginentry), aby poznać wszystkie
    opcje.

  </Step>

  <Step title="Dodaj wpis konfiguracji">
    Utwórz `setup-entry.ts` do lekkiego ładowania podczas onboardingu:

    ```typescript setup-entry.ts
    import { defineSetupPluginEntry } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatPlugin } from "./src/channel.js";

    export default defineSetupPluginEntry(acmeChatPlugin);
    ```

    OpenClaw ładuje to zamiast pełnego punktu wejścia, gdy kanał jest wyłączony
    lub nieskonfigurowany. Pozwala to uniknąć wciągania ciężkiego kodu runtime podczas przepływów konfiguracji.
    Szczegóły znajdziesz w [Konfiguracja i Config](/pl/plugins/sdk-setup#setup-entry).

  </Step>

  <Step title="Obsłuż wiadomości przychodzące">
    Twój plugin musi odbierać wiadomości z platformy i przekazywać je do
    OpenClaw. Typowy wzorzec to webhook, który weryfikuje żądanie i
    przekazuje je przez przychodzący handler Twojego kanału:

    ```typescript
    registerFull(api) {
      api.registerHttpRoute({
        path: "/acme-chat/webhook",
        auth: "plugin", // plugin-managed auth (verify signatures yourself)
        handler: async (req, res) => {
          const event = parseWebhookPayload(req);

          // Your inbound handler dispatches the message to OpenClaw.
          // The exact wiring depends on your platform SDK —
          // see a real example in the bundled Microsoft Teams or Google Chat plugin package.
          await handleAcmeChatInbound(api, event);

          res.statusCode = 200;
          res.end("ok");
          return true;
        },
      });
    }
    ```

    <Note>
      Obsługa wiadomości przychodzących jest specyficzna dla kanału. Każdy plugin kanału zarządza
      własnym pipeline wiadomości przychodzących. Spójrz na dołączone pluginy kanałów
      (na przykład pakiet pluginu Microsoft Teams lub Google Chat), aby zobaczyć rzeczywiste wzorce.
    </Note>

  </Step>

<a id="step-6-test"></a>
<Step title="Testowanie">
Pisz testy współlokalizowane w `src/channel.test.ts`:

    ```typescript src/channel.test.ts
    import { describe, it, expect } from "vitest";
    import { acmeChatPlugin } from "./channel.js";

    describe("acme-chat plugin", () => {
      it("resolves account from config", () => {
        const cfg = {
          channels: {
            "acme-chat": { token: "test-token", allowFrom: ["user1"] },
          },
        } as any;
        const account = acmeChatPlugin.setup!.resolveAccount(cfg, undefined);
        expect(account.token).toBe("test-token");
      });

      it("inspects account without materializing secrets", () => {
        const cfg = {
          channels: { "acme-chat": { token: "test-token" } },
        } as any;
        const result = acmeChatPlugin.setup!.inspectAccount!(cfg, undefined);
        expect(result.configured).toBe(true);
        expect(result.tokenStatus).toBe("available");
      });

      it("reports missing config", () => {
        const cfg = { channels: {} } as any;
        const result = acmeChatPlugin.setup!.inspectAccount!(cfg, undefined);
        expect(result.configured).toBe(false);
      });
    });
    ```

    ```bash
    pnpm test -- <bundled-plugin-root>/acme-chat/
    ```

    Współdzielone helpery testowe znajdziesz w [Testowanie](/pl/plugins/sdk-testing).

  </Step>
</Steps>

## Struktura plików

```
<bundled-plugin-root>/acme-chat/
├── package.json              # metadane openclaw.channel
├── openclaw.plugin.json      # Manifest ze schematem config
├── index.ts                  # defineChannelPluginEntry
├── setup-entry.ts            # defineSetupPluginEntry
├── api.ts                    # Publiczne eksporty (opcjonalnie)
├── runtime-api.ts            # Wewnętrzne eksporty runtime (opcjonalnie)
└── src/
    ├── channel.ts            # ChannelPlugin przez createChatChannelPlugin
    ├── channel.test.ts       # Testy
    ├── client.ts             # Klient API platformy
    └── runtime.ts            # Magazyn runtime (jeśli potrzebny)
```

## Tematy zaawansowane

<CardGroup cols={2}>
  <Card title="Opcje wątkowania" icon="git-branch" href="/pl/plugins/sdk-entrypoints#registration-mode">
    Stałe tryby odpowiedzi, zależne od konta lub niestandardowe
  </Card>
  <Card title="Integracja z narzędziem message" icon="puzzle" href="/pl/plugins/architecture#channel-plugins-and-the-shared-message-tool">
    describeMessageTool i wykrywanie akcji
  </Card>
  <Card title="Rozpoznawanie celu" icon="crosshair" href="/pl/plugins/architecture#channel-target-resolution">
    inferTargetChatType, looksLikeId, resolveTarget
  </Card>
  <Card title="Helpery runtime" icon="settings" href="/pl/plugins/sdk-runtime">
    TTS, STT, multimedia, subagent przez api.runtime
  </Card>
</CardGroup>

<Note>
Niektóre dołączone powierzchnie helperów nadal istnieją dla utrzymania dołączonych pluginów i
zgodności. Nie są zalecanym wzorcem dla nowych pluginów kanałów;
preferuj ogólne subścieżki channel/setup/reply/runtime ze wspólnej
powierzchni SDK, chyba że bezpośrednio utrzymujesz tę rodzinę dołączonych pluginów.
</Note>

## Następne kroki

- [Pluginy dostawców](/pl/plugins/sdk-provider-plugins) — jeśli Twój plugin również udostępnia modele
- [Przegląd SDK](/pl/plugins/sdk-overview) — pełne odniesienie do importów subścieżek
- [Testowanie SDK](/pl/plugins/sdk-testing) — narzędzia testowe i testy kontraktowe
- [Manifest pluginu](/pl/plugins/manifest) — pełny schemat manifestu
