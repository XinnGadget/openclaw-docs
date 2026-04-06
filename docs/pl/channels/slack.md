---
read_when:
    - Konfigurowanie Slack lub debugowanie trybu socket/HTTP w Slack
summary: Konfiguracja Slack i zachowanie środowiska uruchomieniowego (Socket Mode + HTTP Events API)
title: Slack
x-i18n:
    generated_at: "2026-04-06T03:07:09Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7e4ff2ce7d92276d62f4f3d3693ddb56ca163d5fdc2f1082ff7ba3421fada69c
    source_path: channels/slack.md
    workflow: 15
---

# Slack

Status: gotowe do użycia produkcyjnego dla wiadomości prywatnych i kanałów przez integracje aplikacji Slack. Domyślnym trybem jest Socket Mode; tryb HTTP Events API również jest obsługiwany.

<CardGroup cols={3}>
  <Card title="Parowanie" icon="link" href="/pl/channels/pairing">
    Wiadomości prywatne Slack domyślnie używają trybu parowania.
  </Card>
  <Card title="Polecenia slash" icon="terminal" href="/pl/tools/slash-commands">
    Natywne zachowanie poleceń i katalog poleceń.
  </Card>
  <Card title="Rozwiązywanie problemów z kanałami" icon="wrench" href="/pl/channels/troubleshooting">
    Diagnostyka międzykanałowa i instrukcje naprawy.
  </Card>
</CardGroup>

## Szybka konfiguracja

<Tabs>
  <Tab title="Socket Mode (domyślnie)">
    <Steps>
      <Step title="Utwórz aplikację Slack i tokeny">
        W ustawieniach aplikacji Slack:

        - włącz **Socket Mode**
        - utwórz **App Token** (`xapp-...`) z uprawnieniem `connections:write`
        - zainstaluj aplikację i skopiuj **Bot Token** (`xoxb-...`)
      </Step>

      <Step title="Skonfiguruj OpenClaw">

```json5
{
  channels: {
    slack: {
      enabled: true,
      mode: "socket",
      appToken: "xapp-...",
      botToken: "xoxb-...",
    },
  },
}
```

        Zmienna środowiskowa jako awaryjne źródło wartości (tylko konto domyślne):

```bash
SLACK_APP_TOKEN=xapp-...
SLACK_BOT_TOKEN=xoxb-...
```

      </Step>

      <Step title="Subskrybuj zdarzenia aplikacji">
        Subskrybuj zdarzenia bota dla:

        - `app_mention`
        - `message.channels`, `message.groups`, `message.im`, `message.mpim`
        - `reaction_added`, `reaction_removed`
        - `member_joined_channel`, `member_left_channel`
        - `channel_rename`
        - `pin_added`, `pin_removed`

        Włącz także kartę **Messages Tab** w App Home dla wiadomości prywatnych.
      </Step>

      <Step title="Uruchom gateway">

```bash
openclaw gateway
```

      </Step>
    </Steps>

  </Tab>

  <Tab title="Tryb HTTP Events API">
    <Steps>
      <Step title="Skonfiguruj aplikację Slack dla HTTP">

        - ustaw tryb na HTTP (`channels.slack.mode="http"`)
        - skopiuj **Signing Secret** Slack
        - ustaw Request URL dla Event Subscriptions, Interactivity i polecenia Slash na tę samą ścieżkę webhooka (domyślnie `/slack/events`)

      </Step>

      <Step title="Skonfiguruj tryb HTTP w OpenClaw">

```json5
{
  channels: {
    slack: {
      enabled: true,
      mode: "http",
      botToken: "xoxb-...",
      signingSecret: "your-signing-secret",
      webhookPath: "/slack/events",
    },
  },
}
```

      </Step>

      <Step title="Używaj unikalnych ścieżek webhooka dla wielu kont">
        Tryb HTTP dla wielu kont jest obsługiwany.

        Nadaj każdemu kontu odrębny `webhookPath`, aby rejestracje nie kolidowały ze sobą.
      </Step>
    </Steps>

  </Tab>
