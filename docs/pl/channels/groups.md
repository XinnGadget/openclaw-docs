---
read_when:
    - Zmiana zachowania czatu grupowego lub bramkowania wzmianek
summary: Zachowanie czatów grupowych na różnych powierzchniach (Discord/iMessage/Matrix/Microsoft Teams/Signal/Slack/Telegram/WhatsApp/Zalo)
title: Grupy
x-i18n:
    generated_at: "2026-04-06T03:06:41Z"
    model: gpt-5.4
    provider: openai
    source_hash: 8620de6f7f0b866bf43a307fdbec3399790f09f22a87703704b0522caba80b18
    source_path: channels/groups.md
    workflow: 15
---

# Grupy

OpenClaw traktuje czaty grupowe spójnie na różnych powierzchniach: Discord, iMessage, Matrix, Microsoft Teams, Signal, Slack, Telegram, WhatsApp, Zalo.

## Wprowadzenie dla początkujących (2 minuty)

OpenClaw „działa” na Twoich własnych kontach komunikatorów. Nie ma oddzielnego użytkownika bota WhatsApp.
Jeśli **Ty** jesteś w grupie, OpenClaw może widzieć tę grupę i tam odpowiadać.

Domyślne zachowanie:

- Grupy są ograniczone (`groupPolicy: "allowlist"`).
- Odpowiedzi wymagają wzmianki, chyba że jawnie wyłączysz bramkowanie wzmianek.

Innymi słowy: nadawcy z listy dozwolonych mogą uruchomić OpenClaw, wzmiankując go.

> TL;DR
>
> - Dostęp do **DM** jest kontrolowany przez `*.allowFrom`.
> - Dostęp do **grup** jest kontrolowany przez `*.groupPolicy` + listy dozwolonych (`*.groups`, `*.groupAllowFrom`).
> - **Wyzwalanie odpowiedzi** jest kontrolowane przez bramkowanie wzmianek (`requireMention`, `/activation`).

Szybki przepływ (co dzieje się z wiadomością grupową):

```
groupPolicy? disabled -> odrzuć
groupPolicy? allowlist -> grupa dozwolona? nie -> odrzuć
requireMention? tak -> wspomniano? nie -> zapisz tylko jako kontekst
w przeciwnym razie -> odpowiedz
```

## Widoczność kontekstu i listy dozwolonych

W bezpieczeństwie grup uczestniczą dwa różne mechanizmy:

- **Autoryzacja wyzwolenia**: kto może wyzwolić agenta (`groupPolicy`, `groups`, `groupAllowFrom`, listy dozwolonych specyficzne dla kanału).
- **Widoczność kontekstu**: jaki kontekst uzupełniający jest wstrzykiwany do modelu (tekst odpowiedzi, cytaty, historia wątku, metadane przekazania).

Domyślnie OpenClaw priorytetowo traktuje normalne zachowanie czatu i zachowuje kontekst głównie w formie, w jakiej został odebrany. Oznacza to, że listy dozwolonych przede wszystkim decydują o tym, kto może wyzwalać działania, a nie stanowią uniwersalnej granicy redakcji dla każdego cytatu lub fragmentu historii.

Obecne zachowanie zależy od kanału:

- Niektóre kanały już stosują filtrowanie oparte na nadawcy dla kontekstu uzupełniającego w określonych ścieżkach (na przykład inicjalizacja wątków Slack, wyszukiwanie odpowiedzi/wątków Matrix).
- Inne kanały nadal przekazują kontekst cytatu/odpowiedzi/przekazania w otrzymanej postaci.

Kierunek utwardzania (planowany):

- `contextVisibility: "all"` (domyślnie) zachowuje obecne zachowanie zgodne z odebraną postacią.
- `contextVisibility: "allowlist"` filtruje kontekst uzupełniający do nadawców z listy dozwolonych.
- `contextVisibility: "allowlist_quote"` to `allowlist` plus jeden jawny wyjątek dla cytatu/odpowiedzi.

