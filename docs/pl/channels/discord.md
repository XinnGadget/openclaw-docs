---
read_when:
    - Praca nad funkcjami kanału Discord
summary: Status obsługi bota Discord, możliwości i konfiguracja
title: Discord
x-i18n:
    generated_at: "2026-04-06T03:08:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: 54af2176a1b4fa1681e3f07494def0c652a2730165058848000e71a59e2a9d08
    source_path: channels/discord.md
    workflow: 15
---

# Discord (Bot API)

Status: gotowy do DM-ów i kanałów serwerowych przez oficjalną bramę Discord.

<CardGroup cols={3}>
  <Card title="Parowanie" icon="link" href="/pl/channels/pairing">
    DM-y Discord domyślnie działają w trybie parowania.
  </Card>
  <Card title="Polecenia slash" icon="terminal" href="/pl/tools/slash-commands">
    Natywne działanie poleceń i katalog poleceń.
  </Card>
  <Card title="Rozwiązywanie problemów z kanałem" icon="wrench" href="/pl/channels/troubleshooting">
    Diagnostyka i przepływ naprawy między kanałami.
  </Card>
</CardGroup>

## Szybka konfiguracja

Musisz utworzyć nową aplikację z botem, dodać bota do swojego serwera i sparować go z OpenClaw. Zalecamy dodanie bota do własnego prywatnego serwera. Jeśli jeszcze go nie masz, [najpierw utwórz serwer](https://support.discord.com/hc/en-us/articles/204849977-How-do-I-create-a-server) (wybierz **Create My Own > For me and my friends**).

<Steps>
  <Step title="Utwórz aplikację Discord i bota">
    Przejdź do [Discord Developer Portal](https://discord.com/developers/applications) i kliknij **New Application**. Nadaj jej nazwę, na przykład „OpenClaw”.

    Kliknij **Bot** na pasku bocznym. Ustaw **Username** na nazwę, której używasz dla swojego agenta OpenClaw.

  </Step>

  <Step title="Włącz uprzywilejowane intencje">
    Nadal na stronie **Bot**, przewiń w dół do **Privileged Gateway Intents** i włącz:

    - **Message Content Intent** (wymagane)
    - **Server Members Intent** (zalecane; wymagane dla list dozwolonych ról i dopasowywania nazw do ID)
    - **Presence Intent** (opcjonalne; potrzebne tylko do aktualizacji obecności)

  </Step>

  <Step title="Skopiuj token bota">
    Przewiń z powrotem w górę na stronie **Bot** i kliknij **Reset Token**.

    <Note>
    Wbrew nazwie spowoduje to wygenerowanie pierwszego tokena — nic nie jest „resetowane”.
    </Note>

    Skopiuj token i zapisz go w bezpiecznym miejscu. To jest Twój **Bot Token** i będzie potrzebny za chwilę.

  </Step>

  <Step title="Wygeneruj URL zaproszenia i dodaj bota do serwera">
    Kliknij **OAuth2** na pasku bocznym. Wygenerujesz URL zaproszenia z odpowiednimi uprawnieniami do dodania bota do swojego serwera.

    Przewiń w dół do **OAuth2 URL Generator** i włącz:

    - `bot`
    - `applications.commands`

    Poniżej pojawi się sekcja **Bot Permissions**. Włącz:

    - View Channels
    - Send Messages
    - Read Message History
    - Embed Links
    - Attach Files
    - Add Reactions (opcjonalnie)

    Skopiuj wygenerowany URL na dole, wklej go do przeglądarki, wybierz swój serwer i kliknij **Continue**, aby połączyć. Powinieneś teraz zobaczyć swojego bota na serwerze Discord.

  </Step>

  <Step title="Włącz Developer Mode i zbierz swoje ID">
    Po powrocie do aplikacji Discord musisz włączyć Developer Mode, aby móc kopiować wewnętrzne ID.

    1. Kliknij **User Settings** (ikona koła zębatego obok awatara) → **Advanced** → włącz **Developer Mode**
    2. Kliknij prawym przyciskiem myszy **ikonę serwera** na pasku bocznym → **Copy Server ID**
    3. Kliknij prawym przyciskiem myszy **swój awatar** → **Copy User ID**

    Zapisz **Server ID** i **User ID** razem z Bot Token — w następnym kroku prześlesz wszystkie trzy do OpenClaw.

  </Step>

  <Step title="Zezwól na DM-y od członków serwera">
    Aby parowanie działało, Discord musi pozwalać Twojemu botowi wysyłać do Ciebie DM-y. Kliknij prawym przyciskiem myszy **ikonę serwera** → **Privacy Settings** → włącz **Direct Messages**.

    Umożliwia to członkom serwera (w tym botom) wysyłanie Ci DM-ów. Pozostaw to włączone, jeśli chcesz używać DM-ów Discord z OpenClaw. Jeśli planujesz używać tylko kanałów serwerowych, możesz wyłączyć DM-y po sparowaniu.

  </Step>

  <Step title="Ustaw bezpiecznie token bota (nie wysyłaj go na czacie)">
    Token bota Discord jest tajny (jak hasło). Ustaw go na maszynie, na której działa OpenClaw, zanim wyślesz wiadomość do swojego agenta.

```bash
export DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN"
openclaw config set channels.discord.token --ref-provider default --ref-source env --ref-id DISCORD_BOT_TOKEN --dry-run
openclaw config set channels.discord.token --ref-provider default --ref-source env --ref-id DISCORD_BOT_TOKEN
openclaw config set channels.discord.enabled true --strict-json
openclaw gateway
```

    Jeśli OpenClaw działa już jako usługa w tle, uruchom go ponownie przez aplikację OpenClaw Mac albo przez zatrzymanie i ponowne uruchomienie procesu `openclaw gateway run`.

  </Step>

  <Step title="Skonfiguruj OpenClaw i sparuj">

    <Tabs>
      <Tab title="Zapytaj swojego agenta">
        Porozmawiaj ze swoim agentem OpenClaw na dowolnym istniejącym kanale (np. Telegram) i przekaż mu te informacje. Jeśli Discord jest Twoim pierwszym kanałem, użyj zamiast tego karty CLI / config.

        > „Mam już ustawiony token bota Discord w konfiguracji. Dokończ proszę konfigurację Discord przy użyciu User ID `<user_id>` i Server ID `<server_id>`.”
      </Tab>
      <Tab title="CLI / config">
        Jeśli wolisz konfigurację opartą na pliku, ustaw:

```json5
{
  channels: {
    discord: {
      enabled: true,
      token: {
        source: "env",
        provider: "default",
        id: "DISCORD_BOT_TOKEN",
      },
    },
  },
}
```

        Fallback env dla konta domyślnego:

```bash
DISCORD_BOT_TOKEN=...
```

        Jawne wartości `token` są obsługiwane. Wartości SecretRef są także obsługiwane dla `channels.discord.token` u dostawców env/file/exec. Zobacz [Secrets Management](/pl/gateway/secrets).

      </Tab>
    </Tabs>

  </Step>

  <Step title="Zatwierdź pierwsze parowanie DM">
    Poczekaj, aż brama będzie działać, a następnie wyślij DM do swojego bota w Discord. Odpowie kodem parowania.

    <Tabs>
      <Tab title="Zapytaj swojego agenta">
        Wyślij kod parowania do swojego agenta na istniejącym kanale:

        > „Zatwierdź ten kod parowania Discord: `<CODE>`”
      </Tab>
      <Tab title="CLI">

```bash
openclaw pairing list discord
openclaw pairing approve discord <CODE>
```

      </Tab>
    </Tabs>

    Kody parowania wygasają po 1 godzinie.

    Powinieneś teraz móc rozmawiać ze swoim agentem przez DM na Discordzie.

  </Step>
</Steps>

<Note>
Rozpoznawanie tokena uwzględnia konto. Wartości tokena z konfiguracji mają pierwszeństwo przed fallbackiem env. `DISCORD_BOT_TOKEN` jest używany tylko dla konta domyślnego.
W przypadku zaawansowanych wywołań wychodzących (narzędzie wiadomości/działania kanałowe) jawny `token` na poziomie wywołania jest używany dla tego wywołania. Dotyczy to działań typu send oraz read/probe (na przykład read/search/fetch/thread/pins/permissions). Zasady konta i ustawienia ponawiania pochodzą nadal z wybranego konta w aktywnej migawce środowiska uruchomieniowego.
</Note>

## Zalecane: skonfiguruj przestrzeń roboczą serwera

Gdy DM-y już działają, możesz skonfigurować swój serwer Discord jako pełną przestrzeń roboczą, w której każdy kanał ma własną sesję agenta z własnym kontekstem. Jest to zalecane dla prywatnych serwerów, gdzie jesteście tylko Ty i Twój bot.

<Steps>
  <Step title="Dodaj swój serwer do listy dozwolonych serwerów">
    To umożliwia agentowi odpowiadanie na dowolnym kanale na Twoim serwerze, a nie tylko w DM-ach.

    <Tabs>
      <Tab title="Zapytaj swojego agenta">
        > „Dodaj mój Discord Server ID `<server_id>` do listy dozwolonych serwerów”
      </Tab>
      <Tab title="Config">

```json5
{
  channels: {
    discord: {
      groupPolicy: "allowlist",
      guilds: {
        YOUR_SERVER_ID: {
          requireMention: true,
          users: ["YOUR_USER_ID"],
        },
      },
    },
  },
}
```

      </Tab>
    </Tabs>

  </Step>

  <Step title="Zezwól na odpowiedzi bez @wzmianki">
    Domyślnie agent odpowiada na kanałach serwerowych tylko wtedy, gdy zostanie oznaczony przez @mention. W przypadku prywatnego serwera prawdopodobnie chcesz, aby odpowiadał na każdą wiadomość.

    <Tabs>
      <Tab title="Zapytaj swojego agenta">
        > „Pozwól mojemu agentowi odpowiadać na tym serwerze bez konieczności używania @mention”
      </Tab>
      <Tab title="Config">
        Ustaw `requireMention: false` w konfiguracji serwera:

```json5
{
  channels: {
    discord: {
      guilds: {
        YOUR_SERVER_ID: {
          requireMention: false,
        },
      },
    },
  },
}
```

      </Tab>
    </Tabs>

  </Step>

  <Step title="Zaplanuj pamięć dla kanałów serwerowych">
    Domyślnie pamięć długoterminowa (`MEMORY.md`) jest ładowana tylko w sesjach DM. Kanały serwerowe nie ładują automatycznie `MEMORY.md`.

    <Tabs>
      <Tab title="Zapytaj swojego agenta">
        > „Gdy zadaję pytania na kanałach Discord, używaj `memory_search` lub `memory_get`, jeśli potrzebujesz długoterminowego kontekstu z `MEMORY.md`.”
      </Tab>
      <Tab title="Ręcznie">
        Jeśli potrzebujesz współdzielonego kontekstu na każdym kanale, umieść stabilne instrukcje w `AGENTS.md` lub `USER.md` (są wstrzykiwane do każdej sesji). Notatki długoterminowe trzymaj w `MEMORY.md` i uzyskuj do nich dostęp na żądanie za pomocą narzędzi pamięci.
      </Tab>
    </Tabs>

  </Step>
</Steps>

Teraz utwórz kilka kanałów na swoim serwerze Discord i zacznij rozmawiać. Agent widzi nazwę kanału, a każdy kanał otrzymuje własną odizolowaną sesję — możesz więc skonfigurować `#coding`, `#home`, `#research` lub cokolwiek pasuje do Twojego sposobu pracy.

## Model działania środowiska uruchomieniowego

- Brama zarządza połączeniem z Discord.
- Kierowanie odpowiedzi jest deterministyczne: odpowiedzi przychodzące z Discord wracają do Discord.
- Domyślnie (`session.dmScope=main`) bezpośrednie rozmowy współdzielą główną sesję agenta (`agent:main:main`).
- Kanały serwerowe mają odizolowane klucze sesji (`agent:<agentId>:discord:channel:<channelId>`).
- Grupowe DM-y są domyślnie ignorowane (`channels.discord.dm.groupEnabled=false`).
- Natywne polecenia slash działają w odizolowanych sesjach poleceń (`agent:<agentId>:discord:slash:<userId>`), nadal przenosząc `CommandTargetSessionKey` do kierowanej sesji rozmowy.

## Kanały forum

Kanały forum i kanały multimedialne Discord akceptują tylko posty w wątkach. OpenClaw obsługuje dwa sposoby ich tworzenia:

- Wyślij wiadomość do nadrzędnego forum (`channel:<forumId>`), aby automatycznie utworzyć wątek. Tytuł wątku używa pierwszej niepustej linii wiadomości.
- Użyj `openclaw message thread create`, aby utworzyć wątek bezpośrednio. Nie przekazuj `--message-id` dla kanałów forum.

Przykład: wyślij do nadrzędnego forum, aby utworzyć wątek

```bash
openclaw message send --channel discord --target channel:<forumId> \
  --message "Topic title\nBody of the post"
```

Przykład: jawne utworzenie wątku forum

```bash
openclaw message thread create --channel discord --target channel:<forumId> \
  --thread-name "Topic title" --message "Body of the post"
```

Nadrzędne fora nie akceptują komponentów Discord. Jeśli potrzebujesz komponentów, wysyłaj do samego wątku (`channel:<threadId>`).

## Komponenty interaktywne

OpenClaw obsługuje kontenery Discord components v2 dla wiadomości agenta. Użyj narzędzia wiadomości z ładunkiem `components`. Wyniki interakcji są kierowane z powrotem do agenta jako zwykłe wiadomości przychodzące i stosują istniejące ustawienia Discord `replyToMode`.

Obsługiwane bloki:

- `text`, `section`, `separator`, `actions`, `media-gallery`, `file`
- Wiersze akcji pozwalają na maksymalnie 5 przycisków albo jedno menu wyboru
- Typy wyboru: `string`, `user`, `role`, `mentionable`, `channel`

Domyślnie komponenty są jednorazowe. Ustaw `components.reusable=true`, aby pozwolić na wielokrotne użycie przycisków, selektorów i formularzy aż do ich wygaśnięcia.

Aby ograniczyć, kto może kliknąć przycisk, ustaw `allowedUsers` na tym przycisku (ID użytkowników Discord, tagi lub `*`). Gdy jest to skonfigurowane, niedopasowani użytkownicy otrzymują efemeryczną odmowę.

Polecenia slash `/model` i `/models` otwierają interaktywny selektor modelu z listami rozwijanymi dostawcy i modelu oraz krokiem Submit. Odpowiedź selektora jest efemeryczna i tylko użytkownik, który ją wywołał, może z niej korzystać.

Załączniki plików:

- bloki `file` muszą wskazywać na odwołanie do załącznika (`attachment://<filename>`)
- podaj załącznik przez `media`/`path`/`filePath` (pojedynczy plik); użyj `media-gallery` dla wielu plików
- użyj `filename`, aby nadpisać nazwę przesyłanego pliku, gdy ma odpowiadać odwołaniu do załącznika

Formularze modalne:

- Dodaj `components.modal` z maksymalnie 5 polami
- Typy pól: `text`, `checkbox`, `radio`, `select`, `role-select`, `user-select`
- OpenClaw automatycznie dodaje przycisk wyzwalający

Przykład:

```json5
{
  channel: "discord",
  action: "send",
  to: "channel:123456789012345678",
  message: "Optional fallback text",
  components: {
    reusable: true,
    text: "Choose a path",
    blocks: [
      {
        type: "actions",
        buttons: [
          {
            label: "Approve",
            style: "success",
            allowedUsers: ["123456789012345678"],
          },
          { label: "Decline", style: "danger" },
        ],
      },
      {
        type: "actions",
        select: {
          type: "string",
          placeholder: "Pick an option",
          options: [
            { label: "Option A", value: "a" },
            { label: "Option B", value: "b" },
          ],
        },
      },
    ],
    modal: {
      title: "Details",
      triggerLabel: "Open form",
      fields: [
        { type: "text", label: "Requester" },
        {
          type: "select",
          label: "Priority",
          options: [
            { label: "Low", value: "low" },
            { label: "High", value: "high" },
          ],
        },
      ],
    },
  },
}
```

## Kontrola dostępu i routing

<Tabs>
  <Tab title="Zasady DM">
    `channels.discord.dmPolicy` steruje dostępem do DM-ów (starsza nazwa: `channels.discord.dm.policy`):

    - `pairing` (domyślnie)
    - `allowlist`
    - `open` (wymaga, aby `channels.discord.allowFrom` zawierało `"*"`; starsza nazwa: `channels.discord.dm.allowFrom`)
    - `disabled`

    Jeśli zasady DM nie są otwarte, nieznani użytkownicy są blokowani (lub proszeni o sparowanie w trybie `pairing`).

    Priorytet dla wielu kont:

    - `channels.discord.accounts.default.allowFrom` ma zastosowanie tylko do konta `default`.
    - Nazwane konta dziedziczą `channels.discord.allowFrom`, gdy ich własne `allowFrom` nie jest ustawione.
    - Nazwane konta nie dziedziczą `channels.discord.accounts.default.allowFrom`.

    Format celu DM dla dostarczania:

    - `user:<id>`
    - wzmianka `<@id>`

    Same numeryczne ID są niejednoznaczne i są odrzucane, chyba że podano jawnie rodzaj celu user/channel.

  </Tab>

  <Tab title="Zasady serwerów">
    Obsługa serwerów jest kontrolowana przez `channels.discord.groupPolicy`:

    - `open`
    - `allowlist`
    - `disabled`

    Bezpieczną bazą, gdy istnieje `channels.discord`, jest `allowlist`.

    Zachowanie `allowlist`:

    - serwer musi pasować do `channels.discord.guilds` (preferowane `id`, akceptowany slug)
    - opcjonalne listy dozwolonych nadawców: `users` (zalecane stabilne ID) i `roles` (tylko ID ról); jeśli skonfigurowano którekolwiek z nich, nadawcy są dozwoleni, gdy pasują do `users` LUB `roles`
    - bezpośrednie dopasowywanie nazw/tagów jest domyślnie wyłączone; włącz `channels.discord.dangerouslyAllowNameMatching: true` tylko jako tryb zgodności awaryjnej
    - nazwy/tagi są obsługiwane dla `users`, ale ID są bezpieczniejsze; `openclaw security audit` ostrzega, gdy używane są wpisy nazwa/tag
    - jeśli serwer ma skonfigurowane `channels`, kanały nieuwzględnione na liście są odrzucane
    - jeśli serwer nie ma bloku `channels`, wszystkie kanały w tym serwerze z listy dozwolonych są dozwolone

    Przykład:

```json5
{
  channels: {
    discord: {
      groupPolicy: "allowlist",
      guilds: {
        "123456789012345678": {
          requireMention: true,
          ignoreOtherMentions: true,
          users: ["987654321098765432"],
          roles: ["123456789012345678"],
          channels: {
            general: { allow: true },
            help: { allow: true, requireMention: true },
          },
        },
      },
    },
  },
}
```

    Jeśli ustawisz tylko `DISCORD_BOT_TOKEN` i nie utworzysz bloku `channels.discord`, fallback środowiska uruchomieniowego będzie `groupPolicy="allowlist"` (z ostrzeżeniem w logach), nawet jeśli `channels.defaults.groupPolicy` ma wartość `open`.

  </Tab>

  <Tab title="Wzmianki i grupowe DM-y">
    Wiadomości na serwerach są domyślnie bramkowane wzmiankami.

    Wykrywanie wzmianki obejmuje:

    - jawną wzmiankę o bocie
    - skonfigurowane wzorce wzmianki (`agents.list[].groupChat.mentionPatterns`, fallback `messages.groupChat.mentionPatterns`)
    - niejawne zachowanie odpowiedzi-do-bota w obsługiwanych przypadkach

    `requireMention` jest konfigurowane dla każdego serwera/kanału (`channels.discord.guilds...`).
    `ignoreOtherMentions` opcjonalnie odrzuca wiadomości, które wspominają innego użytkownika/rolę, ale nie bota (z wyłączeniem @everyone/@here).

    Grupowe DM-y:

    - domyślnie: ignorowane (`dm.groupEnabled=false`)
    - opcjonalna lista dozwolonych przez `dm.groupChannels` (ID kanałów lub slugi)

  </Tab>
</Tabs>

### Routing agenta oparty na rolach

Użyj `bindings[].match.roles`, aby kierować członków serwerów Discord do różnych agentów według ID ról. Powiązania oparte na rolach akceptują tylko ID ról i są oceniane po powiązaniach peer lub parent-peer, a przed powiązaniami tylko-serwerowymi. Jeśli powiązanie ustawia też inne pola dopasowania (na przykład `peer` + `guildId` + `roles`), wszystkie skonfigurowane pola muszą pasować.

```json5
{
  bindings: [
    {
      agentId: "opus",
      match: {
        channel: "discord",
        guildId: "123456789012345678",
        roles: ["111111111111111111"],
      },
    },
    {
      agentId: "sonnet",
      match: {
        channel: "discord",
        guildId: "123456789012345678",
      },
    },
  ],
}
```

## Konfiguracja Developer Portal

<AccordionGroup>
  <Accordion title="Utwórz aplikację i bota">

    1. Discord Developer Portal -> **Applications** -> **New Application**
    2. **Bot** -> **Add Bot**
    3. Skopiuj token bota

  </Accordion>

  <Accordion title="Uprzywilejowane intencje">
    W **Bot -> Privileged Gateway Intents** włącz:

    - Message Content Intent
    - Server Members Intent (zalecane)

    Presence intent jest opcjonalne i wymagane tylko wtedy, gdy chcesz otrzymywać aktualizacje obecności. Ustawianie obecności bota (`setPresence`) nie wymaga włączenia aktualizacji obecności członków.

  </Accordion>

  <Accordion title="Zakresy OAuth i bazowe uprawnienia">
    Generator URL OAuth:

    - zakresy: `bot`, `applications.commands`

    Typowe bazowe uprawnienia:

    - View Channels
    - Send Messages
    - Read Message History
    - Embed Links
    - Attach Files
    - Add Reactions (opcjonalnie)

    Unikaj `Administrator`, chyba że jest to wyraźnie potrzebne.

  </Accordion>

  <Accordion title="Skopiuj ID">
    Włącz Discord Developer Mode, a następnie skopiuj:

    - ID serwera
    - ID kanału
    - ID użytkownika

    W konfiguracji OpenClaw preferuj numeryczne ID dla wiarygodnych audytów i testów.

  </Accordion>
</AccordionGroup>

## Natywne polecenia i uwierzytelnianie poleceń

- `commands.native` ma domyślnie wartość `"auto"` i jest włączone dla Discord.
- Nadpisanie dla kanału: `channels.discord.commands.native`.
- `commands.native=false` jawnie czyści wcześniej zarejestrowane natywne polecenia Discord.
- Uwierzytelnianie natywnych poleceń używa tych samych list dozwolonych i zasad Discord co zwykła obsługa wiadomości.
- Polecenia mogą być nadal widoczne w interfejsie Discord dla użytkowników bez uprawnień; wykonanie nadal wymusza autoryzację OpenClaw i zwraca „not authorized”.

Zobacz [Slash commands](/pl/tools/slash-commands), aby poznać katalog poleceń i zachowanie.

Domyślne ustawienia poleceń slash:

- `ephemeral: true`

## Szczegóły funkcji

<AccordionGroup>
  <Accordion title="Znaczniki odpowiedzi i natywne odpowiedzi">
    Discord obsługuje znaczniki odpowiedzi w wyjściu agenta:

    - `[[reply_to_current]]`
    - `[[reply_to:<id>]]`

    Sterowane przez `channels.discord.replyToMode`:

    - `off` (domyślnie)
    - `first`
    - `all`
    - `batched`

    Uwaga: `off` wyłącza niejawne wątkowanie odpowiedzi. Jawne znaczniki `[[reply_to_*]]` są nadal respektowane.
    `first` zawsze dołącza niejawną natywną referencję odpowiedzi do pierwszej wychodzącej wiadomości Discord w danej turze.
    `batched` dołącza niejawną natywną referencję odpowiedzi Discord tylko wtedy, gdy
    tura przychodząca była odroczoną partią wielu wiadomości. Jest to przydatne,
    gdy chcesz używać natywnych odpowiedzi głównie przy niejednoznacznych,
    gwałtownych seriach czatu, a nie przy każdej turze pojedynczej wiadomości.

    ID wiadomości są ujawniane w kontekście/historii, dzięki czemu agenci mogą kierować odpowiedzi na konkretne wiadomości.

  </Accordion>

  <Accordion title="Podgląd transmisji na żywo">
    OpenClaw może strumieniować robocze odpowiedzi, wysyłając tymczasową wiadomość i edytując ją w miarę napływu tekstu.

    - `channels.discord.streaming` steruje strumieniowaniem podglądu (`off` | `partial` | `block` | `progress`, domyślnie: `off`).
    - Domyślna wartość pozostaje `off`, ponieważ edycje podglądu w Discord mogą szybko osiągnąć limity szybkości, zwłaszcza gdy wiele botów lub bram współdzieli to samo konto albo ruch serwera.
    - `progress` jest akceptowane dla spójności między kanałami i mapuje się na `partial` w Discord.
    - `channels.discord.streamMode` jest starszym aliasem i jest migrowane automatycznie.
    - `partial` edytuje pojedynczą wiadomość podglądu, gdy napływają tokeny.
    - `block` emituje fragmenty wielkości szkicu (użyj `draftChunk`, aby dostroić rozmiar i punkty podziału).

    Przykład:

```json5
{
  channels: {
    discord: {
      streaming: "partial",
    },
  },
}
```

    Domyślne dzielenie na fragmenty w trybie `block` (ograniczane do `channels.discord.textChunkLimit`):

```json5
{
  channels: {
    discord: {
      streaming: "block",
      draftChunk: {
        minChars: 200,
        maxChars: 800,
        breakPreference: "paragraph",
      },
    },
  },
}
```

    Strumieniowanie podglądu dotyczy tylko tekstu; odpowiedzi multimedialne wracają do zwykłego dostarczania.

    Uwaga: strumieniowanie podglądu jest oddzielne od strumieniowania blokowego. Gdy strumieniowanie blokowe jest jawnie
    włączone dla Discord, OpenClaw pomija strumień podglądu, aby uniknąć podwójnego strumieniowania.

  </Accordion>

  <Accordion title="Historia, kontekst i zachowanie wątków">
    Kontekst historii serwera:

    - `channels.discord.historyLimit` domyślnie `20`
    - fallback: `messages.groupChat.historyLimit`
    - `0` wyłącza

    Ustawienia historii DM:

    - `channels.discord.dmHistoryLimit`
    - `channels.discord.dms["<user_id>"].historyLimit`

    Zachowanie wątków:

    - wątki Discord są kierowane jako sesje kanałów
    - metadane nadrzędnego wątku mogą być używane do połączenia z sesją nadrzędną
    - konfiguracja wątku dziedziczy konfigurację kanału nadrzędnego, chyba że istnieje wpis specyficzny dla wątku

    Tematy kanałów są wstrzykiwane jako kontekst **niezaufany** (nie jako prompt systemowy).
    Kontekst odpowiedzi i cytowanej wiadomości pozostaje obecnie taki, jak został odebrany.
    Listy dozwolonych Discord przede wszystkim ograniczają to, kto może wyzwolić agenta, a nie stanowią pełnej granicy redakcji kontekstu uzupełniającego.

  </Accordion>

  <Accordion title="Sesje powiązane z wątkiem dla subagentów">
    Discord może powiązać wątek z celem sesji, aby kolejne wiadomości w tym wątku nadal trafiały do tej samej sesji (w tym sesji subagentów).

    Polecenia:

    - `/focus <target>` powiąż bieżący/nowy wątek z celem subagenta/sesji
    - `/unfocus` usuń bieżące powiązanie wątku
    - `/agents` pokaż aktywne uruchomienia i stan powiązań
    - `/session idle <duration|off>` sprawdź/zaktualizuj automatyczne odwiązywanie po bezczynności dla powiązań focus
    - `/session max-age <duration|off>` sprawdź/zaktualizuj twardy maksymalny wiek dla powiązań focus

    Konfiguracja:

```json5
{
  session: {
    threadBindings: {
      enabled: true,
      idleHours: 24,
      maxAgeHours: 0,
    },
  },
  channels: {
    discord: {
      threadBindings: {
        enabled: true,
        idleHours: 24,
        maxAgeHours: 0,
        spawnSubagentSessions: false, // opt-in
      },
    },
  },
}
```

    Uwagi:

    - `session.threadBindings.*` ustawia globalne wartości domyślne.
    - `channels.discord.threadBindings.*` nadpisuje zachowanie Discord.
    - `spawnSubagentSessions` musi mieć wartość true, aby automatycznie tworzyć/powiązywać wątki dla `sessions_spawn({ thread: true })`.
    - `spawnAcpSessions` musi mieć wartość true, aby automatycznie tworzyć/powiązywać wątki dla ACP (`/acp spawn ... --thread ...` lub `sessions_spawn({ runtime: "acp", thread: true })`).
    - Jeśli powiązania wątków są wyłączone dla konta, `/focus` i powiązane operacje na powiązaniach wątków są niedostępne.

    Zobacz [Sub-agents](/pl/tools/subagents), [ACP Agents](/pl/tools/acp-agents) i [Configuration Reference](/pl/gateway/configuration-reference).

  </Accordion>

  <Accordion title="Trwałe powiązania kanałów ACP">
    W przypadku stabilnych, „zawsze aktywnych” przestrzeni roboczych ACP skonfiguruj najwyższego poziomu typowane powiązania ACP wskazujące na rozmowy Discord.

    Ścieżka konfiguracji:

    - `bindings[]` z `type: "acp"` i `match.channel: "discord"`

    Przykład:

```json5
{
  agents: {
    list: [
      {
        id: "codex",
        runtime: {
          type: "acp",
          acp: {
            agent: "codex",
            backend: "acpx",
            mode: "persistent",
            cwd: "/workspace/openclaw",
          },
        },
      },
    ],
  },
  bindings: [
    {
      type: "acp",
      agentId: "codex",
      match: {
        channel: "discord",
        accountId: "default",
        peer: { kind: "channel", id: "222222222222222222" },
      },
      acp: { label: "codex-main" },
    },
  ],
  channels: {
    discord: {
      guilds: {
        "111111111111111111": {
          channels: {
            "222222222222222222": {
              requireMention: false,
            },
          },
        },
      },
    },
  },
}
```

    Uwagi:

    - `/acp spawn codex --bind here` wiąże bieżący kanał lub wątek Discord na miejscu i utrzymuje kierowanie przyszłych wiadomości do tej samej sesji ACP.
    - Może to nadal oznaczać „uruchom nową sesję Codex ACP”, ale samo w sobie nie tworzy nowego wątku Discord. Istniejący kanał pozostaje powierzchnią czatu.
    - Codex może nadal działać we własnym `cwd` lub obszarze roboczym backendu na dysku. Ten obszar roboczy jest stanem środowiska uruchomieniowego, a nie wątkiem Discord.
    - Wiadomości w wątku mogą dziedziczyć powiązanie ACP kanału nadrzędnego.
    - W powiązanym kanale lub wątku `/new` i `/reset` resetują tę samą sesję ACP na miejscu.
    - Tymczasowe powiązania wątków nadal działają i mogą nadpisywać rozstrzyganie celu, gdy są aktywne.
    - `spawnAcpSessions` jest wymagane tylko wtedy, gdy OpenClaw musi utworzyć/powiązać podrzędny wątek przez `--thread auto|here`. Nie jest wymagane dla `/acp spawn ... --bind here` w bieżącym kanale.

    Zobacz [ACP Agents](/pl/tools/acp-agents), aby poznać szczegóły zachowania powiązań.

  </Accordion>

  <Accordion title="Powiadomienia o reakcjach">
    Tryb powiadomień o reakcjach dla każdego serwera:

    - `off`
    - `own` (domyślnie)
    - `all`
    - `allowlist` (używa `guilds.<id>.users`)

    Zdarzenia reakcji są zamieniane na zdarzenia systemowe i dołączane do kierowanej sesji Discord.

  </Accordion>

  <Accordion title="Reakcje potwierdzające">
    `ackReaction` wysyła emoji potwierdzenia, gdy OpenClaw przetwarza wiadomość przychodzącą.

    Kolejność rozstrzygania:

    - `channels.discord.accounts.<accountId>.ackReaction`
    - `channels.discord.ackReaction`
    - `messages.ackReaction`
    - fallback emoji tożsamości agenta (`agents.list[].identity.emoji`, w przeciwnym razie "👀")

    Uwagi:

    - Discord akceptuje emoji Unicode lub niestandardowe nazwy emoji.
    - Użyj `""`, aby wyłączyć reakcję dla kanału lub konta.

  </Accordion>

  <Accordion title="Zapisy konfiguracji">
    Zapisy konfiguracji inicjowane z kanału są domyślnie włączone.

    Ma to wpływ na przepływy `/config set|unset` (gdy funkcje poleceń są włączone).

    Wyłącz:

```json5
{
  channels: {
    discord: {
      configWrites: false,
    },
  },
}
```

  </Accordion>

  <Accordion title="Proxy bramy">
    Kieruj ruch WebSocket bramy Discord i wyszukiwania REST przy uruchamianiu (ID aplikacji + rozstrzyganie listy dozwolonych) przez proxy HTTP(S) za pomocą `channels.discord.proxy`.

```json5
{
  channels: {
    discord: {
      proxy: "http://proxy.example:8080",
    },
  },
}
```

    Nadpisanie dla konta:

```json5
{
  channels: {
    discord: {
      accounts: {
        primary: {
          proxy: "http://proxy.example:8080",
        },
      },
    },
  },
}
```

  </Accordion>

  <Accordion title="Obsługa PluralKit">
    Włącz rozstrzyganie PluralKit, aby mapować wiadomości proxy na tożsamość członka systemu:

```json5
{
  channels: {
    discord: {
      pluralkit: {
        enabled: true,
        token: "pk_live_...", // optional; needed for private systems
      },
    },
  },
}
```

    Uwagi:

    - listy dozwolonych mogą używać `pk:<memberId>`
    - wyświetlane nazwy członków są dopasowywane według nazwy/slugu tylko wtedy, gdy `channels.discord.dangerouslyAllowNameMatching: true`
    - wyszukiwania używają oryginalnego ID wiadomości i są ograniczone oknem czasowym
    - jeśli wyszukiwanie się nie powiedzie, wiadomości proxy są traktowane jako wiadomości bota i odrzucane, chyba że `allowBots=true`

  </Accordion>

  <Accordion title="Konfiguracja obecności">
    Aktualizacje obecności są stosowane, gdy ustawisz pole statusu lub aktywności albo gdy włączysz auto presence.

    Przykład tylko ze statusem:

```json5
{
  channels: {
    discord: {
      status: "idle",
    },
  },
}
```

    Przykład aktywności (niestandardowy status jest domyślnym typem aktywności):

```json5
{
  channels: {
    discord: {
      activity: "Focus time",
      activityType: 4,
    },
  },
}
```

    Przykład transmisji:

```json5
{
  channels: {
    discord: {
      activity: "Live coding",
      activityType: 1,
      activityUrl: "https://twitch.tv/openclaw",
    },
  },
}
```

    Mapa typów aktywności:

    - 0: Playing
    - 1: Streaming (wymaga `activityUrl`)
    - 2: Listening
    - 3: Watching
    - 4: Custom (używa tekstu aktywności jako stanu statusu; emoji jest opcjonalne)
    - 5: Competing

    Przykład auto presence (sygnał kondycji środowiska uruchomieniowego):

```json5
{
  channels: {
    discord: {
      autoPresence: {
        enabled: true,
        intervalMs: 30000,
        minUpdateIntervalMs: 15000,
        exhaustedText: "token exhausted",
      },
    },
  },
}
```

    Auto presence mapuje dostępność środowiska uruchomieniowego na status Discord: healthy => online, degraded lub unknown => idle, exhausted lub unavailable => dnd. Opcjonalne nadpisania tekstu:

    - `autoPresence.healthyText`
    - `autoPresence.degradedText`
    - `autoPresence.exhaustedText` (obsługuje placeholder `{reason}`)

  </Accordion>

  <Accordion title="Zatwierdzenia w Discord">
    Discord obsługuje zatwierdzanie oparte na przyciskach w DM-ach i może opcjonalnie publikować prośby o zatwierdzenie w kanale źródłowym.

    Ścieżka konfiguracji:

    - `channels.discord.execApprovals.enabled`
    - `channels.discord.execApprovals.approvers` (opcjonalnie; jeśli to możliwe, fallback do `commands.ownerAllowFrom`)
    - `channels.discord.execApprovals.target` (`dm` | `channel` | `both`, domyślnie: `dm`)
    - `agentFilter`, `sessionFilter`, `cleanupAfterResolve`

    Discord automatycznie włącza natywne zatwierdzenia exec, gdy `enabled` jest nieustawione lub ma wartość `"auto"` i można rozstrzygnąć co najmniej jednego zatwierdzającego, albo z `execApprovals.approvers`, albo z `commands.ownerAllowFrom`. Discord nie wywodzi zatwierdzających exec z kanałowego `allowFrom`, starszego `dm.allowFrom` ani z bezpośredniego `defaultTo`. Ustaw `enabled: false`, aby jawnie wyłączyć Discord jako natywnego klienta zatwierdzeń.

    Gdy `target` ma wartość `channel` lub `both`, prośba o zatwierdzenie jest widoczna w kanale. Tylko rozstrzygnięci zatwierdzający mogą używać przycisków; inni użytkownicy otrzymują efemeryczną odmowę. Prośby o zatwierdzenie zawierają tekst polecenia, więc włączaj dostarczanie do kanału tylko na zaufanych kanałach. Jeśli nie da się wyprowadzić ID kanału z klucza sesji, OpenClaw wraca do dostarczenia przez DM.

    Discord renderuje także współdzielone przyciski zatwierdzania używane przez inne kanały czatu. Natywny adapter Discord głównie dodaje routowanie DM dla zatwierdzających oraz rozsyłanie do kanału.
    Gdy te przyciski są obecne, stanowią podstawowy interfejs zatwierdzania; OpenClaw
    powinien dołączać ręczne polecenie `/approve` tylko wtedy, gdy wynik narzędzia mówi,
    że zatwierdzenia na czacie są niedostępne lub ręczne zatwierdzenie jest jedyną ścieżką.

    Uwierzytelnianie bramy dla tego modułu obsługi używa tego samego współdzielonego kontraktu rozstrzygania poświadczeń co inni klienci Gateway:

    - uwierzytelnianie lokalne z pierwszeństwem env (`OPENCLAW_GATEWAY_TOKEN` / `OPENCLAW_GATEWAY_PASSWORD`, potem `gateway.auth.*`)
    - w trybie lokalnym `gateway.remote.*` może być użyte jako fallback tylko wtedy, gdy `gateway.auth.*` nie jest ustawione; skonfigurowane, ale nierozstrzygnięte lokalne SecretRef są zamykane fail-closed
    - obsługa trybu zdalnego przez `gateway.remote.*`, gdy ma zastosowanie
    - nadpisania URL są bezpieczne względem nadpisywania: nadpisania CLI nie używają ponownie niejawnych poświadczeń, a nadpisania env używają tylko poświadczeń env

    Zachowanie rozstrzygania zatwierdzeń:

    - ID z prefiksem `plugin:` są rozstrzygane przez `plugin.approval.resolve`.
    - Inne ID są rozstrzygane przez `exec.approval.resolve`.
    - Discord nie wykonuje tu dodatkowego kroku fallback z exec do plugin; prefiks
      id decyduje, którą metodę bramy wywoła.

    Zatwierdzenia exec domyślnie wygasają po 30 minutach. Jeśli zatwierdzenia zawodzą z
    nieznanymi ID zatwierdzeń, sprawdź rozstrzyganie zatwierdzających, włączenie funkcji oraz
    czy dostarczony rodzaj id zatwierdzenia pasuje do oczekującego żądania.

    Powiązane dokumenty: [Exec approvals](/pl/tools/exec-approvals)

  </Accordion>
</AccordionGroup>

## Narzędzia i bramki działań

Działania wiadomości Discord obejmują wiadomości, administrację kanałami, moderację, obecność i działania na metadanych.

Podstawowe przykłady:

- wiadomości: `sendMessage`, `readMessages`, `editMessage`, `deleteMessage`, `threadReply`
- reakcje: `react`, `reactions`, `emojiList`
- moderacja: `timeout`, `kick`, `ban`
- obecność: `setPresence`

Bramki działań znajdują się pod `channels.discord.actions.*`.

Domyślne zachowanie bramek:

| Grupa działań                                                                                                                                                             | Domyślnie |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| reactions, messages, threads, pins, polls, search, memberInfo, roleInfo, channelInfo, channels, voiceStatus, events, stickers, emojiUploads, stickerUploads, permissions | włączone  |
| roles                                                                                                                                                                     | wyłączone |
| moderation                                                                                                                                                                | wyłączone |
| presence                                                                                                                                                                  | wyłączone |

## Components v2 UI

OpenClaw używa Discord components v2 do zatwierdzeń exec i znaczników między kontekstami. Działania wiadomości Discord mogą również przyjmować `components` dla niestandardowego interfejsu (zaawansowane; wymaga skonstruowania ładunku komponentu przez narzędzie discord), podczas gdy starsze `embeds` pozostają dostępne, ale nie są zalecane.

- `channels.discord.ui.components.accentColor` ustawia kolor akcentu używany przez kontenery komponentów Discord (hex).
- Ustawienie dla konta: `channels.discord.accounts.<id>.ui.components.accentColor`.
- `embeds` są ignorowane, gdy obecne są components v2.

Przykład:

```json5
{
  channels: {
    discord: {
      ui: {
        components: {
          accentColor: "#5865F2",
        },
      },
    },
  },
}
```

## Kanały głosowe

OpenClaw może dołączać do kanałów głosowych Discord na potrzeby rozmów w czasie rzeczywistym i ciągłych konwersacji. To jest oddzielne od załączników z wiadomościami głosowymi.

Wymagania:

- Włącz natywne polecenia (`commands.native` lub `channels.discord.commands.native`).
- Skonfiguruj `channels.discord.voice`.
- Bot potrzebuje uprawnień Connect + Speak w docelowym kanale głosowym.

Użyj polecenia natywnego tylko dla Discord `/vc join|leave|status`, aby sterować sesjami. Polecenie używa domyślnego agenta konta i podlega tym samym regułom list dozwolonych i zasad grupowych co inne polecenia Discord.

Przykład automatycznego dołączania:

```json5
{
  channels: {
    discord: {
      voice: {
        enabled: true,
        autoJoin: [
          {
            guildId: "123456789012345678",
            channelId: "234567890123456789",
          },
        ],
        daveEncryption: true,
        decryptionFailureTolerance: 24,
        tts: {
          provider: "openai",
          openai: { voice: "alloy" },
        },
      },
    },
  },
}
```

Uwagi:

- `voice.tts` nadpisuje `messages.tts` tylko dla odtwarzania głosowego.
- Tury transkrypcji głosowej wyprowadzają status właściciela z Discord `allowFrom` (lub `dm.allowFrom`); mówcy niebędący właścicielami nie mogą uzyskać dostępu do narzędzi tylko dla właściciela (na przykład `gateway` i `cron`).
- Voice jest domyślnie włączone; ustaw `channels.discord.voice.enabled=false`, aby je wyłączyć.
- `voice.daveEncryption` i `voice.decryptionFailureTolerance` są przekazywane do opcji dołączania `@discordjs/voice`.
- Domyślne wartości `@discordjs/voice` to `daveEncryption=true` i `decryptionFailureTolerance=24`, jeśli nie są ustawione.
- OpenClaw monitoruje także błędy odszyfrowywania odbioru i automatycznie odzyskuje działanie, opuszczając i ponownie dołączając do kanału głosowego po powtarzających się błędach w krótkim oknie czasu.
- Jeśli logi odbioru wielokrotnie pokazują `DecryptionFailed(UnencryptedWhenPassthroughDisabled)`, może to być błąd odbioru upstream `@discordjs/voice` śledzony w [discord.js #11419](https://github.com/discordjs/discord.js/issues/11419).

## Wiadomości głosowe

Wiadomości głosowe Discord pokazują podgląd fali dźwiękowej i wymagają dźwięku OGG/Opus oraz metadanych. OpenClaw generuje falę automatycznie, ale potrzebuje dostępnych `ffmpeg` i `ffprobe` na hoście bramy do sprawdzania i konwersji plików audio.

Wymagania i ograniczenia:

- Podaj **lokalną ścieżkę pliku** (URL-e są odrzucane).
- Pomiń treść tekstową (Discord nie pozwala na tekst + wiadomość głosową w tym samym ładunku).
- Akceptowany jest dowolny format audio; OpenClaw konwertuje do OGG/Opus, gdy jest to potrzebne.

Przykład:

```bash
message(action="send", channel="discord", target="channel:123", path="/path/to/audio.mp3", asVoice=true)
```

## Rozwiązywanie problemów

<AccordionGroup>
  <Accordion title="Użyto niedozwolonych intencji albo bot nie widzi wiadomości z serwera">

    - włącz Message Content Intent
    - włącz Server Members Intent, gdy zależysz od rozstrzygania użytkowników/członków
    - uruchom ponownie bramę po zmianie intencji

  </Accordion>

  <Accordion title="Wiadomości z serwera są nieoczekiwanie blokowane">

    - sprawdź `groupPolicy`
    - sprawdź listę dozwolonych serwerów w `channels.discord.guilds`
    - jeśli istnieje mapa `channels` dla serwera, dozwolone są tylko wymienione kanały
    - sprawdź działanie `requireMention` i wzorce wzmianki

    Przydatne sprawdzenia:

```bash
openclaw doctor
openclaw channels status --probe
openclaw logs --follow
```

  </Accordion>

  <Accordion title="Require mention false, ale nadal blokowane">
    Typowe przyczyny:

    - `groupPolicy="allowlist"` bez pasującej listy dozwolonych serwerów/kanałów
    - `requireMention` skonfigurowane w niewłaściwym miejscu (musi być pod `channels.discord.guilds` lub wpisem kanału)
    - nadawca zablokowany przez listę dozwolonych `users` serwera/kanału

  </Accordion>

  <Accordion title="Długotrwałe moduły obsługi przekraczają limit czasu albo duplikują odpowiedzi">

    Typowe logi:

    - `Listener DiscordMessageListener timed out after 30000ms for event MESSAGE_CREATE`
    - `Slow listener detected ...`
    - `discord inbound worker timed out after ...`

    Parametr budżetu listenera:

    - pojedyncze konto: `channels.discord.eventQueue.listenerTimeout`
    - wiele kont: `channels.discord.accounts.<accountId>.eventQueue.listenerTimeout`

    Parametr limitu czasu wykonania workera:

    - pojedyncze konto: `channels.discord.inboundWorker.runTimeoutMs`
    - wiele kont: `channels.discord.accounts.<accountId>.inboundWorker.runTimeoutMs`
    - domyślnie: `1800000` (30 minut); ustaw `0`, aby wyłączyć

    Zalecana baza:

```json5
{
  channels: {
    discord: {
      accounts: {
        default: {
          eventQueue: {
            listenerTimeout: 120000,
          },
          inboundWorker: {
            runTimeoutMs: 1800000,
          },
        },
      },
    },
  },
}
```

    Użyj `eventQueue.listenerTimeout` dla wolnej konfiguracji listenera, a `inboundWorker.runTimeoutMs`
    tylko wtedy, gdy chcesz osobnego bezpiecznika dla kolejkowanych tur agenta.

  </Accordion>

  <Accordion title="Niezgodności audytu uprawnień">
    Kontrole uprawnień `channels status --probe` działają tylko dla numerycznych ID kanałów.

    Jeśli używasz kluczy slug, dopasowanie w środowisku uruchomieniowym nadal może działać, ale test nie może w pełni zweryfikować uprawnień.

  </Accordion>

  <Accordion title="Problemy z DM i parowaniem">

    - DM wyłączone: `channels.discord.dm.enabled=false`
    - zasady DM wyłączone: `channels.discord.dmPolicy="disabled"` (starsza nazwa: `channels.discord.dm.policy`)
    - oczekiwanie na zatwierdzenie parowania w trybie `pairing`

  </Accordion>

  <Accordion title="Pętle bot-do-bota">
    Domyślnie wiadomości napisane przez boty są ignorowane.

    Jeśli ustawisz `channels.discord.allowBots=true`, użyj ścisłych reguł wzmianki i list dozwolonych, aby uniknąć zapętlenia.
    Preferuj `channels.discord.allowBots="mentions"`, aby akceptować tylko wiadomości od botów, które wspominają bota.

  </Accordion>

  <Accordion title="Głosowe STT wypada z DecryptionFailed(...)">

    - utrzymuj OpenClaw w aktualnej wersji (`openclaw update`), aby logika odzyskiwania odbioru głosowego Discord była obecna
    - potwierdź `channels.discord.voice.daveEncryption=true` (domyślnie)
    - zacznij od `channels.discord.voice.decryptionFailureTolerance=24` (domyślna wartość upstream) i dostrajaj tylko w razie potrzeby
    - obserwuj logi pod kątem:
      - `discord voice: DAVE decrypt failures detected`
      - `discord voice: repeated decrypt failures; attempting rejoin`
    - jeśli błędy utrzymują się po automatycznym ponownym dołączeniu, zbierz logi i porównaj z [discord.js #11419](https://github.com/discordjs/discord.js/issues/11419)

  </Accordion>
</AccordionGroup>

## Wskaźniki do dokumentacji referencyjnej konfiguracji

Główna dokumentacja referencyjna:

- [Configuration reference - Discord](/pl/gateway/configuration-reference#discord)

Najważniejsze pola Discord:

- uruchamianie/uwierzytelnianie: `enabled`, `token`, `accounts.*`, `allowBots`
- zasady: `groupPolicy`, `dm.*`, `guilds.*`, `guilds.*.channels.*`
- polecenia: `commands.native`, `commands.useAccessGroups`, `configWrites`, `slashCommand.*`
- kolejka zdarzeń: `eventQueue.listenerTimeout` (budżet listenera), `eventQueue.maxQueueSize`, `eventQueue.maxConcurrency`
- worker przychodzący: `inboundWorker.runTimeoutMs`
- odpowiedzi/historia: `replyToMode`, `historyLimit`, `dmHistoryLimit`, `dms.*.historyLimit`
- dostarczanie: `textChunkLimit`, `chunkMode`, `maxLinesPerMessage`
- strumieniowanie: `streaming` (starszy alias: `streamMode`), `draftChunk`, `blockStreaming`, `blockStreamingCoalesce`
- media/ponawianie: `mediaMaxMb`, `retry`
  - `mediaMaxMb` ogranicza wychodzące przesyłanie do Discord (domyślnie: `100MB`)
- działania: `actions.*`
- obecność: `activity`, `status`, `activityType`, `activityUrl`
- UI: `ui.components.accentColor`
- funkcje: `threadBindings`, najwyższego poziomu `bindings[]` (`type: "acp"`), `pluralkit`, `execApprovals`, `intents`, `agentComponents`, `heartbeat`, `responsePrefix`

## Bezpieczeństwo i operacje

- Traktuj tokeny bota jak sekrety (w środowiskach nadzorowanych preferowany jest `DISCORD_BOT_TOKEN`).
- Nadawaj uprawnienia Discord zgodnie z zasadą najmniejszych uprawnień.
- Jeśli wdrożenie/stan poleceń jest nieaktualny, uruchom ponownie bramę i sprawdź ponownie przez `openclaw channels status --probe`.

## Powiązane

- [Parowanie](/pl/channels/pairing)
- [Grupy](/pl/channels/groups)
- [Routing kanałów](/pl/channels/channel-routing)
- [Bezpieczeństwo](/pl/gateway/security)
- [Routing wielu agentów](/pl/concepts/multi-agent)
- [Rozwiązywanie problemów](/pl/channels/troubleshooting)
- [Polecenia slash](/pl/tools/slash-commands)