</Tabs>

## Lista kontrolna manifestu i zakresów

<AccordionGroup>
  <Accordion title="Przykład manifestu aplikacji Slack" defaultOpen>

```json
{
  "display_information": {
    "name": "OpenClaw",
    "description": "Slack connector for OpenClaw"
  },
  "features": {
    "bot_user": {
      "display_name": "OpenClaw",
      "always_online": true
    },
    "app_home": {
      "messages_tab_enabled": true,
      "messages_tab_read_only_enabled": false
    },
    "slash_commands": [
      {
        "command": "/openclaw",
        "description": "Send a message to OpenClaw",
        "should_escape": false
      }
    ]
  },
  "oauth_config": {
    "scopes": {
      "bot": [
        "app_mentions:read",
        "assistant:write",
        "channels:history",
        "channels:read",
        "chat:write",
        "commands",
        "emoji:read",
        "files:read",
        "files:write",
        "groups:history",
        "groups:read",
        "im:history",
        "im:read",
        "im:write",
        "mpim:history",
        "mpim:read",
        "mpim:write",
        "pins:read",
        "pins:write",
        "reactions:read",
        "reactions:write",
        "users:read"
      ]
    }
  },
  "settings": {
    "socket_mode_enabled": true,
    "event_subscriptions": {
      "bot_events": [
        "app_mention",
        "channel_rename",
        "member_joined_channel",
        "member_left_channel",
        "message.channels",
        "message.groups",
        "message.im",
        "message.mpim",
        "pin_added",
        "pin_removed",
        "reaction_added",
        "reaction_removed"
      ]
    }
  }
}
```

  </Accordion>

  <Accordion title="Opcjonalne zakresy tokena użytkownika (operacje odczytu)">
    Jeśli skonfigurujesz `channels.slack.userToken`, typowe zakresy odczytu to:

    - `channels:history`, `groups:history`, `im:history`, `mpim:history`
    - `channels:read`, `groups:read`, `im:read`, `mpim:read`
    - `users:read`
    - `reactions:read`
    - `pins:read`
    - `emoji:read`
    - `search:read` (jeśli polegasz na odczytach wyszukiwania Slack)

  </Accordion>
</AccordionGroup>

## Model tokenów

- `botToken` + `appToken` są wymagane dla Socket Mode.
- Tryb HTTP wymaga `botToken` + `signingSecret`.
- `botToken`, `appToken`, `signingSecret` i `userToken` akceptują zwykłe
  ciągi znaków lub obiekty SecretRef.
- Tokeny w konfiguracji mają pierwszeństwo przed awaryjnym źródłem wartości ze środowiska.
- Awaryjne źródło wartości środowiskowych `SLACK_BOT_TOKEN` / `SLACK_APP_TOKEN` dotyczy tylko konta domyślnego.
- `userToken` (`xoxp-...`) jest dostępny tylko w konfiguracji (bez awaryjnego źródła wartości ze środowiska) i domyślnie działa tylko do odczytu (`userTokenReadOnly: true`).
- Opcjonalnie: dodaj `chat:write.customize`, jeśli chcesz, aby wiadomości wychodzące używały tożsamości aktywnego agenta (niestandardowe `username` i ikona). `icon_emoji` używa składni `:emoji_name:`.

Zachowanie migawki stanu:

- Inspekcja konta Slack śledzi pola `*Source` i `*Status`
  dla każdego poświadczenia (`botToken`, `appToken`, `signingSecret`, `userToken`).
- Stan to `available`, `configured_unavailable` lub `missing`.
- `configured_unavailable` oznacza, że konto jest skonfigurowane przez SecretRef
  lub inne niejawne źródło sekretu, ale bieżąca ścieżka polecenia/uruchomienia
  nie mogła rozwiązać rzeczywistej wartości.
