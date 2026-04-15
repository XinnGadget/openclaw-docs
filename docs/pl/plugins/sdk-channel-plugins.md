---
read_when:
    - Tworzysz nowy Plugin kanału komunikatora
    - Chcesz połączyć OpenClaw z platformą komunikacyjną
    - Musisz zrozumieć powierzchnię adaptera ChannelPlugin
sidebarTitle: Channel Plugins
summary: Przewodnik krok po kroku dotyczący tworzenia Pluginu kanału komunikatora dla OpenClaw
title: Tworzenie Pluginów kanałów
x-i18n:
    generated_at: "2026-04-15T19:41:36Z"
    model: gpt-5.4
    provider: openai
    source_hash: 80e47e61d1e47738361692522b79aff276544446c58a7b41afe5296635dfad4b
    source_path: plugins/sdk-channel-plugins.md
    workflow: 15
---

# Tworzenie Pluginów kanałów

Ten przewodnik przeprowadzi Cię przez tworzenie Pluginu kanału, który łączy OpenClaw z platformą komunikacyjną. Na końcu będziesz mieć działający kanał z zabezpieczeniami DM, parowaniem, wątkowaniem odpowiedzi i wiadomościami wychodzącymi.

<Info>
  Jeśli nie tworzyłeś wcześniej żadnego Pluginu OpenClaw, najpierw przeczytaj
  [Pierwsze kroki](/pl/plugins/building-plugins), aby poznać podstawową strukturę
  pakietu i konfigurację manifestu.
</Info>

## Jak działają Pluginy kanałów

Pluginy kanałów nie potrzebują własnych narzędzi do wysyłania/edycji/reakcji. OpenClaw utrzymuje jedno współdzielone narzędzie `message` w rdzeniu. Twój Plugin odpowiada za:

- **Konfigurację** — rozpoznawanie konta i kreator konfiguracji
- **Bezpieczeństwo** — zasady DM i listy dozwolonych
- **Parowanie** — przepływ zatwierdzania DM
- **Gramatykę sesji** — sposób, w jaki identyfikatory konwersacji specyficzne dla dostawcy są mapowane na czaty bazowe, identyfikatory wątków i zapasowe elementy nadrzędne
- **Ruch wychodzący** — wysyłanie tekstu, multimediów i ankiet na platformę
- **Wątkowanie** — sposób wątkowania odpowiedzi

Rdzeń odpowiada za współdzielone narzędzie wiadomości, połączenie promptów, zewnętrzny kształt klucza sesji, ogólne księgowanie `:thread:` i dyspozycję.

Jeśli Twój kanał dodaje parametry narzędzia wiadomości, które przenoszą źródła multimediów, udostępnij te nazwy parametrów przez `describeMessageTool(...).mediaSourceParams`. Rdzeń używa tej jawnej listy do normalizacji ścieżek sandboxa i zasad dostępu do multimediów wychodzących, więc Pluginy nie potrzebują wyjątków w współdzielonym rdzeniu dla parametrów awatarów, załączników lub obrazów okładek specyficznych dla dostawcy.
Preferuj zwracanie mapy kluczowanej akcją, takiej jak
`{ "set-profile": ["avatarUrl", "avatarPath"] }`, aby niezwiązane akcje nie dziedziczyły argumentów multimediów innej akcji. Płaska tablica nadal działa dla parametrów, które celowo są współdzielone przez każdą udostępnioną akcję.

Jeśli Twoja platforma przechowuje dodatkowy zakres wewnątrz identyfikatorów konwersacji, zachowaj to parsowanie w Pluginie za pomocą `messaging.resolveSessionConversation(...)`. To jest kanoniczny hook do mapowania `rawId` na bazowy identyfikator konwersacji, opcjonalny identyfikator wątku, jawny `baseConversationId` i wszelkie `parentConversationCandidates`.
Gdy zwracasz `parentConversationCandidates`, zachowaj ich kolejność od najbardziej zawężonego elementu nadrzędnego do najszerszej/bazowej konwersacji.

Bundlowane Pluginy, które potrzebują tego samego parsowania przed uruchomieniem rejestru kanałów, mogą także udostępniać plik najwyższego poziomu `session-key-api.ts` z pasującym eksportem `resolveSessionConversation(...)`. Rdzeń używa tej bezpiecznej dla bootstrapu powierzchni tylko wtedy, gdy rejestr Pluginów środowiska uruchomieniowego nie jest jeszcze dostępny.