Dopóki ten model utwardzania nie zostanie wdrożony spójnie we wszystkich kanałach, należy oczekiwać różnic zależnie od powierzchni.

![Przepływ wiadomości grupowej](/images/groups-flow.svg)

Jeśli chcesz...

| Cel                                          | Co ustawić                                                 |
| -------------------------------------------- | ---------------------------------------------------------- |
| Zezwolić na wszystkie grupy, ale odpowiadać tylko na @wzmianki | `groups: { "*": { requireMention: true } }`                |
| Wyłączyć wszystkie odpowiedzi grupowe        | `groupPolicy: "disabled"`                                  |
| Tylko określone grupy                        | `groups: { "<group-id>": { ... } }` (bez klucza `"*"`)     |
| Tylko Ty możesz wyzwalać w grupach           | `groupPolicy: "allowlist"`, `groupAllowFrom: ["+1555..."]` |

## Klucze sesji

- Sesje grupowe używają kluczy sesji `agent:<agentId>:<channel>:group:<id>` (pokoje/kanały używają `agent:<agentId>:<channel>:channel:<id>`).
- Tematy forum Telegram dodają `:topic:<threadId>` do identyfikatora grupy, dzięki czemu każdy temat ma własną sesję.
- Czat bezpośredni używa sesji głównej (lub sesji per nadawca, jeśli skonfigurowano).
- Heartbeaty są pomijane dla sesji grupowych.

<a id="pattern-personal-dms-public-groups-single-agent"></a>

## Wzorzec: prywatne DM + publiczne grupy (jeden agent)

Tak — to działa dobrze, jeśli Twój „prywatny” ruch to **DM**, a Twój „publiczny” ruch to **grupy**.

Dlaczego: w trybie jednego agenta DM zwykle trafiają do **głównego** klucza sesji (`agent:main:main`), a grupy zawsze używają kluczy sesji **niegłównych** (`agent:main:<channel>:group:<id>`). Jeśli włączysz sandboxing z `mode: "non-main"`, te sesje grupowe będą działać w Dockerze, podczas gdy Twoja główna sesja DM pozostanie na hoście.

Daje to jeden „mózg” agenta (wspólny workspace + pamięć), ale dwie postawy wykonania:

- **DM**: pełne narzędzia (host)
- **Grupy**: sandbox + ograniczone narzędzia (Docker)

> Jeśli potrzebujesz naprawdę oddzielnych workspace'ów/person („prywatne” i „publiczne” nigdy nie mogą się mieszać), użyj drugiego agenta + powiązań. Zobacz [Multi-Agent Routing](/pl/concepts/multi-agent).

Przykład (DM na hoście, grupy w sandboxie + tylko narzędzia do wiadomości):

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main", // grupy/kanały są non-main -> sandboxowane
        scope: "session", // najsilniejsza izolacja (jeden kontener na grupę/kanał)
        workspaceAccess: "none",
      },
    },
  },
  tools: {
    sandbox: {
      tools: {
        // Jeśli allow nie jest puste, wszystko inne jest blokowane (deny nadal ma pierwszeństwo).
        allow: ["group:messaging", "group:sessions"],
        deny: ["group:runtime", "group:fs", "group:ui", "nodes", "cron", "gateway"],
      },
    },
  },
}
```

Chcesz, aby „grupy mogły widzieć tylko folder X” zamiast „braku dostępu do hosta”? Zachowaj `workspaceAccess: "none"` i zamontuj w sandboxie tylko ścieżki z listy dozwolonych:

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none",
        docker: {
          binds: [
            // hostPath:containerPath:mode
            "/home/user/FriendsShared:/data:ro",
          ],
        },
      },
    },
  },
}
```

Powiązane:

