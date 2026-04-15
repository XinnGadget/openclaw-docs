---
read_when:
    - Potrzebujesz dokładnej semantyki pól konfiguracji lub wartości domyślnych
    - Weryfikujesz bloki konfiguracji kanałów, modeli, Gateway lub narzędzi
summary: Odwołanie do konfiguracji Gateway dla podstawowych kluczy OpenClaw, wartości domyślnych i linków do dedykowanych odwołań podsystemów
title: Odwołanie do konfiguracji
x-i18n:
    generated_at: "2026-04-15T14:40:34Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7a4da3b41d0304389bd6359aac1185c231e529781b607656ab352f8a8104bdba
    source_path: gateway/configuration-reference.md
    workflow: 15
---

# Odwołanie do konfiguracji

Podstawowe odwołanie do konfiguracji `~/.openclaw/openclaw.json`. Aby zobaczyć omówienie zorientowane na zadania, przejdź do [Configuration](/pl/gateway/configuration).

Ta strona obejmuje główne powierzchnie konfiguracji OpenClaw i odsyła dalej, gdy dany podsystem ma własne, bardziej szczegółowe odwołanie. **Nie** próbuje umieszczać na jednej stronie każdego katalogu poleceń należącego do kanału/Plugin ani każdego szczegółowego pokrętła pamięci/QMD.

Źródło prawdy w kodzie:

- `openclaw config schema` wypisuje aktualny schemat JSON używany do walidacji i interfejsu Control UI, z dołączonymi metadanymi bundled/plugin/channel, gdy są dostępne
- `config.schema.lookup` zwraca jeden węzeł schematu ograniczony do ścieżki dla narzędzi do szczegółowej eksploracji
- `pnpm config:docs:check` / `pnpm config:docs:gen` walidują skrót bazowy dokumentacji konfiguracji względem bieżącej powierzchni schematu

Dedykowane szczegółowe odwołania:

- [Odwołanie do konfiguracji pamięci](/pl/reference/memory-config) dla `agents.defaults.memorySearch.*`, `memory.qmd.*`, `memory.citations` oraz konfiguracji Dreaming w `plugins.entries.memory-core.config.dreaming`
- [Slash Commands](/pl/tools/slash-commands) dla bieżącego katalogu poleceń wbudowanych + bundled
- strony właścicieli kanałów/Pluginów dla powierzchni poleceń specyficznych dla kanałów

Format konfiguracji to **JSON5** (dozwolone komentarze i końcowe przecinki). Wszystkie pola są opcjonalne — OpenClaw używa bezpiecznych wartości domyślnych, gdy zostaną pominięte.

---

## Kanały

Każdy kanał uruchamia się automatycznie, gdy istnieje jego sekcja konfiguracji (chyba że `enabled: false`).

### Dostęp do DM i grup

Wszystkie kanały obsługują zasady DM i zasady grup:

| Zasada DM            | Zachowanie                                                     |
| -------------------- | -------------------------------------------------------------- |
| `pairing` (domyślna) | Nieznani nadawcy otrzymują jednorazowy kod parowania; właściciel musi zatwierdzić |
| `allowlist`          | Tylko nadawcy z `allowFrom` (lub sparowanego magazynu dozwolonych) |
| `open`               | Zezwalaj na wszystkie przychodzące DM (wymaga `allowFrom: ["*"]`) |
| `disabled`           | Ignoruj wszystkie przychodzące DM                              |

| Zasada grup          | Zachowanie                                           |
| -------------------- | ---------------------------------------------------- |
| `allowlist` (domyślna) | Tylko grupy pasujące do skonfigurowanej listy dozwolonych |
| `open`               | Pomijaj listy dozwolonych grup (nadal obowiązuje ograniczanie przez wzmianki) |
| `disabled`           | Blokuj wszystkie wiadomości grupowe/pokojów          |

<Note>
`channels.defaults.groupPolicy` ustawia wartość domyślną, gdy `groupPolicy` dostawcy nie jest ustawione.
Kody parowania wygasają po 1 godzinie. Oczekujące żądania parowania DM są ograniczone do **3 na kanał**.
Jeśli blok dostawcy jest całkowicie nieobecny (`channels.<provider>` nie istnieje), zasada grup w czasie działania wraca do `allowlist` (fail-closed) z ostrzeżeniem przy uruchomieniu.
</Note>

### Nadpisania modelu dla kanałów

Użyj `channels.modelByChannel`, aby przypiąć określone identyfikatory kanałów do modelu. Wartości akceptują `provider/model` lub skonfigurowane aliasy modeli. Mapowanie kanałów jest stosowane, gdy sesja nie ma już nadpisania modelu (na przykład ustawionego przez `/model`).

```json5
{
  channels: {
    modelByChannel: {
      discord: {
        "123456789012345678": "anthropic/claude-opus-4-6",
      },
      slack: {
        C1234567890: "openai/gpt-4.1",
      },
      telegram: {
        "-1001234567890": "openai/gpt-4.1-mini",
        "-1001234567890:topic:99": "anthropic/claude-sonnet-4-6",
      },
    },
  },
}
```

### Wartości domyślne kanałów i Heartbeat

Użyj `channels.defaults` dla współdzielonych zasad grup i zachowania Heartbeat między dostawcami:

```json5
{
  channels: {
    defaults: {
      groupPolicy: "allowlist", // open | allowlist | disabled
      contextVisibility: "all", // all | allowlist | allowlist_quote
      heartbeat: {
        showOk: false,
        showAlerts: true,
        useIndicator: true,
      },
    },
  },
}
```

- `channels.defaults.groupPolicy`: zapasowa zasada grup, gdy `groupPolicy` na poziomie dostawcy nie jest ustawione.
- `channels.defaults.contextVisibility`: domyślny tryb widoczności dodatkowego kontekstu dla wszystkich kanałów. Wartości: `all` (domyślna, uwzględnia cały cytowany/wątkowy/historyczny kontekst), `allowlist` (uwzględnia tylko kontekst od nadawców z listy dozwolonych), `allowlist_quote` (jak allowlist, ale zachowuje jawny kontekst cytatu/odpowiedzi). Nadpisanie per kanał: `channels.<channel>.contextVisibility`.
- `channels.defaults.heartbeat.showOk`: uwzględniaj zdrowe statusy kanałów w wyjściu Heartbeat.
- `channels.defaults.heartbeat.showAlerts`: uwzględniaj statusy pogorszone/błędów w wyjściu Heartbeat.
- `channels.defaults.heartbeat.useIndicator`: renderuj zwarte wyjście Heartbeat w stylu wskaźnika.

### WhatsApp

WhatsApp działa przez kanał web Gateway (`Baileys Web`). Uruchamia się automatycznie, gdy istnieje połączona sesja.

```json5
{
  channels: {
    whatsapp: {
      dmPolicy: "pairing", // pairing | allowlist | open | disabled
      allowFrom: ["+15555550123", "+447700900123"],
      textChunkLimit: 4000,
      chunkMode: "length", // length | newline
      mediaMaxMb: 50,
      sendReadReceipts: true, // niebieskie znaczniki (false w trybie czatu do siebie)
      groups: {
        "*": { requireMention: true },
      },
      groupPolicy: "allowlist",
      groupAllowFrom: ["+15551234567"],
    },
  },
  web: {
    enabled: true,
    heartbeatSeconds: 60,
    reconnect: {
      initialMs: 2000,
      maxMs: 120000,
      factor: 1.4,
      jitter: 0.2,
      maxAttempts: 0,
    },
  },
}
```

<Accordion title="Wiele kont WhatsApp">

```json5
{
  channels: {
    whatsapp: {
      accounts: {
        default: {},
        personal: {},
        biz: {
          // authDir: "~/.openclaw/credentials/whatsapp/biz",
        },
      },
    },
  },
}
```

- Polecenia wychodzące domyślnie używają konta `default`, jeśli istnieje; w przeciwnym razie pierwszego skonfigurowanego identyfikatora konta (posortowanego).
- Opcjonalne `channels.whatsapp.defaultAccount` nadpisuje ten zapasowy wybór domyślnego konta, gdy pasuje do skonfigurowanego identyfikatora konta.
- Starszy katalog uwierzytelniania Baileys dla jednego konta jest migrowany przez `openclaw doctor` do `whatsapp/default`.
- Nadpisania per konto: `channels.whatsapp.accounts.<id>.sendReadReceipts`, `channels.whatsapp.accounts.<id>.dmPolicy`, `channels.whatsapp.accounts.<id>.allowFrom`.

</Accordion>

### Telegram

```json5
{
  channels: {
    telegram: {
      enabled: true,
      botToken: "your-bot-token",
      dmPolicy: "pairing",
      allowFrom: ["tg:123456789"],
      groups: {
        "*": { requireMention: true },
        "-1001234567890": {
          allowFrom: ["@admin"],
          systemPrompt: "Keep answers brief.",
          topics: {
            "99": {
              requireMention: false,
              skills: ["search"],
              systemPrompt: "Stay on topic.",
            },
          },
        },
      },
      customCommands: [
        { command: "backup", description: "Git backup" },
        { command: "generate", description: "Create an image" },
      ],
      historyLimit: 50,
      replyToMode: "first", // off | first | all | batched
      linkPreview: true,
      streaming: "partial", // off | partial | block | progress (default: off; opt in explicitly to avoid preview-edit rate limits)
      actions: { reactions: true, sendMessage: true },
      reactionNotifications: "own", // off | own | all
      mediaMaxMb: 100,
      retry: {
        attempts: 3,
        minDelayMs: 400,
        maxDelayMs: 30000,
        jitter: 0.1,
      },
      network: {
        autoSelectFamily: true,
        dnsResultOrder: "ipv4first",
      },
      proxy: "socks5://localhost:9050",
      webhookUrl: "https://example.com/telegram-webhook",
      webhookSecret: "secret",
      webhookPath: "/telegram-webhook",
    },
  },
}
```