`messaging.resolveParentConversationCandidates(...)` pozostaje dostępne jako starszy, zgodnościowy mechanizm zapasowy, gdy Plugin potrzebuje jedynie zapasowych elementów nadrzędnych ponad ogólnym/nieprzetworzonym identyfikatorem. Jeśli istnieją oba hooki, rdzeń najpierw używa
`resolveSessionConversation(...).parentConversationCandidates`, a do
`resolveParentConversationCandidates(...)` wraca tylko wtedy, gdy kanoniczny hook ich nie zwraca.

## Zatwierdzenia i możliwości kanału

Większość Pluginów kanałów nie potrzebuje kodu specyficznego dla zatwierdzeń.

- Rdzeń odpowiada za `/approve` w tym samym czacie, współdzielone payloady przycisków zatwierdzeń i ogólne dostarczanie zapasowe.
- Preferuj pojedynczy obiekt `approvalCapability` na Pluginie kanału, gdy kanał potrzebuje zachowania specyficznego dla zatwierdzeń.
- `ChannelPlugin.approvals` zostało usunięte. Umieść fakty dotyczące dostarczania/natywności/renderowania/uwierzytelniania zatwierdzeń w `approvalCapability`.
- `plugin.auth` służy tylko do logowania/wylogowania; rdzeń nie odczytuje już hooków uwierzytelniania zatwierdzeń z tego obiektu.
- `approvalCapability.authorizeActorAction` i `approvalCapability.getActionAvailabilityState` to kanoniczna powierzchnia uwierzytelniania zatwierdzeń.
- Użyj `approvalCapability.getActionAvailabilityState` do dostępności uwierzytelniania zatwierdzeń w tym samym czacie.
- Jeśli Twój kanał udostępnia natywne zatwierdzenia exec, użyj `approvalCapability.getExecInitiatingSurfaceState` dla stanu powierzchni inicjującej/klienta natywnego, gdy różni się on od uwierzytelniania zatwierdzeń w tym samym czacie. Rdzeń używa tego hooka specyficznego dla exec, aby odróżniać `enabled` od `disabled`, zdecydować, czy kanał inicjujący obsługuje natywne zatwierdzenia exec, i uwzględnić kanał we wskazówkach zapasowych dla klienta natywnego. `createApproverRestrictedNativeApprovalCapability(...)` wypełnia to dla typowego przypadku.
- Użyj `outbound.shouldSuppressLocalPayloadPrompt` lub `outbound.beforeDeliverPayload` dla zachowań cyklu życia payloadu specyficznych dla kanału, takich jak ukrywanie zduplikowanych lokalnych promptów zatwierdzeń lub wysyłanie wskaźników pisania przed dostarczeniem.
- Użyj `approvalCapability.delivery` tylko do natywnego trasowania zatwierdzeń lub wyłączania mechanizmu zapasowego.
- Użyj `approvalCapability.nativeRuntime` dla natywnych faktów zatwierdzeń należących do kanału. Zachowaj leniwe ładowanie dla gorących entrypointów kanału za pomocą `createLazyChannelApprovalNativeRuntimeAdapter(...)`, które może importować moduł runtime na żądanie, jednocześnie pozwalając rdzeniowi złożyć cykl życia zatwierdzenia.
- Użyj `approvalCapability.render` tylko wtedy, gdy kanał naprawdę potrzebuje niestandardowych payloadów zatwierdzeń zamiast współdzielonego renderera.
- Użyj `approvalCapability.describeExecApprovalSetup`, gdy kanał chce, aby odpowiedź na ścieżce wyłączonej wyjaśniała dokładne przełączniki konfiguracyjne potrzebne do włączenia natywnych zatwierdzeń exec. Hook otrzymuje `{ channel, channelLabel, accountId }`; kanały z nazwanymi kontami powinny renderować ścieżki o zakresie konta, takie jak `channels.<channel>.accounts.<id>.execApprovals.*`, zamiast domyślnych ścieżek najwyższego poziomu.
- Jeśli kanał może wywnioskować stabilne tożsamości typu właściciela DM z istniejącej konfiguracji, użyj `createResolvedApproverActionAuthAdapter` z `openclaw/plugin-sdk/approval-runtime`, aby ograniczyć `/approve` w tym samym czacie bez dodawania logiki specyficznej dla zatwierdzeń w rdzeniu.
- Jeśli kanał potrzebuje natywnego dostarczania zatwierdzeń, utrzymuj kod kanału skupiony na normalizacji celu oraz faktach dotyczących transportu/prezentacji. Użyj `createChannelExecApprovalProfile`, `createChannelNativeOriginTargetResolver`, `createChannelApproverDmTargetResolver` i `createApproverRestrictedNativeApprovalCapability` z `openclaw/plugin-sdk/approval-runtime`. Umieść fakty specyficzne dla kanału za `approvalCapability.nativeRuntime`, najlepiej przez `createChannelApprovalNativeRuntimeAdapter(...)` lub `createLazyChannelApprovalNativeRuntimeAdapter(...)`, aby rdzeń mógł złożyć handler i przejąć filtrowanie żądań, trasowanie, deduplikację, wygasanie, subskrypcję Gateway oraz powiadomienia o przekierowaniu gdzie indziej. `nativeRuntime` jest podzielone na kilka mniejszych powierzchni:
- `availability` — czy konto jest skonfigurowane i czy żądanie powinno zostać obsłużone
- `presentation` — mapowanie współdzielonego modelu widoku zatwierdzenia na oczekujące/rozwiązane/wygasłe natywne payloady lub działania końcowe
- `transport` — przygotowywanie celów oraz wysyłanie/aktualizowanie/usuwanie natywnych wiadomości zatwierdzeń
- `interactions` — opcjonalne hooki bind/unbind/clear-action dla natywnych przycisków lub reakcji
- `observe` — opcjonalne hooki diagnostyki dostarczeń
- Jeśli kanał potrzebuje obiektów należących do runtime, takich jak klient, token, aplikacja Bolt lub odbiornik Webhooków, zarejestruj je przez `openclaw/plugin-sdk/channel-runtime-context`. Ogólny rejestr kontekstu runtime pozwala rdzeniowi uruchamiać handlery sterowane możliwościami na podstawie stanu uruchomienia kanału bez dodawania kodu opakowującego specyficznego dla zatwierdzeń.
- Sięgaj po niższopoziomowe `createChannelApprovalHandler` lub `createChannelNativeApprovalRuntime` tylko wtedy, gdy powierzchnia oparta na możliwościach nie jest jeszcze wystarczająco ekspresyjna.
- Kanały natywnych zatwierdzeń muszą trasować zarówno `accountId`, jak i `approvalKind` przez te helpery. `accountId` utrzymuje zasady zatwierdzeń wielu kont w odpowiednim zakresie konta bota, a `approvalKind` utrzymuje zachowanie zatwierdzeń exec vs Plugin dostępne dla kanału bez zakodowanych na sztywno rozgałęzień w rdzeniu.
- Rdzeń odpowiada teraz również za powiadomienia o przekierowaniu zatwierdzeń. Pluginy kanałów nie powinny wysyłać własnych wiadomości uzupełniających typu „zatwierdzenie trafiło do DM / innego kanału” z `createChannelNativeApprovalRuntime`; zamiast tego udostępnij dokładne trasowanie pochodzenia + DM osoby zatwierdzającej przez współdzielone helpery możliwości zatwierdzeń i pozwól rdzeniowi agregować rzeczywiste dostarczenia przed opublikowaniem powiadomienia z powrotem do czatu inicjującego.
- Zachowuj typ identyfikatora dostarczonego zatwierdzenia od początku do końca. Klienci natywni nie powinni zgadywać ani przepisywać trasowania zatwierdzeń exec vs Plugin na podstawie lokalnego stanu kanału.
- Różne typy zatwierdzeń mogą celowo udostępniać różne powierzchnie natywne.
  Obecne przykłady bundlowane:
  - Slack zachowuje natywne trasowanie zatwierdzeń dostępne zarówno dla identyfikatorów exec, jak i Plugin.
  - Matrix zachowuje to samo natywne trasowanie DM/kanału i UX reakcji dla zatwierdzeń exec i Plugin, jednocześnie nadal pozwalając, by uwierzytelnianie różniło się w zależności od typu zatwierdzenia.