- Klucze konfiguracji i wartości domyślne: [Konfiguracja Gateway](/pl/gateway/configuration-reference#agentsdefaultssandbox)
- Debugowanie, dlaczego narzędzie jest blokowane: [Sandbox vs Tool Policy vs Elevated](/pl/gateway/sandbox-vs-tool-policy-vs-elevated)
- Szczegóły bind mountów: [Sandboxing](/pl/gateway/sandboxing#custom-bind-mounts)

## Etykiety wyświetlania

- Etykiety UI używają `displayName`, gdy jest dostępne, w formacie `<channel>:<token>`.
- `#room` jest zarezerwowane dla pokoi/kanałów; czaty grupowe używają `g-<slug>` (małe litery, spacje -> `-`, zachowaj `#@+._-`).

## Polityka grup

Kontroluj sposób obsługi wiadomości grupowych/pokojów dla każdego kanału:

```json5
{
  channels: {
    whatsapp: {
      groupPolicy: "disabled", // "open" | "disabled" | "allowlist"
      groupAllowFrom: ["+15551234567"],
    },
    telegram: {
      groupPolicy: "disabled",
      groupAllowFrom: ["123456789"], // numeryczny identyfikator użytkownika Telegram (kreator może rozpoznać @username)
    },
    signal: {
      groupPolicy: "disabled",
      groupAllowFrom: ["+15551234567"],
    },
    imessage: {
      groupPolicy: "disabled",
      groupAllowFrom: ["chat_id:123"],
    },
    msteams: {
      groupPolicy: "disabled",
      groupAllowFrom: ["user@org.com"],
    },
    discord: {
      groupPolicy: "allowlist",
      guilds: {
        GUILD_ID: { channels: { help: { allow: true } } },
      },
    },
    slack: {
      groupPolicy: "allowlist",
      channels: { "#general": { allow: true } },
    },
    matrix: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["@owner:example.org"],
      groups: {
        "!roomId:example.org": { allow: true },
        "#alias:example.org": { allow: true },
      },
    },
  },
}
```

| Polityka      | Zachowanie                                                   |
| ------------- | ------------------------------------------------------------ |
| `"open"`      | Grupy omijają listy dozwolonych; bramkowanie wzmianek nadal obowiązuje. |
| `"disabled"`  | Całkowicie blokuj wszystkie wiadomości grupowe.              |
| `"allowlist"` | Zezwalaj tylko na grupy/pokoje pasujące do skonfigurowanej listy dozwolonych. |

Uwagi:

- `groupPolicy` jest oddzielne od bramkowania wzmianek (które wymaga @wzmianek).
- WhatsApp/Telegram/Signal/iMessage/Microsoft Teams/Zalo: użyj `groupAllowFrom` (fallback: jawne `allowFrom`).
- Zatwierdzenia parowania DM (wpisy w magazynie `*-allowFrom`) dotyczą wyłącznie dostępu do DM; autoryzacja nadawców grupowych pozostaje jawnie kontrolowana przez listy dozwolonych grup.
- Discord: lista dozwolonych używa `channels.discord.guilds.<id>.channels`.
- Slack: lista dozwolonych używa `channels.slack.channels`.
- Matrix: lista dozwolonych używa `channels.matrix.groups`. Preferuj identyfikatory pokoi lub aliasy; wyszukiwanie nazw dołączonych pokoi jest best-effort, a nierozpoznane nazwy są ignorowane w runtime. Użyj `channels.matrix.groupAllowFrom`, aby ograniczyć nadawców; obsługiwane są także listy dozwolonych `users` per pokój.
- DM grupowe są kontrolowane osobno (`channels.discord.dm.*`, `channels.slack.dm.*`).
- Lista dozwolonych Telegram może dopasowywać identyfikatory użytkowników (`"123456789"`, `"telegram:123456789"`, `"tg:123456789"`) albo nazwy użytkowników (`"@alice"` lub `"alice"`); prefiksy są nieczułe na wielkość liter.
- Domyślnie ustawione jest `groupPolicy: "allowlist"`; jeśli Twoja lista dozwolonych grup jest pusta, wiadomości grupowe są blokowane.
- Bezpieczeństwo runtime: gdy blok providera całkowicie nie istnieje (`channels.<provider>` nieobecne), polityka grup przełącza się na tryb fail-closed (zwykle `allowlist`) zamiast dziedziczyć `channels.defaults.groupPolicy`.

Szybki model mentalny (kolejność oceny dla wiadomości grupowych):

1. `groupPolicy` (open/disabled/allowlist)
2. listy dozwolonych grup (`*.groups`, `*.groupAllowFrom`, lista dozwolonych specyficzna dla kanału)
3. bramkowanie wzmianek (`requireMention`, `/activation`)

## Bramkowanie wzmianek (domyślnie)

Wiadomości grupowe wymagają wzmianki, chyba że zostanie to nadpisane dla danej grupy. Wartości domyślne są definiowane per podsystem w `*.groups."*"`.

Odpowiedź na wiadomość bota liczy się jako niejawna wzmianka (gdy kanał obsługuje metadane odpowiedzi). Dotyczy to Telegram, WhatsApp, Slack, Discord i Microsoft Teams.

```json5
{
  channels: {
    whatsapp: {
      groups: {
        "*": { requireMention: true },
        "123@g.us": { requireMention: false },
      },
    },
    telegram: {
      groups: {
        "*": { requireMention: true },
        "123456789": { requireMention: false },
      },
    },
    imessage: {
      groups: {
        "*": { requireMention: true },
        "123": { requireMention: false },
      },
    },
  },
  agents: {
    list: [
      {
        id: "main",
        groupChat: {
          mentionPatterns: ["@openclaw", "openclaw", "\\+15555550123"],
          historyLimit: 50,
        },
      },
    ],
  },
}
```

Uwagi:

- `mentionPatterns` to bezpieczne wzorce regex nieczułe na wielkość liter; nieprawidłowe wzorce i niebezpieczne formy zagnieżdżonych powtórzeń są ignorowane.
- Powierzchnie dostarczające jawne wzmianki nadal przechodzą; wzorce są mechanizmem zapasowym.
- Nadpisanie per agent: `agents.list[].groupChat.mentionPatterns` (przydatne, gdy wiele agentów współdzieli grupę).
- Bramkowanie wzmianek jest egzekwowane tylko wtedy, gdy wykrywanie wzmianek jest możliwe (natywne wzmianki lub skonfigurowane `mentionPatterns`).
- Wartości domyślne Discord znajdują się w `channels.discord.guilds."*"` (z możliwością nadpisania per serwer/kanał).
- Kontekst historii grupy jest opakowany jednolicie we wszystkich kanałach i jest **tylko oczekujący** (`pending-only`) (wiadomości pominięte z powodu bramkowania wzmianek); użyj `messages.groupChat.historyLimit` dla globalnej wartości domyślnej oraz `channels.<channel>.historyLimit` (lub `channels.<channel>.accounts.*.historyLimit`) dla nadpisań. Ustaw `0`, aby wyłączyć.

## Ograniczenia narzędzi dla grup/kanałów (opcjonalnie)

Niektóre konfiguracje kanałów obsługują ograniczanie, które narzędzia są dostępne **wewnątrz konkretnej grupy/pokoju/kanału**.

- `tools`: zezwalaj/zabraniaj narzędzi dla całej grupy.
- `toolsBySender`: nadpisania per nadawca w obrębie grupy.
  Używaj jawnych prefiksów kluczy:
  `id:<senderId>`, `e164:<phone>`, `username:<handle>`, `name:<displayName>` oraz wildcard `"*"`.
  Starsze klucze bez prefiksu są nadal akceptowane i dopasowywane wyłącznie jako `id:`.

Kolejność rozstrzygania (najbardziej szczegółowe wygrywa):

1. dopasowanie `toolsBySender` dla grupy/kanału
2. `tools` dla grupy/kanału
3. domyślne dopasowanie `toolsBySender` (`"*"`)
4. domyślne `tools` (`"*"`)

Przykład (Telegram):

```json5
{
  channels: {
    telegram: {
      groups: {
        "*": { tools: { deny: ["exec"] } },
        "-1001234567890": {
          tools: { deny: ["exec", "read", "write"] },
          toolsBySender: {
            "id:123456789": { alsoAllow: ["exec"] },
          },
        },
      },
    },
  },
}
```

Uwagi:

- Ograniczenia narzędzi dla grup/kanałów są stosowane dodatkowo do globalnej/powiązanej z agentem polityki narzędzi (deny nadal ma pierwszeństwo).
- Niektóre kanały używają innego zagnieżdżenia dla pokoi/kanałów (np. Discord `guilds.*.channels.*`, Slack `channels.*`, Microsoft Teams `teams.*.channels.*`).

## Listy dozwolonych grup

Gdy skonfigurowano `channels.whatsapp.groups`, `channels.telegram.groups` lub `channels.imessage.groups`, klucze działają jako lista dozwolonych grup. Użyj `"*"`, aby zezwolić na wszystkie grupy, jednocześnie ustawiając domyślne zachowanie wzmianek.

Częsta pomyłka: zatwierdzenie parowania DM to nie to samo co autoryzacja grupy.
W kanałach obsługujących parowanie DM magazyn parowania odblokowuje tylko DM. Polecenia grupowe nadal wymagają jawnej autoryzacji nadawcy grupowego z list dozwolonych w konfiguracji, takich jak `groupAllowFrom` lub udokumentowany fallback konfiguracji dla danego kanału.

Typowe zamiary (kopiuj/wklej):

1. Wyłącz wszystkie odpowiedzi grupowe

```json5
{
  channels: { whatsapp: { groupPolicy: "disabled" } },
}
```

2. Zezwól tylko na określone grupy (WhatsApp)

```json5
{
  channels: {
    whatsapp: {
      groups: {
        "123@g.us": { requireMention: true },
        "456@g.us": { requireMention: false },
      },
    },
  },
}
```

3. Zezwól na wszystkie grupy, ale wymagaj wzmianki (jawnie)

```json5
{
  channels: {
    whatsapp: {
      groups: { "*": { requireMention: true } },
    },
  },
}
```

4. Tylko właściciel może wyzwalać w grupach (WhatsApp)

```json5
{
  channels: {
    whatsapp: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["+15551234567"],
      groups: { "*": { requireMention: true } },
    },
  },
}
```

## Aktywacja (tylko właściciel)

Właściciele grup mogą przełączać aktywację per grupa:

- `/activation mention`
- `/activation always`

Właściciel jest określany przez `channels.whatsapp.allowFrom` (lub własny E.164 bota, jeśli nie ustawiono). Wyślij polecenie jako samodzielną wiadomość. Inne powierzchnie obecnie ignorują `/activation`.

## Pola kontekstu

Przychodzące payloady grupowe ustawiają:

- `ChatType=group`
- `GroupSubject` (jeśli znane)
- `GroupMembers` (jeśli znane)
- `WasMentioned` (wynik bramkowania wzmianek)
- Tematy forum Telegram zawierają również `MessageThreadId` i `IsForum`.

Uwagi specyficzne dla kanału:

- BlueBubbles może opcjonalnie wzbogacać nienazwanych uczestników grup macOS z lokalnej bazy Contacts przed wypełnieniem `GroupMembers`. Ta funkcja jest domyślnie wyłączona i uruchamia się dopiero po przejściu standardowego bramkowania grup.

System prompt agenta zawiera wprowadzenie do grupy przy pierwszej turze nowej sesji grupowej. Przypomina modelowi, aby odpowiadał jak człowiek, unikał tabel Markdown, minimalizował puste linie i stosował normalne odstępy czatu, a także unikał wpisywania dosłownych sekwencji `\n`.

## Szczegóły iMessage

- Preferuj `chat_id:<id>` podczas routingu lub dodawania do listy dozwolonych.
- Wyświetl czaty: `imsg chats --limit 20`.
- Odpowiedzi grupowe zawsze wracają do tego samego `chat_id`.

## Szczegóły WhatsApp

Zobacz [Wiadomości grupowe](/pl/channels/group-messages), aby poznać zachowanie specyficzne tylko dla WhatsApp (wstrzykiwanie historii, szczegóły obsługi wzmianek).