- W trybie HTTP uwzględniane jest `signingSecretStatus`; w Socket Mode
  wymagana para to `botTokenStatus` + `appTokenStatus`.

<Tip>
W przypadku działań/odczytów katalogu token użytkownika może mieć pierwszeństwo, jeśli jest skonfigurowany. W przypadku zapisów nadal preferowany jest token bota; zapisy z użyciem tokena użytkownika są dozwolone tylko wtedy, gdy `userTokenReadOnly: false` i token bota jest niedostępny.
</Tip>

## Działania i bramki

Działania Slack są kontrolowane przez `channels.slack.actions.*`.

Dostępne grupy działań w bieżących narzędziach Slack:

| Group      | Default |
| ---------- | ------- |
| messages   | enabled |
| reactions  | enabled |
| pins       | enabled |
| memberInfo | enabled |
| emojiList  | enabled |

Bieżące działania wiadomości Slack obejmują `send`, `upload-file`, `download-file`, `read`, `edit`, `delete`, `pin`, `unpin`, `list-pins`, `member-info` i `emoji-list`.

## Kontrola dostępu i routing

<Tabs>
  <Tab title="Zasady wiadomości prywatnych">
    `channels.slack.dmPolicy` kontroluje dostęp do wiadomości prywatnych (starsza nazwa: `channels.slack.dm.policy`):

    - `pairing` (domyślnie)
    - `allowlist`
    - `open` (wymaga, aby `channels.slack.allowFrom` zawierało `"*"`; starsza nazwa: `channels.slack.dm.allowFrom`)
    - `disabled`

    Flagi wiadomości prywatnych:

    - `dm.enabled` (domyślnie true)
    - `channels.slack.allowFrom` (preferowane)
    - `dm.allowFrom` (starsza nazwa)
    - `dm.groupEnabled` (grupowe wiadomości prywatne domyślnie false)
    - `dm.groupChannels` (opcjonalna lista dozwolonych MPIM)

    Pierwszeństwo dla wielu kont:

    - `channels.slack.accounts.default.allowFrom` dotyczy tylko konta `default`.
    - Nazwane konta dziedziczą `channels.slack.allowFrom`, gdy ich własne `allowFrom` nie jest ustawione.
    - Nazwane konta nie dziedziczą `channels.slack.accounts.default.allowFrom`.

    Parowanie w wiadomościach prywatnych używa `openclaw pairing approve slack <code>`.

  </Tab>

  <Tab title="Zasady kanałów">
    `channels.slack.groupPolicy` kontroluje obsługę kanałów:

    - `open`
    - `allowlist`
    - `disabled`

    Lista dozwolonych kanałów znajduje się pod `channels.slack.channels` i powinna używać stabilnych identyfikatorów kanałów.

    Uwaga dotycząca środowiska uruchomieniowego: jeśli `channels.slack` całkowicie nie istnieje (konfiguracja tylko przez zmienne środowiskowe), środowisko uruchomieniowe wraca do `groupPolicy="allowlist"` i zapisuje ostrzeżenie w logach (nawet jeśli ustawiono `channels.defaults.groupPolicy`).

    Rozwiązywanie nazw/identyfikatorów:

    - wpisy listy dozwolonych kanałów i wpisy listy dozwolonych wiadomości prywatnych są rozwiązywane przy uruchomieniu, gdy pozwala na to dostęp tokena
    - nierozwiązane wpisy nazw kanałów są zachowywane zgodnie z konfiguracją, ale domyślnie ignorowane przy routingu
    - autoryzacja przychodząca i routing kanałów są domyślnie oparte najpierw na identyfikatorach; bezpośrednie dopasowanie nazwy użytkownika/slug wymaga `channels.slack.dangerouslyAllowNameMatching: true`

  </Tab>

  <Tab title="Wzmianki i użytkownicy kanałów">
    Wiadomości kanałowe są domyślnie bramkowane wzmiankami.

    Źródła wzmianki:

    - jawna wzmianka o aplikacji (`<@botId>`)
    - wzorce regex wzmianki (`agents.list[].groupChat.mentionPatterns`, awaryjnie `messages.groupChat.mentionPatterns`)
    - niejawne zachowanie wątku odpowiedzi do bota

    Kontrole per kanał (`channels.slack.channels.<id>`; nazwy tylko przez rozwiązywanie przy uruchomieniu lub `dangerouslyAllowNameMatching`):

    - `requireMention`
    - `users` (lista dozwolonych)
    - `allowBots`
    - `skills`
    - `systemPrompt`
    - `tools`, `toolsBySender`
    - format klucza `toolsBySender`: `id:`, `e164:`, `username:`, `name:` lub wildcard `"*"`
      (starsze klucze bez prefiksu nadal mapują się tylko na `id:`)

  </Tab>