- `createApproverRestrictedNativeApprovalAdapter` nadal istnieje jako opakowanie zgodnościowe, ale nowy kod powinien preferować konstruktor możliwości i udostępniać `approvalCapability` w Pluginie.

Dla gorących entrypointów kanału preferuj węższe podścieżki runtime, gdy potrzebujesz tylko jednej części tej rodziny:

- `openclaw/plugin-sdk/approval-auth-runtime`
- `openclaw/plugin-sdk/approval-client-runtime`
- `openclaw/plugin-sdk/approval-delivery-runtime`
- `openclaw/plugin-sdk/approval-gateway-runtime`
- `openclaw/plugin-sdk/approval-handler-adapter-runtime`
- `openclaw/plugin-sdk/approval-handler-runtime`
- `openclaw/plugin-sdk/approval-native-runtime`
- `openclaw/plugin-sdk/approval-reply-runtime`
- `openclaw/plugin-sdk/channel-runtime-context`

Podobnie preferuj `openclaw/plugin-sdk/setup-runtime`,
`openclaw/plugin-sdk/setup-adapter-runtime`,
`openclaw/plugin-sdk/reply-runtime`,
`openclaw/plugin-sdk/reply-dispatch-runtime`,
`openclaw/plugin-sdk/reply-reference` i
`openclaw/plugin-sdk/reply-chunking`, gdy nie potrzebujesz szerszej, zbiorczej
powierzchni.