- Token bota: `channels.telegram.botToken` lub `channels.telegram.tokenFile` (tylko zwykły plik; dowiązania symboliczne są odrzucane), z `TELEGRAM_BOT_TOKEN` jako zapasową wartością dla konta domyślnego.
- Opcjonalne `channels.telegram.defaultAccount` nadpisuje wybór domyślnego konta, gdy pasuje do skonfigurowanego identyfikatora konta.
- W konfiguracjach wielokontowych (2+ identyfikatory kont) ustaw jawnie konto domyślne (`channels.telegram.defaultAccount` lub `channels.telegram.accounts.default`), aby uniknąć routingu zapasowego; `openclaw doctor` ostrzega, gdy tego brakuje lub jest nieprawidłowe.
- `configWrites: false` blokuje zapisy konfiguracji inicjowane z Telegrama (migracje identyfikatorów supergrup, `/config set|unset`).
- Wpisy najwyższego poziomu `bindings[]` z `type: "acp"` konfigurują trwałe powiązania ACP dla tematów forów (użyj kanonicznego `chatId:topic:topicId` w `match.peer.id`). Semantyka pól jest współdzielona w [ACP Agents](/pl/tools/acp-agents#channel-specific-settings).
- Podglądy strumieni w Telegramie używają `sendMessage` + `editMessageText` (działa w czatach bezpośrednich i grupowych).
- Zasady ponawiania: zobacz [Retry policy](/pl/concepts/retry).

### Discord

```json5
{
  channels: {
    discord: {
      enabled: true,
      token: "your-bot-token",
      mediaMaxMb: 100,
      allowBots: false,
      actions: {
        reactions: true,
        stickers: true,
        polls: true,
        permissions: true,
        messages: true,
        threads: true,
        pins: true,
        search: true,
        memberInfo: true,
        roleInfo: true,
        roles: false,
        channelInfo: true,
        voiceStatus: true,
        events: true,
        moderation: false,
      },
      replyToMode: "off", // off | first | all | batched
      dmPolicy: "pairing",
      allowFrom: ["1234567890", "123456789012345678"],
      dm: { enabled: true, groupEnabled: false, groupChannels: ["openclaw-dm"] },
      guilds: {
        "123456789012345678": {
          slug: "friends-of-openclaw",
          requireMention: false,
          ignoreOtherMentions: true,
          reactionNotifications: "own",
          users: ["987654321098765432"],
          channels: {
            general: { allow: true },
            help: {
              allow: true,
              requireMention: true,
              users: ["987654321098765432"],
              skills: ["docs"],
              systemPrompt: "Short answers only.",
            },
          },
        },
      },
      historyLimit: 20,
      textChunkLimit: 2000,
      chunkMode: "length", // length | newline
      streaming: "off", // off | partial | block | progress (progress maps to partial on Discord)
      maxLinesPerMessage: 17,
      ui: {
        components: {
          accentColor: "#5865F2",
        },
      },
      threadBindings: {
        enabled: true,
        idleHours: 24,
        maxAgeHours: 0,
        spawnSubagentSessions: false, // opt-in for sessions_spawn({ thread: true })
      },
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
      execApprovals: {
        enabled: "auto", // true | false | "auto"
        approvers: ["987654321098765432"],
        agentFilter: ["default"],
        sessionFilter: ["discord:"],
        target: "dm", // dm | channel | both
        cleanupAfterResolve: false,
      },
      retry: {
        attempts: 3,
        minDelayMs: 500,
        maxDelayMs: 30000,
        jitter: 0.1,
      },
    },
  },
}
```

- Token: `channels.discord.token`, z `DISCORD_BOT_TOKEN` jako wartością zapasową dla konta domyślnego.
- Bezpośrednie wywołania wychodzące, które podają jawny `token` Discorda, używają tego tokena do wywołania; ustawienia ponawiania/zasad konta nadal pochodzą z wybranego konta w aktywnej migawce runtime.
- Opcjonalne `channels.discord.defaultAccount` nadpisuje wybór konta domyślnego, gdy pasuje do skonfigurowanego identyfikatora konta.
- Używaj `user:<id>` (DM) lub `channel:<id>` (kanał serwera) jako celów dostarczenia; same numeryczne identyfikatory są odrzucane.
- Slugi serwerów są pisane małymi literami, a spacje są zastępowane przez `-`; klucze kanałów używają nazwy w postaci sluga (bez `#`). Preferuj identyfikatory serwerów.
- Wiadomości napisane przez bota są domyślnie ignorowane. `allowBots: true` je włącza; użyj `allowBots: "mentions"`, aby akceptować tylko wiadomości botów, które wspominają bota (własne wiadomości nadal są filtrowane).
- `channels.discord.guilds.<id>.ignoreOtherMentions` (oraz nadpisania kanałów) odrzuca wiadomości, które wspominają innego użytkownika lub rolę, ale nie bota (z wyłączeniem @everyone/@here).
- `maxLinesPerMessage` (domyślnie 17) dzieli wysokie wiadomości nawet wtedy, gdy mają mniej niż 2000 znaków.
- `channels.discord.threadBindings` kontroluje routowanie powiązane z wątkami Discorda:
  - `enabled`: nadpisanie Discorda dla funkcji sesji powiązanych z wątkami (`/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age` oraz dostarczanie/routowanie powiązane)
  - `idleHours`: nadpisanie Discorda dla automatycznego odpinania po bezczynności w godzinach (`0` wyłącza)
  - `maxAgeHours`: nadpisanie Discorda dla twardego maksymalnego wieku w godzinach (`0` wyłącza)
  - `spawnSubagentSessions`: przełącznik opt-in dla automatycznego tworzenia/powiązywania wątków przez `sessions_spawn({ thread: true })`
- Wpisy najwyższego poziomu `bindings[]` z `type: "acp"` konfigurują trwałe powiązania ACP dla kanałów i wątków (użyj identyfikatora kanału/wątku w `match.peer.id`). Semantyka pól jest współdzielona w [ACP Agents](/pl/tools/acp-agents#channel-specific-settings).
- `channels.discord.ui.components.accentColor` ustawia kolor akcentu dla kontenerów Discord components v2.
- `channels.discord.voice` włącza rozmowy w kanałach głosowych Discorda oraz opcjonalne automatyczne dołączanie i nadpisania TTS.
- `channels.discord.voice.daveEncryption` i `channels.discord.voice.decryptionFailureTolerance` są przekazywane do opcji DAVE `@discordjs/voice` (domyślnie `true` i `24`).
- OpenClaw dodatkowo próbuje odzyskać odbiór głosu przez opuszczenie i ponowne dołączenie do sesji głosowej po powtarzających się błędach deszyfrowania.
- `channels.discord.streaming` to kanoniczny klucz trybu strumieniowania. Starsze wartości `streamMode` i logiczne `streaming` są automatycznie migrowane.
- `channels.discord.autoPresence` mapuje dostępność runtime na obecność bota (healthy => online, degraded => idle, exhausted => dnd) i pozwala na opcjonalne nadpisania tekstu statusu.
- `channels.discord.dangerouslyAllowNameMatching` ponownie włącza dopasowywanie po zmiennej nazwie/tagu (tryb kompatybilności break-glass).
- `channels.discord.execApprovals`: natywne dla Discorda dostarczanie zatwierdzeń exec i autoryzacja zatwierdzających.
  - `enabled`: `true`, `false` lub `"auto"` (domyślnie). W trybie auto zatwierdzenia exec aktywują się, gdy zatwierdzający mogą zostać rozwiązani z `approvers` lub `commands.ownerAllowFrom`.
  - `approvers`: identyfikatory użytkowników Discorda uprawnionych do zatwierdzania żądań exec. Gdy pominięte, używana jest wartość zapasowa z `commands.ownerAllowFrom`.
  - `agentFilter`: opcjonalna lista dozwolonych identyfikatorów agentów. Pomiń, aby przekazywać zatwierdzenia dla wszystkich agentów.
  - `sessionFilter`: opcjonalne wzorce kluczy sesji (podciąg lub regex).
  - `target`: gdzie wysyłać monity o zatwierdzenie. `"dm"` (domyślnie) wysyła do DM zatwierdzającego, `"channel"` wysyła do kanału źródłowego, `"both"` wysyła do obu. Gdy target obejmuje `"channel"`, przyciski mogą być używane tylko przez rozwiązanych zatwierdzających.
  - `cleanupAfterResolve`: gdy `true`, usuwa DM zatwierdzeń po zatwierdzeniu, odrzuceniu lub przekroczeniu limitu czasu.

**Tryby powiadomień o reakcjach:** `off` (brak), `own` (wiadomości bota, domyślnie), `all` (wszystkie wiadomości), `allowlist` (z `guilds.<id>.users` dla wszystkich wiadomości).

### Google Chat

```json5
{
  channels: {
    googlechat: {
      enabled: true,
      serviceAccountFile: "/path/to/service-account.json",
      audienceType: "app-url", // app-url | project-number
      audience: "https://gateway.example.com/googlechat",
      webhookPath: "/googlechat",
      botUser: "users/1234567890",
      dm: {
        enabled: true,
        policy: "pairing",
        allowFrom: ["users/1234567890"],
      },
      groupPolicy: "allowlist",
      groups: {
        "spaces/AAAA": { allow: true, requireMention: true },
      },
      actions: { reactions: true },
      typingIndicator: "message",
      mediaMaxMb: 20,
    },
  },
}
```

- JSON konta usługi: osadzone (`serviceAccount`) lub oparte na pliku (`serviceAccountFile`).
- SecretRef konta usługi jest również obsługiwany (`serviceAccountRef`).
- Zapasowe wartości środowiskowe: `GOOGLE_CHAT_SERVICE_ACCOUNT` lub `GOOGLE_CHAT_SERVICE_ACCOUNT_FILE`.
- Używaj `spaces/<spaceId>` lub `users/<userId>` jako celów dostarczenia.
- `channels.googlechat.dangerouslyAllowNameMatching` ponownie włącza dopasowywanie po zmiennym principalu e-mail (tryb kompatybilności break-glass).

### Slack

```json5
{
  channels: {
    slack: {
      enabled: true,
      botToken: "xoxb-...",
      appToken: "xapp-...",
      dmPolicy: "pairing",
      allowFrom: ["U123", "U456", "*"],
      dm: { enabled: true, groupEnabled: false, groupChannels: ["G123"] },
      channels: {
        C123: { allow: true, requireMention: true, allowBots: false },
        "#general": {
          allow: true,
          requireMention: true,
          allowBots: false,
          users: ["U123"],
          skills: ["docs"],
          systemPrompt: "Short answers only.",
        },
      },
      historyLimit: 50,
      allowBots: false,
      reactionNotifications: "own",
      reactionAllowlist: ["U123"],
      replyToMode: "off", // off | first | all | batched
      thread: {
        historyScope: "thread", // thread | channel
        inheritParent: false,
      },
      actions: {
        reactions: true,
        messages: true,
        pins: true,
        memberInfo: true,
        emojiList: true,
      },
      slashCommand: {
        enabled: true,
        name: "openclaw",
        sessionPrefix: "slack:slash",
        ephemeral: true,
      },
      typingReaction: "hourglass_flowing_sand",
      textChunkLimit: 4000,
      chunkMode: "length",
      streaming: {
        mode: "partial", // off | partial | block | progress
        nativeTransport: true, // use Slack native streaming API when mode=partial
      },
      mediaMaxMb: 20,
      execApprovals: {
        enabled: "auto", // true | false | "auto"
        approvers: ["U123"],
        agentFilter: ["default"],
        sessionFilter: ["slack:"],
        target: "dm", // dm | channel | both
      },
    },
  },
}
```

- **Tryb Socket** wymaga zarówno `botToken`, jak i `appToken` (`SLACK_BOT_TOKEN` + `SLACK_APP_TOKEN` jako zapasowe zmienne środowiskowe dla konta domyślnego).
- **Tryb HTTP** wymaga `botToken` oraz `signingSecret` (na poziomie głównym lub per konto).
- `botToken`, `appToken`, `signingSecret` i `userToken` akceptują zwykłe
  ciągi znaków albo obiekty SecretRef.
- Migawki kont Slacka udostępniają pola źródła/statusu per poświadczenie, takie jak
  `botTokenSource`, `botTokenStatus`, `appTokenStatus`, a w trybie HTTP także
  `signingSecretStatus`. `configured_unavailable` oznacza, że konto jest
  skonfigurowane przez SecretRef, ale bieżąca ścieżka polecenia/runtime nie mogła
  rozwiązać wartości sekretu.
- `configWrites: false` blokuje zapisy konfiguracji inicjowane ze Slacka.
- Opcjonalne `channels.slack.defaultAccount` nadpisuje wybór konta domyślnego, gdy pasuje do skonfigurowanego identyfikatora konta.
- `channels.slack.streaming.mode` to kanoniczny klucz trybu strumieniowania Slacka. `channels.slack.streaming.nativeTransport` kontroluje natywny transport strumieniowania Slacka. Starsze wartości `streamMode`, logiczne `streaming` i `nativeStreaming` są automatycznie migrowane.
- Używaj `user:<id>` (DM) lub `channel:<id>` jako celów dostarczenia.

**Tryby powiadomień o reakcjach:** `off`, `own` (domyślnie), `all`, `allowlist` (z `reactionAllowlist`).

**Izolacja sesji wątków:** `thread.historyScope` jest per wątek (domyślnie) lub współdzielone w obrębie kanału. `thread.inheritParent` kopiuje transkrypt kanału nadrzędnego do nowych wątków.

- Natywne strumieniowanie Slacka oraz status wątku Slacka w stylu asystenta „is typing...” wymagają celu odpowiedzi w wątku. DM najwyższego poziomu domyślnie pozostają poza wątkiem, więc używają `typingReaction` lub normalnego dostarczania zamiast podglądu w stylu wątku.
- `typingReaction` dodaje tymczasową reakcję do przychodzącej wiadomości Slacka podczas tworzenia odpowiedzi, a następnie usuwa ją po zakończeniu. Użyj skrótu emoji Slacka, takiego jak `"hourglass_flowing_sand"`.
- `channels.slack.execApprovals`: natywne dla Slacka dostarczanie zatwierdzeń exec i autoryzacja zatwierdzających. Ten sam schemat co w Discordzie: `enabled` (`true`/`false`/`"auto"`), `approvers` (identyfikatory użytkowników Slacka), `agentFilter`, `sessionFilter` oraz `target` (`"dm"`, `"channel"` lub `"both"`).

| Grupa akcji | Domyślnie | Uwagi                     |
| ----------- | --------- | ------------------------- |
| reactions   | włączone  | Reagowanie + lista reakcji |
| messages    | włączone  | Odczyt/wysyłanie/edycja/usuwanie |
| pins        | włączone  | Przypinanie/odpinanie/lista |
| memberInfo  | włączone  | Informacje o członku      |
| emojiList   | włączone  | Lista niestandardowych emoji |

### Mattermost

Mattermost jest dostarczany jako Plugin: `openclaw plugins install @openclaw/mattermost`.

```json5
{
  channels: {
    mattermost: {
      enabled: true,
      botToken: "mm-token",
      baseUrl: "https://chat.example.com",
      dmPolicy: "pairing",
      chatmode: "oncall", // oncall | onmessage | onchar
      oncharPrefixes: [">", "!"],
      groups: {
        "*": { requireMention: true },
        "team-channel-id": { requireMention: false },
      },
      commands: {
        native: true, // opt-in
        nativeSkills: true,
        callbackPath: "/api/channels/mattermost/command",
        // Optional explicit URL for reverse-proxy/public deployments
        callbackUrl: "https://gateway.example.com/api/channels/mattermost/command",
      },
      textChunkLimit: 4000,
      chunkMode: "length",
    },
  },
}
```

Tryby czatu: `oncall` (odpowiada na wzmiankę @, domyślnie), `onmessage` (na każdą wiadomość), `onchar` (wiadomości zaczynające się od prefiksu wyzwalacza).

Gdy natywne polecenia Mattermost są włączone:

- `commands.callbackPath` musi być ścieżką (na przykład `/api/channels/mattermost/command`), a nie pełnym adresem URL.
- `commands.callbackUrl` musi wskazywać punkt końcowy Gateway OpenClaw i być osiągalny z serwera Mattermost.
- Natywne wywołania slash callback są uwierzytelniane za pomocą tokenów per polecenie zwracanych
  przez Mattermost podczas rejestracji polecenia slash. Jeśli rejestracja się nie powiedzie lub nie
  zostaną aktywowane żadne polecenia, OpenClaw odrzuca callbacki z komunikatem
  `Unauthorized: invalid command token.`
- Dla prywatnych/tailnet/wewnętrznych hostów callbacków Mattermost może wymagać, aby
  `ServiceSettings.AllowedUntrustedInternalConnections` zawierało host/domenę callbacku.
  Używaj wartości host/domena, a nie pełnych adresów URL.
- `channels.mattermost.configWrites`: zezwalaj lub zabraniaj zapisów konfiguracji inicjowanych z Mattermost.
- `channels.mattermost.requireMention`: wymagaj `@mention` przed odpowiedzią na kanałach.
- `channels.mattermost.groups.<channelId>.requireMention`: nadpisanie ograniczania przez wzmianki per kanał (`"*"` dla wartości domyślnej).
- Opcjonalne `channels.mattermost.defaultAccount` nadpisuje wybór konta domyślnego, gdy pasuje do skonfigurowanego identyfikatora konta.

### Signal

```json5
{
  channels: {
    signal: {
      enabled: true,
      account: "+15555550123", // opcjonalne powiązanie konta
      dmPolicy: "pairing",
      allowFrom: ["+15551234567", "uuid:123e4567-e89b-12d3-a456-426614174000"],
      configWrites: true,
      reactionNotifications: "own", // off | own | all | allowlist
      reactionAllowlist: ["+15551234567", "uuid:123e4567-e89b-12d3-a456-426614174000"],
      historyLimit: 50,
    },
  },
}
```

**Tryby powiadomień o reakcjach:** `off`, `own` (domyślnie), `all`, `allowlist` (z `reactionAllowlist`).

- `channels.signal.account`: przypnij uruchamianie kanału do określonej tożsamości konta Signal.
- `channels.signal.configWrites`: zezwalaj lub zabraniaj zapisów konfiguracji inicjowanych z Signal.
- Opcjonalne `channels.signal.defaultAccount` nadpisuje wybór konta domyślnego, gdy pasuje do skonfigurowanego identyfikatora konta.

### BlueBubbles

BlueBubbles to zalecana ścieżka iMessage (oparta na Pluginie, konfigurowana w `channels.bluebubbles`).

```json5
{
  channels: {
    bluebubbles: {
      enabled: true,
      dmPolicy: "pairing",
      // serverUrl, password, webhookPath, group controls, and advanced actions:
      // see /channels/bluebubbles
    },
  },
}
```

- Uwzględnione tutaj podstawowe ścieżki kluczy: `channels.bluebubbles`, `channels.bluebubbles.dmPolicy`.
- Opcjonalne `channels.bluebubbles.defaultAccount` nadpisuje wybór konta domyślnego, gdy pasuje do skonfigurowanego identyfikatora konta.
- Wpisy najwyższego poziomu `bindings[]` z `type: "acp"` mogą wiązać konwersacje BlueBubbles z trwałymi sesjami ACP. Użyj uchwytu BlueBubbles lub ciągu docelowego (`chat_id:*`, `chat_guid:*`, `chat_identifier:*`) w `match.peer.id`. Współdzielona semantyka pól: [ACP Agents](/pl/tools/acp-agents#channel-specific-settings).
- Pełna konfiguracja kanału BlueBubbles jest udokumentowana w [BlueBubbles](/pl/channels/bluebubbles).

### iMessage

OpenClaw uruchamia `imsg rpc` (JSON-RPC przez stdio). Nie jest wymagany demon ani port.

```json5
{
  channels: {
    imessage: {
      enabled: true,
      cliPath: "imsg",
      dbPath: "~/Library/Messages/chat.db",
      remoteHost: "user@gateway-host",
      dmPolicy: "pairing",
      allowFrom: ["+15555550123", "user@example.com", "chat_id:123"],
      historyLimit: 50,
      includeAttachments: false,
      attachmentRoots: ["/Users/*/Library/Messages/Attachments"],
      remoteAttachmentRoots: ["/Users/*/Library/Messages/Attachments"],
      mediaMaxMb: 16,
      service: "auto",
      region: "US",
    },
  },
}
```

- Opcjonalne `channels.imessage.defaultAccount` nadpisuje wybór konta domyślnego, gdy pasuje do skonfigurowanego identyfikatora konta.

- Wymaga Full Disk Access do bazy danych Messages.
- Preferuj cele `chat_id:<id>`. Użyj `imsg chats --limit 20`, aby wyświetlić listę czatów.
- `cliPath` może wskazywać na wrapper SSH; ustaw `remoteHost` (`host` lub `user@host`) do pobierania załączników przez SCP.
- `attachmentRoots` i `remoteAttachmentRoots` ograniczają ścieżki przychodzących załączników (domyślnie: `/Users/*/Library/Messages/Attachments`).
- SCP używa ścisłego sprawdzania klucza hosta, więc upewnij się, że klucz hosta przekaźnika już istnieje w `~/.ssh/known_hosts`.
- `channels.imessage.configWrites`: zezwalaj lub zabraniaj zapisów konfiguracji inicjowanych z iMessage.
- Wpisy najwyższego poziomu `bindings[]` z `type: "acp"` mogą wiązać konwersacje iMessage z trwałymi sesjami ACP. Użyj znormalizowanego uchwytu lub jawnego celu czatu (`chat_id:*`, `chat_guid:*`, `chat_identifier:*`) w `match.peer.id`. Współdzielona semantyka pól: [ACP Agents](/pl/tools/acp-agents#channel-specific-settings).

<Accordion title="Przykład wrappera SSH dla iMessage">

```bash
#!/usr/bin/env bash
exec ssh -T gateway-host imsg "$@"
```

</Accordion>

### Matrix

Matrix jest obsługiwany przez rozszerzenie i konfigurowany w `channels.matrix`.

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_bot_xxx",
      proxy: "http://127.0.0.1:7890",
      encryption: true,
      initialSyncLimit: 20,
      defaultAccount: "ops",
      accounts: {
        ops: {
          name: "Ops",
          userId: "@ops:example.org",
          accessToken: "syt_ops_xxx",
        },
        alerts: {
          userId: "@alerts:example.org",
          password: "secret",
          proxy: "http://127.0.0.1:7891",
        },
      },
    },
  },
}
```

- Uwierzytelnianie tokenem używa `accessToken`; uwierzytelnianie hasłem używa `userId` + `password`.
- `channels.matrix.proxy` kieruje ruch HTTP Matrix przez jawny serwer proxy HTTP(S). Nazwane konta mogą go nadpisać przez `channels.matrix.accounts.<id>.proxy`.
- `channels.matrix.network.dangerouslyAllowPrivateNetwork` zezwala na prywatne/wewnętrzne homeservery. `proxy` i ten opt-in sieciowy są niezależnymi mechanizmami sterowania.
- `channels.matrix.defaultAccount` wybiera preferowane konto w konfiguracjach wielokontowych.
- `channels.matrix.autoJoin` ma domyślnie wartość `off`, więc zaproszone pokoje i nowe zaproszenia w stylu DM są ignorowane, dopóki nie ustawisz `autoJoin: "allowlist"` z `autoJoinAllowlist` albo `autoJoin: "always"`.
- `channels.matrix.execApprovals`: natywne dla Matrix dostarczanie zatwierdzeń exec i autoryzacja zatwierdzających.
  - `enabled`: `true`, `false` lub `"auto"` (domyślnie). W trybie auto zatwierdzenia exec aktywują się, gdy zatwierdzający mogą zostać rozwiązani z `approvers` lub `commands.ownerAllowFrom`.
  - `approvers`: identyfikatory użytkowników Matrix (np. `@owner:example.org`) uprawnionych do zatwierdzania żądań exec.
  - `agentFilter`: opcjonalna lista dozwolonych identyfikatorów agentów. Pomiń, aby przekazywać zatwierdzenia dla wszystkich agentów.
  - `sessionFilter`: opcjonalne wzorce kluczy sesji (podciąg lub regex).
  - `target`: gdzie wysyłać monity o zatwierdzenie. `"dm"` (domyślnie), `"channel"` (pokój źródłowy) lub `"both"`.
  - Nadpisania per konto: `channels.matrix.accounts.<id>.execApprovals`.
- `channels.matrix.dm.sessionScope` kontroluje, jak DM Matrix są grupowane w sesje: `per-user` (domyślnie) współdzieli według routowanego peera, a `per-room` izoluje każdy pokój DM.
- Sondy statusu Matrix i wyszukiwania katalogu na żywo używają tej samej polityki proxy co ruch runtime.
- Pełna konfiguracja Matrix, reguły kierowania i przykłady konfiguracji są udokumentowane w [Matrix](/pl/channels/matrix).

### Microsoft Teams

Microsoft Teams jest obsługiwany przez rozszerzenie i konfigurowany w `channels.msteams`.

```json5
{
  channels: {
    msteams: {
      enabled: true,
      configWrites: true,
      // appId, appPassword, tenantId, webhook, team/channel policies:
      // see /channels/msteams
    },
  },
}
```

- Uwzględnione tutaj podstawowe ścieżki kluczy: `channels.msteams`, `channels.msteams.configWrites`.
- Pełna konfiguracja Teams (poświadczenia, Webhook, zasady DM/grup, nadpisania per zespół/per kanał) jest udokumentowana w [Microsoft Teams](/pl/channels/msteams).

### IRC

IRC jest obsługiwany przez rozszerzenie i konfigurowany w `channels.irc`.

```json5
{
  channels: {
    irc: {
      enabled: true,
      dmPolicy: "pairing",
      configWrites: true,
      nickserv: {
        enabled: true,
        service: "NickServ",
        password: "${IRC_NICKSERV_PASSWORD}",
        register: false,
        registerEmail: "bot@example.com",
      },
    },
  },
}
```

- Uwzględnione tutaj podstawowe ścieżki kluczy: `channels.irc`, `channels.irc.dmPolicy`, `channels.irc.configWrites`, `channels.irc.nickserv.*`.
- Opcjonalne `channels.irc.defaultAccount` nadpisuje wybór konta domyślnego, gdy pasuje do skonfigurowanego identyfikatora konta.
- Pełna konfiguracja kanału IRC (host/port/TLS/kanały/listy dozwolonych/ograniczanie przez wzmianki) jest udokumentowana w [IRC](/pl/channels/irc).

### Wiele kont (wszystkie kanały)

Uruchamiaj wiele kont na kanał (każde z własnym `accountId`):

```json5
{
  channels: {
    telegram: {
      accounts: {
        default: {
          name: "Primary bot",
          botToken: "123456:ABC...",
        },
        alerts: {
          name: "Alerts bot",
          botToken: "987654:XYZ...",
        },
      },
    },
  },
}
```

- `default` jest używane, gdy `accountId` zostanie pominięte (CLI + routing).
- Tokeny środowiskowe mają zastosowanie tylko do konta **default**.
- Podstawowe ustawienia kanału mają zastosowanie do wszystkich kont, chyba że zostaną nadpisane per konto.
- Użyj `bindings[].match.accountId`, aby kierować każde konto do innego agenta.
- Jeśli dodasz konto inne niż domyślne przez `openclaw channels add` (lub onboarding kanału), pozostając nadal przy jednokontowej konfiguracji kanału na poziomie głównym, OpenClaw najpierw promuje wartości najwyższego poziomu przypisane do pojedynczego konta do mapy kont kanału, aby oryginalne konto nadal działało. Większość kanałów przenosi je do `channels.<channel>.accounts.default`; Matrix może zamiast tego zachować istniejący pasujący nazwany/domyslny cel.
- Istniejące powiązania tylko kanałowe (bez `accountId`) nadal pasują do konta domyślnego; powiązania zakresowane do konta pozostają opcjonalne.
- `openclaw doctor --fix` również naprawia mieszane kształty, przenosząc wartości najwyższego poziomu przypisane do pojedynczego konta do promowanego konta wybranego dla tego kanału. Większość kanałów używa `accounts.default`; Matrix może zamiast tego zachować istniejący pasujący nazwany/domyslny cel.

### Inne kanały rozszerzeń

Wiele kanałów rozszerzeń jest konfigurowanych jako `channels.<id>` i udokumentowanych na ich dedykowanych stronach kanałów (na przykład Feishu, Matrix, LINE, Nostr, Zalo, Nextcloud Talk, Synology Chat i Twitch).
Zobacz pełny indeks kanałów: [Channels](/pl/channels).

### Ograniczanie odpowiedzi w czatach grupowych przez wzmianki

Wiadomości grupowe domyślnie **wymagają wzmianki** (wzmianka w metadanych lub bezpieczne wzorce regex). Dotyczy czatów grupowych WhatsApp, Telegram, Discord, Google Chat i iMessage.

**Typy wzmianek:**

- **Wzmianki w metadanych**: natywne wzmianki @ platformy. Ignorowane w trybie czatu do siebie w WhatsApp.
- **Wzorce tekstowe**: bezpieczne wzorce regex w `agents.list[].groupChat.mentionPatterns`. Nieprawidłowe wzorce i niebezpieczne zagnieżdżone powtórzenia są ignorowane.
- Ograniczanie przez wzmianki jest wymuszane tylko wtedy, gdy wykrycie jest możliwe (natywne wzmianki lub co najmniej jeden wzorzec).

```json5
{
  messages: {
    groupChat: { historyLimit: 50 },
  },
  agents: {
    list: [{ id: "main", groupChat: { mentionPatterns: ["@openclaw", "openclaw"] } }],
  },
}
```

`messages.groupChat.historyLimit` ustawia globalną wartość domyślną. Kanały mogą ją nadpisywać przez `channels.<channel>.historyLimit` (lub per konto). Ustaw `0`, aby wyłączyć.

#### Limity historii DM

```json5
{
  channels: {
    telegram: {
      dmHistoryLimit: 30,
      dms: {
        "123456789": { historyLimit: 50 },
      },
    },
  },
}
```

Rozwiązywanie: nadpisanie per DM → wartość domyślna dostawcy → brak limitu (zachowywane wszystko).

Obsługiwane: `telegram`, `whatsapp`, `discord`, `slack`, `signal`, `imessage`, `msteams`.

#### Tryb czatu do siebie

Uwzględnij własny numer w `allowFrom`, aby włączyć tryb czatu do siebie (ignoruje natywne wzmianki @, odpowiada tylko na wzorce tekstowe):

```json5
{
  channels: {
    whatsapp: {
      allowFrom: ["+15555550123"],
      groups: { "*": { requireMention: true } },
    },
  },
  agents: {
    list: [
      {
        id: "main",
        groupChat: { mentionPatterns: ["reisponde", "@openclaw"] },
      },
    ],
  },
}
```

### Polecenia (obsługa poleceń czatu)

```json5
{
  commands: {
    native: "auto", // register native commands when supported
    nativeSkills: "auto", // register native skill commands when supported
    text: true, // parse /commands in chat messages
    bash: false, // allow ! (alias: /bash)
    bashForegroundMs: 2000,
    config: false, // allow /config
    mcp: false, // allow /mcp
    plugins: false, // allow /plugins
    debug: false, // allow /debug
    restart: true, // allow /restart + gateway restart tool
    ownerAllowFrom: ["discord:123456789012345678"],
    ownerDisplay: "raw", // raw | hash
    ownerDisplaySecret: "${OWNER_ID_HASH_SECRET}",
    allowFrom: {
      "*": ["user1"],
      discord: ["user:123"],
    },
    useAccessGroups: true,
  },
}
```

<Accordion title="Szczegóły poleceń">

- Ten blok konfiguruje powierzchnie poleceń. Aktualny katalog poleceń wbudowanych + bundled znajdziesz w [Slash Commands](/pl/tools/slash-commands).
- Ta strona jest **odwołaniem do kluczy konfiguracji**, a nie pełnym katalogiem poleceń. Polecenia należące do kanałów/Pluginów, takie jak QQ Bot `/bot-ping` `/bot-help` `/bot-logs`, LINE `/card`, device-pair `/pair`, memory `/dreaming`, phone-control `/phone` i Talk `/voice`, są udokumentowane na stronach ich kanałów/Pluginów oraz w [Slash Commands](/pl/tools/slash-commands).
- Polecenia tekstowe muszą być **samodzielnymi** wiadomościami zaczynającymi się od `/`.
- `native: "auto"` włącza natywne polecenia dla Discorda/Telegrama, pozostawia Slack wyłączony.
- `nativeSkills: "auto"` włącza natywne polecenia Skills dla Discorda/Telegrama, pozostawia Slack wyłączony.
- Nadpisanie per kanał: `channels.discord.commands.native` (bool lub `"auto"`). `false` czyści wcześniej zarejestrowane polecenia.
- Nadpisz rejestrację natywnych Skills per kanał przez `channels.<provider>.commands.nativeSkills`.
- `channels.telegram.customCommands` dodaje dodatkowe wpisy menu bota Telegrama.
- `bash: true` włącza `! <cmd>` dla powłoki hosta. Wymaga `tools.elevated.enabled` oraz nadawcy w `tools.elevated.allowFrom.<channel>`.
- `config: true` włącza `/config` (odczytuje/zapisuje `openclaw.json`). Dla klientów Gateway `chat.send` trwałe zapisy `/config set|unset` wymagają także `operator.admin`; tylko do odczytu `/config show` pozostaje dostępne dla zwykłych klientów operatora z zakresem zapisu.
- `mcp: true` włącza `/mcp` dla konfiguracji serwera MCP zarządzanego przez OpenClaw w `mcp.servers`.
- `plugins: true` włącza `/plugins` dla wykrywania Pluginów, instalacji oraz sterowania włączaniem/wyłączaniem.
- `channels.<provider>.configWrites` steruje mutacjami konfiguracji per kanał (domyślnie: true).
- Dla kanałów wielokontowych `channels.<provider>.accounts.<id>.configWrites` steruje także zapisami, które dotyczą tego konta (na przykład `/allowlist --config --account <id>` lub `/config set channels.<provider>.accounts.<id>...`).
- `restart: false` wyłącza `/restart` i działania narzędzia restartu Gateway. Domyślnie: `true`.
- `ownerAllowFrom` to jawna lista dozwolonych właściciela dla poleceń/narzędzi tylko dla właściciela. Jest oddzielna od `allowFrom`.
- `ownerDisplay: "hash"` haszuje identyfikatory właścicieli w system prompt. Ustaw `ownerDisplaySecret`, aby kontrolować haszowanie.
- `allowFrom` jest per dostawca. Gdy jest ustawione, jest **jedynym** źródłem autoryzacji (listy dozwolonych/parowanie kanałów i `useAccessGroups` są ignorowane).
- `useAccessGroups: false` pozwala poleceniom omijać zasady grup dostępu, gdy `allowFrom` nie jest ustawione.
- Mapa dokumentacji poleceń:
  - katalog wbudowany + bundled: [Slash Commands](/pl/tools/slash-commands)
  - powierzchnie poleceń specyficzne dla kanałów: [Channels](/pl/channels)
  - polecenia QQ Bot: [QQ Bot](/pl/channels/qqbot)
  - polecenia parowania: [Pairing](/pl/channels/pairing)
  - polecenie karty LINE: [LINE](/pl/channels/line)
  - memory dreaming: [Dreaming](/pl/concepts/dreaming)

</Accordion>

---

## Wartości domyślne agenta

### `agents.defaults.workspace`

Domyślnie: `~/.openclaw/workspace`.

```json5
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
}
```

### `agents.defaults.repoRoot`

Opcjonalny katalog główny repozytorium wyświetlany w wierszu Runtime system prompt. Jeśli nie jest ustawiony, OpenClaw wykrywa go automatycznie, przechodząc w górę od obszaru roboczego.

```json5
{
  agents: { defaults: { repoRoot: "~/Projects/openclaw" } },
}
```

### `agents.defaults.skills`

Opcjonalna domyślna lista dozwolonych Skills dla agentów, które nie ustawiają
`agents.list[].skills`.

```json5
{
  agents: {
    defaults: { skills: ["github", "weather"] },
    list: [
      { id: "writer" }, // dziedziczy github, weather
      { id: "docs", skills: ["docs-search"] }, // zastępuje wartości domyślne
      { id: "locked-down", skills: [] }, // bez Skills
    ],
  },
}
```

- Pomiń `agents.defaults.skills`, aby domyślnie nie ograniczać Skills.
- Pomiń `agents.list[].skills`, aby dziedziczyć wartości domyślne.
- Ustaw `agents.list[].skills: []`, aby nie używać żadnych Skills.
- Niepusta lista `agents.list[].skills` jest ostatecznym zestawem dla tego agenta; nie
  jest łączona z wartościami domyślnymi.

### `agents.defaults.skipBootstrap`

Wyłącza automatyczne tworzenie plików bootstrap obszaru roboczego (`AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`, `BOOTSTRAP.md`).

```json5
{
  agents: { defaults: { skipBootstrap: true } },
}
```

### `agents.defaults.contextInjection`

Kontroluje, kiedy pliki bootstrap obszaru roboczego są wstrzykiwane do system prompt. Domyślnie: `"always"`.

- `"continuation-skip"`: bezpieczne tury kontynuacji (po ukończonej odpowiedzi asystenta) pomijają ponowne wstrzyknięcie bootstrap obszaru roboczego, zmniejszając rozmiar promptu. Uruchomienia Heartbeat i ponowne próby po Compaction nadal odbudowują kontekst.

```json5
{
  agents: { defaults: { contextInjection: "continuation-skip" } },
}
```

### `agents.defaults.bootstrapMaxChars`

Maksymalna liczba znaków na plik bootstrap obszaru roboczego przed obcięciem. Domyślnie: `20000`.

```json5
{
  agents: { defaults: { bootstrapMaxChars: 20000 } },
}
```

### `agents.defaults.bootstrapTotalMaxChars`

Maksymalna łączna liczba znaków wstrzykiwanych ze wszystkich plików bootstrap obszaru roboczego. Domyślnie: `150000`.

```json5
{
  agents: { defaults: { bootstrapTotalMaxChars: 150000 } },
}
```

### `agents.defaults.bootstrapPromptTruncationWarning`

Kontroluje widoczny dla agenta tekst ostrzegawczy, gdy kontekst bootstrap jest obcięty.
Domyślnie: `"once"`.

- `"off"`: nigdy nie wstrzykuj tekstu ostrzeżenia do system prompt.
- `"once"`: wstrzyknij ostrzeżenie raz dla każdego unikalnego podpisu obcięcia (zalecane).
- `"always"`: wstrzykuj ostrzeżenie przy każdym uruchomieniu, gdy istnieje obcięcie.

```json5
{
  agents: { defaults: { bootstrapPromptTruncationWarning: "once" } }, // off | once | always
}
```

### `agents.defaults.imageMaxDimensionPx`

Maksymalny rozmiar w pikselach dłuższego boku obrazu w blokach obrazów transkryptu/narzędzi przed wywołaniami dostawcy.
Domyślnie: `1200`.

Niższe wartości zwykle zmniejszają użycie tokenów vision i rozmiar ładunku żądania w przebiegach z dużą liczbą zrzutów ekranu.
Wyższe wartości zachowują więcej szczegółów wizualnych.

```json5
{
  agents: { defaults: { imageMaxDimensionPx: 1200 } },
}
```

### `agents.defaults.userTimezone`

Strefa czasowa dla kontekstu system prompt (nie znaczników czasu wiadomości). Wartość zapasowa to strefa czasowa hosta.

```json5
{
  agents: { defaults: { userTimezone: "America/Chicago" } },
}
```

### `agents.defaults.timeFormat`

Format czasu w system prompt. Domyślnie: `auto` (preferencja systemu operacyjnego).

```json5
{
  agents: { defaults: { timeFormat: "auto" } }, // auto | 12 | 24
}
```

### `agents.defaults.model`

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": { alias: "opus" },
        "minimax/MiniMax-M2.7": { alias: "minimax" },
      },
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["minimax/MiniMax-M2.7"],
      },
      imageModel: {
        primary: "openrouter/qwen/qwen-2.5-vl-72b-instruct:free",
        fallbacks: ["openrouter/google/gemini-2.0-flash-vision:free"],
      },
      imageGenerationModel: {
        primary: "openai/gpt-image-1",
        fallbacks: ["google/gemini-3.1-flash-image-preview"],
      },
      videoGenerationModel: {
        primary: "qwen/wan2.6-t2v",
        fallbacks: ["qwen/wan2.6-i2v"],
      },
      pdfModel: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["openai/gpt-5.4-mini"],
      },
      params: { cacheRetention: "long" }, // globalne domyślne parametry dostawcy
      embeddedHarness: {
        runtime: "auto", // auto | pi | registered harness id, e.g. codex
        fallback: "pi", // pi | none
      },
      pdfMaxBytesMb: 10,
      pdfMaxPages: 20,
      thinkingDefault: "low",
      verboseDefault: "off",
      elevatedDefault: "on",
      timeoutSeconds: 600,
      mediaMaxMb: 5,
      contextTokens: 200000,
      maxConcurrent: 3,
    },
  },
}
```