</Tabs>

## Wątki, sesje i tagi odpowiedzi

- Wiadomości prywatne są routowane jako `direct`; kanały jako `channel`; MPIM jako `group`.
- Przy domyślnym `session.dmScope=main` wiadomości prywatne Slack są zwijane do głównej sesji agenta.
- Sesje kanałów: `agent:<agentId>:slack:channel:<channelId>`.
- Odpowiedzi w wątkach mogą tworzyć sufiksy sesji wątku (`:thread:<threadTs>`), gdy ma to zastosowanie.
- Domyślna wartość `channels.slack.thread.historyScope` to `thread`; domyślna wartość `thread.inheritParent` to `false`.
- `channels.slack.thread.initialHistoryLimit` kontroluje, ile istniejących wiadomości w wątku jest pobieranych przy starcie nowej sesji wątku (domyślnie `20`; ustaw `0`, aby wyłączyć).

Kontrole wątkowania odpowiedzi:

- `channels.slack.replyToMode`: `off|first|all|batched` (domyślnie `off`)
- `channels.slack.replyToModeByChatType`: per `direct|group|channel`
- starsze awaryjne ustawienie dla czatów bezpośrednich: `channels.slack.dm.replyToMode`

Obsługiwane są ręczne tagi odpowiedzi:

- `[[reply_to_current]]`
- `[[reply_to:<id>]]`

Uwaga: `replyToMode="off"` wyłącza **całe** wątkowanie odpowiedzi w Slack, w tym jawne tagi `[[reply_to_*]]`. Różni się to od Telegram, gdzie jawne tagi są nadal honorowane w trybie `"off"`. Różnica wynika z modeli wątków na tych platformach: w Slack wątki ukrywają wiadomości przed kanałem, podczas gdy odpowiedzi w Telegram pozostają widoczne w głównym przepływie czatu.

## Reakcje potwierdzające

`ackReaction` wysyła emoji potwierdzenia, gdy OpenClaw przetwarza wiadomość przychodzącą.

Kolejność rozwiązywania:

- `channels.slack.accounts.<accountId>.ackReaction`
- `channels.slack.ackReaction`
- `messages.ackReaction`
- awaryjnie emoji tożsamości agenta (`agents.list[].identity.emoji`, w przeciwnym razie "👀")

Uwagi:

- Slack oczekuje shortcode'ów (na przykład `"eyes"`).
- Użyj `""`, aby wyłączyć reakcję dla konta Slack lub globalnie.

## Strumieniowanie tekstu

`channels.slack.streaming` kontroluje zachowanie podglądu na żywo:

- `off`: wyłącza strumieniowanie podglądu na żywo.
- `partial` (domyślnie): zastępuje tekst podglądu najnowszym częściowym wynikiem.
- `block`: dołącza porcjowane aktualizacje podglądu.
- `progress`: pokazuje tekst stanu postępu podczas generowania, a następnie wysyła tekst końcowy.