Konkretnie dla konfiguracji:

- `openclaw/plugin-sdk/setup-runtime` obejmuje bezpieczne dla runtime helpery konfiguracji:
  adaptery patchowania konfiguracji bezpieczne importowo (`createPatchedAccountSetupAdapter`,
  `createEnvPatchedAccountSetupAdapter`,
  `createSetupInputPresenceValidator`), wyjście notatek wyszukiwania,
  `promptResolvedAllowFrom`, `splitSetupEntries` i delegowane
  konstruktory proxy konfiguracji
- `openclaw/plugin-sdk/setup-adapter-runtime` to wąska powierzchnia adaptera świadoma env
  dla `createEnvPatchedAccountSetupAdapter`
- `openclaw/plugin-sdk/channel-setup` obejmuje konstruktory konfiguracji opcjonalnej instalacji
  oraz kilka prymitywów bezpiecznych dla konfiguracji:
  `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`,

Jeśli Twój kanał obsługuje konfigurację lub uwierzytelnianie sterowane przez env i ogólne przepływy uruchamiania/konfiguracji powinny znać te nazwy env jeszcze przed załadowaniem runtime, zadeklaruj je w manifeście Pluginu za pomocą `channelEnvVars`. Zachowaj `envVars` runtime kanału lub lokalne stałe tylko dla kopii przeznaczonej dla operatora.
`createOptionalChannelSetupWizard`, `DEFAULT_ACCOUNT_ID`,
`createTopLevelChannelDmPolicy`, `setSetupChannelEnabled` i
`splitSetupEntries`

- używaj szerszej powierzchni `openclaw/plugin-sdk/setup` tylko wtedy, gdy potrzebujesz również
  cięższych współdzielonych helperów konfiguracji/ustawień, takich jak
  `moveSingleAccountChannelSectionToDefaultAccount(...)`

Jeśli Twój kanał chce jedynie komunikować na powierzchniach konfiguracji „najpierw zainstaluj ten Plugin”, preferuj `createOptionalChannelSetupSurface(...)`. Wygenerowany adapter/kreator domyślnie odmawia zapisu konfiguracji i finalizacji, a także ponownie wykorzystuje ten sam komunikat wymagający instalacji w walidacji, finalizacji i treści z linkiem do dokumentacji.

Dla innych gorących ścieżek kanału preferuj wąskie helpery zamiast szerszych starszych powierzchni:

- `openclaw/plugin-sdk/account-core`,
  `openclaw/plugin-sdk/account-id`,
  `openclaw/plugin-sdk/account-resolution` i
  `openclaw/plugin-sdk/account-helpers` dla konfiguracji wielu kont i
  zapasowego przejścia do konta domyślnego
- `openclaw/plugin-sdk/inbound-envelope` i
  `openclaw/plugin-sdk/inbound-reply-dispatch` dla tras/kopert przychodzących oraz
  połączenia zapisywania i dyspozycji
- `openclaw/plugin-sdk/messaging-targets` dla parsowania/dopasowywania celów
- `openclaw/plugin-sdk/outbound-media` i
  `openclaw/plugin-sdk/outbound-runtime` dla ładowania multimediów oraz delegatów
  tożsamości/wysyłki ruchu wychodzącego