- `model`: akceptuje albo ciąg znaków (`"provider/model"`), albo obiekt (`{ primary, fallbacks }`).
  - Forma ciągu ustawia tylko model podstawowy.
  - Forma obiektu ustawia model podstawowy oraz uporządkowane modele przełączenia awaryjnego.
- `imageModel`: akceptuje albo ciąg znaków (`"provider/model"`), albo obiekt (`{ primary, fallbacks }`).
  - Używany przez ścieżkę narzędzia `image` jako konfiguracja modelu vision.
  - Używany także jako routing zapasowy, gdy wybrany/domyslny model nie może przyjąć obrazu jako wejścia.
- `imageGenerationModel`: akceptuje albo ciąg znaków (`"provider/model"`), albo obiekt (`{ primary, fallbacks }`).
  - Używany przez współdzieloną funkcję generowania obrazów oraz każdą przyszłą powierzchnię narzędzia/Pluginu, która generuje obrazy.
  - Typowe wartości: `google/gemini-3.1-flash-image-preview` dla natywnego generowania obrazów Gemini, `fal/fal-ai/flux/dev` dla fal albo `openai/gpt-image-1` dla OpenAI Images.
  - Jeśli wybierzesz bezpośrednio `provider/model`, skonfiguruj też pasujące uwierzytelnianie/klucz API dostawcy (na przykład `GEMINI_API_KEY` lub `GOOGLE_API_KEY` dla `google/*`, `OPENAI_API_KEY` dla `openai/*`, `FAL_KEY` dla `fal/*`).
  - Jeśli pominięte, `image_generate` nadal może wywnioskować domyślny dostawca na podstawie uwierzytelnienia. Najpierw próbuje bieżącego domyślnego dostawcy, potem pozostałych zarejestrowanych dostawców generowania obrazów w kolejności identyfikatorów dostawców.
- `musicGenerationModel`: akceptuje albo ciąg znaków (`"provider/model"`), albo obiekt (`{ primary, fallbacks }`).
  - Używany przez współdzieloną funkcję generowania muzyki oraz wbudowane narzędzie `music_generate`.
  - Typowe wartości: `google/lyria-3-clip-preview`, `google/lyria-3-pro-preview` albo `minimax/music-2.5+`.
  - Jeśli pominięte, `music_generate` nadal może wywnioskować domyślny dostawca na podstawie uwierzytelnienia. Najpierw próbuje bieżącego domyślnego dostawcy, potem pozostałych zarejestrowanych dostawców generowania muzyki w kolejności identyfikatorów dostawców.
  - Jeśli wybierzesz bezpośrednio `provider/model`, skonfiguruj też pasujące uwierzytelnianie/klucz API dostawcy.
- `videoGenerationModel`: akceptuje albo ciąg znaków (`"provider/model"`), albo obiekt (`{ primary, fallbacks }`).
  - Używany przez współdzieloną funkcję generowania wideo oraz wbudowane narzędzie `video_generate`.
  - Typowe wartości: `qwen/wan2.6-t2v`, `qwen/wan2.6-i2v`, `qwen/wan2.6-r2v`, `qwen/wan2.6-r2v-flash` albo `qwen/wan2.7-r2v`.
  - Jeśli pominięte, `video_generate` nadal może wywnioskować domyślny dostawca na podstawie uwierzytelnienia. Najpierw próbuje bieżącego domyślnego dostawcy, potem pozostałych zarejestrowanych dostawców generowania wideo w kolejności identyfikatorów dostawców.
  - Jeśli wybierzesz bezpośrednio `provider/model`, skonfiguruj też pasujące uwierzytelnianie/klucz API dostawcy.
  - Bundled dostawca generowania wideo Qwen obsługuje maksymalnie 1 wyjściowe wideo, 1 wejściowy obraz, 4 wejściowe filmy, 10 sekund czasu trwania oraz opcje na poziomie dostawcy `size`, `aspectRatio`, `resolution`, `audio` i `watermark`.
- `pdfModel`: akceptuje albo ciąg znaków (`"provider/model"`), albo obiekt (`{ primary, fallbacks }`).
  - Używany przez narzędzie `pdf` do routingu modeli.
  - Jeśli pominięte, narzędzie PDF wraca do `imageModel`, a potem do rozwiązanego modelu sesji/domyslnego.
- `pdfMaxBytesMb`: domyślny limit rozmiaru PDF dla narzędzia `pdf`, gdy `maxBytesMb` nie jest przekazane w czasie wywołania.
- `pdfMaxPages`: domyślna maksymalna liczba stron uwzględnianych przez tryb zapasowego wyodrębniania w narzędziu `pdf`.
- `verboseDefault`: domyślny poziom szczegółowości dla agentów. Wartości: `"off"`, `"on"`, `"full"`. Domyślnie: `"off"`.
- `elevatedDefault`: domyślny poziom wyjścia podwyższonego dla agentów. Wartości: `"off"`, `"on"`, `"ask"`, `"full"`. Domyślnie: `"on"`.
- `model.primary`: format `provider/model` (np. `openai/gpt-5.4`). Jeśli pominiesz dostawcę, OpenClaw najpierw próbuje aliasu, potem jednoznacznego dopasowania dokładnego identyfikatora modelu wśród skonfigurowanych dostawców, a dopiero potem wraca do skonfigurowanego dostawcy domyślnego (przestarzałe zachowanie zgodności, więc preferuj jawne `provider/model`). Jeśli ten dostawca nie udostępnia już skonfigurowanego modelu domyślnego, OpenClaw wraca do pierwszego skonfigurowanego dostawcy/modelu zamiast ujawniać nieaktualną wartość domyślną usuniętego dostawcy.
- `models`: skonfigurowany katalog modeli i lista dozwolonych dla `/model`. Każdy wpis może zawierać `alias` (skrót) i `params` (specyficzne dla dostawcy, na przykład `temperature`, `maxTokens`, `cacheRetention`, `context1m`).
- `params`: globalne domyślne parametry dostawcy stosowane do wszystkich modeli. Ustawiane w `agents.defaults.params` (np. `{ cacheRetention: "long" }`).
- Priorytet scalania `params` (konfiguracja): `agents.defaults.params` (globalna baza) jest nadpisywane przez `agents.defaults.models["provider/model"].params` (per model), a potem `agents.list[].params` (pasujący identyfikator agenta) nadpisuje według klucza. Szczegóły znajdziesz w [Prompt Caching](/pl/reference/prompt-caching).
- `embeddedHarness`: domyślna polityka runtime osadzonego agenta niskiego poziomu. Użyj `runtime: "auto"`, aby pozwolić zarejestrowanym harnessom Pluginów przejąć obsługiwane modele, `runtime: "pi"`, aby wymusić wbudowany harness PI, albo zarejestrowanego identyfikatora harnessu, takiego jak `runtime: "codex"`. Ustaw `fallback: "none"`, aby wyłączyć automatyczny zapasowy powrót do PI.
- Narzędzia zapisujące konfigurację, które mutują te pola (na przykład `/models set`, `/models set-image` i polecenia dodawania/usuwania fallback), zapisują kanoniczną formę obiektu i zachowują istniejące listy fallbacków, gdy to możliwe.
- `maxConcurrent`: maksymalna liczba równoległych uruchomień agentów między sesjami (każda sesja nadal jest serializowana). Domyślnie: 4.

### `agents.defaults.embeddedHarness`

`embeddedHarness` kontroluje, który wykonawca niskiego poziomu obsługuje tury osadzonego agenta.
W większości wdrożeń należy pozostawić wartość domyślną `{ runtime: "auto", fallback: "pi" }`.
Użyj tego, gdy zaufany Plugin dostarcza natywny harness, taki jak bundled
harness serwera aplikacji Codex.

```json5
{
  agents: {
    defaults: {
      model: "codex/gpt-5.4",
      embeddedHarness: {
        runtime: "codex",
        fallback: "none",
      },
    },
  },
}
```

- `runtime`: `"auto"`, `"pi"` albo identyfikator zarejestrowanego harnessu Pluginu. Bundled Plugin Codex rejestruje `codex`.
- `fallback`: `"pi"` albo `"none"`. `"pi"` zachowuje wbudowany harness PI jako zgodnościowy fallback. `"none"` powoduje, że brakujący lub nieobsługiwany wybór harnessu Pluginu kończy się błędem zamiast cichego użycia PI.
- Nadpisania środowiskowe: `OPENCLAW_AGENT_RUNTIME=<id|auto|pi>` nadpisuje `runtime`; `OPENCLAW_AGENT_HARNESS_FALLBACK=none` wyłącza fallback PI dla tego procesu.
- W wdrożeniach tylko z Codex ustaw `model: "codex/gpt-5.4"`, `embeddedHarness.runtime: "codex"` i `embeddedHarness.fallback: "none"`.
- To kontroluje tylko osadzony harness czatu. Generowanie mediów, vision, PDF, muzyka, wideo i TTS nadal używają swoich ustawień dostawcy/modelu.

**Wbudowane skróty aliasów** (mają zastosowanie tylko wtedy, gdy model znajduje się w `agents.defaults.models`):

| Alias               | Model                                  |
| ------------------- | -------------------------------------- |
| `opus`              | `anthropic/claude-opus-4-6`            |
| `sonnet`            | `anthropic/claude-sonnet-4-6`          |
| `gpt`               | `openai/gpt-5.4`                       |
| `gpt-mini`          | `openai/gpt-5.4-mini`                  |
| `gpt-nano`          | `openai/gpt-5.4-nano`                  |
| `gemini`            | `google/gemini-3.1-pro-preview`        |
| `gemini-flash`      | `google/gemini-3-flash-preview`        |
| `gemini-flash-lite` | `google/gemini-3.1-flash-lite-preview` |

Skonfigurowane przez Ciebie aliasy zawsze mają pierwszeństwo przed domyślnymi.

Modele Z.AI GLM-4.x automatycznie włączają tryb thinking, chyba że ustawisz `--thinking off` albo samodzielnie zdefiniujesz `agents.defaults.models["zai/<model>"].params.thinking`.
Modele Z.AI domyślnie włączają `tool_stream` dla strumieniowania wywołań narzędzi. Ustaw `agents.defaults.models["zai/<model>"].params.tool_stream` na `false`, aby to wyłączyć.
Modele Anthropic Claude 4.6 domyślnie używają thinking `adaptive`, gdy nie ustawiono jawnego poziomu thinking.

### `agents.defaults.cliBackends`

Opcjonalne backendy CLI dla zapasowych przebiegów tylko tekstowych (bez wywołań narzędzi). Przydatne jako kopia zapasowa, gdy dostawcy API zawodzą.

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "codex-cli": {
          command: "/opt/homebrew/bin/codex",
        },
        "my-cli": {
          command: "my-cli",
          args: ["--json"],
          output: "json",
          modelArg: "--model",
          sessionArg: "--session",
          sessionMode: "existing",
          systemPromptArg: "--system",
          systemPromptWhen: "first",
          imageArg: "--image",
          imageMode: "repeat",
        },
      },
    },
  },
}
```

- Backendy CLI są przede wszystkim tekstowe; narzędzia są zawsze wyłączone.
- Sesje są obsługiwane, gdy ustawione jest `sessionArg`.
- Przekazywanie obrazów jest obsługiwane, gdy `imageArg` akceptuje ścieżki plików.

### `agents.defaults.systemPromptOverride`

Zastąp cały system prompt składany przez OpenClaw stałym ciągiem znaków. Ustawiane na poziomie domyślnym (`agents.defaults.systemPromptOverride`) albo per agent (`agents.list[].systemPromptOverride`). Wartości per agent mają pierwszeństwo; pusta wartość albo zawierająca tylko białe znaki jest ignorowana. Przydatne do kontrolowanych eksperymentów z promptami.

```json5
{
  agents: {
    defaults: {
      systemPromptOverride: "You are a helpful assistant.",
    },
  },
}
```

### `agents.defaults.heartbeat`

Okresowe uruchomienia Heartbeat.

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m", // 0m disables
        model: "openai/gpt-5.4-mini",
        includeReasoning: false,
        includeSystemPromptSection: true, // default: true; false omits the Heartbeat section from the system prompt
        lightContext: false, // default: false; true keeps only HEARTBEAT.md from workspace bootstrap files
        isolatedSession: false, // default: false; true runs each heartbeat in a fresh session (no conversation history)
        session: "main",
        to: "+15555550123",
        directPolicy: "allow", // allow (default) | block
        target: "none", // default: none | options: last | whatsapp | telegram | discord | ...
        prompt: "Read HEARTBEAT.md if it exists...",
        ackMaxChars: 300,
        suppressToolErrorWarnings: false,
        timeoutSeconds: 45,
      },
    },
  },
}
```

- `every`: ciąg czasu trwania (ms/s/m/h). Domyślnie: `30m` (uwierzytelnianie kluczem API) albo `1h` (uwierzytelnianie OAuth). Ustaw `0m`, aby wyłączyć.
- `includeSystemPromptSection`: gdy false, pomija sekcję Heartbeat w system prompt i pomija wstrzykiwanie `HEARTBEAT.md` do kontekstu bootstrap. Domyślnie: `true`.
- `suppressToolErrorWarnings`: gdy true, tłumi ładunki ostrzeżeń o błędach narzędzi podczas uruchomień Heartbeat.
- `timeoutSeconds`: maksymalny czas w sekundach dozwolony dla tury agenta Heartbeat, po którym zostaje ona przerwana. Pozostaw nieustawione, aby użyć `agents.defaults.timeoutSeconds`.
- `directPolicy`: zasada dostarczania bezpośredniego/DM. `allow` (domyślnie) zezwala na dostarczanie do celu bezpośredniego. `block` tłumi dostarczanie do celu bezpośredniego i emituje `reason=dm-blocked`.
- `lightContext`: gdy true, uruchomienia Heartbeat używają lekkiego kontekstu bootstrap i zachowują tylko `HEARTBEAT.md` z plików bootstrap obszaru roboczego.
- `isolatedSession`: gdy true, każde uruchomienie Heartbeat działa w świeżej sesji bez wcześniejszej historii rozmowy. Ten sam wzorzec izolacji co w Cron `sessionTarget: "isolated"`. Zmniejsza koszt tokenów na Heartbeat z około 100K do około 2–5K tokenów.
- Per agent: ustaw `agents.list[].heartbeat`. Gdy dowolny agent definiuje `heartbeat`, Heartbeat uruchamiają **tylko ci agenci**.
- Heartbeat uruchamiają pełne tury agentów — krótsze interwały spalają więcej tokenów.

### `agents.defaults.compaction`

```json5
{
  agents: {
    defaults: {
      compaction: {
        mode: "safeguard", // default | safeguard
        provider: "my-provider", // id of a registered compaction provider plugin (optional)
        timeoutSeconds: 900,
        reserveTokensFloor: 24000,
        identifierPolicy: "strict", // strict | off | custom
        identifierInstructions: "Preserve deployment IDs, ticket IDs, and host:port pairs exactly.", // used when identifierPolicy=custom
        postCompactionSections: ["Session Startup", "Red Lines"], // [] disables reinjection
        model: "openrouter/anthropic/claude-sonnet-4-6", // optional compaction-only model override
        notifyUser: true, // send a brief notice when compaction starts (default: false)
        memoryFlush: {
          enabled: true,
          softThresholdTokens: 6000,
          systemPrompt: "Session nearing compaction. Store durable memories now.",
          prompt: "Write any lasting notes to memory/YYYY-MM-DD.md; reply with the exact silent token NO_REPLY if nothing to store.",
        },
      },
    },
  },
}
```

- `mode`: `default` lub `safeguard` (sumaryzacja porcjami dla długich historii). Zobacz [Compaction](/pl/concepts/compaction).
- `provider`: identyfikator zarejestrowanego Pluginu dostawcy Compaction. Gdy jest ustawiony, wywoływane jest `summarize()` tego dostawcy zamiast wbudowanej sumaryzacji LLM. W razie błędu wraca do wbudowanej. Ustawienie dostawcy wymusza `mode: "safeguard"`. Zobacz [Compaction](/pl/concepts/compaction).
- `timeoutSeconds`: maksymalna liczba sekund dozwolona dla pojedynczej operacji Compaction, po której OpenClaw ją przerywa. Domyślnie: `900`.
- `identifierPolicy`: `strict` (domyślnie), `off` lub `custom`. `strict` dodaje na początku wbudowane wskazówki zachowania nieprzezroczystych identyfikatorów podczas sumaryzacji Compaction.
- `identifierInstructions`: opcjonalny niestandardowy tekst zachowania identyfikatorów używany, gdy `identifierPolicy=custom`.
- `postCompactionSections`: opcjonalne nazwy sekcji H2/H3 z AGENTS.md do ponownego wstrzyknięcia po Compaction. Domyślnie `["Session Startup", "Red Lines"]`; ustaw `[]`, aby wyłączyć ponowne wstrzykiwanie. Gdy nieustawione albo jawnie ustawione na tę domyślną parę, starsze nagłówki `Every Session`/`Safety` są również akceptowane jako starszy fallback.
- `model`: opcjonalne nadpisanie `provider/model-id` tylko dla sumaryzacji Compaction. Użyj tego, gdy główna sesja ma zachować jeden model, ale podsumowania Compaction mają działać na innym; gdy nieustawione, Compaction używa podstawowego modelu sesji.
- `notifyUser`: gdy `true`, wysyła krótkie powiadomienie do użytkownika, gdy rozpoczyna się Compaction (na przykład „Compacting context...” ). Domyślnie wyłączone, aby Compaction pozostał cichy.
- `memoryFlush`: cicha agentowa tura przed automatycznym Compaction, aby zapisać trwałe wspomnienia. Pomijane, gdy obszar roboczy jest tylko do odczytu.

### `agents.defaults.contextPruning`

Przycina **stare wyniki narzędzi** z kontekstu w pamięci przed wysłaniem do LLM. **Nie** modyfikuje historii sesji na dysku.

```json5
{
  agents: {
    defaults: {
      contextPruning: {
        mode: "cache-ttl", // off | cache-ttl
        ttl: "1h", // duration (ms/s/m/h), default unit: minutes
        keepLastAssistants: 3,
        softTrimRatio: 0.3,
        hardClearRatio: 0.5,
        minPrunableToolChars: 50000,
        softTrim: { maxChars: 4000, headChars: 1500, tailChars: 1500 },
        hardClear: { enabled: true, placeholder: "[Old tool result content cleared]" },
        tools: { deny: ["browser", "canvas"] },
      },
    },
  },
}
```

<Accordion title="Zachowanie trybu cache-ttl">

- `mode: "cache-ttl"` włącza przebiegi przycinania.
- `ttl` kontroluje, jak często przycinanie może zostać uruchomione ponownie (od ostatniego dotknięcia cache).
- Przycinanie najpierw miękko przycina zbyt duże wyniki narzędzi, a potem w razie potrzeby całkowicie czyści starsze wyniki narzędzi.

**Miękkie przycinanie** zachowuje początek + koniec i wstawia `...` pośrodku.

**Twarde czyszczenie** zastępuje cały wynik narzędzia placeholderem.

Uwagi:

- Bloki obrazów nigdy nie są przycinane/czyszczone.
- Współczynniki są oparte na znakach (w przybliżeniu), a nie na dokładnej liczbie tokenów.
- Jeśli istnieje mniej niż `keepLastAssistants` wiadomości asystenta, przycinanie jest pomijane.

</Accordion>

Szczegóły zachowania znajdziesz w [Session Pruning](/pl/concepts/session-pruning).

### Strumieniowanie blokowe

```json5
{
  agents: {
    defaults: {
      blockStreamingDefault: "off", // on | off
      blockStreamingBreak: "text_end", // text_end | message_end
      blockStreamingChunk: { minChars: 800, maxChars: 1200 },
      blockStreamingCoalesce: { idleMs: 1000 },
      humanDelay: { mode: "natural" }, // off | natural | custom (use minMs/maxMs)
    },
  },
}
```

- Kanały inne niż Telegram wymagają jawnego `*.blockStreaming: true`, aby włączyć odpowiedzi blokowe.
- Nadpisania kanałów: `channels.<channel>.blockStreamingCoalesce` (oraz warianty per konto). Signal/Slack/Discord/Google Chat mają domyślnie `minChars: 1500`.
- `humanDelay`: losowa pauza między odpowiedziami blokowymi. `natural` = 800–2500 ms. Nadpisanie per agent: `agents.list[].humanDelay`.

Szczegóły zachowania i porcjowania znajdziesz w [Streaming](/pl/concepts/streaming).

### Wskaźniki pisania

```json5
{
  agents: {
    defaults: {
      typingMode: "instant", // never | instant | thinking | message
      typingIntervalSeconds: 6,
    },
  },
}
```

- Domyślne: `instant` dla czatów bezpośrednich/wzmianek, `message` dla czatów grupowych bez wzmianki.
- Nadpisania per sesja: `session.typingMode`, `session.typingIntervalSeconds`.

Zobacz [Typing Indicators](/pl/concepts/typing-indicators).

<a id="agentsdefaultssandbox"></a>

### `agents.defaults.sandbox`