`channels.slack.nativeStreaming` kontroluje natywne strumieniowanie tekstu Slack, gdy `streaming` ma wartość `partial` (domyślnie: `true`).

- Aby pojawiło się natywne strumieniowanie tekstu, musi być dostępny wątek odpowiedzi. Wybór wątku nadal podlega `replyToMode`. Bez niego używany jest zwykły podgląd wersji roboczej.
- Media i ładunki inne niż tekst wracają do zwykłego dostarczania.
- Jeśli strumieniowanie nie powiedzie się w trakcie odpowiedzi, OpenClaw wraca do zwykłego dostarczania dla pozostałych ładunków.

Użyj podglądu wersji roboczej zamiast natywnego strumieniowania tekstu Slack:

```json5
{
  channels: {
    slack: {
      streaming: "partial",
      nativeStreaming: false,
    },
  },
}
```

Starsze klucze:

- `channels.slack.streamMode` (`replace | status_final | append`) jest automatycznie migrowane do `channels.slack.streaming`.
- wartość logiczna `channels.slack.streaming` jest automatycznie migrowana do `channels.slack.nativeStreaming`.

## Awaryjna reakcja pisania

`typingReaction` dodaje tymczasową reakcję do przychodzącej wiadomości Slack, gdy OpenClaw przetwarza odpowiedź, a następnie usuwa ją po zakończeniu działania. Jest to najbardziej przydatne poza odpowiedziami we wątkach, które używają domyślnego wskaźnika stanu „pisze...”.

Kolejność rozwiązywania:

- `channels.slack.accounts.<accountId>.typingReaction`
- `channels.slack.typingReaction`

Uwagi:

- Slack oczekuje shortcode'ów (na przykład `"hourglass_flowing_sand"`).
- Reakcja jest wykonywana w trybie best-effort, a próba sprzątania następuje automatycznie po zakończeniu odpowiedzi lub ścieżki błędu.

## Media, dzielenie na części i dostarczanie

<AccordionGroup>
  <Accordion title="Załączniki przychodzące">
    Załączniki plików Slack są pobierane z prywatnych adresów URL hostowanych przez Slack (przepływ żądania uwierzytelnionego tokenem) i zapisywane w magazynie mediów, jeśli pobranie się powiedzie i limity rozmiaru na to pozwalają.

    Domyślny limit rozmiaru przychodzącego w środowisku uruchomieniowym to `20MB`, chyba że zostanie nadpisany przez `channels.slack.mediaMaxMb`.

  </Accordion>

  <Accordion title="Tekst i pliki wychodzące">
    - części tekstu używają `channels.slack.textChunkLimit` (domyślnie 4000)
    - `channels.slack.chunkMode="newline"` włącza dzielenie najpierw według akapitów
    - wysyłanie plików używa API przesyłania Slack i może obejmować odpowiedzi we wątkach (`thread_ts`)
    - limit mediów wychodzących podlega `channels.slack.mediaMaxMb`, jeśli jest skonfigurowany; w przeciwnym razie wysyłanie kanałowe używa domyślnych wartości według rodzaju MIME z pipeline'u mediów
  </Accordion>

  <Accordion title="Cele dostarczania">
    Preferowane jawne cele:

    - `user:<id>` dla wiadomości prywatnych
    - `channel:<id>` dla kanałów

    Wiadomości prywatne Slack są otwierane przez API konwersacji Slack podczas wysyłania do celów użytkownika.

  </Accordion>
</AccordionGroup>

## Polecenia i zachowanie slash

- Natywny tryb automatyczny poleceń jest **wyłączony** dla Slack (`commands.native: "auto"` nie włącza natywnych poleceń Slack).
- Włącz natywne handlery poleceń Slack przez `channels.slack.commands.native: true` (lub globalne `commands.native: true`).
- Gdy natywne polecenia są włączone, zarejestruj pasujące polecenia slash w Slack (`/<command>`), z jednym wyjątkiem:
  - zarejestruj `/agentstatus` dla polecenia statusu (Slack rezerwuje `/status`)