- `openclaw/plugin-sdk/thread-bindings-runtime` dla cyklu życia powiązań wątków
  i rejestracji adapterów
- `openclaw/plugin-sdk/agent-media-payload` tylko wtedy, gdy nadal wymagany jest
  starszy układ pól payloadu agenta/multimediów
- `openclaw/plugin-sdk/telegram-command-config` dla normalizacji niestandardowych poleceń Telegram,
  walidacji duplikatów/konfliktów oraz kontraktu konfiguracji poleceń
  stabilnego względem mechanizmu zapasowego

Kanały tylko z uwierzytelnianiem zwykle mogą zakończyć na ścieżce domyślnej: rdzeń obsługuje zatwierdzenia, a Plugin jedynie udostępnia możliwości ruchu wychodzącego/uwierzytelniania. Kanały natywnych zatwierdzeń, takie jak Matrix, Slack, Telegram i niestandardowe transporty czatu, powinny używać współdzielonych helperów natywnych zamiast implementować własny cykl życia zatwierdzeń.

## Zasady wzmianek przychodzących

Obsługę wzmianek przychodzących utrzymuj podzieloną na dwie warstwy:

- gromadzenie danych należące do Pluginu
- współdzielone ocenianie zasad

Dla warstwy współdzielonej użyj `openclaw/plugin-sdk/channel-inbound`.

Dobrze pasuje do logiki lokalnej dla Pluginu:

- wykrywanie odpowiedzi do bota
- wykrywanie cytatu bota
- sprawdzanie udziału w wątku
- wykluczenia wiadomości usługowych/systemowych
- natywne dla platformy cache potrzebne do potwierdzenia udziału bota

Dobrze pasuje do współdzielonego helpera:

- `requireMention`
- jawny wynik wzmianki
- lista dozwolonych niejawnych wzmianek
- obejście poleceń
- ostateczna decyzja o pominięciu

Preferowany przepływ:

1. Oblicz lokalne fakty dotyczące wzmianki.
2. Przekaż te fakty do `resolveInboundMentionDecision({ facts, policy })`.
3. Użyj `decision.effectiveWasMentioned`, `decision.shouldBypassMention` i `decision.shouldSkip` w swojej bramce ruchu przychodzącego.

```typescript
import {
  implicitMentionKindWhen,
  matchesMentionWithExplicit,
  resolveInboundMentionDecision,
} from "openclaw/plugin-sdk/channel-inbound";

const mentionMatch = matchesMentionWithExplicit(text, {
  mentionRegexes,
  mentionPatterns,
});

const facts = {
  canDetectMention: true,
  wasMentioned: mentionMatch.matched,
  hasAnyMention: mentionMatch.hasExplicitMention,
  implicitMentionKinds: [
    ...implicitMentionKindWhen("reply_to_bot", isReplyToBot),
    ...implicitMentionKindWhen("quoted_bot", isQuoteOfBot),
  ],
};

const decision = resolveInboundMentionDecision({
  facts,
  policy: {
    isGroup,
    requireMention,
    allowedImplicitMentionKinds: requireExplicitMention ? [] : ["reply_to_bot", "quoted_bot"],
    allowTextCommands,
    hasControlCommand,
    commandAuthorized,
  },
});

if (decision.shouldSkip) return;
```

`api.runtime.channel.mentions` udostępnia te same współdzielone helpery wzmianek dla
bundlowanych Pluginów kanałów, które już zależą od wstrzykiwania runtime:

- `buildMentionRegexes`
- `matchesMentionPatterns`
- `matchesMentionWithExplicit`
- `implicitMentionKindWhen`
- `resolveInboundMentionDecision`

Starsze helpery `resolveMentionGating*` pozostają w
`openclaw/plugin-sdk/channel-inbound` jedynie jako eksporty zgodnościowe. Nowy kod
powinien używać `resolveInboundMentionDecision({ facts, policy })`.