Opcjonalny sandboxing dla osadzonego agenta. Pełny przewodnik znajdziesz w [Sandboxing](/pl/gateway/sandboxing).

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main", // off | non-main | all
        backend: "docker", // docker | ssh | openshell
        scope: "agent", // session | agent | shared
        workspaceAccess: "none", // none | ro | rw
        workspaceRoot: "~/.openclaw/sandboxes",
        docker: {
          image: "openclaw-sandbox:bookworm-slim",
          containerPrefix: "openclaw-sbx-",
          workdir: "/workspace",
          readOnlyRoot: true,
          tmpfs: ["/tmp", "/var/tmp", "/run"],
          network: "none",
          user: "1000:1000",
          capDrop: ["ALL"],
          env: { LANG: "C.UTF-8" },
          setupCommand: "apt-get update && apt-get install -y git curl jq",
          pidsLimit: 256,
          memory: "1g",
          memorySwap: "2g",
          cpus: 1,
          ulimits: {
            nofile: { soft: 1024, hard: 2048 },
            nproc: 256,
          },
          seccompProfile: "/path/to/seccomp.json",
          apparmorProfile: "openclaw-sandbox",
          dns: ["1.1.1.1", "8.8.8.8"],
          extraHosts: ["internal.service:10.0.0.5"],
          binds: ["/home/user/source:/source:rw"],
        },
        ssh: {
          target: "user@gateway-host:22",
          command: "ssh",
          workspaceRoot: "/tmp/openclaw-sandboxes",
          strictHostKeyChecking: true,
          updateHostKeys: true,
          identityFile: "~/.ssh/id_ed25519",
          certificateFile: "~/.ssh/id_ed25519-cert.pub",
          knownHostsFile: "~/.ssh/known_hosts",
          // SecretRefs / inline contents also supported:
          // identityData: { source: "env", provider: "default", id: "SSH_IDENTITY" },
          // certificateData: { source: "env", provider: "default", id: "SSH_CERTIFICATE" },
          // knownHostsData: { source: "env", provider: "default", id: "SSH_KNOWN_HOSTS" },
        },
        browser: {
          enabled: false,
          image: "openclaw-sandbox-browser:bookworm-slim",
          network: "openclaw-sandbox-browser",
          cdpPort: 9222,
          cdpSourceRange: "172.21.0.1/32",
          vncPort: 5900,
          noVncPort: 6080,
          headless: false,
          enableNoVnc: true,
          allowHostControl: false,
          autoStart: true,
          autoStartTimeoutMs: 12000,
        },
        prune: {
          idleHours: 24,
          maxAgeDays: 7,
        },
      },
    },
  },
  tools: {
    sandbox: {
      tools: {
        allow: [
          "exec",
          "process",
          "read",
          "write",
          "edit",
          "apply_patch",
          "sessions_list",
          "sessions_history",
          "sessions_send",
          "sessions_spawn",
          "session_status",
        ],
        deny: ["browser", "canvas", "nodes", "cron", "discord", "gateway"],
      },
    },
  },
}
```

<Accordion title="Szczegóły sandbox">

**Backend:**

- `docker`: lokalne środowisko Docker runtime (domyślne)
- `ssh`: ogólne zdalne środowisko runtime oparte na SSH
- `openshell`: środowisko runtime OpenShell

Gdy wybrano `backend: "openshell"`, ustawienia specyficzne dla runtime są przenoszone do
`plugins.entries.openshell.config`.

**Konfiguracja backendu SSH:**

- `target`: cel SSH w formacie `user@host[:port]`
- `command`: polecenie klienta SSH (domyślnie: `ssh`)
- `workspaceRoot`: bezwzględny zdalny katalog główny używany dla obszarów roboczych per scope
- `identityFile` / `certificateFile` / `knownHostsFile`: istniejące pliki lokalne przekazywane do OpenSSH
- `identityData` / `certificateData` / `knownHostsData`: treść inline lub SecretRefs, które OpenClaw materializuje do plików tymczasowych w runtime
- `strictHostKeyChecking` / `updateHostKeys`: elementy sterowania polityką kluczy hosta OpenSSH

**Priorytet uwierzytelniania SSH:**

- `identityData` ma pierwszeństwo przed `identityFile`
- `certificateData` ma pierwszeństwo przed `certificateFile`
- `knownHostsData` ma pierwszeństwo przed `knownHostsFile`
- Wartości `*Data` oparte na SecretRef są rozwiązywane z aktywnej migawki runtime sekretów przed rozpoczęciem sesji sandbox

**Zachowanie backendu SSH:**

- inicjuje zdalny obszar roboczy raz po utworzeniu lub odtworzeniu
- następnie utrzymuje zdalny obszar roboczy SSH jako kanoniczny
- kieruje `exec`, narzędzia plikowe i ścieżki mediów przez SSH
- nie synchronizuje automatycznie zmian zdalnych z powrotem do hosta
- nie obsługuje kontenerów przeglądarki sandbox

**Dostęp do obszaru roboczego:**

- `none`: obszar roboczy sandbox per scope w `~/.openclaw/sandboxes`
- `ro`: obszar roboczy sandbox w `/workspace`, obszar roboczy agenta montowany tylko do odczytu w `/agent`
- `rw`: obszar roboczy agenta montowany do odczytu i zapisu w `/workspace`

**Scope:**

- `session`: kontener + obszar roboczy per sesja
- `agent`: jeden kontener + obszar roboczy na agenta (domyślnie)
- `shared`: współdzielony kontener i obszar roboczy (bez izolacji między sesjami)

**Konfiguracja Pluginu OpenShell:**

```json5
{
  plugins: {
    entries: {
      openshell: {
        enabled: true,
        config: {
          mode: "mirror", // mirror | remote
          from: "openclaw",
          remoteWorkspaceDir: "/sandbox",
          remoteAgentWorkspaceDir: "/agent",
          gateway: "lab", // optional
          gatewayEndpoint: "https://lab.example", // optional
          policy: "strict", // optional OpenShell policy id
          providers: ["openai"], // optional
          autoProviders: true,
          timeoutSeconds: 120,
        },
      },
    },
  },
}
```

**Tryb OpenShell:**

- `mirror`: inicjuje zdalne środowisko z lokalnego przed `exec`, synchronizuje z powrotem po `exec`; lokalny obszar roboczy pozostaje kanoniczny
- `remote`: inicjuje zdalne środowisko raz podczas tworzenia sandbox, a następnie utrzymuje zdalny obszar roboczy jako kanoniczny

W trybie `remote` lokalne na hoście edycje wykonane poza OpenClaw nie są automatycznie synchronizowane do sandbox po kroku inicjalizacji.
Transport odbywa się przez SSH do sandbox OpenShell, ale Plugin zarządza cyklem życia sandbox i opcjonalną synchronizacją mirror.

**`setupCommand`** uruchamia się raz po utworzeniu kontenera (przez `sh -lc`). Wymaga wychodzącego dostępu do sieci, zapisywalnego katalogu głównego i użytkownika root.

**Kontenery domyślnie mają `network: "none"`** — ustaw na `"bridge"` (lub niestandardową sieć bridge), jeśli agent potrzebuje dostępu wychodzącego.
`"host"` jest blokowane. `"container:<id>"` jest domyślnie blokowane, chyba że jawnie ustawisz
`sandbox.docker.dangerouslyAllowContainerNamespaceJoin: true` (tryb break-glass).

**Załączniki przychodzące** są przygotowywane w `media/inbound/*` w aktywnym obszarze roboczym.

**`docker.binds`** montuje dodatkowe katalogi hosta; globalne i per-agent `binds` są scalane.

**Sandboxed browser** (`sandbox.browser.enabled`): Chromium + CDP w kontenerze. Adres URL noVNC jest wstrzykiwany do system prompt. Nie wymaga `browser.enabled` w `openclaw.json`.
Dostęp obserwatora noVNC domyślnie używa uwierzytelniania VNC, a OpenClaw emituje adres URL z krótkotrwałym tokenem (zamiast ujawniać hasło we współdzielonym adresie URL).

- `allowHostControl: false` (domyślnie) blokuje możliwość kierowania sesji sandbox do przeglądarki hosta.
- `network` ma domyślnie wartość `openclaw-sandbox-browser` (dedykowana sieć bridge). Ustaw `bridge` tylko wtedy, gdy jawnie chcesz globalnej łączności bridge.
- `cdpSourceRange` opcjonalnie ogranicza wejściowy ruch CDP na granicy kontenera do zakresu CIDR (na przykład `172.21.0.1/32`).
- `sandbox.browser.binds` montuje dodatkowe katalogi hosta tylko do kontenera przeglądarki sandbox. Gdy jest ustawione (w tym `[]`), zastępuje `docker.binds` dla kontenera przeglądarki.
- Domyślne opcje uruchamiania są zdefiniowane w `scripts/sandbox-browser-entrypoint.sh` i dostrojone pod hosty kontenerowe:
  - `--remote-debugging-address=127.0.0.1`
  - `--remote-debugging-port=<derived from OPENCLAW_BROWSER_CDP_PORT>`
  - `--user-data-dir=${HOME}/.chrome`
  - `--no-first-run`
  - `--no-default-browser-check`
  - `--disable-3d-apis`
  - `--disable-gpu`
  - `--disable-software-rasterizer`
  - `--disable-dev-shm-usage`
  - `--disable-background-networking`
  - `--disable-features=TranslateUI`
  - `--disable-breakpad`
  - `--disable-crash-reporter`
  - `--renderer-process-limit=2`
  - `--no-zygote`
  - `--metrics-recording-only`
  - `--disable-extensions` (domyślnie włączone)
  - `--disable-3d-apis`, `--disable-software-rasterizer` i `--disable-gpu` są
    domyślnie włączone i można je wyłączyć przez
    `OPENCLAW_BROWSER_DISABLE_GRAPHICS_FLAGS=0`, jeśli użycie WebGL/3D tego wymaga.
  - `OPENCLAW_BROWSER_DISABLE_EXTENSIONS=0` ponownie włącza rozszerzenia, jeśli Twój workflow
    od nich zależy.
  - `--renderer-process-limit=2` można zmienić przez
    `OPENCLAW_BROWSER_RENDERER_PROCESS_LIMIT=<N>`; ustaw `0`, aby użyć
    domyślnego limitu procesów Chromium.
  - plus `--no-sandbox` i `--disable-setuid-sandbox`, gdy `noSandbox` jest włączone.
  - Wartości domyślne są bazą obrazu kontenera; aby zmienić domyślne ustawienia kontenera, użyj niestandardowego
    obrazu przeglądarki z niestandardowym entrypoint.

</Accordion>

Sandboxing przeglądarki i `sandbox.docker.binds` są dostępne tylko dla Docker.

Budowanie obrazów:

```bash
scripts/sandbox-setup.sh           # główny obraz sandbox
scripts/sandbox-browser-setup.sh   # opcjonalny obraz przeglądarki
```

### `agents.list` (nadpisania per agent)

```json5
{
  agents: {
    list: [
      {
        id: "main",
        default: true,
        name: "Main Agent",
        workspace: "~/.openclaw/workspace",
        agentDir: "~/.openclaw/agents/main/agent",
        model: "anthropic/claude-opus-4-6", // or { primary, fallbacks }
        thinkingDefault: "high", // per-agent thinking level override
        reasoningDefault: "on", // per-agent reasoning visibility override
        fastModeDefault: false, // per-agent fast mode override
        embeddedHarness: { runtime: "auto", fallback: "pi" },
        params: { cacheRetention: "none" }, // overrides matching defaults.models params by key
        skills: ["docs-search"], // replaces agents.defaults.skills when set
        identity: {
          name: "Samantha",
          theme: "helpful sloth",
          emoji: "🦥",
          avatar: "avatars/samantha.png",
        },
        groupChat: { mentionPatterns: ["@openclaw"] },
        sandbox: { mode: "off" },
        runtime: {
          type: "acp",
          acp: {
            agent: "codex",
            backend: "acpx",
            mode: "persistent",
            cwd: "/workspace/openclaw",
          },
        },
        subagents: { allowAgents: ["*"] },
        tools: {
          profile: "coding",
          allow: ["browser"],
          deny: ["canvas"],
          elevated: { enabled: true },
        },
      },
    ],
  },
}
```

- `id`: stabilny identyfikator agenta (wymagany).
- `default`: gdy ustawiono wiele, wygrywa pierwszy (rejestrowane jest ostrzeżenie). Jeśli żaden nie jest ustawiony, domyślny jest pierwszy wpis listy.
- `model`: forma ciągu nadpisuje tylko `primary`; forma obiektu `{ primary, fallbacks }` nadpisuje oba (`[]` wyłącza globalne fallbacki). Zadania Cron, które nadpisują tylko `primary`, nadal dziedziczą domyślne fallbacki, chyba że ustawisz `fallbacks: []`.
- `params`: parametry strumienia per agent scalane ponad wybranym wpisem modelu w `agents.defaults.models`. Użyj tego do nadpisań specyficznych dla agenta, takich jak `cacheRetention`, `temperature` lub `maxTokens`, bez duplikowania całego katalogu modeli.
- `skills`: opcjonalna lista dozwolonych Skills per agent. Jeśli pominięta, agent dziedziczy `agents.defaults.skills`, gdy jest ustawione; jawna lista zastępuje wartości domyślne zamiast je scalać, a `[]` oznacza brak Skills.
- `thinkingDefault`: opcjonalny domyślny poziom thinking per agent (`off | minimal | low | medium | high | xhigh | adaptive`). Nadpisuje `agents.defaults.thinkingDefault` dla tego agenta, gdy nie ustawiono nadpisania per wiadomość ani per sesja.
- `reasoningDefault`: opcjonalna domyślna widoczność reasoning per agent (`on | off | stream`). Stosowane, gdy nie ustawiono nadpisania reasoning per wiadomość ani per sesja.
- `fastModeDefault`: opcjonalna wartość domyślna trybu fast per agent (`true | false`). Stosowane, gdy nie ustawiono nadpisania trybu fast per wiadomość ani per sesja.
- `embeddedHarness`: opcjonalne nadpisanie polityki niskopoziomowego harnessu per agent. Użyj `{ runtime: "codex", fallback: "none" }`, aby jeden agent był tylko dla Codex, podczas gdy inni agenci zachowają domyślny fallback PI.
- `runtime`: opcjonalny deskryptor runtime per agent. Użyj `type: "acp"` z wartościami domyślnymi `runtime.acp` (`agent`, `backend`, `mode`, `cwd`), gdy agent ma domyślnie używać sesji harness ACP.
- `identity.avatar`: ścieżka względna względem workspace, adres URL `http(s)` albo URI `data:`.
- `identity` wyprowadza wartości domyślne: `ackReaction` z `emoji`, `mentionPatterns` z `name`/`emoji`.
- `subagents.allowAgents`: lista dozwolonych identyfikatorów agentów dla `sessions_spawn` (`["*"]` = dowolny; domyślnie: tylko ten sam agent).
- Zabezpieczenie dziedziczenia sandbox: jeśli sesja żądająca jest objęta sandboxem, `sessions_spawn` odrzuca cele, które działałyby bez sandbox.
- `subagents.requireAgentId`: gdy true, blokuje wywołania `sessions_spawn`, które pomijają `agentId` (wymusza jawny wybór profilu; domyślnie: false).

---

## Routing wielu agentów

Uruchamiaj wielu odizolowanych agentów w jednym Gateway. Zobacz [Multi-Agent](/pl/concepts/multi-agent).

```json5
{
  agents: {
    list: [
      { id: "home", default: true, workspace: "~/.openclaw/workspace-home" },
      { id: "work", workspace: "~/.openclaw/workspace-work" },
    ],
  },
  bindings: [
    { agentId: "home", match: { channel: "whatsapp", accountId: "personal" } },
    { agentId: "work", match: { channel: "whatsapp", accountId: "biz" } },
  ],
}
```

### Pola dopasowania binding

- `type` (opcjonalne): `route` dla normalnego routingu (brak typu domyślnie oznacza route), `acp` dla trwałych powiązań konwersacji ACP.
- `match.channel` (wymagane)
- `match.accountId` (opcjonalne; `*` = dowolne konto; pominięte = konto domyślne)
- `match.peer` (opcjonalne; `{ kind: direct|group|channel, id }`)
- `match.guildId` / `match.teamId` (opcjonalne; specyficzne dla kanału)
- `acp` (opcjonalne; tylko dla wpisów `type: "acp"`): `{ mode, label, cwd, backend }`

**Deterministyczna kolejność dopasowania:**

1. `match.peer`
2. `match.guildId`
3. `match.teamId`
4. `match.accountId` (dokładne, bez peer/guild/team)
5. `match.accountId: "*"` (dla całego kanału)
6. Agent domyślny

W obrębie każdego poziomu wygrywa pierwszy pasujący wpis `bindings`.

Dla wpisów `type: "acp"` OpenClaw rozwiązuje według dokładnej tożsamości konwersacji (`match.channel` + konto + `match.peer.id`) i nie używa powyższej kolejności poziomów binding route.

### Profile dostępu per agent

<Accordion title="Pełny dostęp (bez sandbox)">

```json5
{
  agents: {
    list: [
      {
        id: "personal",
        workspace: "~/.openclaw/workspace-personal",
        sandbox: { mode: "off" },
      },
    ],
  },
}
```

</Accordion>

<Accordion title="Narzędzia + workspace tylko do odczytu">

```json5
{
  agents: {
    list: [
      {
        id: "family",
        workspace: "~/.openclaw/workspace-family",
        sandbox: { mode: "all", scope: "agent", workspaceAccess: "ro" },
        tools: {
          allow: [
            "read",
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
          ],
          deny: ["write", "edit", "apply_patch", "exec", "process", "browser"],
        },
      },
    ],
  },
}
```

</Accordion>

<Accordion title="Brak dostępu do systemu plików (tylko wiadomości)">

```json5
{
  agents: {
    list: [
      {
        id: "public",
        workspace: "~/.openclaw/workspace-public",
        sandbox: { mode: "all", scope: "agent", workspaceAccess: "none" },
        tools: {
          allow: [
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
            "whatsapp",
            "telegram",
            "slack",
            "discord",
            "gateway",
          ],
          deny: [
            "read",
            "write",
            "edit",
            "apply_patch",
            "exec",
            "process",
            "browser",
            "canvas",
            "nodes",
            "cron",
            "gateway",
            "image",
          ],
        },
      },
    ],
  },
}
```

</Accordion>

Szczegóły priorytetów znajdziesz w [Multi-Agent Sandbox & Tools](/pl/tools/multi-agent-sandbox-tools).

---

## Sesja

```json5
{
  session: {
    scope: "per-sender",
    dmScope: "main", // main | per-peer | per-channel-peer | per-account-channel-peer
    identityLinks: {
      alice: ["telegram:123456789", "discord:987654321012345678"],
    },
    reset: {
      mode: "daily", // daily | idle
      atHour: 4,
      idleMinutes: 60,
    },
    resetByType: {
      thread: { mode: "daily", atHour: 4 },
      direct: { mode: "idle", idleMinutes: 240 },
      group: { mode: "idle", idleMinutes: 120 },
    },
    resetTriggers: ["/new", "/reset"],
    store: "~/.openclaw/agents/{agentId}/sessions/sessions.json",
    parentForkMaxTokens: 100000, // skip parent-thread fork above this token count (0 disables)
    maintenance: {
      mode: "warn", // warn | enforce
      pruneAfter: "30d",
      maxEntries: 500,
      rotateBytes: "10mb",
      resetArchiveRetention: "30d", // duration or false
      maxDiskBytes: "500mb", // optional hard budget
      highWaterBytes: "400mb", // optional cleanup target
    },
    threadBindings: {
      enabled: true,
      idleHours: 24, // default inactivity auto-unfocus in hours (`0` disables)
      maxAgeHours: 0, // default hard max age in hours (`0` disables)
    },
    mainKey: "main", // legacy (runtime always uses "main")
    agentToAgent: { maxPingPongTurns: 5 },
    sendPolicy: {
      rules: [{ action: "deny", match: { channel: "discord", chatType: "group" } }],
      default: "allow",
    },
  },
}
```

<Accordion title="Szczegóły pól sesji">

- **`scope`**: podstawowa strategia grupowania sesji dla kontekstów czatów grupowych.
  - `per-sender` (domyślnie): każdy nadawca otrzymuje odizolowaną sesję w kontekście kanału.
  - `global`: wszyscy uczestnicy w kontekście kanału współdzielą jedną sesję (używaj tylko wtedy, gdy zamierzony jest współdzielony kontekst).
- **`dmScope`**: sposób grupowania DM.
  - `main`: wszystkie DM współdzielą główną sesję.
  - `per-peer`: izolacja według identyfikatora nadawcy między kanałami.
  - `per-channel-peer`: izolacja per kanał + nadawca (zalecane dla skrzynek odbiorczych wielu użytkowników).
  - `per-account-channel-peer`: izolacja per konto + kanał + nadawca (zalecane dla wielu kont).
- **`identityLinks`**: mapuje kanoniczne identyfikatory na peery z prefiksem dostawcy do współdzielenia sesji między kanałami.
- **`reset`**: główna polityka resetu. `daily` resetuje o `atHour` czasu lokalnego; `idle` resetuje po `idleMinutes`. Gdy skonfigurowane są oba, wygrywa to, które wygaśnie wcześniej.
- **`resetByType`**: nadpisania per typ (`direct`, `group`, `thread`). Starsze `dm` jest akceptowane jako alias dla `direct`.
- **`parentForkMaxTokens`**: maksymalna liczba `totalTokens` sesji nadrzędnej dozwolona przy tworzeniu rozwidlonej sesji wątku (domyślnie `100000`).
  - Jeśli `totalTokens` sesji nadrzędnej przekracza tę wartość, OpenClaw rozpoczyna świeżą sesję wątku zamiast dziedziczyć historię transkryptu sesji nadrzędnej.
  - Ustaw `0`, aby wyłączyć to zabezpieczenie i zawsze zezwalać na rozwidlanie z sesji nadrzędnej.
- **`mainKey`**: starsze pole. Runtime zawsze używa `"main"` dla głównego koszyka czatu bezpośredniego.
- **`agentToAgent.maxPingPongTurns`**: maksymalna liczba tur odpowiedzi zwrotnych między agentami podczas wymian agent-agent (liczba całkowita, zakres: `0`–`5`). `0` wyłącza łańcuchowanie ping-pong.
- **`sendPolicy`**: dopasowuje po `channel`, `chatType` (`direct|group|channel`, ze starszym aliasem `dm`), `keyPrefix` lub `rawKeyPrefix`. Pierwsze dopasowanie deny wygrywa.
- **`maintenance`**: kontrolki czyszczenia magazynu sesji + retencji.
  - `mode`: `warn` emituje tylko ostrzeżenia; `enforce` stosuje czyszczenie.
  - `pruneAfter`: granica wieku dla nieaktualnych wpisów (domyślnie `30d`).
  - `maxEntries`: maksymalna liczba wpisów w `sessions.json` (domyślnie `500`).
  - `rotateBytes`: rotuj `sessions.json`, gdy przekroczy ten rozmiar (domyślnie `10mb`).
  - `resetArchiveRetention`: retencja dla archiwów transkryptów `*.reset.<timestamp>`. Domyślnie taka jak `pruneAfter`; ustaw `false`, aby wyłączyć.
  - `maxDiskBytes`: opcjonalny limit miejsca na dysku dla katalogu sesji. W trybie `warn` zapisuje ostrzeżenia; w trybie `enforce` najpierw usuwa najstarsze artefakty/sesje.
  - `highWaterBytes`: opcjonalny cel po czyszczeniu limitu. Domyślnie `80%` wartości `maxDiskBytes`.
- **`threadBindings`**: globalne wartości domyślne dla funkcji sesji powiązanych z wątkami.
  - `enabled`: główny domyślny przełącznik (dostawcy mogą go nadpisywać; Discord używa `channels.discord.threadBindings.enabled`)
  - `idleHours`: domyślne automatyczne odpinanie po bezczynności w godzinach (`0` wyłącza; dostawcy mogą nadpisywać)
  - `maxAgeHours`: domyślny twardy maksymalny wiek w godzinach (`0` wyłącza; dostawcy mogą nadpisywać)

</Accordion>

---

## Wiadomości

```json5
{
  messages: {
    responsePrefix: "🦞", // or "auto"
    ackReaction: "👀",
    ackReactionScope: "group-mentions", // group-mentions | group-all | direct | all
    removeAckAfterReply: false,
    queue: {
      mode: "collect", // steer | followup | collect | steer-backlog | steer+backlog | queue | interrupt
      debounceMs: 1000,
      cap: 20,
      drop: "summarize", // old | new | summarize
      byChannel: {
        whatsapp: "collect",
        telegram: "collect",
      },
    },
    inbound: {
      debounceMs: 2000, // 0 disables
      byChannel: {
        whatsapp: 5000,
        slack: 1500,
      },
    },
  },
}
```

### Prefiks odpowiedzi

Nadpisania per kanał/konto: `channels.<channel>.responsePrefix`, `channels.<channel>.accounts.<id>.responsePrefix`.

Rozwiązywanie (wygrywa najbardziej szczegółowe): konto → kanał → globalne. `""` wyłącza i zatrzymuje kaskadę. `"auto"` wyprowadza `[{identity.name}]`.

**Zmienne szablonu:**

| Zmienna          | Opis                   | Przykład                    |
| ---------------- | ---------------------- | --------------------------- |
| `{model}`        | Krótka nazwa modelu    | `claude-opus-4-6`           |
| `{modelFull}`    | Pełny identyfikator modelu | `anthropic/claude-opus-4-6` |
| `{provider}`     | Nazwa dostawcy         | `anthropic`                 |
| `{thinkingLevel}` | Bieżący poziom thinking | `high`, `low`, `off`        |
| `{identity.name}` | Nazwa tożsamości agenta | (to samo co `"auto"`)       |

Zmienne nie rozróżniają wielkości liter. `{think}` jest aliasem dla `{thinkingLevel}`.

### Reakcja ack

- Domyślnie przyjmuje `identity.emoji` aktywnego agenta, w przeciwnym razie `"👀"`. Ustaw `""`, aby wyłączyć.
- Nadpisania per kanał: `channels.<channel>.ackReaction`, `channels.<channel>.accounts.<id>.ackReaction`.
- Kolejność rozwiązywania: konto → kanał → `messages.ackReaction` → fallback tożsamości.
- Zakres: `group-mentions` (domyślnie), `group-all`, `direct`, `all`.
- `removeAckAfterReply`: usuwa ack po odpowiedzi w Slack, Discord i Telegram.
- `messages.statusReactions.enabled`: włącza reakcje statusu cyklu życia w Slack, Discord i Telegram.
  W Slack i Discord brak ustawienia utrzymuje reakcje statusu włączone, gdy reakcje ack są aktywne.
  W Telegram ustaw to jawnie na `true`, aby włączyć reakcje statusu cyklu życia.

### Debounce przychodzący

Łączy szybkie wiadomości tekstowe od tego samego nadawcy w jedną turę agenta. Multimedia/załączniki są opróżniane natychmiast. Polecenia sterujące omijają debounce.

### TTS (text-to-speech)

```json5
{
  messages: {
    tts: {
      auto: "always", // off | always | inbound | tagged
      mode: "final", // final | all
      provider: "elevenlabs",
      summaryModel: "openai/gpt-4.1-mini",
      modelOverrides: { enabled: true },
      maxTextLength: 4000,
      timeoutMs: 30000,
      prefsPath: "~/.openclaw/settings/tts.json",
      elevenlabs: {
        apiKey: "elevenlabs_api_key",
        baseUrl: "https://api.elevenlabs.io",
        voiceId: "voice_id",
        modelId: "eleven_multilingual_v2",
        seed: 42,
        applyTextNormalization: "auto",
        languageCode: "en",
        voiceSettings: {
          stability: 0.5,
          similarityBoost: 0.75,
          style: 0.0,
          useSpeakerBoost: true,
          speed: 1.0,
        },
      },
      openai: {
        apiKey: "openai_api_key",
        baseUrl: "https://api.openai.com/v1",
        model: "gpt-4o-mini-tts",
        voice: "alloy",
      },
    },
  },
}
```

- `auto` kontroluje domyślny tryb auto-TTS: `off`, `always`, `inbound` lub `tagged`. `/tts on|off` może nadpisać lokalne preferencje, a `/tts status` pokazuje stan efektywny.
- `summaryModel` nadpisuje `agents.defaults.model.primary` dla automatycznego podsumowania.
- `modelOverrides` jest domyślnie włączone; `modelOverrides.allowProvider` ma domyślnie wartość `false` (opt-in).
- Klucze API wracają do `ELEVENLABS_API_KEY`/`XI_API_KEY` oraz `OPENAI_API_KEY`.
- `openai.baseUrl` nadpisuje punkt końcowy OpenAI TTS. Kolejność rozwiązywania to konfiguracja, następnie `OPENAI_TTS_BASE_URL`, a potem `https://api.openai.com/v1`.
- Gdy `openai.baseUrl` wskazuje punkt końcowy inny niż OpenAI, OpenClaw traktuje go jako serwer TTS zgodny z OpenAI i łagodzi walidację modelu/głosu.

---

## Talk

Wartości domyślne dla trybu Talk (macOS/iOS/Android).

```json5
{
  talk: {
    provider: "elevenlabs",
    providers: {
      elevenlabs: {
        voiceId: "elevenlabs_voice_id",
        voiceAliases: {
          Clawd: "EXAVITQu4vr4xnSDxMaL",
          Roger: "CwhRBWXzGAHq8TQ4Fs17",
        },
        modelId: "eleven_v3",
        outputFormat: "mp3_44100_128",
        apiKey: "elevenlabs_api_key",
      },
    },
    silenceTimeoutMs: 1500,
    interruptOnSpeech: true,
  },
}
```

- `talk.provider` musi odpowiadać kluczowi w `talk.providers`, gdy skonfigurowano wielu dostawców Talk.
- Starsze płaskie klucze Talk (`talk.voiceId`, `talk.voiceAliases`, `talk.modelId`, `talk.outputFormat`, `talk.apiKey`) służą wyłącznie zgodności i są automatycznie migrowane do `talk.providers.<provider>`.
- Identyfikatory głosów wracają do `ELEVENLABS_VOICE_ID` lub `SAG_VOICE_ID`.
- `providers.*.apiKey` akceptuje zwykłe ciągi znaków albo obiekty SecretRef.
- Zapasowa wartość `ELEVENLABS_API_KEY` ma zastosowanie tylko wtedy, gdy nie skonfigurowano klucza API Talk.
- `providers.*.voiceAliases` pozwala dyrektywom Talk używać przyjaznych nazw.
- `silenceTimeoutMs` kontroluje, jak długo tryb Talk czeka po ciszy użytkownika, zanim wyśle transkrypt. Brak ustawienia zachowuje domyślne okno pauzy platformy (`700 ms na macOS i Androidzie, 900 ms na iOS`).

---

## Narzędzia

### Profile narzędzi

`tools.profile` ustawia bazową listę dozwolonych przed `tools.allow`/`tools.deny`:

Lokalny onboarding domyślnie ustawia nowe lokalne konfiguracje na `tools.profile: "coding"`, gdy pole nie jest ustawione (istniejące jawne profile są zachowywane).

| Profil      | Zawiera                                                                                                                        |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `minimal`   | tylko `session_status`                                                                                                          |
| `coding`    | `group:fs`, `group:runtime`, `group:web`, `group:sessions`, `group:memory`, `cron`, `image`, `image_generate`, `video_generate` |
| `messaging` | `group:messaging`, `sessions_list`, `sessions_history`, `sessions_send`, `session_status`                                       |
| `full`      | Bez ograniczeń (tak samo jak brak ustawienia)                                                                                   |

### Grupy narzędzi

| Grupa              | Narzędzia                                                                                                                |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| `group:runtime`    | `exec`, `process`, `code_execution` (`bash` jest akceptowane jako alias dla `exec`)                                      |
| `group:fs`         | `read`, `write`, `edit`, `apply_patch`                                                                                   |
| `group:sessions`   | `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`, `sessions_yield`, `subagents`, `session_status` |
| `group:memory`     | `memory_search`, `memory_get`                                                                                            |
| `group:web`        | `web_search`, `x_search`, `web_fetch`                                                                                    |
| `group:ui`         | `browser`, `canvas`                                                                                                      |
| `group:automation` | `cron`, `gateway`                                                                                                        |
| `group:messaging`  | `message`                                                                                                                |
| `group:nodes`      | `nodes`                                                                                                                  |
| `group:agents`     | `agents_list`                                                                                                            |
| `group:media`      | `image`, `image_generate`, `video_generate`, `tts`                                                                       |
| `group:openclaw`   | Wszystkie wbudowane narzędzia (z wyłączeniem Pluginów dostawców)                                                         |

### `tools.allow` / `tools.deny`

Globalna polityka zezwalania/zabraniania narzędzi (deny wygrywa). Nierozróżniająca wielkości liter, obsługuje wildcardy `*`. Stosowana nawet wtedy, gdy sandbox Docker jest wyłączony.

```json5
{
  tools: { deny: ["browser", "canvas"] },
}
```

### `tools.byProvider`

Dodatkowo ogranicza narzędzia dla określonych dostawców lub modeli. Kolejność: profil bazowy → profil dostawcy → allow/deny.

```json5
{
  tools: {
    profile: "coding",
    byProvider: {
      "google-antigravity": { profile: "minimal" },
      "openai/gpt-5.4": { allow: ["group:fs", "sessions_list"] },
    },
  },
}
```

### `tools.elevated`

Kontroluje podwyższony dostęp `exec` poza sandbox:

```json5
{
  tools: {
    elevated: {
      enabled: true,
      allowFrom: {
        whatsapp: ["+15555550123"],
        discord: ["1234567890123", "987654321098765432"],
      },
    },
  },
}
```

- Nadpisanie per agent (`agents.list[].tools.elevated`) może tylko dalej ograniczać.
- `/elevated on|off|ask|full` zapisuje stan per sesja; dyrektywy inline dotyczą pojedynczej wiadomości.
- Podwyższone `exec` omija sandboxing i używa skonfigurowanej ścieżki ucieczki (`gateway` domyślnie albo `node`, gdy celem exec jest `node`).

### `tools.exec`

```json5
{
  tools: {
    exec: {
      backgroundMs: 10000,
      timeoutSec: 1800,
      cleanupMs: 1800000,
      notifyOnExit: true,
      notifyOnExitEmptySuccess: false,
      applyPatch: {
        enabled: false,
        allowModels: ["gpt-5.4"],
      },
    },
  },
}
```

### `tools.loopDetection`

Kontrole bezpieczeństwa pętli narzędzi są **domyślnie wyłączone**. Ustaw `enabled: true`, aby włączyć wykrywanie.
Ustawienia można zdefiniować globalnie w `tools.loopDetection` i nadpisywać per agent w `agents.list[].tools.loopDetection`.

```json5
{
  tools: {
    loopDetection: {
      enabled: true,
      historySize: 30,
      warningThreshold: 10,
      criticalThreshold: 20,
      globalCircuitBreakerThreshold: 30,
      detectors: {
        genericRepeat: true,
        knownPollNoProgress: true,
        pingPong: true,
      },
    },
  },
}
```

- `historySize`: maksymalna historia wywołań narzędzi zachowywana do analizy pętli.
- `warningThreshold`: próg powtarzającego się wzorca bez postępu dla ostrzeżeń.
- `criticalThreshold`: wyższy próg powtórzeń do blokowania krytycznych pętli.
- `globalCircuitBreakerThreshold`: próg twardego zatrzymania dla dowolnego przebiegu bez postępu.
- `detectors.genericRepeat`: ostrzegaj o powtarzanych wywołaniach tego samego narzędzia z tymi samymi argumentami.
- `detectors.knownPollNoProgress`: ostrzegaj/blokuj dla znanych narzędzi poll (`process.poll`, `command_status` itd.).
- `detectors.pingPong`: ostrzegaj/blokuj dla naprzemiennych wzorców par bez postępu.
- Jeśli `warningThreshold >= criticalThreshold` albo `criticalThreshold >= globalCircuitBreakerThreshold`, walidacja kończy się błędem.

### `tools.web`

```json5
{
  tools: {
    web: {
      search: {
        enabled: true,
        apiKey: "brave_api_key", // or BRAVE_API_KEY env
        maxResults: 5,
        timeoutSeconds: 30,
        cacheTtlMinutes: 15,
      },
      fetch: {
        enabled: true,
        provider: "firecrawl", // optional; omit for auto-detect
        maxChars: 50000,
        maxCharsCap: 50000,
        maxResponseBytes: 2000000,
        timeoutSeconds: 30,
        cacheTtlMinutes: 15,
        maxRedirects: 3,
        readability: true,
        userAgent: "custom-ua",
      },
    },
  },
}
```

### `tools.media`

Konfiguruje rozumienie mediów przychodzących (obraz/audio/wideo):

```json5
{
  tools: {
    media: {
      concurrency: 2,
      asyncCompletion: {
        directSend: false, // opt-in: send finished async music/video directly to the channel
      },
      audio: {
        enabled: true,
        maxBytes: 20971520,
        scope: {
          default: "deny",
          rules: [{ action: "allow", match: { chatType: "direct" } }],
        },
        models: [
          { provider: "openai", model: "gpt-4o-mini-transcribe" },
          { type: "cli", command: "whisper", args: ["--model", "base", "{{MediaPath}}"] },
        ],
      },
      video: {
        enabled: true,
        maxBytes: 52428800,
        models: [{ provider: "google", model: "gemini-3-flash-preview" }],
      },
    },
  },
}
```

<Accordion title="Pola wpisów modeli mediów">

**Wpis dostawcy** (`type: "provider"` lub pominięte):

- `provider`: identyfikator dostawcy API (`openai`, `anthropic`, `google`/`gemini`, `groq` itd.)
- `model`: nadpisanie identyfikatora modelu
- `profile` / `preferredProfile`: wybór profilu `auth-profiles.json`

**Wpis CLI** (`type: "cli"`):

- `command`: plik wykonywalny do uruchomienia
- `args`: argumenty szablonowe (obsługuje `{{MediaPath}}`, `{{Prompt}}`, `{{MaxChars}}` itd.)

**Pola wspólne:**

- `capabilities`: opcjonalna lista (`image`, `audio`, `video`). Domyślnie: `openai`/`anthropic`/`minimax` → image, `google` → image+audio+video, `groq` → audio.
- `prompt`, `maxChars`, `maxBytes`, `timeoutSeconds`, `language`: nadpisania per wpis.
- W przypadku błędów następuje przejście do kolejnego wpisu.

Uwierzytelnianie dostawców odbywa się według standardowej kolejności: `auth-profiles.json` → zmienne środowiskowe → `models.providers.*.apiKey`.

**Pola asynchronicznego ukończenia:**

- `asyncCompletion.directSend`: gdy `true`, ukończone asynchroniczne zadania `music_generate`
  i `video_generate` najpierw próbują bezpośredniego dostarczenia do kanału. Domyślnie: `false`
  (starsza ścieżka wybudzenia sesji żądającego/dostarczenia modelu).

</Accordion>

### `tools.agentToAgent`

```json5
{
  tools: {
    agentToAgent: {
      enabled: false,
      allow: ["home", "work"],
    },
  },
}
```

### `tools.sessions`

Kontroluje, które sesje mogą być celem dla narzędzi sesji (`sessions_list`, `sessions_history`, `sessions_send`).

Domyślnie: `tree` (bieżąca sesja + sesje uruchomione przez nią, takie jak subagenci).

```json5
{
  tools: {
    sessions: {
      // "self" | "tree" | "agent" | "all"
      visibility: "tree",
    },
  },
}
```

Uwagi:

- `self`: tylko bieżący klucz sesji.
- `tree`: bieżąca sesja + sesje uruchomione przez bieżącą sesję (subagenci).
- `agent`: dowolna sesja należąca do bieżącego identyfikatora agenta (może obejmować innych użytkowników, jeśli uruchamiasz sesje per nadawca pod tym samym identyfikatorem agenta).
- `all`: dowolna sesja. Kierowanie między agentami nadal wymaga `tools.agentToAgent`.
- Ograniczenie sandbox: gdy bieżąca sesja jest objęta sandboxem i `agents.defaults.sandbox.sessionToolsVisibility="spawned"`, widoczność jest wymuszana na `tree`, nawet jeśli `tools.sessions.visibility="all"`.

### `tools.sessions_spawn`

Kontroluje obsługę załączników inline dla `sessions_spawn`.

```json5
{
  tools: {
    sessions_spawn: {
      attachments: {
        enabled: false, // opt-in: set true to allow inline file attachments
        maxTotalBytes: 5242880, // 5 MB total across all files
        maxFiles: 50,
        maxFileBytes: 1048576, // 1 MB per file
        retainOnSessionKeep: false, // keep attachments when cleanup="keep"
      },
    },
  },
}
```

Uwagi:

- Załączniki są obsługiwane tylko dla `runtime: "subagent"`. Runtime ACP je odrzuca.
- Pliki są materializowane w obszarze roboczym dziecka w `.openclaw/attachments/<uuid>/` z `.manifest.json`.
- Treść załączników jest automatycznie redagowana z trwałości transkryptu.
- Wejścia base64 są walidowane przy użyciu ścisłych kontroli alfabetu/dopełnienia oraz zabezpieczenia rozmiaru przed dekodowaniem.
- Uprawnienia plików to `0700` dla katalogów i `0600` dla plików.
- Czyszczenie podąża za polityką `cleanup`: `delete` zawsze usuwa załączniki; `keep` zachowuje je tylko wtedy, gdy `retainOnSessionKeep: true`.

### `tools.experimental`

Flagi eksperymentalnych wbudowanych narzędzi. Domyślnie wyłączone, chyba że zastosowanie ma reguła automatycznego włączania strict-agentic GPT-5.

```json5
{
  tools: {
    experimental: {
      planTool: true, // enable experimental update_plan
    },
  },
}
```

Uwagi:

- `planTool`: włącza strukturalne narzędzie `update_plan` do śledzenia nietrywialnej pracy wieloetapowej.
- Domyślnie: `false`, chyba że `agents.defaults.embeddedPi.executionContract` (albo nadpisanie per agent) jest ustawione na `"strict-agentic"` dla przebiegu OpenAI lub OpenAI Codex z rodziny GPT-5. Ustaw `true`, aby wymusić narzędzie poza tym zakresem, albo `false`, aby pozostawić je wyłączone nawet dla przebiegów strict-agentic GPT-5.
- Gdy włączone, system prompt dodaje także wskazówki użycia, aby model używał go tylko do istotnej pracy i utrzymywał najwyżej jeden krok `in_progress`.

### `agents.defaults.subagents`

```json5
{
  agents: {
    defaults: {
      subagents: {
        allowAgents: ["research"],
        model: "minimax/MiniMax-M2.7",
        maxConcurrent: 8,
        runTimeoutSeconds: 900,
        archiveAfterMinutes: 60,
      },
    },
  },
}
```

- `model`: domyślny model dla uruchomionych subagentów. Jeśli pominięte, subagenci dziedziczą model wywołującego.
- `allowAgents`: domyślna lista dozwolonych docelowych identyfikatorów agentów dla `sessions_spawn`, gdy agent żądający nie ustawia własnego `subagents.allowAgents` (`["*"]` = dowolny; domyślnie: tylko ten sam agent).
- `runTimeoutSeconds`: domyślny limit czasu (sekundy) dla `sessions_spawn`, gdy wywołanie narzędzia pomija `runTimeoutSeconds`. `0` oznacza brak limitu czasu.
- Polityka narzędzi per subagent: `tools.subagents.tools.allow` / `tools.subagents.tools.deny`.

---

## Niestandardowi dostawcy i base URL

OpenClaw używa wbudowanego katalogu modeli. Dodaj niestandardowych dostawców przez `models.providers` w konfiguracji albo `~/.openclaw/agents/<agentId>/agent/models.json`.

```json5
{
  models: {
    mode: "merge", // merge (default) | replace
    providers: {
      "custom-proxy": {
        baseUrl: "http://localhost:4000/v1",
        apiKey: "LITELLM_KEY",
        api: "openai-completions", // openai-completions | openai-responses | anthropic-messages | google-generative-ai
        models: [
          {
            id: "llama-3.1-8b",
            name: "Llama 3.1 8B",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 128000,
            contextTokens: 96000,
            maxTokens: 32000,
          },
        ],
      },
    },
  },
}
```

- Użyj `authHeader: true` + `headers` dla niestandardowych potrzeb uwierzytelniania.
- Nadpisz katalog główny konfiguracji agenta przez `OPENCLAW_AGENT_DIR` (lub `PI_CODING_AGENT_DIR`, starszy alias zmiennej środowiskowej).
- Priorytet scalania dla pasujących identyfikatorów dostawców:
  - Niepuste wartości `baseUrl` w agent `models.json` mają pierwszeństwo.
  - Niepuste wartości `apiKey` agenta mają pierwszeństwo tylko wtedy, gdy ten dostawca nie jest zarządzany przez SecretRef w bieżącym kontekście config/auth-profile.
  - Wartości `apiKey` dostawców zarządzanych przez SecretRef są odświeżane ze znaczników źródła (`ENV_VAR_NAME` dla referencji env, `secretref-managed` dla referencji file/exec) zamiast utrwalania rozwiązanych sekretów.
  - Wartości nagłówków dostawców zarządzanych przez SecretRef są odświeżane ze znaczników źródła (`secretref-env:ENV_VAR_NAME` dla referencji env, `secretref-managed` dla referencji file/exec).
  - Puste lub brakujące `apiKey`/`baseUrl` agenta wracają do `models.providers` w konfiguracji.
  - Pasujące `contextWindow`/`maxTokens` modelu używają wyższej wartości spośród jawnej konfiguracji i niejawnych wartości katalogu.
  - Pasujące `contextTokens` modelu zachowuje jawny limit runtime, gdy jest obecny; użyj go, aby ograniczyć efektywny kontekst bez zmieniania natywnych metadanych modelu.
  - Użyj `models.mode: "replace"`, gdy chcesz, aby konfiguracja całkowicie nadpisała `models.json`.
  - Utrwalanie znaczników jest autorytatywne względem źródła: znaczniki są zapisywane z aktywnej migawki konfiguracji źródłowej (przed rozwiązaniem), a nie z rozwiązanych wartości sekretów runtime.

### Szczegóły pól dostawcy

- `models.mode`: zachowanie katalogu dostawców (`merge` lub `replace`).
- `models.providers`: mapa niestandardowych dostawców kluczowana identyfikatorem dostawcy.
- `models.providers.*.api`: adapter żądań (`openai-completions`, `openai-responses`, `anthropic-messages`, `google-generative-ai` itd.).
- `models.providers.*.apiKey`: poświadczenie dostawcy (preferowane SecretRef/podstawienie env).
- `models.providers.*.auth`: strategia uwierzytelniania (`api-key`, `token`, `oauth`, `aws-sdk`).
- `models.providers.*.injectNumCtxForOpenAICompat`: dla Ollama + `openai-completions`, wstrzykuje `options.num_ctx` do żądań (domyślnie: `true`).
- `models.providers.*.authHeader`: wymusza przesyłanie poświadczeń w nagłówku `Authorization`, gdy jest to wymagane.
- `models.providers.*.baseUrl`: bazowy adres URL nadrzędnego API.
- `models.providers.*.headers`: dodatkowe statyczne nagłówki do routingu proxy/tenant.
- `models.providers.*.request`: nadpisania transportu dla żądań HTTP model-provider.
  - `request.headers`: dodatkowe nagłówki (scalane z domyślnymi dostawcy). Wartości akceptują SecretRef.
  - `request.auth`: nadpisanie strategii uwierzytelniania. Tryby: `"provider-default"` (użyj wbudowanego uwierzytelniania dostawcy), `"authorization-bearer"` (z `token`), `"header"` (z `headerName`, `value`, opcjonalnym `prefix`).
  - `request.proxy`: nadpisanie proxy HTTP. Tryby: `"env-proxy"` (użyj zmiennych środowiskowych `HTTP_PROXY`/`HTTPS_PROXY`), `"explicit-proxy"` (z `url`). Oba tryby akceptują opcjonalny podobiekt `tls`.
  - `request.tls`: nadpisanie TLS dla połączeń bezpośrednich. Pola: `ca`, `cert`, `key`, `passphrase` (wszystkie akceptują SecretRef), `serverName`, `insecureSkipVerify`.
  - `request.allowPrivateNetwork`: gdy `true`, zezwala na HTTPS do `baseUrl`, gdy DNS rozwiązuje do prywatnych, CGNAT lub podobnych zakresów, przez zabezpieczenie pobierania HTTP dostawcy (opt-in operatora dla zaufanych, samohostowanych punktów końcowych zgodnych z OpenAI). WebSocket używa tego samego `request` dla nagłówków/TLS, ale nie dla tej bramki SSRF fetch. Domyślnie `false`.
- `models.providers.*.models`: jawne wpisy katalogu modeli dostawcy.
- `models.providers.*.models.*.contextWindow`: metadane natywnego okna kontekstu modelu.
- `models.providers.*.models.*.contextTokens`: opcjonalny limit kontekstu runtime. Użyj tego, gdy chcesz mniejszego efektywnego budżetu kontekstu niż natywne `contextWindow` modelu.
- `models.providers.*.models.*.compat.supportsDeveloperRole`: opcjonalna wskazówka zgodności. Dla `api: "openai-completions"` z niepustym, nienatywnym `baseUrl` (host inny niż `api.openai.com`) OpenClaw wymusza w runtime wartość `false`. Puste/pominięte `baseUrl` zachowuje domyślne zachowanie OpenAI.
- `models.providers.*.models.*.compat.requiresStringContent`: opcjonalna wskazówka zgodności dla punktów końcowych czatu zgodnych z OpenAI, które obsługują tylko ciągi znaków. Gdy `true`, OpenClaw spłaszcza czysto tekstowe tablice `messages[].content` do zwykłych ciągów przed wysłaniem żądania.
- `plugins.entries.amazon-bedrock.config.discovery`: główny katalog ustawień automatycznego wykrywania Bedrock.
- `plugins.entries.amazon-bedrock.config.discovery.enabled`: włącz/wyłącz niejawne wykrywanie.
- `plugins.entries.amazon-bedrock.config.discovery.region`: region AWS do wykrywania.
- `plugins.entries.amazon-bedrock.config.discovery.providerFilter`: opcjonalny filtr identyfikatora dostawcy dla wykrywania ukierunkowanego.
- `plugins.entries.amazon-bedrock.config.discovery.refreshInterval`: interwał odpytywania dla odświeżania wykrywania.
- `plugins.entries.amazon-bedrock.config.discovery.defaultContextWindow`: zapasowe okno kontekstu dla wykrytych modeli.
- `plugins.entries.amazon-bedrock.config.discovery.defaultMaxTokens`: zapasowa maksymalna liczba tokenów wyjściowych dla wykrytych modeli.

### Przykłady dostawców

<Accordion title="Cerebras (GLM 4.6 / 4.7)">

```json5
{
  env: { CEREBRAS_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: {
        primary: "cerebras/zai-glm-4.7",
        fallbacks: ["cerebras/zai-glm-4.6"],
      },
      models: {
        "cerebras/zai-glm-4.7": { alias: "GLM 4.7 (Cerebras)" },
        "cerebras/zai-glm-4.6": { alias: "GLM 4.6 (Cerebras)" },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      cerebras: {
        baseUrl: "https://api.cerebras.ai/v1",
        apiKey: "${CEREBRAS_API_KEY}",
        api: "openai-completions",
        models: [
          { id: "zai-glm-4.7", name: "GLM 4.7 (Cerebras)" },
          { id: "zai-glm-4.6", name: "GLM 4.6 (Cerebras)" },
        ],
      },
    },
  },
}
```

Użyj `cerebras/zai-glm-4.7` dla Cerebras; `zai/glm-4.7` dla bezpośredniego Z.AI.

</Accordion>

<Accordion title="OpenCode">

```json5
{
  agents: {
    defaults: {
      model: { primary: "opencode/claude-opus-4-6" },
      models: { "opencode/claude-opus-4-6": { alias: "Opus" } },
    },
  },
}
```

Ustaw `OPENCODE_API_KEY` (lub `OPENCODE_ZEN_API_KEY`). Używaj odwołań `opencode/...` dla katalogu Zen albo odwołań `opencode-go/...` dla katalogu Go. Skrót: `openclaw onboard --auth-choice opencode-zen` albo `openclaw onboard --auth-choice opencode-go`.

</Accordion>

<Accordion title="Z.AI (GLM-4.7)">

```json5
{
  agents: {
    defaults: {
      model: { primary: "zai/glm-4.7" },
      models: { "zai/glm-4.7": {} },
    },
  },
}
```

Ustaw `ZAI_API_KEY`. `z.ai/*` i `z-ai/*` są akceptowanymi aliasami. Skrót: `openclaw onboard --auth-choice zai-api-key`.

- Ogólny punkt końcowy: `https://api.z.ai/api/paas/v4`
- Punkt końcowy do kodowania (domyślny): `https://api.z.ai/api/coding/paas/v4`
- Dla ogólnego punktu końcowego zdefiniuj niestandardowego dostawcę z nadpisaniem base URL.

</Accordion>

<Accordion title="Moonshot AI (Kimi)">

```json5
{
  env: { MOONSHOT_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "moonshot/kimi-k2.5" },
      models: { "moonshot/kimi-k2.5": { alias: "Kimi K2.5" } },
    },
  },
  models: {
    mode: "merge",
    providers: {
      moonshot: {
        baseUrl: "https://api.moonshot.ai/v1",
        apiKey: "${MOONSHOT_API_KEY}",
        api: "openai-completions",
        models: [
          {
            id: "kimi-k2.5",
            name: "Kimi K2.5",
            reasoning: false,
            input: ["text", "image"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 262144,
            maxTokens: 262144,
          },
        ],
      },
    },
  },
}
```

Dla punktu końcowego China: `baseUrl: "https://api.moonshot.cn/v1"` albo `openclaw onboard --auth-choice moonshot-api-key-cn`.

Natywne punkty końcowe Moonshot ogłaszają zgodność użycia strumieniowania na współdzielonym
transporcie `openai-completions`, a OpenClaw opiera to na możliwościach punktu końcowego,
a nie wyłącznie na wbudowanym identyfikatorze dostawcy.

</Accordion>

<Accordion title="Kimi Coding">

```json5
{
  env: { KIMI_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "kimi/kimi-code" },
      models: { "kimi/kimi-code": { alias: "Kimi Code" } },
    },
  },
}
```

Zgodny z Anthropic, wbudowany dostawca. Skrót: `openclaw onboard --auth-choice kimi-code-api-key`.

</Accordion>

<Accordion title="Synthetic (zgodny z Anthropic)">

```json5
{
  env: { SYNTHETIC_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "synthetic/hf:MiniMaxAI/MiniMax-M2.5" },
      models: { "synthetic/hf:MiniMaxAI/MiniMax-M2.5": { alias: "MiniMax M2.5" } },
    },
  },
  models: {
    mode: "merge",
    providers: {
      synthetic: {
        baseUrl: "https://api.synthetic.new/anthropic",
        apiKey: "${SYNTHETIC_API_KEY}",
        api: "anthropic-messages",
        models: [
          {
            id: "hf:MiniMaxAI/MiniMax-M2.5",
            name: "MiniMax M2.5",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 192000,
            maxTokens: 65536,
          },
        ],
      },
    },
  },
}
```

Base URL powinien pomijać `/v1` (klient Anthropic dopisuje je sam). Skrót: `openclaw onboard --auth-choice synthetic-api-key`.

</Accordion>

<Accordion title="MiniMax M2.7 (bezpośrednio)">

```json5
{
  agents: {
    defaults: {
      model: { primary: "minimax/MiniMax-M2.7" },
      models: {
        "minimax/MiniMax-M2.7": { alias: "Minimax" },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      minimax: {
        baseUrl: "https://api.minimax.io/anthropic",
        apiKey: "${MINIMAX_API_KEY}",
        api: "anthropic-messages",
        models: [
          {
            id: "MiniMax-M2.7",
            name: "MiniMax M2.7",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0.3, output: 1.2, cacheRead: 0.06, cacheWrite: 0.375 },
            contextWindow: 204800,
            maxTokens: 131072,
          },
        ],
      },
    },
  },
}
```

Ustaw `MINIMAX_API_KEY`. Skróty:
`openclaw onboard --auth-choice minimax-global-api` albo
`openclaw onboard --auth-choice minimax-cn-api`.
Katalog modeli domyślnie obejmuje tylko M2.7.
Na ścieżce strumieniowania zgodnej z Anthropic OpenClaw domyślnie wyłącza thinking MiniMax,
chyba że jawnie ustawisz `thinking`. `/fast on` albo
`params.fastMode: true` przepisuje `MiniMax-M2.7` na
`MiniMax-M2.7-highspeed`.

</Accordion>

<Accordion title="Modele lokalne (LM Studio)">

Zobacz [Local Models](/pl/gateway/local-models). W skrócie: uruchom duży model lokalny przez LM Studio Responses API na odpowiednio wydajnym sprzęcie; zachowaj modele hostowane scalone jako fallback.

</Accordion>

---

## Skills

```json5
{
  skills: {
    allowBundled: ["gemini", "peekaboo"],
    load: {
      extraDirs: ["~/Projects/agent-scripts/skills"],
    },
    install: {
      preferBrew: true,
      nodeManager: "npm", // npm | pnpm | yarn | bun
    },
    entries: {
      "image-lab": {
        apiKey: { source: "env", provider: "default", id: "GEMINI_API_KEY" }, // or plaintext string
        env: { GEMINI_API_KEY: "GEMINI_KEY_HERE" },
      },
      peekaboo: { enabled: true },
      sag: { enabled: false },
    },
  },
}
```

- `allowBundled`: opcjonalna lista dozwolonych tylko dla bundled skills (Skills zarządzane/workspace pozostają bez zmian).
- `load.extraDirs`: dodatkowe współdzielone katalogi główne Skills (najniższy priorytet).
- `install.preferBrew`: gdy true, preferuje instalatory Homebrew, gdy `brew` jest
  dostępne, zanim wróci do innych rodzajów instalatorów.
- `install.nodeManager`: preferencja instalatora node dla specyfikacji `metadata.openclaw.install`
  (`npm` | `pnpm` | `yarn` | `bun`).
- `entries.<skillKey>.enabled: false` wyłącza Skill nawet wtedy, gdy jest bundled/zainstalowany.
- `entries.<skillKey>.apiKey`: wygodny skrót dla Skills deklarujących podstawową zmienną env (zwykły ciąg znaków albo obiekt SecretRef).

---

## Pluginy

```json5
{
  plugins: {
    enabled: true,
    allow: ["voice-call"],
    deny: [],
    load: {
      paths: ["~/Projects/oss/voice-call-extension"],
    },
    entries: {
      "voice-call": {
        enabled: true,
        hooks: {
          allowPromptInjection: false,
        },
        config: { provider: "twilio" },
      },
    },
  },
}
```

- Ładowane z `~/.openclaw/extensions`, `<workspace>/.openclaw/extensions` oraz `plugins.load.paths`.
- Wykrywanie akceptuje natywne Pluginy OpenClaw oraz zgodne bundlery Codex i Claude, w tym bundlery Claude w domyślnym układzie bez manifestu.
- **Zmiany konfiguracji wymagają restartu Gateway.**
- `allow`: opcjonalna lista dozwolonych (ładują się tylko wymienione Pluginy). `deny` ma pierwszeństwo.
- `plugins.entries.<id>.apiKey`: wygodne pole klucza API na poziomie Pluginu (gdy obsługiwane przez Plugin).
- `plugins.entries.<id>.env`: mapa zmiennych środowiskowych o zakresie Pluginu.
- `plugins.entries.<id>.hooks.allowPromptInjection`: gdy `false`, rdzeń blokuje `before_prompt_build` i ignoruje pola mutujące prompt ze starszego `before_agent_start`, zachowując starsze `modelOverride` i `providerOverride`. Dotyczy natywnych hooków Pluginów i obsługiwanych katalogów hooków dostarczanych przez bundle.
- `plugins.entries.<id>.subagent.allowModelOverride`: jawnie ufa temu Pluginowi, że może żądać nadpisań `provider` i `model` per uruchomienie dla przebiegów subagentów w tle.
- `plugins.entries.<id>.subagent.allowedModels`: opcjonalna lista dozwolonych kanonicznych celów `provider/model` dla zaufanych nadpisań subagentów. Używaj `"*"` tylko wtedy, gdy celowo chcesz zezwolić na dowolny model.
- `plugins.entries.<id>.config`: obiekt konfiguracji zdefiniowany przez Plugin (walidowany przez natywny schemat Pluginów OpenClaw, gdy jest dostępny).
- `plugins.entries.firecrawl.config.webFetch`: ustawienia dostawcy pobierania web Firecrawl.
  - `apiKey`: klucz API Firecrawl (akceptuje SecretRef). Wartość zapasowa pochodzi z `plugins.entries.firecrawl.config.webSearch.apiKey`, starszego `tools.web.fetch.firecrawl.apiKey` albo zmiennej środowiskowej `FIRECRAWL_API_KEY`.
  - `baseUrl`: bazowy adres URL API Firecrawl (domyślnie: `https://api.firecrawl.dev`).
  - `onlyMainContent`: wyodrębniaj tylko główną treść ze stron (domyślnie: `true`).
  - `maxAgeMs`: maksymalny wiek cache w milisekundach (domyślnie: `172800000` / 2 dni).
  - `timeoutSeconds`: limit czasu żądania scrapingu w sekundach (domyślnie: `60`).
- `plugins.entries.xai.config.xSearch`: ustawienia xAI X Search (wyszukiwanie web Grok).
  - `enabled`: włącza dostawcę X Search.
  - `model`: model Grok używany do wyszukiwania (np. `"grok-4-1-fast"`).
- `plugins.entries.memory-core.config.dreaming`: ustawienia memory dreaming. Fazy i progi znajdziesz w [Dreaming](/pl/concepts/dreaming).
  - `enabled`: główny przełącznik dreaming (domyślnie `false`).
  - `frequency`: harmonogram Cron dla każdego pełnego przebiegu dreaming (domyślnie `"0 3 * * *"`).
  - polityka faz i progi są szczegółami implementacji (nie są kluczami konfiguracji widocznymi dla użytkownika).
- Pełna konfiguracja pamięci znajduje się w [Odwołaniu do konfiguracji pamięci](/pl/reference/memory-config):
  - `agents.defaults.memorySearch.*`
  - `memory.backend`
  - `memory.citations`
  - `memory.qmd.*`
  - `plugins.entries.memory-core.config.dreaming`
- Włączone Pluginy bundli Claude mogą także wnosić osadzone domyślne ustawienia Pi z `settings.json`; OpenClaw stosuje je jako oczyszczone ustawienia agentów, a nie jako surowe patche konfiguracji OpenClaw.
- `plugins.slots.memory`: wybiera identyfikator aktywnego Pluginu pamięci albo `"none"`, aby wyłączyć Pluginy pamięci.
- `plugins.slots.contextEngine`: wybiera identyfikator aktywnego Pluginu silnika kontekstu; domyślnie `"legacy"`, chyba że zainstalujesz i wybierzesz inny silnik.
- `plugins.installs`: metadane instalacji zarządzane przez CLI używane przez `openclaw plugins update`.
  - Obejmuje `source`, `spec`, `sourcePath`, `installPath`, `version`, `resolvedName`, `resolvedVersion`, `resolvedSpec`, `integrity`, `shasum`, `resolvedAt`, `installedAt`.
  - Traktuj `plugins.installs.*` jako stan zarządzany; preferuj polecenia CLI zamiast ręcznych edycji.

Zobacz [Plugins](/pl/tools/plugin).

---

## Przeglądarka

```json5
{
  browser: {
    enabled: true,
    evaluateEnabled: true,
    defaultProfile: "user",
    ssrfPolicy: {
      // dangerouslyAllowPrivateNetwork: true, // opt in only for trusted private-network access
      // allowPrivateNetwork: true, // legacy alias
      // hostnameAllowlist: ["*.example.com", "example.com"],
      // allowedHostnames: ["localhost"],
    },
    profiles: {
      openclaw: { cdpPort: 18800, color: "#FF4500" },
      work: { cdpPort: 18801, color: "#0066CC" },
      user: { driver: "existing-session", attachOnly: true, color: "#00AA00" },
      brave: {
        driver: "existing-session",
        attachOnly: true,
        userDataDir: "~/Library/Application Support/BraveSoftware/Brave-Browser",
        color: "#FB542B",
      },
      remote: { cdpUrl: "http://10.0.0.42:9222", color: "#00AA00" },
    },
    color: "#FF4500",
    // headless: false,
    // noSandbox: false,
    // extraArgs: [],
    // executablePath: "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    // attachOnly: false,
  },
}
```

- `evaluateEnabled: false` wyłącza `act:evaluate` i `wait --fn`.
- `ssrfPolicy.dangerouslyAllowPrivateNetwork` jest wyłączone, gdy nie jest ustawione, więc nawigacja przeglądarki domyślnie pozostaje ścisła.
- Ustaw `ssrfPolicy.dangerouslyAllowPrivateNetwork: true` tylko wtedy, gdy celowo ufasz nawigacji przeglądarki po sieci prywatnej.
- W trybie ścisłym zdalne punkty końcowe profilu CDP (`profiles.*.cdpUrl`) podlegają temu samemu blokowaniu sieci prywatnej podczas kontroli osiągalności/wykrywania.
- `ssrfPolicy.allowPrivateNetwork` pozostaje obsługiwane jako starszy alias.
- W trybie ścisłym używaj `ssrfPolicy.hostnameAllowlist` i `ssrfPolicy.allowedHostnames` dla jawnych wyjątków.
- Zdalne profile są tylko do podłączania (start/stop/reset są wyłączone).
- `profiles.*.cdpUrl` akceptuje `http://`, `https://`, `ws://` i `wss://`.
  Używaj HTTP(S), gdy chcesz, aby OpenClaw wykrył `/json/version`; używaj WS(S),
  gdy dostawca daje bezpośredni adres URL WebSocket DevTools.
- Profile `existing-session` są tylko dla hosta i używają Chrome MCP zamiast CDP.
- Profile `existing-session` mogą ustawiać `userDataDir`, aby wskazać określony
  profil przeglądarki opartej na Chromium, taki jak Brave albo Edge.
- Profile `existing-session` zachowują bieżące ograniczenia ścieżki Chrome MCP:
  działania oparte na snapshot/ref zamiast targetowania selektorem CSS, hooki
  przesyłania jednego pliku, brak nadpisań limitu czasu dialogów, brak `wait --load networkidle`
  oraz brak `responsebody`, eksportu PDF, przechwytywania pobrań ani działań wsadowych.
- Lokalnie zarządzane profile `openclaw` automatycznie przypisują `cdpPort` i `cdpUrl`; jawnie
  ustawiaj `cdpUrl` tylko dla zdalnego CDP.
- Kolejność automatycznego wykrywania: domyślna przeglądarka, jeśli jest oparta na Chromium → Chrome → Brave → Edge → Chromium → Chrome Canary.
- Usługa sterowania: tylko loopback (port wyprowadzany z `gateway.port`, domyślnie `18791`).
- `extraArgs` dopisuje dodatkowe flagi uruchamiania do lokalnego startu Chromium (na przykład
  `--disable-gpu`, rozmiar okna albo flagi debugowania).

---

## UI

```json5
{
  ui: {
    seamColor: "#FF4500",
    assistant: {
      name: "OpenClaw",
      avatar: "CB", // emoji, short text, image URL, or data URI
    },
  },
}
```

- `seamColor`: kolor akcentu dla chromu natywnego UI aplikacji (odcień dymku trybu Talk itd.).
- `assistant`: nadpisanie tożsamości interfejsu Control UI. Wartość zapasowa pochodzi z aktywnej tożsamości agenta.

---

## Gateway

```json5
{
  gateway: {
    mode: "local", // local | remote
    port: 18789,
    bind: "loopback",
    auth: {
      mode: "token", // none | token | password | trusted-proxy
      token: "your-token",
      // password: "your-password", // or OPENCLAW_GATEWAY_PASSWORD
      // trustedProxy: { userHeader: "x-forwarded-user" }, // for mode=trusted-proxy; see /gateway/trusted-proxy-auth
      allowTailscale: true,
      rateLimit: {
        maxAttempts: 10,
        windowMs: 60000,
        lockoutMs: 300000,
        exemptLoopback: true,
      },
    },
    tailscale: {
      mode: "off", // off | serve | funnel
      resetOnExit: false,
    },
    controlUi: {
      enabled: true,
      basePath: "/openclaw",
      // root: "dist/control-ui",
      // embedSandbox: "scripts", // strict | scripts | trusted
      // allowExternalEmbedUrls: false, // dangerous: allow absolute external http(s) embed URLs
      // allowedOrigins: ["https://control.example.com"], // required for non-loopback Control UI
      // dangerouslyAllowHostHeaderOriginFallback: false, // dangerous Host-header origin fallback mode
      // allowInsecureAuth: false,
      // dangerouslyDisableDeviceAuth: false,
    },
    remote: {
      url: "ws://gateway.tailnet:18789",
      transport: "ssh", // ssh | direct
      token: "your-token",
      // password: "your-password",
    },
    trustedProxies: ["10.0.0.1"],
    // Optional. Default false.
    allowRealIpFallback: false,
    tools: {
      // Additional /tools/invoke HTTP denies
      deny: ["browser"],
      // Remove tools from the default HTTP deny list
      allow: ["gateway"],
    },
    push: {
      apns: {
        relay: {
          baseUrl: "https://relay.example.com",
          timeoutMs: 10000,
        },
      },
    },
  },
}
```

<Accordion title="Szczegóły pól Gateway">

- `mode`: `local` (uruchom Gateway) albo `remote` (połącz ze zdalnym Gateway). Gateway odmawia uruchomienia, jeśli nie jest to `local`.
- `port`: pojedynczy multipleksowany port dla WS + HTTP. Priorytet: `--port` > `OPENCLAW_GATEWAY_PORT` > `gateway.port` > `18789`.
- `bind`: `auto`, `loopback` (domyślnie), `lan` (`0.0.0.0`), `tailnet` (tylko adres IP Tailscale) albo `custom`.
- **Starsze aliasy bind**: używaj wartości trybu bind w `gateway.bind` (`auto`, `loopback`, `lan`, `tailnet`, `custom`), a nie aliasów hosta (`0.0.0.0`, `127.0.0.1`, `localhost`, `::`, `::1`).
- **Uwaga dotycząca Docker**: domyślne wiązanie `loopback` nasłuchuje na `127.0.0.1` wewnątrz kontenera. Przy sieci bridge Dockera (`-p 18789:18789`) ruch dociera przez `eth0`, więc Gateway jest nieosiągalny. Użyj `--network host` albo ustaw `bind: "lan"` (lub `bind: "custom"` z `customBindHost: "0.0.0.0"`), aby nasłuchiwać na wszystkich interfejsach.
- **Auth**: domyślnie wymagane. Wiązania inne niż loopback wymagają uwierzytelniania Gateway. W praktyce oznacza to współdzielony token/hasło albo proxy reverse proxy świadome tożsamości z `gateway.auth.mode: "trusted-proxy"`. Kreator onboardingu domyślnie generuje token.
- Jeśli zarówno `gateway.auth.token`, jak i `gateway.auth.password` są skonfigurowane (w tym przez SecretRefs), ustaw jawnie `gateway.auth.mode` na `token` albo `password`. Uruchamianie oraz przepływy instalacji/naprawy usługi kończą się błędem, gdy oba są skonfigurowane, a tryb nie jest ustawiony.
- `gateway.auth.mode: "none"`: jawny tryb bez uwierzytelniania. Używaj tylko dla zaufanych lokalnych konfiguracji local loopback; ten tryb celowo nie jest oferowany w promptach onboardingu.
- `gateway.auth.mode: "trusted-proxy"`: deleguj uwierzytelnianie do reverse proxy świadomego tożsamości i ufaj nagłówkom tożsamości z `gateway.trustedProxies` (zobacz [Trusted Proxy Auth](/pl/gateway/trusted-proxy-auth)). Ten tryb oczekuje źródła proxy **innego niż loopback**; reverse proxy loopback na tym samym hoście nie spełniają wymagań uwierzytelniania trusted-proxy.
- `gateway.auth.allowTailscale`: gdy `true`, nagłówki tożsamości Tailscale Serve mogą spełniać uwierzytelnianie Control UI/WebSocket (weryfikowane przez `tailscale whois`). Punkty końcowe HTTP API **nie** używają tego uwierzytelniania nagłówkami Tailscale; zamiast tego stosują zwykły tryb uwierzytelniania HTTP Gateway. Ten przepływ bez tokena zakłada, że host Gateway jest zaufany. Domyślnie `true`, gdy `tailscale.mode = "serve"`.
- `gateway.auth.rateLimit`: opcjonalny ogranicznik nieudanych prób uwierzytelniania. Stosowany per adres IP klienta i per zakres uwierzytelniania (współdzielony sekret i token urządzenia są śledzone niezależnie). Zablokowane próby zwracają `429` + `Retry-After`.
  - W asynchronicznej ścieżce Tailscale Serve Control UI nieudane próby dla tego samego `{scope, clientIp}` są serializowane przed zapisem niepowodzenia. Współbieżne błędne próby od tego samego klienta mogą więc uruchomić limiter przy drugim żądaniu, zamiast aby oba przeszły wyścigowo jako zwykłe niedopasowania.
  - `gateway.auth.rateLimit.exemptLoopback` ma domyślnie wartość `true`; ustaw `false`, gdy celowo chcesz objąć ograniczaniem także ruch localhost (dla konfiguracji testowych lub ścisłych wdrożeń proxy).
- Próby uwierzytelniania WS pochodzące z przeglądarki są zawsze ograniczane z wyłączonym wyjątkiem loopback (defense-in-depth przeciw brute force localhost z poziomu przeglądarki).
- Na loopback te blokady pochodzące z przeglądarki są izolowane per znormalizowana
  wartość `Origin`, więc powtarzające się niepowodzenia z jednego źródła localhost nie blokują automatycznie
  innego źródła.
- `tailscale.mode`: `serve` (tylko tailnet, wiązanie loopback) albo `funnel` (publiczne, wymaga uwierzytelniania).
- `controlUi.allowedOrigins`: jawna lista dozwolonych źródeł przeglądarki dla połączeń Gateway WebSocket. Wymagana, gdy oczekiwani są klienci przeglądarkowi z originów innych niż loopback.
- `controlUi.dangerouslyAllowHostHeaderOriginFallback`: niebezpieczny tryb, który włącza zapasowy mechanizm origin oparty na nagłówku Host dla wdrożeń, które celowo polegają na tej polityce origin.
- `remote.transport`: `ssh` (domyślnie) albo `direct` (ws/wss). Dla `direct` `remote.url` musi mieć postać `ws://` albo `wss://`.
- `OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1`: klienckie nadpisanie typu break-glass, które dopuszcza jawny tekst `ws://` do zaufanych adresów IP sieci prywatnej; domyślnie zwykły tekst pozostaje dozwolony tylko dla loopback.
- `gateway.remote.token` / `.password` to pola poświadczeń klienta zdalnego. Same w sobie nie konfigurują uwierzytelniania Gateway.
- `gateway.push.apns.relay.baseUrl`: bazowy adres HTTPS zewnętrznego przekaźnika APNs używanego przez oficjalne/TestFlight buildy iOS po opublikowaniu przez nie rejestracji opartych na przekaźniku do Gateway. Ten adres URL musi odpowiadać adresowi przekaźnika skompilowanemu w buildzie iOS.
- `gateway.push.apns.relay.timeoutMs`: limit czasu wysyłania z Gateway do przekaźnika w milisekundach. Domyślnie `10000`.
- Rejestracje oparte na przekaźniku są delegowane do określonej tożsamości Gateway. Sparowana aplikacja iOS pobiera `gateway.identity.get`, uwzględnia tę tożsamość w rejestracji przekaźnika i przekazuje do Gateway uprawnienie wysyłania o zakresie rejestracji. Inny Gateway nie może ponownie użyć tej zapisanej rejestracji.
- `OPENCLAW_APNS_RELAY_BASE_URL` / `OPENCLAW_APNS_RELAY_TIMEOUT_MS`: tymczasowe nadpisania środowiskowe dla powyższej konfiguracji przekaźnika.
- `OPENCLAW_APNS_RELAY_ALLOW_HTTP=true`: przeznaczona wyłącznie do developmentu furtka dla adresów URL przekaźnika HTTP na loopback. Produkcyjne adresy URL przekaźnika powinny pozostać przy HTTPS.
- `gateway.channelHealthCheckMinutes`: interwał monitora zdrowia kanałów w minutach. Ustaw `0`, aby globalnie wyłączyć restarty monitora zdrowia. Domyślnie: `5`.
- `gateway.channelStaleEventThresholdMinutes`: próg nieaktualnego gniazda w minutach. Utrzymuj tę wartość większą lub równą `gateway.channelHealthCheckMinutes`. Domyślnie: `30`.
- `gateway.channelMaxRestartsPerHour`: maksymalna liczba restartów monitora zdrowia na kanał/konto w ruchomej godzinie. Domyślnie: `10`.
- `channels.<provider>.healthMonitor.enabled`: per-kanałowy opt-out z restartów monitora zdrowia przy zachowaniu globalnego monitora.
- `channels.<provider>.accounts.<accountId>.healthMonitor.enabled`: nadpisanie per konto dla kanałów wielokontowych. Gdy ustawione, ma pierwszeństwo przed nadpisaniem na poziomie kanału.
- Lokalne ścieżki wywołań Gateway mogą używać `gateway.remote.*` jako wartości zapasowej tylko wtedy, gdy `gateway.auth.*` nie jest ustawione.
- Jeśli `gateway.auth.token` / `gateway.auth.password` jest jawnie skonfigurowane przez SecretRef i nierozwiązane, rozwiązywanie kończy się fail-closed (bez maskującego zdalnego fallbacku).
- `trustedProxies`: adresy IP reverse proxy, które kończą TLS lub wstrzykują nagłówki przekazanego klienta. Wymieniaj tylko proxy, które kontrolujesz. Wpisy loopback są nadal prawidłowe dla konfiguracji wykrywania lokalnego/proxy na tym samym hoście (na przykład Tailscale Serve lub lokalne reverse proxy), ale **nie** kwalifikują żądań loopback do `gateway.auth.mode: "trusted-proxy"`.
- `allowRealIpFallback`: gdy `true`, Gateway akceptuje `X-Real-IP`, jeśli brakuje `X-Forwarded-For`. Domyślnie `false` dla zachowania fail-closed.
- `gateway.tools.deny`: dodatkowe nazwy narzędzi blokowane dla HTTP `POST /tools/invoke` (rozszerza domyślną listę deny).
- `gateway.tools.allow`: usuwa nazwy narzędzi z domyślnej listy deny HTTP.

</Accordion>

### Punkty końcowe zgodne z OpenAI

- Chat Completions: domyślnie wyłączone. Włącz przez `gateway.http.endpoints.chatCompletions.enabled: true`.
- Responses API: `gateway.http.endpoints.responses.enabled`.
- Utwardzanie wejść URL dla Responses:
  - `gateway.http.endpoints.responses.maxUrlParts`
  - `gateway.http.endpoints.responses.files.urlAllowlist`
  - `gateway.http.endpoints.responses.images.urlAllowlist`
    Puste listy dozwolonych są traktowane jak nieustawione; użyj `gateway.http.endpoints.responses.files.allowUrl=false`
    i/lub `gateway.http.endpoints.responses.images.allowUrl=false`, aby wyłączyć pobieranie URL.
- Opcjonalny nagłówek utwardzający odpowiedzi:
  - `gateway.http.securityHeaders.strictTransportSecurity` (ustawiaj tylko dla kontrolowanych przez siebie originów HTTPS; zobacz [Trusted Proxy Auth](/pl/gateway/trusted-proxy-auth#tls-termination-and-hsts))

### Izolacja wielu instancji

Uruchamiaj wiele Gateway na jednym hoście z unikalnymi portami i katalogami stanu:

```bash
OPENCLAW_CONFIG_PATH=~/.openclaw/a.json \
OPENCLAW_STATE_DIR=~/.openclaw-a \
openclaw gateway --port 19001
```

Wygodne flagi: `--dev` (używa `~/.openclaw-dev` + portu `19001`), `--profile <name>` (używa `~/.openclaw-<name>`).

Zobacz [Multiple Gateways](/pl/gateway/multiple-gateways).

### `gateway.tls`

```json5
{
  gateway: {
    tls: {
      enabled: false,
      autoGenerate: false,
      certPath: "/etc/openclaw/tls/server.crt",
      keyPath: "/etc/openclaw/tls/server.key",
      caPath: "/etc/openclaw/tls/ca-bundle.crt",
    },
  },
}
```

- `enabled`: włącza terminację TLS na nasłuchu Gateway (HTTPS/WSS) (domyślnie: `false`).
- `autoGenerate`: automatycznie generuje lokalną samopodpisaną parę certyfikat/klucz, gdy nie skonfigurowano jawnych plików; tylko do użytku lokalnego/deweloperskiego.
- `certPath`: ścieżka systemu plików do pliku certyfikatu TLS.
- `keyPath`: ścieżka systemu plików do pliku klucza prywatnego TLS; zachowuj ograniczone uprawnienia.
- `caPath`: opcjonalna ścieżka do pakietu CA do weryfikacji klienta lub niestandardowych łańcuchów zaufania.

### `gateway.reload`

```json5
{
  gateway: {
    reload: {
      mode: "hybrid", // off | restart | hot | hybrid
      debounceMs: 500,
      deferralTimeoutMs: 300000,
    },
  },
}
```

- `mode`: kontroluje sposób stosowania edycji konfiguracji w runtime.
  - `"off"`: ignoruj edycje na żywo; zmiany wymagają jawnego restartu.
  - `"restart"`: zawsze restartuj proces Gateway przy zmianie konfiguracji.
  - `"hot"`: stosuj zmiany w procesie bez restartu.
  - `"hybrid"` (domyślnie): najpierw spróbuj hot reload; wróć do restartu, jeśli to wymagane.
- `debounceMs`: okno debounce w ms przed zastosowaniem zmian konfiguracji (nieujemna liczba całkowita).
- `deferralTimeoutMs`: maksymalny czas w ms oczekiwania na operacje w toku przed wymuszeniem restartu (domyślnie: `300000` = 5 minut).

---

## Hooki

```json5
{
  hooks: {
    enabled: true,
    token: "shared-secret",
    path: "/hooks",
    maxBodyBytes: 262144,
    defaultSessionKey: "hook:ingress",
    allowRequestSessionKey: false,
    allowedSessionKeyPrefixes: ["hook:"],
    allowedAgentIds: ["hooks", "main"],
    presets: ["gmail"],
    transformsDir: "~/.openclaw/hooks/transforms",
    mappings: [
      {
        match: { path: "gmail" },
        action: "agent",
        agentId: "hooks",
        wakeMode: "now",
        name: "Gmail",
        sessionKey: "hook:gmail:{{messages[0].id}}",
        messageTemplate: "From: {{messages[0].from}}\nSubject: {{messages[0].subject}}\n{{messages[0].snippet}}",
        deliver: true,
        channel: "last",
        model: "openai/gpt-5.4-mini",
      },
    ],
  },
}
```

Auth: `Authorization: Bearer <token>` albo `x-openclaw-token: <token>`.
Tokeny hooków w query string są odrzucane.

Uwagi dotyczące walidacji i bezpieczeństwa:

- `hooks.enabled=true` wymaga niepustego `hooks.token`.
- `hooks.token` musi być **inne** niż `gateway.auth.token`; ponowne użycie tokenu Gateway jest odrzucane.
- `hooks.path` nie może być `/`; użyj dedykowanej podścieżki, takiej jak `/hooks`.
- Jeśli `hooks.allowRequestSessionKey=true`, ogranicz `hooks.allowedSessionKeyPrefixes` (na przykład `["hook:"]`).

**Punkty końcowe:**

- `POST /hooks/wake` → `{ text, mode?: "now"|"next-heartbeat" }`
- `POST /hooks/agent` → `{ message, name?, agentId?, sessionKey?, wakeMode?, deliver?, channel?, to?, model?, thinking?, timeoutSeconds? }`
  - `sessionKey` z ładunku żądania jest akceptowane tylko wtedy, gdy `hooks.allowRequestSessionKey=true` (domyślnie: `false`).
- `POST /hooks/<name>` → rozwiązywane przez `hooks.mappings`

<Accordion title="Szczegóły mapowania">

- `match.path` dopasowuje podścieżkę po `/hooks` (np. `/hooks/gmail` → `gmail`).
- `match.source` dopasowuje pole ładunku dla ścieżek ogólnych.
- Szablony takie jak `{{messages[0].subject}}` odczytują dane z ładunku.
- `transform` może wskazywać moduł JS/TS zwracający akcję hooka.
  - `transform.module` musi być ścieżką względną i pozostaje w obrębie `hooks.transformsDir` (ścieżki bezwzględne i traversal są odrzucane).
- `agentId` kieruje do określonego agenta; nieznane identyfikatory wracają do domyślnego.
- `allowedAgentIds`: ogranicza jawne kierowanie (`*` lub pominięte = zezwól na wszystkie, `[]` = zabroń wszystkim).
- `defaultSessionKey`: opcjonalny stały klucz sesji dla uruchomień agentów hooków bez jawnego `sessionKey`.
- `allowRequestSessionKey`: zezwala wywołującym `/hooks/agent` na ustawianie `sessionKey` (domyślnie: `false`).
- `allowedSessionKeyPrefixes`: opcjonalna lista dozwolonych prefiksów dla jawnych wartości `sessionKey` (żądanie + mapowanie), np. `["hook:"]`.
- `deliver: true` wysyła końcową odpowiedź do kanału; `channel` domyślnie ma wartość `last`.
- `model` nadpisuje LLM dla tego uruchomienia hooka (musi być dozwolony, jeśli ustawiono katalog modeli).

</Accordion>

### Integracja z Gmail

```json5
{
  hooks: {
    gmail: {
      account: "openclaw@gmail.com",
      topic: "projects/<project-id>/topics/gog-gmail-watch",
      subscription: "gog-gmail-watch-push",
      pushToken: "shared-push-token",
      hookUrl: "http://127.0.0.1:18789/hooks/gmail",
      includeBody: true,
      maxBytes: 20000,
      renewEveryMinutes: 720,
      serve: { bind: "127.0.0.1", port: 8788, path: "/" },
      tailscale: { mode: "funnel", path: "/gmail-pubsub" },
      model: "openrouter/meta-llama/llama-3.3-70b-instruct:free",
      thinking: "off",
    },
  },
}
```

- Gateway automatycznie uruchamia `gog gmail watch serve` podczas startu, gdy jest skonfigurowane. Ustaw `OPENCLAW_SKIP_GMAIL_WATCHER=1`, aby to wyłączyć.
- Nie uruchamiaj osobnego `gog gmail watch serve` równolegle z Gateway.

---

## Host Canvas

```json5
{
  canvasHost: {
    root: "~/.openclaw/workspace/canvas",
    liveReload: true,
    // enabled: false, // or OPENCLAW_SKIP_CANVAS_HOST=1
  },
}
```

- Udostępnia edytowalne przez agenta HTML/CSS/JS i A2UI przez HTTP pod portem Gateway:
  - `http://<gateway-host>:<gateway.port>/__openclaw__/canvas/`
  - `http://<gateway-host>:<gateway.port>/__openclaw__/a2ui/`
- Tylko lokalnie: zachowaj `gateway.bind: "loopback"` (domyślnie).
- Wiązania inne niż loopback: ścieżki canvas wymagają uwierzytelniania Gateway (token/hasło/trusted-proxy), tak samo jak inne powierzchnie HTTP Gateway.
- Node WebViews zwykle nie wysyłają nagłówków uwierzytelniania; po sparowaniu i połączeniu noda Gateway ogłasza adresy URL capabilities o zakresie noda dla dostępu do canvas/A2UI.
- Adresy URL capabilities są związane z aktywną sesją WS noda i szybko wygasają. Nie jest używany fallback oparty na IP.
- Wstrzykuje klienta live-reload do serwowanego HTML.
- Automatycznie tworzy początkowy `index.html`, gdy katalog jest pusty.
- Serwuje także A2UI pod `/__openclaw__/a2ui/`.
- Zmiany wymagają restartu Gateway.
- Wyłącz live reload dla dużych katalogów albo przy błędach `EMFILE`.

---

## Discovery

### mDNS (Bonjour)

```json5
{
  discovery: {
    mdns: {
      mode: "minimal", // minimal | full | off
    },
  },
}
```

- `minimal` (domyślnie): pomija `cliPath` + `sshPort` z rekordów TXT.
- `full`: uwzględnia `cliPath` + `sshPort`.
- Nazwa hosta domyślnie to `openclaw`. Nadpisz przez `OPENCLAW_MDNS_HOSTNAME`.

### Wide-area (DNS-SD)

```json5
{
  discovery: {
    wideArea: { enabled: true },
  },
}
```

Zapisuje strefę unicast DNS-SD w `~/.openclaw/dns/`. Do wykrywania między sieciami połącz to z serwerem DNS (zalecany CoreDNS) + Tailscale split DNS.

Konfiguracja: `openclaw dns setup --apply`.

---

## Środowisko

### `env` (zmienne środowiskowe inline)

```json5
{
  env: {
    OPENROUTER_API_KEY: "sk-or-...",
    vars: {
      GROQ_API_KEY: "gsk-...",
    },
    shellEnv: {
      enabled: true,
      timeoutMs: 15000,
    },
  },
}
```

- Zmienne środowiskowe inline są stosowane tylko wtedy, gdy w środowisku procesu brakuje danego klucza.
- Pliki `.env`: `.env` z bieżącego katalogu roboczego + `~/.openclaw/.env` (żaden nie nadpisuje istniejących zmiennych).
- `shellEnv`: importuje brakujące oczekiwane klucze z profilu powłoki logowania.
- Pełny priorytet znajdziesz w [Environment](/pl/help/environment).

### Podstawianie zmiennych środowiskowych

Odwołuj się do zmiennych środowiskowych w dowolnym ciągu konfiguracji za pomocą `${VAR_NAME}`:

```json5
{
  gateway: {
    auth: { token: "${OPENCLAW_GATEWAY_TOKEN}" },
  },
}
```

- Dopasowywane są tylko nazwy pisane wielkimi literami: `[A-Z_][A-Z0-9_]*`.
- Brakujące/puste zmienne powodują błąd przy ładowaniu konfiguracji.
- Ucieknij przez `$${VAR}`, aby uzyskać literał `${VAR}`.
- Działa z `$include`.

---

## Sekrety

Odwołania do sekretów są addytywne: wartości tekstowe nadal działają.

### `SecretRef`

Użyj jednego kształtu obiektu:

```json5
{ source: "env" | "file" | "exec", provider: "default", id: "..." }
```

Walidacja:

- wzorzec `provider`: `^[a-z][a-z0-9_-]{0,63}$`
- wzorzec `source: "env"` dla id: `^[A-Z][A-Z0-9_]{0,127}$`
- `source: "file"` id: bezwzględny wskaźnik JSON (na przykład `"/providers/openai/apiKey"`)
- wzorzec `source: "exec"` dla id: `^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$`
- identyfikatory `source: "exec"` nie mogą zawierać segmentów ścieżki `.` ani `..` rozdzielanych ukośnikami (na przykład `a/../b` jest odrzucane)

### Obsługiwana powierzchnia poświadczeń

- Kanoniczna macierz: [SecretRef Credential Surface](/pl/reference/secretref-credential-surface)
- `secrets apply` kieruje na obsługiwane ścieżki poświadczeń `openclaw.json`.
- Odwołania `auth-profiles.json` są uwzględniane w rozwiązywaniu runtime i pokryciu audytu.

### Konfiguracja dostawców sekretów

```json5
{
  secrets: {
    providers: {
      default: { source: "env" }, // optional explicit env provider
      filemain: {
        source: "file",
        path: "~/.openclaw/secrets.json",
        mode: "json",
        timeoutMs: 5000,
      },
      vault: {
        source: "exec",
        command: "/usr/local/bin/openclaw-vault-resolver",
        passEnv: ["PATH", "VAULT_ADDR"],
      },
    },
    defaults: {
      env: "default",
      file: "filemain",
      exec: "vault",
    },
  },
}
```

Uwagi:

- Dostawca `file` obsługuje `mode: "json"` i `mode: "singleValue"` (`id` musi mieć wartość `"value"` w trybie singleValue).
- Dostawca `exec` wymaga bezwzględnej ścieżki `command` i używa ładunków protokołu na stdin/stdout.
- Domyślnie ścieżki poleceń będące dowiązaniami symbolicznymi są odrzucane. Ustaw `allowSymlinkCommand: true`, aby zezwolić na ścieżki dowiązań przy jednoczesnej walidacji ścieżki rozwiązanego celu.
- Jeśli skonfigurowano `trustedDirs`, kontrola zaufanych katalogów dotyczy ścieżki rozwiązanego celu.
- Środowisko potomne `exec` jest domyślnie minimalne; przekaż wymagane zmienne jawnie przez `passEnv`.
- Odwołania do sekretów są rozwiązywane w czasie aktywacji do migawki w pamięci, a następnie ścieżki żądań odczytują już tylko tę migawkę.
- Filtrowanie aktywnej powierzchni obowiązuje podczas aktywacji: nierozwiązane odwołania na włączonych powierzchniach powodują błąd uruchomienia/przeładowania, a nieaktywne powierzchnie są pomijane z diagnostyką.

---

## Magazyn auth

```json5
{
  auth: {
    profiles: {
      "anthropic:default": { provider: "anthropic", mode: "api_key" },
      "anthropic:work": { provider: "anthropic", mode: "api_key" },
      "openai-codex:personal": { provider: "openai-codex", mode: "oauth" },
    },
    order: {
      anthropic: ["anthropic:default", "anthropic:work"],
      "openai-codex": ["openai-codex:personal"],
    },
  },
}
```

- Profile per agent są przechowywane w `<agentDir>/auth-profiles.json`.
- `auth-profiles.json` obsługuje odwołania na poziomie wartości (`keyRef` dla `api_key`, `tokenRef` dla `token`) dla statycznych trybów poświadczeń.
- Profile w trybie OAuth (`auth.profiles.<id>.mode = "oauth"`) nie obsługują poświadczeń `auth-profile` opartych na SecretRef.
- Statyczne poświadczenia runtime pochodzą z rozwiązanych migawek w pamięci; starsze statyczne wpisy `auth.json` są czyszczone po wykryciu.
- Starsze importy OAuth z `~/.openclaw/credentials/oauth.json`.
- Zobacz [OAuth](/pl/concepts/oauth).
- Zachowanie runtime sekretów oraz narzędzia `audit/configure/apply`: [Secrets Management](/pl/gateway/secrets).

### `auth.cooldowns`

```json5
{
  auth: {
    cooldowns: {
      billingBackoffHours: 5,
      billingBackoffHoursByProvider: { anthropic: 3, openai: 8 },
      billingMaxHours: 24,
      authPermanentBackoffMinutes: 10,
      authPermanentMaxMinutes: 60,
      failureWindowHours: 24,
      overloadedProfileRotations: 1,
      overloadedBackoffMs: 0,
      rateLimitedProfileRotations: 1,
    },
  },
}
```

- `billingBackoffHours`: bazowy backoff w godzinach, gdy profil kończy się niepowodzeniem z powodu rzeczywistych błędów
  billing/insufficient-credit (domyślnie: `5`). Jawny tekst billing może
  nadal trafić tutaj nawet przy odpowiedziach `401`/`403`, ale dopasowania tekstu specyficzne
  dla dostawcy pozostają ograniczone do dostawcy, który jest ich właścicielem (na przykład OpenRouter
  `Key limit exceeded`). Odpowiedzi HTTP `402` typu retryable usage-window lub
  komunikaty o limicie wydatków organizacji/obszaru roboczego pozostają zamiast tego na ścieżce `rate_limit`.
- `billingBackoffHoursByProvider`: opcjonalne nadpisania godzin backoff billing per dostawca.
- `billingMaxHours`: limit w godzinach dla wykładniczego wzrostu backoff billing (domyślnie: `24`).
- `authPermanentBackoffMinutes`: bazowy backoff w minutach dla błędów `auth_permanent` o wysokiej pewności (domyślnie: `10`).
- `authPermanentMaxMinutes`: limit w minutach dla wzrostu backoff `auth_permanent` (domyślnie: `60`).
- `failureWindowHours`: ruchome okno w godzinach używane dla liczników backoff (domyślnie: `24`).
- `overloadedProfileRotations`: maksymalna liczba rotacji `auth-profile` tego samego dostawcy dla błędów przeciążenia przed przełączeniem na fallback modelu (domyślnie: `1`). Kształty typu provider-busy, takie jak `ModelNotReadyException`, trafiają tutaj.
- `overloadedBackoffMs`: stałe opóźnienie przed ponowną próbą rotacji przeciążonego dostawcy/profilu (domyślnie: `0`).
- `rateLimitedProfileRotations`: maksymalna liczba rotacji `auth-profile` tego samego dostawcy dla błędów limitu szybkości przed przełączeniem na fallback modelu (domyślnie: `1`). Ten koszyk `rate_limit` obejmuje teksty zależne od dostawcy, takie jak `Too many concurrent requests`, `ThrottlingException`, `concurrency limit reached`, `workers_ai ... quota limit exceeded` oraz `resource exhausted`.

---

## Logowanie

```json5
{
  logging: {
    level: "info",
    file: "/tmp/openclaw/openclaw.log",
    consoleLevel: "info",
    consoleStyle: "pretty", // pretty | compact | json
    redactSensitive: "tools", // off | tools
    redactPatterns: ["\\bTOKEN\\b\\s*[=:]\\s*([\"']?)([^\\s\"']+)\\1"],
  },
}
```

- Domyślny plik logu: `/tmp/openclaw/openclaw-YYYY-MM-DD.log`.
- Ustaw `logging.file`, aby uzyskać stałą ścieżkę.
- `consoleLevel` podnosi się do `debug` przy `--verbose`.
- `maxFileBytes`: maksymalny rozmiar pliku logu w bajtach, po którego przekroczeniu zapisy są wstrzymywane (dodatnia liczba całkowita; domyślnie: `524288000` = 500 MB). W wdrożeniach produkcyjnych używaj zewnętrznej rotacji logów.

---

## Diagnostyka

```json5
{
  diagnostics: {
    enabled: true,
    flags: ["telegram.*"],
    stuckSessionWarnMs: 30000,

    otel: {
      enabled: false,
      endpoint: "https://otel-collector.example.com:4318",
      protocol: "http/protobuf", // http/protobuf | grpc
      headers: { "x-tenant-id": "my-org" },
      serviceName: "openclaw-gateway",
      traces: true,
      metrics: true,
      logs: false,
      sampleRate: 1.0,
      flushIntervalMs: 5000,
    },

    cacheTrace: {
      enabled: false,
      filePath: "~/.openclaw/logs/cache-trace.jsonl",
      includeMessages: true,
      includePrompt: true,
      includeSystem: true,
    },
  },
}
```

- `enabled`: główny przełącznik wyjścia instrumentacji (domyślnie: `true`).
- `flags`: tablica ciągów flag włączających ukierunkowane wyjście logów (obsługuje wildcardy takie jak `"telegram.*"` albo `"*"`).
- `stuckSessionWarnMs`: próg wieku w ms do emitowania ostrzeżeń o zablokowanej sesji, gdy sesja pozostaje w stanie przetwarzania.
- `otel.enabled`: włącza potok eksportu OpenTelemetry (domyślnie: `false`).
- `otel.endpoint`: adres URL collectora dla eksportu OTel.
- `otel.protocol`: `"http/protobuf"` (domyślnie) albo `"grpc"`.
- `otel.headers`: dodatkowe nagłówki metadanych HTTP/gRPC wysyłane z żądaniami eksportu OTel.
- `otel.serviceName`: nazwa usługi dla atrybutów zasobu.
- `otel.traces` / `otel.metrics` / `otel.logs`: włącz eksport trace, metrics lub logs.
- `otel.sampleRate`: współczynnik próbkowania trace `0`–`1`.
- `otel.flushIntervalMs`: okresowy interwał flush telemetrii w ms.
- `cacheTrace.enabled`: loguje migawki śledzenia cache dla przebiegów osadzonych (domyślnie: `false`).
- `cacheTrace.filePath`: ścieżka wyjściowa dla cache trace JSONL (domyślnie: `$OPENCLAW_STATE_DIR/logs/cache-trace.jsonl`).
- `cacheTrace.includeMessages` / `includePrompt` / `includeSystem`: kontrolują, co jest uwzględniane w wyjściu cache trace (wszystkie domyślnie: `true`).

---

## Aktualizacja

```json5
{
  update: {
    channel: "stable", // stable | beta | dev
    checkOnStart: true,

    auto: {
      enabled: false,
      stableDelayHours: 6,
      stableJitterHours: 12,
      betaCheckIntervalHours: 1,
    },
  },
}
```

- `channel`: kanał wydań dla instalacji npm/git — `"stable"`, `"beta"` albo `"dev"`.
- `checkOnStart`: sprawdza aktualizacje npm przy uruchomieniu Gateway (domyślnie: `true`).
- `auto.enabled`: włącza aktualizacje automatyczne w tle dla instalacji pakietowych (domyślnie: `false`).
- `auto.stableDelayHours`: minimalne opóźnienie w godzinach przed automatycznym zastosowaniem na kanale stable (domyślnie: `6`; maks.: `168`).
- `auto.stableJitterHours`: dodatkowe okno rozłożenia wdrożenia kanału stable w godzinach (domyślnie: `12`; maks.: `168`).
- `auto.betaCheckIntervalHours`: jak często wykonywane są kontrole kanału beta, w godzinach (domyślnie: `1`; maks.: `24`).

---

## ACP

```json5
{
  acp: {
    enabled: false,
    dispatch: { enabled: true },
    backend: "acpx",
    defaultAgent: "main",
    allowedAgents: ["main", "ops"],
    maxConcurrentSessions: 10,

    stream: {
      coalesceIdleMs: 50,
      maxChunkChars: 1000,
      repeatSuppression: true,
      deliveryMode: "live", // live | final_only
      hiddenBoundarySeparator: "paragraph", // none | space | newline | paragraph
      maxOutputChars: 50000,
      maxSessionUpdateChars: 500,
    },

    runtime: {
      ttlMinutes: 30,
    },
  },
}
```

- `enabled`: globalna bramka funkcji ACP (domyślnie: `false`).
- `dispatch.enabled`: niezależna bramka dla wysyłania tur sesji ACP (domyślnie: `true`). Ustaw `false`, aby zachować dostępność poleceń ACP przy jednoczesnym blokowaniu wykonania.
- `backend`: domyślny identyfikator backendu runtime ACP (musi odpowiadać zarejestrowanemu Pluginowi runtime ACP).
- `defaultAgent`: zapasowy identyfikator docelowego agenta ACP, gdy uruchomienia nie określają jawnego celu.
- `allowedAgents`: lista dozwolonych identyfikatorów agentów dla sesji runtime ACP; pusta oznacza brak dodatkowego ograniczenia.
- `maxConcurrentSessions`: maksymalna liczba jednocześnie aktywnych sesji ACP.
- `stream.coalesceIdleMs`: okno flush bezczynności w ms dla strumieniowanego tekstu.
- `stream.maxChunkChars`: maksymalny rozmiar chunk przed podziałem projekcji strumieniowanego bloku.
- `stream.repeatSuppression`: tłumi powtarzające się linie statusu/narzędzi per tura (domyślnie: `true`).
- `stream.deliveryMode`: `"live"` strumieniuje przyrostowo; `"final_only"` buforuje do terminalnych zdarzeń tury.
- `stream.hiddenBoundarySeparator`: separator przed widocznym tekstem po ukrytych zdarzeniach narzędzi (domyślnie: `"paragraph"`).
- `stream.maxOutputChars`: maksymalna liczba znaków wyjścia asystenta projektowanych per tura ACP.
- `stream.maxSessionUpdateChars`: maksymalna liczba znaków dla projektowanych linii statusu/aktualizacji ACP.
- `stream.tagVisibility`: zapis nazw tagów do logicznych nadpisań widoczności dla strumieniowanych zdarzeń.
- `runtime.ttlMinutes`: TTL bezczynności w minutach dla workerów sesji ACP przed kwalifikacją do czyszczenia.
- `runtime.installCommand`: opcjonalne polecenie instalacji uruchamiane podczas bootstrapowania środowiska runtime ACP.

---

## CLI

```json5
{
  cli: {
    banner: {
      taglineMode: "off", // random | default | off
    },
  },
}
```

- `cli.banner.taglineMode` kontroluje styl sloganu bannera:
  - `"random"` (domyślnie): rotujące zabawne/sezonowe slogany.
  - `"default"`: stały neutralny slogan (`All your chats, one OpenClaw.`).
  - `"off"`: brak tekstu sloganu (tytuł/wersja bannera nadal są pokazywane).
- Aby ukryć cały banner (nie tylko slogany), ustaw zmienną środowiskową `OPENCLAW_HIDE_BANNER=1`.

---

## Kreator

Metadane zapisywane przez przepływy konfiguracji prowadzonej przez CLI (`onboard`, `configure`, `doctor`):

```json5
{
  wizard: {
    lastRunAt: "2026-01-01T00:00:00.000Z",
    lastRunVersion: "2026.1.4",
    lastRunCommit: "abc1234",
    lastRunCommand: "configure",
    lastRunMode: "local",
  },
}
```

---

## Tożsamość

Zobacz pola tożsamości `agents.list` w sekcji [Wartości domyślne agenta](#agent-defaults).

---

## Bridge (starszy, usunięty)

Bieżące buildy nie zawierają już mostu TCP. Nody łączą się przez Gateway WebSocket. Klucze `bridge.*` nie są już częścią schematu konfiguracji (walidacja kończy się błędem, dopóki nie zostaną usunięte; `openclaw doctor --fix` może usunąć nieznane klucze).

<Accordion title="Starsza konfiguracja bridge (odwołanie historyczne)">

```json
{
  "bridge": {
    "enabled": true,
    "port": 18790,
    "bind": "tailnet",
    "tls": {
      "enabled": true,
      "autoGenerate": true
    }
  }
}
```

</Accordion>

---

## Cron

```json5
{
  cron: {
    enabled: true,
    maxConcurrentRuns: 2,
    webhook: "https://example.invalid/legacy", // deprecated fallback for stored notify:true jobs
    webhookToken: "replace-with-dedicated-token", // optional bearer token for outbound webhook auth
    sessionRetention: "24h", // duration string or false
    runLog: {
      maxBytes: "2mb", // default 2_000_000 bytes
      keepLines: 2000, // default 2000
    },
  },
}
```

- `sessionRetention`: jak długo przechowywać ukończone sesje odizolowanych uruchomień Cron przed usunięciem z `sessions.json`. Kontroluje także czyszczenie zarchiwizowanych usuniętych transkryptów Cron. Domyślnie: `24h`; ustaw `false`, aby wyłączyć.
- `runLog.maxBytes`: maksymalny rozmiar na plik logu uruchomienia (`cron/runs/<jobId>.jsonl`) przed przycięciem. Domyślnie: `2_000_000` bajtów.
- `runLog.keepLines`: najnowsze linie zachowywane, gdy uruchamiane jest przycinanie logu uruchomienia. Domyślnie: `2000`.
- `webhookToken`: token bearer używany do dostarczania POST Webhook Cron (`delivery.mode = "webhook"`); jeśli pominięty, nie jest wysyłany nagłówek auth.
- `webhook`: przestarzały starszy zapasowy adres URL Webhook (http/https) używany tylko dla zapisanych zadań, które nadal mają `notify: true`.

### `cron.retry`

```json5
{
  cron: {
    retry: {
      maxAttempts: 3,
      backoffMs: [30000, 60000, 300000],
      retryOn: ["rate_limit", "overloaded", "network", "timeout", "server_error"],
    },
  },
}
```

- `maxAttempts`: maksymalna liczba ponownych prób dla zadań jednorazowych przy błędach przejściowych (domyślnie: `3`; zakres: `0`–`10`).
- `backoffMs`: tablica opóźnień backoff w ms dla każdej ponownej próby (domyślnie: `[30000, 60000, 300000]`; 1–10 wpisów).
- `retryOn`: typy błędów, które uruchamiają ponowne próby — `"rate_limit"`, `"overloaded"`, `"network"`, `"timeout"`, `"server_error"`. Pomiń, aby ponawiać dla wszystkich typów przejściowych.

Dotyczy tylko jednorazowych zadań Cron. Zadania cykliczne używają osobnej obsługi błędów.

### `cron.failureAlert`

```json5
{
  cron: {
    failureAlert: {
      enabled: false,
      after: 3,
      cooldownMs: 3600000,
      mode: "announce",
      accountId: "main",
    },
  },
}
```

- `enabled`: włącza alerty o błędach dla zadań Cron (domyślnie: `false`).
- `after`: liczba kolejnych niepowodzeń przed uruchomieniem alertu (dodatnia liczba całkowita, min.: `1`).
- `cooldownMs`: minimalna liczba milisekund między powtarzającymi się alertami dla tego samego zadania (nieujemna liczba całkowita).
- `mode`: tryb dostarczenia — `"announce"` wysyła przez wiadomość kanałową; `"webhook"` wykonuje POST do skonfigurowanego Webhook.
- `accountId`: opcjonalny identyfikator konta lub kanału do ograniczenia dostarczania alertu.

### `cron.failureDestination`

```json5
{
  cron: {
    failureDestination: {
      mode: "announce",
      channel: "last",
      to: "channel:C1234567890",
      accountId: "main",
    },
  },
}
```

- Domyślny cel powiadomień o błędach Cron dla wszystkich zadań.
- `mode`: `"announce"` albo `"webhook"`; domyślnie `"announce"`, gdy istnieje wystarczająca ilość danych docelowych.
- `channel`: nadpisanie kanału dla dostarczania announce. `"last"` ponownie używa ostatniego znanego kanału dostarczenia.
- `to`: jawny cel announce albo adres URL Webhook. Wymagane dla trybu webhook.
- `accountId`: opcjonalne nadpisanie konta dla dostarczania.
- Per-zadaniowe `delivery.failureDestination` nadpisuje tę globalną wartość domyślną.
- Gdy nie ustawiono ani globalnego, ani per-zadaniowego celu błędu, zadania, które już dostarczają przez `announce`, przy błędzie wracają do tego podstawowego celu announce.
- `delivery.failureDestination` jest obsługiwane tylko dla zadań `sessionTarget="isolated"`, chyba że podstawowe `delivery.mode` zadania ma wartość `"webhook"`.

Zobacz [Cron Jobs](/pl/automation/cron-jobs). Odizolowane wykonania Cron są śledzone jako [background tasks](/pl/automation/tasks).

---

## Zmienne szablonu modelu mediów

Placeholdery szablonów rozwijane w `tools.media.models[].args`:

| Zmienna           | Opis                                               |
| ----------------- | -------------------------------------------------- |
| `{{Body}}`        | Pełna treść wiadomości przychodzącej               |
| `{{RawBody}}`     | Surowa treść (bez opakowania historii/nadawcy)     |
| `{{BodyStripped}}`| Treść z usuniętymi wzmiankami grupowymi            |
| `{{From}}`        | Identyfikator nadawcy                              |
| `{{To}}`          | Identyfikator celu                                 |
| `{{MessageSid}}`  | Identyfikator wiadomości kanału                    |
| `{{SessionId}}`   | Bieżący UUID sesji                                 |
| `{{IsNewSession}}`| `"true"` po utworzeniu nowej sesji                 |
| `{{MediaUrl}}`    | Pseudo-URL mediów przychodzących                   |
| `{{MediaPath}}`   | Lokalna ścieżka mediów                             |
| `{{MediaType}}`   | Typ mediów (image/audio/document/…)                |
| `{{Transcript}}`  | Transkrypt audio                                   |
| `{{Prompt}}`      | Rozwiązany prompt mediów dla wpisów CLI            |
| `{{MaxChars}}`    | Rozwiązana maksymalna liczba znaków wyjścia dla wpisów CLI |
| `{{ChatType}}`    | `"direct"` albo `"group"`                          |
| `{{GroupSubject}}`| Temat grupy (best effort)                          |
| `{{GroupMembers}}`| Podgląd członków grupy (best effort)               |
| `{{SenderName}}`  | Wyświetlana nazwa nadawcy (best effort)            |
| `{{SenderE164}}`  | Numer telefonu nadawcy (best effort)               |
| `{{Provider}}`    | Wskazówka dostawcy (whatsapp, telegram, discord itd.) |

---

## Include konfiguracji (`$include`)

Podziel konfigurację na wiele plików:

```json5
// ~/.openclaw/openclaw.json
{
  gateway: { port: 18789 },
  agents: { $include: "./agents.json5" },
  broadcast: {
    $include: ["./clients/mueller.json5", "./clients/schmidt.json5"],
  },
}
```

**Zachowanie scalania:**

- Pojedynczy plik: zastępuje obiekt zawierający.
- Tablica plików: głęboko scalana w kolejności (późniejsze nadpisują wcześniejsze).
- Klucze rodzeństwa: scalane po include (nadpisują dołączone wartości).
- Zagnieżdżone include: do 10 poziomów głębokości.
- Ścieżki: rozwiązywane względem pliku dołączającego, ale muszą pozostać w obrębie katalogu głównego konfiguracji najwyższego poziomu (`dirname` dla `openclaw.json`). Formy bezwzględne/`../` są dozwolone tylko wtedy, gdy nadal rozwiązują się w obrębie tej granicy.
- Błędy: jasne komunikaty dla brakujących plików, błędów parsowania i cyklicznych include.

---

_Powiązane: [Configuration](/pl/gateway/configuration) · [Configuration Examples](/pl/gateway/configuration-examples) · [Doctor](/pl/gateway/doctor)_