- Jeśli natywne polecenia nie są włączone, możesz uruchomić pojedyncze skonfigurowane polecenie slash przez `channels.slack.slashCommand`.
- Natywne menu argumentów dostosowują teraz strategię renderowania:
  - do 5 opcji: bloki przycisków
  - 6-100 opcji: statyczne menu wyboru
  - powyżej 100 opcji: zewnętrzny wybór z asynchronicznym filtrowaniem opcji, gdy dostępne są handlery opcji interaktywności
  - jeśli zakodowane wartości opcji przekraczają limity Slack, przepływ wraca do przycisków
- W przypadku długich ładunków opcji menu argumentów polecenia slash używają okna potwierdzenia przed wysłaniem wybranej wartości.

Domyślne ustawienia polecenia slash:

- `enabled: false`
- `name: "openclaw"`
- `sessionPrefix: "slack:slash"`
- `ephemeral: true`

Sesje slash używają odizolowanych kluczy:

- `agent:<agentId>:slack:slash:<userId>`

i nadal kierują wykonanie polecenia względem docelowej sesji konwersacji (`CommandTargetSessionKey`).

## Interaktywne odpowiedzi

Slack może renderować interaktywne kontrolki odpowiedzi tworzone przez agenta, ale ta funkcja jest domyślnie wyłączona.

Włącz ją globalnie:

```json5
{
  channels: {
    slack: {
      capabilities: {
        interactiveReplies: true,
      },
    },
  },
}
```

Lub włącz ją tylko dla jednego konta Slack:

```json5
{
  channels: {
    slack: {
      accounts: {
        ops: {
          capabilities: {
            interactiveReplies: true,
          },
        },
      },
    },
  },
}
```

Po włączeniu agenci mogą emitować dyrektywy odpowiedzi tylko dla Slack:

- `[[slack_buttons: Approve:approve, Reject:reject]]`
- `[[slack_select: Choose a target | Canary:canary, Production:production]]`

Te dyrektywy są kompilowane do Slack Block Kit i kierują kliknięcia lub wybory z powrotem przez istniejącą ścieżkę zdarzeń interakcji Slack.

Uwagi:

- To interfejs specyficzny dla Slack. Inne kanały nie tłumaczą dyrektyw Slack Block Kit na własne systemy przycisków.
- Wartości interaktywnego callbacka to generowane przez OpenClaw nieprzezroczyste tokeny, a nie surowe wartości tworzone przez agenta.
- Jeśli wygenerowane interaktywne bloki przekroczyłyby limity Slack Block Kit, OpenClaw wraca do oryginalnej odpowiedzi tekstowej zamiast wysyłać nieprawidłowy ładunek blocks.

## Zgody exec w Slack

Slack może działać jako natywny klient zatwierdzeń z interaktywnymi przyciskami i interakcjami, zamiast wracać do Web UI lub terminala.

- Zgody exec używają `channels.slack.execApprovals.*` do natywnego routingu wiadomości prywatnych/kanałów.
- Zgody pluginów mogą nadal być rozwiązywane przez tę samą natywną powierzchnię przycisków Slack, gdy żądanie trafia już do Slack, a typ identyfikatora zgody to `plugin:`.
- Autoryzacja zatwierdzającego nadal jest egzekwowana: tylko użytkownicy zidentyfikowani jako zatwierdzający mogą zatwierdzać lub odrzucać żądania przez Slack.

Używa to tej samej współdzielonej powierzchni przycisków zatwierdzeń co inne kanały. Gdy `interactivity` jest włączone w ustawieniach aplikacji Slack, prompty zatwierdzeń są renderowane bezpośrednio w konwersacji jako przyciski Block Kit.
Gdy te przyciski są obecne, są podstawowym UX zatwierdzeń; OpenClaw
powinno dołączać ręczne polecenie `/approve` tylko wtedy, gdy wynik narzędzia mówi, że zatwierdzenia na czacie
są niedostępne lub ręczne zatwierdzenie jest jedyną ścieżką.