## Przewodnik

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="Pakiet i manifest">
    Utwórz standardowe pliki Pluginu. Pole `channel` w `package.json` to
    właśnie to, co sprawia, że jest to Plugin kanału. Pełną powierzchnię metadanych pakietu
    znajdziesz w [Konfiguracja Pluginu i Config](/pl/plugins/sdk-setup#openclaw-channel):

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
          "blurb": "Połącz OpenClaw z Acme Chat."
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
      "description": "Plugin kanału Acme Chat",
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

  <Step title="Zbuduj obiekt Pluginu kanału">
    Interfejs `ChannelPlugin` ma wiele opcjonalnych powierzchni adapterów. Zacznij od
    minimum — `id` i `setup` — i dodawaj adaptery w razie potrzeby.

    Utwórz `src/channel.ts`:

    ```typescript src/channel.ts
    import {
      createChatChannelPlugin,
      createChannelPluginBase,
    } from "openclaw/plugin-sdk/channel-core";
    import type { OpenClawConfig } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatApi } from "./client.js"; // klient API Twojej platformy

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

      // Bezpieczeństwo DM: kto może wysyłać wiadomości do bota
      security: {
        dm: {
          channelKey: "acme-chat",
          resolvePolicy: (account) => account.dmPolicy,
          resolveAllowFrom: (account) => account.allowFrom,
          defaultPolicy: "allowlist",
        },
      },

      // Parowanie: przepływ zatwierdzania dla nowych kontaktów DM
      pairing: {
        text: {
          idLabel: "Nazwa użytkownika Acme Chat",
          message: "Wyślij ten kod, aby zweryfikować swoją tożsamość:",
          notify: async ({ target, code }) => {
            await acmeChatApi.sendDm(target, `Pairing code: ${code}`);
          },
        },
      },

      // Wątkowanie: sposób dostarczania odpowiedzi
      threading: { topLevelReplyToMode: "reply" },

      // Ruch wychodzący: wysyłanie wiadomości na platformę
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

    <Accordion title="Co robi za Ciebie createChatChannelPlugin">
      Zamiast ręcznie implementować niskopoziomowe interfejsy adapterów,
      przekazujesz deklaratywne opcje, a konstruktor składa je razem:

      | Opcja | Co podłącza |
      | --- | --- |
      | `security.dm` | Resolver bezpieczeństwa DM o zakresie z pól config |
      | `pairing.text` | Przepływ parowania DM oparty na tekście z wymianą kodu |
      | `threading` | Resolver trybu odpowiedzi (stały, o zakresie konta lub niestandardowy) |
      | `outbound.attachedResults` | Funkcje wysyłania, które zwracają metadane wyniku (identyfikatory wiadomości) |

      Możesz też przekazać surowe obiekty adapterów zamiast deklaratywnych opcji,
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
      description: "Plugin kanału Acme Chat",
      plugin: acmeChatPlugin,
      registerCliMetadata(api) {
        api.registerCli(
          ({ program }) => {
            program
              .command("acme-chat")
              .description("Zarządzanie Acme Chat");
          },
          {
            descriptors: [
              {
                name: "acme-chat",
                description: "Zarządzanie Acme Chat",
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

    Umieść deskryptory CLI należące do kanału w `registerCliMetadata(...)`, aby OpenClaw
    mógł pokazywać je w głównej pomocy bez aktywowania pełnego runtime kanału,
    podczas gdy zwykłe pełne ładowania nadal pobiorą te same deskryptory do rzeczywistej
    rejestracji poleceń. `registerFull(...)` zachowaj dla pracy wyłącznie w runtime.
    Jeśli `registerFull(...)` rejestruje metody RPC Gateway, użyj
    prefiksu specyficznego dla Pluginu. Przestrzenie nazw administracyjnych rdzenia (`config.*`,
    `exec.approvals.*`, `wizard.*`, `update.*`) pozostają zarezerwowane i zawsze
    są rozwiązywane do `operator.admin`.
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

    Bundlowane kanały workspace, które rozdzielają eksporty bezpieczne dla konfiguracji do modułów
    pomocniczych, mogą używać `defineBundledChannelSetupEntry(...)` z
    `openclaw/plugin-sdk/channel-entry-contract`, gdy potrzebują także
    jawnego settera runtime dla czasu konfiguracji.

  </Step>

  <Step title="Obsłuż wiadomości przychodzące">
    Twój Plugin musi odbierać wiadomości z platformy i przekazywać je do
    OpenClaw. Typowy wzorzec to Webhook, który weryfikuje żądanie i
    przekazuje je przez handler przychodzący Twojego kanału:

    ```typescript
    registerFull(api) {
      api.registerHttpRoute({
        path: "/acme-chat/webhook",
        auth: "plugin", // uwierzytelnianie zarządzane przez Plugin (samodzielnie zweryfikuj podpisy)
        handler: async (req, res) => {
          const event = parseWebhookPayload(req);

          // Twój handler przychodzący przekazuje wiadomość do OpenClaw.
          // Dokładne podłączenie zależy od SDK Twojej platformy —
          // zobacz rzeczywisty przykład w bundlowanym pakiecie Pluginu Microsoft Teams lub Google Chat.
          await handleAcmeChatInbound(api, event);

          res.statusCode = 200;
          res.end("ok");
          return true;
        },
      });
    }
    ```

    <Note>
      Obsługa wiadomości przychodzących jest specyficzna dla kanału. Każdy Plugin kanału
      posiada własny potok przychodzący. Zobacz bundlowane Pluginy kanałów
      (na przykład pakiet Pluginu Microsoft Teams lub Google Chat), aby poznać rzeczywiste wzorce.
    </Note>

  </Step>

<a id="step-6-test"></a>
<Step title="Test">
Pisz testy współlokowane w `src/channel.test.ts`:

    ```typescript src/channel.test.ts
    import { describe, it, expect } from "vitest";
    import { acmeChatPlugin } from "./channel.js";

    describe("plugin acme-chat", () => {
      it("rozpoznaje konto na podstawie config", () => {
        const cfg = {
          channels: {
            "acme-chat": { token: "test-token", allowFrom: ["user1"] },
          },
        } as any;
        const account = acmeChatPlugin.setup!.resolveAccount(cfg, undefined);
        expect(account.token).toBe("test-token");
      });

      it("sprawdza konto bez materializowania sekretów", () => {
        const cfg = {
          channels: { "acme-chat": { token: "test-token" } },
        } as any;
        const result = acmeChatPlugin.setup!.inspectAccount!(cfg, undefined);
        expect(result.configured).toBe(true);
        expect(result.tokenStatus).toBe("available");
      });

      it("zgłasza brakujący config", () => {
        const cfg = { channels: {} } as any;
        const result = acmeChatPlugin.setup!.inspectAccount!(cfg, undefined);
        expect(result.configured).toBe(false);
      });
    });
    ```

    ```bash
    pnpm test -- <bundled-plugin-root>/acme-chat/
    ```

    Informacje o współdzielonych helperach testowych znajdziesz w sekcji [Testowanie](/pl/plugins/sdk-testing).

  </Step>
</Steps>

## Struktura plików

```
<bundled-plugin-root>/acme-chat/
├── package.json              # metadane openclaw.channel
├── openclaw.plugin.json      # Manifest z schematem config
├── index.ts                  # defineChannelPluginEntry
├── setup-entry.ts            # defineSetupPluginEntry
├── api.ts                    # Eksporty publiczne (opcjonalnie)
├── runtime-api.ts            # Eksporty wewnętrznego runtime (opcjonalnie)
└── src/
    ├── channel.ts            # ChannelPlugin przez createChatChannelPlugin
    ├── channel.test.ts       # Testy
    ├── client.ts             # Klient API platformy
    └── runtime.ts            # Magazyn runtime (jeśli potrzebny)
```

## Tematy zaawansowane

<CardGroup cols={2}>
  <Card title="Opcje wątkowania" icon="git-branch" href="/pl/plugins/sdk-entrypoints#registration-mode">
    Stałe, o zakresie konta lub niestandardowe tryby odpowiedzi
  </Card>
  <Card title="Integracja z narzędziem wiadomości" icon="puzzle" href="/pl/plugins/architecture#channel-plugins-and-the-shared-message-tool">
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
Niektóre bundlowane powierzchnie helperów nadal istnieją na potrzeby utrzymania bundlowanych Pluginów i zgodności. Nie są one zalecanym wzorcem dla nowych Pluginów kanałów; preferuj ogólne podścieżki channel/setup/reply/runtime ze wspólnej powierzchni SDK, chyba że bezpośrednio utrzymujesz tę rodzinę bundlowanych Pluginów.
</Note>

## Następne kroki

- [Pluginy dostawców](/pl/plugins/sdk-provider-plugins) — jeśli Twój Plugin udostępnia także modele
- [Przegląd SDK](/pl/plugins/sdk-overview) — pełne odniesienie do importów podścieżek
- [Testowanie SDK](/pl/plugins/sdk-testing) — narzędzia testowe i testy kontraktowe
- [Manifest Pluginu](/pl/plugins/manifest) — pełny schemat manifestu