Ścieżka konfiguracji:

- `channels.slack.execApprovals.enabled`
- `channels.slack.execApprovals.approvers` (opcjonalne; w miarę możliwości wraca do `commands.ownerAllowFrom`)
- `channels.slack.execApprovals.target` (`dm` | `channel` | `both`, domyślnie: `dm`)
- `agentFilter`, `sessionFilter`

Slack automatycznie włącza natywne zgody exec, gdy `enabled` nie jest ustawione lub ma wartość `"auto"` i zostanie rozpoznany co najmniej jeden
zatwierdzający. Ustaw `enabled: false`, aby jawnie wyłączyć Slack jako natywnego klienta zatwierdzeń.
Ustaw `enabled: true`, aby wymusić natywne zatwierdzenia, gdy zostaną rozpoznani zatwierdzający.

Domyślne zachowanie bez jawnej konfiguracji zatwierdzeń exec dla Slack:

```json5
{
  commands: {
    ownerAllowFrom: ["slack:U12345678"],
  },
}
```

Jawna konfiguracja natywna dla Slack jest potrzebna tylko wtedy, gdy chcesz nadpisać zatwierdzających, dodać filtry lub
włączyć dostarczanie do czatu źródłowego:

```json5
{
  channels: {
    slack: {
      execApprovals: {
        enabled: true,
        approvers: ["U12345678"],
        target: "both",
      },
    },
  },
}
```

Współdzielone przekazywanie `approvals.exec` jest oddzielne. Używaj go tylko wtedy, gdy prompty zatwierdzeń exec muszą być także
kierowane do innych czatów lub jawnych celów poza pasmem. Współdzielone przekazywanie `approvals.plugin` jest również
oddzielne; natywne przyciski Slack mogą nadal rozwiązywać zgody pluginów, gdy te żądania już trafiają
do Slack.

`/approve` w tym samym czacie również działa w kanałach i wiadomościach prywatnych Slack, które już obsługują polecenia. Zobacz [Zgody exec](/pl/tools/exec-approvals), aby poznać pełny model przekazywania zatwierdzeń.

## Zdarzenia i zachowanie operacyjne

- Edycje/usunięcia wiadomości oraz rozgłoszenia wątków są mapowane na zdarzenia systemowe.
- Zdarzenia dodania/usunięcia reakcji są mapowane na zdarzenia systemowe.
- Zdarzenia dołączenia/opuszczenia członka, utworzenia/zmiany nazwy kanału oraz dodania/usunięcia pinezki są mapowane na zdarzenia systemowe.
- `channel_id_changed` może migrować klucze konfiguracji kanału, gdy `configWrites` jest włączone.
- Metadane tematu/opisu kanału są traktowane jako niezaufany kontekst i mogą zostać wstrzyknięte do kontekstu routingu.
- Kontekst autora wątku i początkowej historii wątku jest filtrowany przez skonfigurowane listy dozwolonych nadawców, gdy ma to zastosowanie.
- Akcje bloków i interakcje z modalami emitują ustrukturyzowane zdarzenia systemowe `Slack interaction: ...` z bogatymi polami ładunku:
  - akcje bloków: wybrane wartości, etykiety, wartości selektorów i metadane `workflow_*`
  - zdarzenia modalne `view_submission` i `view_closed` z kierowanymi metadanymi kanału i danymi wejściowymi formularza

## Wskaźniki do dokumentacji konfiguracji

Główne źródło:

- [Dokumentacja konfiguracji - Slack](/pl/gateway/configuration-reference#slack)

  Najważniejsze pola Slack:
  - tryb/uwierzytelnianie: `mode`, `botToken`, `appToken`, `signingSecret`, `webhookPath`, `accounts.*`
  - dostęp do wiadomości prywatnych: `dm.enabled`, `dmPolicy`, `allowFrom` (starsze nazwy: `dm.policy`, `dm.allowFrom`), `dm.groupEnabled`, `dm.groupChannels`
  - przełącznik zgodności: `dangerouslyAllowNameMatching` (awaryjny; pozostaw wyłączone, jeśli nie jest potrzebne)
  - dostęp do kanałów: `groupPolicy`, `channels.*`, `channels.*.users`, `channels.*.requireMention`
  - wątki/historia: `replyToMode`, `replyToModeByChatType`, `thread.*`, `historyLimit`, `dmHistoryLimit`, `dms.*.historyLimit`
  - dostarczanie: `textChunkLimit`, `chunkMode`, `mediaMaxMb`, `streaming`, `nativeStreaming`
  - operacje/funkcje: `configWrites`, `commands.native`, `slashCommand.*`, `actions.*`, `userToken`, `userTokenReadOnly`

## Rozwiązywanie problemów

<AccordionGroup>
  <Accordion title="Brak odpowiedzi w kanałach">
    Sprawdź po kolei:

    - `groupPolicy`
    - listę dozwolonych kanałów (`channels.slack.channels`)
    - `requireMention`
    - listę dozwolonych `users` per kanał

    Przydatne polecenia:

```bash
openclaw channels status --probe
openclaw logs --follow
openclaw doctor
```

  </Accordion>

  <Accordion title="Wiadomości prywatne są ignorowane">
    Sprawdź:

    - `channels.slack.dm.enabled`
    - `channels.slack.dmPolicy` (lub starsze `channels.slack.dm.policy`)
    - zatwierdzenia parowania / wpisy listy dozwolonych

```bash
openclaw pairing list slack
```

  </Accordion>

  <Accordion title="Tryb socket nie łączy się">
    Zweryfikuj tokeny bota i aplikacji oraz włączenie Socket Mode w ustawieniach aplikacji Slack.

    Jeśli `openclaw channels status --probe --json` pokazuje `botTokenStatus` lub
    `appTokenStatus: "configured_unavailable"`, konto Slack jest
    skonfigurowane, ale bieżące środowisko uruchomieniowe nie mogło rozwiązać wartości
    opartej na SecretRef.

  </Accordion>

  <Accordion title="Tryb HTTP nie odbiera zdarzeń">
    Zweryfikuj:

    - signing secret
    - ścieżkę webhooka
    - Slack Request URL (Events + Interactivity + Slash Commands)
    - unikalny `webhookPath` dla każdego konta HTTP

    Jeśli `signingSecretStatus: "configured_unavailable"` pojawia się w migawkach
    konta, konto HTTP jest skonfigurowane, ale bieżące środowisko uruchomieniowe nie mogło
    rozwiązać signing secret opartego na SecretRef.

  </Accordion>

  <Accordion title="Natywne/polecenia slash nie działają">
    Sprawdź, czy zamierzałeś użyć:

    - natywnego trybu poleceń (`channels.slack.commands.native: true`) z pasującymi poleceniami slash zarejestrowanymi w Slack
    - albo trybu pojedynczego polecenia slash (`channels.slack.slashCommand.enabled: true`)

    Sprawdź również `commands.useAccessGroups` oraz listy dozwolonych kanałów/użytkowników.

  </Accordion>
</AccordionGroup>

## Powiązane

- [Parowanie](/pl/channels/pairing)
- [Grupy](/pl/channels/groups)
- [Bezpieczeństwo](/pl/gateway/security)
- [Routing kanałów](/pl/channels/channel-routing)
- [Rozwiązywanie problemów](/pl/channels/troubleshooting)
- [Konfiguracja](/pl/gateway/configuration)
- [Polecenia slash](/pl/tools/slash-commands)
