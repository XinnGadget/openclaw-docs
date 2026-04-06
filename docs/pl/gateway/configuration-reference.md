---
read_when:
    - Potrzebujesz dokładnej semantyki lub wartości domyślnych na poziomie pól konfiguracji
    - Weryfikujesz bloki konfiguracji kanałów, modeli, gateway lub narzędzi
summary: Pełna dokumentacja każdego klucza konfiguracji OpenClaw, wartości domyślnych i ustawień kanałów
title: Dokumentacja konfiguracji
x-i18n:
    generated_at: "2026-04-06T03:13:39Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6aa6b24b593f6f07118817afabea4cc7842aca6b7c5602b45f479b40c1685230
    source_path: gateway/configuration-reference.md
    workflow: 15
---

# Dokumentacja konfiguracji

Każde pole dostępne w `~/.openclaw/openclaw.json`. Aby zobaczyć omówienie zorientowane na zadania, przejdź do [Configuration](/pl/gateway/configuration).

Format konfiguracji to **JSON5** (dozwolone są komentarze i przecinki końcowe). Wszystkie pola są opcjonalne — OpenClaw używa bezpiecznych wartości domyślnych, gdy zostaną pominięte.

---

## Kanały

Każdy kanał uruchamia się automatycznie, gdy istnieje jego sekcja konfiguracji (chyba że ustawiono `enabled: false`).

### Dostęp do DM i grup

Wszystkie kanały obsługują zasady DM i zasady grup:

| Zasada DM            | Zachowanie                                                      |
| -------------------- | --------------------------------------------------------------- |
| `pairing` (domyślna) | Nieznani nadawcy otrzymują jednorazowy kod parowania; właściciel musi zatwierdzić |
| `allowlist`          | Tylko nadawcy z `allowFrom` (lub sparowanego magazynu zezwoleń) |
| `open`               | Zezwalaj na wszystkie przychodzące DM (wymaga `allowFrom: ["*"]`) |
| `disabled`           | Ignoruj wszystkie przychodzące DM                               |

| Zasada grup          | Zachowanie                                             |
| -------------------- | ------------------------------------------------------ |
| `allowlist` (domyślna) | Tylko grupy pasujące do skonfigurowanej listy zezwoleń |
| `open`               | Pomija listy zezwoleń grup (nadal obowiązuje blokowanie przez wzmianki) |
| `disabled`           | Blokuje wszystkie wiadomości grupowe/pokojów           |

<Note>
`channels.defaults.groupPolicy` ustawia wartość domyślną, gdy `groupPolicy` dostawcy nie jest ustawione.
Kody parowania wygasają po 1 godzinie. Oczekujące żądania parowania DM są ograniczone do **3 na kanał**.
Jeśli blok dostawcy całkowicie nie istnieje (`channels.<provider>` jest nieobecne), zasada grup środowiska uruchomieniowego wraca do `allowlist` (fail-closed) z ostrzeżeniem przy starcie.
</Note>

### Nadpisania modelu dla kanałów

Użyj `channels.modelByChannel`, aby przypiąć określone ID kanałów do modelu. Wartości akceptują `provider/model` lub skonfigurowane aliasy modeli. Mapowanie kanałów jest stosowane, gdy sesja nie ma już nadpisania modelu (na przykład ustawionego przez `/model`).

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

### Domyślne ustawienia kanałów i heartbeat

Użyj `channels.defaults` dla współdzielonych zachowań zasad grup i heartbeat we wszystkich dostawcach:

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
- `channels.defaults.contextVisibility`: domyślny tryb widoczności kontekstu uzupełniającego dla wszystkich kanałów. Wartości: `all` (domyślnie, uwzględnia cały kontekst cytatów/wątków/historii), `allowlist` (uwzględnia tylko kontekst od nadawców z listy zezwoleń), `allowlist_quote` (jak allowlist, ale zachowuje jawny kontekst cytatu/odpowiedzi). Nadpisanie per kanał: `channels.<channel>.contextVisibility`.
- `channels.defaults.heartbeat.showOk`: uwzględnia zdrowe statusy kanałów w wyjściu heartbeat.
- `channels.defaults.heartbeat.showAlerts`: uwzględnia statusy zdegradowane/błędów w wyjściu heartbeat.
- `channels.defaults.heartbeat.useIndicator`: renderuje zwarte wyjście heartbeat w stylu wskaźnika.

### WhatsApp

WhatsApp działa przez web kanał gateway (`Baileys Web`). Uruchamia się automatycznie, gdy istnieje połączona sesja.

```json5
{
  channels: {
    whatsapp: {
      dmPolicy: "pairing", // pairing | allowlist | open | disabled
      allowFrom: ["+15555550123", "+447700900123"],
      textChunkLimit: 4000,
      chunkMode: "length", // length | newline
      mediaMaxMb: 50,
      sendReadReceipts: true, // niebieskie ptaszki (false w trybie self-chat)
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

<Accordion title="Wielo-kontowy WhatsApp">

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
- Opcjonalne `channels.whatsapp.defaultAccount` nadpisuje ten zapasowy wybór konta domyślnego, jeśli pasuje do skonfigurowanego identyfikatora konta.
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
      streaming: "partial", // off | partial | block | progress (default: off; włącz jawnie, aby uniknąć limitów szybkości edycji podglądu)
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

- Token bota: `channels.telegram.botToken` lub `channels.telegram.tokenFile` (tylko zwykły plik; symlinki są odrzucane), z `TELEGRAM_BOT_TOKEN` jako zapasem dla konta domyślnego.
- Opcjonalne `channels.telegram.defaultAccount` nadpisuje wybór konta domyślnego, jeśli pasuje do skonfigurowanego identyfikatora konta.
- W konfiguracjach wielo-kontowych (2+ identyfikatorów kont) ustaw jawne konto domyślne (`channels.telegram.defaultAccount` lub `channels.telegram.accounts.default`), aby uniknąć routingu zapasowego; `openclaw doctor` ostrzega, gdy go brakuje lub jest nieprawidłowe.
- `configWrites: false` blokuje zapisy konfiguracji inicjowane przez Telegram (migracje ID supergrup, `/config set|unset`).
- Wpisy najwyższego poziomu `bindings[]` z `type: "acp"` konfigurują trwałe powiązania ACP dla tematów forum (użyj kanonicznego `chatId:topic:topicId` w `match.peer.id`). Semantyka pól jest współdzielona w [ACP Agents](/pl/tools/acp-agents#channel-specific-settings).
- Podglądy strumieni Telegrama używają `sendMessage` + `editMessageText` (działa w czatach bezpośrednich i grupowych).
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
      streaming: "off", // off | partial | block | progress (progress mapuje się do partial na Discord)
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
        spawnSubagentSessions: false, // opt-in dla `sessions_spawn({ thread: true })`
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

- Token: `channels.discord.token`, z `DISCORD_BOT_TOKEN` jako zapasem dla konta domyślnego.
- Bezpośrednie wywołania wychodzące, które podają jawny Discord `token`, używają tego tokena do wywołania; ustawienia ponawiania/zasad kont nadal pochodzą z wybranego konta w aktywnej migawce środowiska uruchomieniowego.
- Opcjonalne `channels.discord.defaultAccount` nadpisuje wybór konta domyślnego, jeśli pasuje do skonfigurowanego identyfikatora konta.
- Używaj `user:<id>` (DM) lub `channel:<id>` (kanał serwera) dla celów dostarczania; same numeryczne ID są odrzucane.
- Slugi serwerów są pisane małymi literami, a spacje są zastępowane przez `-`; klucze kanałów używają nazwy w formie sluga (bez `#`). Preferuj ID serwerów.
- Wiadomości napisane przez boty są domyślnie ignorowane. `allowBots: true` je włącza; użyj `allowBots: "mentions"`, aby akceptować tylko wiadomości botów, które wspominają bota (własne wiadomości nadal są filtrowane).
- `channels.discord.guilds.<id>.ignoreOtherMentions` (oraz nadpisania kanałów) odrzuca wiadomości, które wspominają innego użytkownika lub rolę, ale nie bota (z wyłączeniem @everyone/@here).
- `maxLinesPerMessage` (domyślnie 17) dzieli wysokie wiadomości nawet wtedy, gdy mają mniej niż 2000 znaków.
- `channels.discord.threadBindings` kontroluje routing związany z wątkami Discord:
  - `enabled`: nadpisanie Discord dla funkcji sesji związanych z wątkami (`/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age` oraz dostarczanie/routing związany z powiązaniem)
  - `idleHours`: nadpisanie Discord dla automatycznego odfokusowania po bezczynności w godzinach (`0` wyłącza)
  - `maxAgeHours`: nadpisanie Discord dla twardego maksymalnego wieku w godzinach (`0` wyłącza)
  - `spawnSubagentSessions`: przełącznik opt-in dla automatycznego tworzenia/powiązywania wątków przez `sessions_spawn({ thread: true })`
- Wpisy najwyższego poziomu `bindings[]` z `type: "acp"` konfigurują trwałe powiązania ACP dla kanałów i wątków (użyj ID kanału/wątku w `match.peer.id`). Semantyka pól jest współdzielona w [ACP Agents](/pl/tools/acp-agents#channel-specific-settings).
- `channels.discord.ui.components.accentColor` ustawia kolor akcentu dla kontenerów komponentów Discord v2.
- `channels.discord.voice` włącza rozmowy w kanałach głosowych Discord oraz opcjonalne auto-dołączanie i nadpisania TTS.
- `channels.discord.voice.daveEncryption` i `channels.discord.voice.decryptionFailureTolerance` są przekazywane do opcji DAVE w `@discordjs/voice` (domyślnie `true` i `24`).
- OpenClaw dodatkowo próbuje odzyskać odbiór głosu przez opuszczenie i ponowne dołączenie do sesji głosowej po powtarzających się błędach odszyfrowania.
- `channels.discord.streaming` to kanoniczny klucz trybu strumieniowania. Starsze wartości `streamMode` i logiczne `streaming` są automatycznie migrowane.
- `channels.discord.autoPresence` mapuje dostępność środowiska uruchomieniowego na obecność bota (healthy => online, degraded => idle, exhausted => dnd) i pozwala na opcjonalne nadpisania tekstu statusu.
- `channels.discord.dangerouslyAllowNameMatching` ponownie włącza dopasowywanie po zmiennych nazwach/tagach (tryb kompatybilności break-glass).
- `channels.discord.execApprovals`: natywne dla Discord dostarczanie zatwierdzeń exec i autoryzacja zatwierdzających.
  - `enabled`: `true`, `false` lub `"auto"` (domyślnie). W trybie auto zatwierdzenia exec aktywują się, gdy zatwierdzający mogą zostać rozwiązani na podstawie `approvers` lub `commands.ownerAllowFrom`.
  - `approvers`: ID użytkowników Discord, którzy mogą zatwierdzać żądania exec. Gdy pominięte, używany jest zapas z `commands.ownerAllowFrom`.
  - `agentFilter`: opcjonalna lista zezwoleń identyfikatorów agentów. Pomiń, aby przekazywać zatwierdzenia dla wszystkich agentów.
  - `sessionFilter`: opcjonalne wzorce kluczy sesji (podciąg lub regex).
  - `target`: gdzie wysyłać prośby o zatwierdzenie. `"dm"` (domyślnie) wysyła je do DM zatwierdzających, `"channel"` wysyła je do kanału źródłowego, `"both"` wysyła do obu. Gdy target obejmuje `"channel"`, przyciski mogą być używane tylko przez rozwiązanych zatwierdzających.
  - `cleanupAfterResolve`: gdy `true`, usuwa DM zatwierdzeń po zatwierdzeniu, odrzuceniu lub przekroczeniu czasu.

**Tryby powiadomień reakcji:** `off` (brak), `own` (wiadomości bota, domyślnie), `all` (wszystkie wiadomości), `allowlist` (z `guilds.<id>.users` dla wszystkich wiadomości).

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

- JSON konta usługi: inline (`serviceAccount`) lub z pliku (`serviceAccountFile`).
- Obsługiwany jest również SecretRef dla konta usługi (`serviceAccountRef`).
- Zapasowe zmienne środowiskowe: `GOOGLE_CHAT_SERVICE_ACCOUNT` lub `GOOGLE_CHAT_SERVICE_ACCOUNT_FILE`.
- Używaj `spaces/<spaceId>` lub `users/<userId>` dla celów dostarczania.
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
      streaming: "partial", // off | partial | block | progress (tryb podglądu)
      nativeStreaming: true, // użyj natywnego API strumieniowania Slack, gdy streaming=partial
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

- **Socket mode** wymaga zarówno `botToken`, jak i `appToken` (`SLACK_BOT_TOKEN` + `SLACK_APP_TOKEN` jako zapas zmiennych środowiskowych dla konta domyślnego).
- **HTTP mode** wymaga `botToken` oraz `signingSecret` (na poziomie głównym lub per konto).
- `botToken`, `appToken`, `signingSecret` i `userToken` akceptują zwykłe
  ciągi tekstowe lub obiekty SecretRef.
- Migawki kont Slack ujawniają pola per poświadczenie dotyczące źródła/statusu, takie jak
  `botTokenSource`, `botTokenStatus`, `appTokenStatus` oraz, w trybie HTTP,
  `signingSecretStatus`. `configured_unavailable` oznacza, że konto jest
  skonfigurowane przez SecretRef, ale bieżąca ścieżka polecenia/środowiska uruchomieniowego nie mogła
  rozwiązać wartości sekretu.
- `configWrites: false` blokuje zapisy konfiguracji inicjowane przez Slack.
- Opcjonalne `channels.slack.defaultAccount` nadpisuje wybór konta domyślnego, jeśli pasuje do skonfigurowanego identyfikatora konta.
- `channels.slack.streaming` to kanoniczny klucz trybu strumieniowania. Starsze wartości `streamMode` i logiczne `streaming` są automatycznie migrowane.
- Używaj `user:<id>` (DM) lub `channel:<id>` dla celów dostarczania.

**Tryby powiadomień reakcji:** `off`, `own` (domyślnie), `all`, `allowlist` (z `reactionAllowlist`).

**Izolacja sesji wątków:** `thread.historyScope` jest per wątek (domyślnie) lub współdzielone w obrębie kanału. `thread.inheritParent` kopiuje transkrypt kanału nadrzędnego do nowych wątków.

- `typingReaction` dodaje tymczasową reakcję do przychodzącej wiadomości Slack podczas generowania odpowiedzi, a po zakończeniu ją usuwa. Użyj skrótu emoji Slack, takiego jak `"hourglass_flowing_sand"`.
- `channels.slack.execApprovals`: natywne dla Slack dostarczanie zatwierdzeń exec i autoryzacja zatwierdzających. Ten sam schemat co w Discord: `enabled` (`true`/`false`/`"auto"`), `approvers` (ID użytkowników Slack), `agentFilter`, `sessionFilter` oraz `target` (`"dm"`, `"channel"` lub `"both"`).

| Grupa działań | Domyślnie | Uwagi                    |
| ------------- | --------- | ------------------------ |
| reactions     | włączone  | Reagowanie + lista reakcji |
| messages      | włączone  | Odczyt/wysyłanie/edycja/usuwanie |
| pins          | włączone  | Przypnij/odepnij/lista   |
| memberInfo    | włączone  | Informacje o członku     |
| emojiList     | włączone  | Lista niestandardowych emoji |

### Mattermost

Mattermost jest dostarczany jako plugin: `openclaw plugins install @openclaw/mattermost`.

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
        // Opcjonalny jawny URL dla wdrożeń za reverse proxy/publicznych
        callbackUrl: "https://gateway.example.com/api/channels/mattermost/command",
      },
      textChunkLimit: 4000,
      chunkMode: "length",
    },
  },
}
```

Tryby czatu: `oncall` (odpowiada po wzmiance @, domyślnie), `onmessage` (każda wiadomość), `onchar` (wiadomości zaczynające się od prefiksu wyzwalacza).

Gdy natywne polecenia Mattermost są włączone:

- `commands.callbackPath` musi być ścieżką (na przykład `/api/channels/mattermost/command`), a nie pełnym URL.
- `commands.callbackUrl` musi rozwiązywać się do endpointu gateway OpenClaw i być osiągalny z serwera Mattermost.
- Natywne wywołania slash callback są uwierzytelniane za pomocą tokenów per polecenie zwracanych
  przez Mattermost podczas rejestracji poleceń slash. Jeśli rejestracja się nie powiedzie lub nie
  zostaną aktywowane żadne polecenia, OpenClaw odrzuca callbacki z
  `Unauthorized: invalid command token.`
- Dla prywatnych/tailnet/wewnętrznych hostów callback Mattermost może wymagać, aby
  `ServiceSettings.AllowedUntrustedInternalConnections` zawierało host/domenę callbacku.
  Używaj wartości host/domena, a nie pełnych URL.
- `channels.mattermost.configWrites`: zezwalaj lub blokuj zapisy konfiguracji inicjowane przez Mattermost.
- `channels.mattermost.requireMention`: wymagaj `@mention` przed odpowiedzią w kanałach.
- `channels.mattermost.groups.<channelId>.requireMention`: nadpisanie blokowania przez wzmianki per kanał (`"*"` dla domyślnego).
- Opcjonalne `channels.mattermost.defaultAccount` nadpisuje wybór konta domyślnego, jeśli pasuje do skonfigurowanego identyfikatora konta.

### Signal

```json5
{
  channels: {
    signal: {
      enabled: true,
      account: "+15555550123", // opcjonalne powiązanie z kontem
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

**Tryby powiadomień reakcji:** `off`, `own` (domyślnie), `all`, `allowlist` (z `reactionAllowlist`).

- `channels.signal.account`: przypina uruchamianie kanału do konkretnej tożsamości konta Signal.
- `channels.signal.configWrites`: zezwalaj lub blokuj zapisy konfiguracji inicjowane przez Signal.
- Opcjonalne `channels.signal.defaultAccount` nadpisuje wybór konta domyślnego, jeśli pasuje do skonfigurowanego identyfikatora konta.

### BlueBubbles

BlueBubbles to zalecana ścieżka iMessage (oparta na plugin, konfigurowana w `channels.bluebubbles`).

```json5
{
  channels: {
    bluebubbles: {
      enabled: true,
      dmPolicy: "pairing",
      // serverUrl, password, webhookPath, kontrola grup i zaawansowane działania:
      // zobacz /channels/bluebubbles
    },
  },
}
```

- Główne ścieżki kluczy objęte tutaj: `channels.bluebubbles`, `channels.bluebubbles.dmPolicy`.
- Opcjonalne `channels.bluebubbles.defaultAccount` nadpisuje wybór konta domyślnego, jeśli pasuje do skonfigurowanego identyfikatora konta.
- Wpisy najwyższego poziomu `bindings[]` z `type: "acp"` mogą wiązać rozmowy BlueBubbles z trwałymi sesjami ACP. Użyj uchwytu BlueBubbles lub ciągu docelowego (`chat_id:*`, `chat_guid:*`, `chat_identifier:*`) w `match.peer.id`. Współdzielona semantyka pól: [ACP Agents](/pl/tools/acp-agents#channel-specific-settings).
- Pełna konfiguracja kanału BlueBubbles jest udokumentowana w [BlueBubbles](/pl/channels/bluebubbles).

### iMessage

OpenClaw uruchamia `imsg rpc` (JSON-RPC przez stdio). Nie wymaga demona ani portu.

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

- Opcjonalne `channels.imessage.defaultAccount` nadpisuje wybór konta domyślnego, jeśli pasuje do skonfigurowanego identyfikatora konta.

- Wymaga Full Disk Access do bazy danych Messages.
- Preferuj cele `chat_id:<id>`. Użyj `imsg chats --limit 20`, aby wyświetlić listę czatów.
- `cliPath` może wskazywać wrapper SSH; ustaw `remoteHost` (`host` lub `user@host`) dla pobierania załączników przez SCP.
- `attachmentRoots` i `remoteAttachmentRoots` ograniczają ścieżki przychodzących załączników (domyślnie: `/Users/*/Library/Messages/Attachments`).
- SCP używa ścisłego sprawdzania klucza hosta, więc upewnij się, że klucz hosta przekaźnika już istnieje w `~/.ssh/known_hosts`.
- `channels.imessage.configWrites`: zezwalaj lub blokuj zapisy konfiguracji inicjowane przez iMessage.
- Wpisy najwyższego poziomu `bindings[]` z `type: "acp"` mogą wiązać rozmowy iMessage z trwałymi sesjami ACP. Użyj znormalizowanego uchwytu lub jawnego celu czatu (`chat_id:*`, `chat_guid:*`, `chat_identifier:*`) w `match.peer.id`. Współdzielona semantyka pól: [ACP Agents](/pl/tools/acp-agents#channel-specific-settings).

<Accordion title="Przykład wrappera SSH dla iMessage">

```bash
#!/usr/bin/env bash
exec ssh -T gateway-host imsg "$@"
```

</Accordion>

### Matrix

Matrix jest wspierany przez rozszerzenie i konfigurowany w `channels.matrix`.

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
- `channels.matrix.proxy` kieruje ruch HTTP Matrix przez jawny serwer proxy HTTP(S). Nazwane konta mogą to nadpisać przez `channels.matrix.accounts.<id>.proxy`.
- `channels.matrix.allowPrivateNetwork` zezwala na prywatne/wewnętrzne homeserwery. `proxy` i `allowPrivateNetwork` to niezależne mechanizmy.
- `channels.matrix.defaultAccount` wybiera preferowane konto w konfiguracjach wielo-kontowych.
- `channels.matrix.execApprovals`: natywne dla Matrix dostarczanie zatwierdzeń exec i autoryzacja zatwierdzających.
  - `enabled`: `true`, `false` lub `"auto"` (domyślnie). W trybie auto zatwierdzenia exec aktywują się, gdy zatwierdzający mogą zostać rozwiązani na podstawie `approvers` lub `commands.ownerAllowFrom`.
  - `approvers`: ID użytkowników Matrix (np. `@owner:example.org`), którzy mogą zatwierdzać żądania exec.
  - `agentFilter`: opcjonalna lista zezwoleń identyfikatorów agentów. Pomiń, aby przekazywać zatwierdzenia dla wszystkich agentów.
  - `sessionFilter`: opcjonalne wzorce kluczy sesji (podciąg lub regex).
  - `target`: gdzie wysyłać prośby o zatwierdzenie. `"dm"` (domyślnie), `"channel"` (pokój źródłowy) lub `"both"`.
  - Nadpisania per konto: `channels.matrix.accounts.<id>.execApprovals`.
- `channels.matrix.dm.sessionScope` kontroluje, jak DM Matrix są grupowane w sesje: `per-user` (domyślnie) współdzieli po routowanym peeringu, natomiast `per-room` izoluje każdy pokój DM.
- Sondy statusu Matrix i wyszukiwania katalogu live używają tej samej polityki proxy co ruch środowiska uruchomieniowego.
- Pełna konfiguracja Matrix, zasady targetowania i przykłady konfiguracji są udokumentowane w [Matrix](/pl/channels/matrix).

### Microsoft Teams

Microsoft Teams jest wspierany przez rozszerzenie i konfigurowany w `channels.msteams`.

```json5
{
  channels: {
    msteams: {
      enabled: true,
      configWrites: true,
      // appId, appPassword, tenantId, webhook, zasady zespołów/kanałów:
      // zobacz /channels/msteams
    },
  },
}
```

- Główne ścieżki kluczy objęte tutaj: `channels.msteams`, `channels.msteams.configWrites`.
- Pełna konfiguracja Teams (poświadczenia, webhook, zasady DM/grup, nadpisania per zespół/per kanał) jest udokumentowana w [Microsoft Teams](/pl/channels/msteams).

### IRC

IRC jest wspierany przez rozszerzenie i konfigurowany w `channels.irc`.

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

- Główne ścieżki kluczy objęte tutaj: `channels.irc`, `channels.irc.dmPolicy`, `channels.irc.configWrites`, `channels.irc.nickserv.*`.
- Opcjonalne `channels.irc.defaultAccount` nadpisuje wybór konta domyślnego, jeśli pasuje do skonfigurowanego identyfikatora konta.
- Pełna konfiguracja kanału IRC (host/port/TLS/kanały/listy zezwoleń/blokowanie przez wzmianki) jest udokumentowana w [IRC](/pl/channels/irc).

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
- Tokeny ze zmiennych środowiskowych mają zastosowanie tylko do konta **default**.
- Bazowe ustawienia kanału dotyczą wszystkich kont, chyba że zostaną nadpisane per konto.
- Użyj `bindings[].match.accountId`, aby kierować każde konto do innego agenta.
- Jeśli dodasz konto inne niż domyślne przez `openclaw channels add` (lub onboarding kanału), gdy nadal używasz jednokontowej konfiguracji kanału na poziomie głównym, OpenClaw najpierw promuje wartości głównego poziomu ograniczone do konta do mapy kont kanału, aby oryginalne konto nadal działało. Większość kanałów przenosi je do `channels.<channel>.accounts.default`; Matrix może zamiast tego zachować istniejący pasujący cel nazwany/domyslny.
- Istniejące powiązania tylko-kanałowe (bez `accountId`) nadal dopasowują konto domyślne; powiązania ograniczone do kont pozostają opcjonalne.
- `openclaw doctor --fix` również naprawia mieszane kształty, przenosząc wartości głównego poziomu ograniczone do konta do promowanego konta wybranego dla tego kanału. Większość kanałów używa `accounts.default`; Matrix może zamiast tego zachować istniejący pasujący cel nazwany/domyslny.

### Inne kanały rozszerzeń

Wiele kanałów rozszerzeń jest konfigurowanych jako `channels.<id>` i opisanych na swoich dedykowanych stronach kanałów (na przykład Feishu, Matrix, LINE, Nostr, Zalo, Nextcloud Talk, Synology Chat i Twitch).
Zobacz pełny indeks kanałów: [Channels](/pl/channels).

### Blokowanie przez wzmianki w czatach grupowych

Wiadomości grupowe domyślnie **wymagają wzmianki** (wzmianka w metadanych lub bezpieczne wzorce regex). Dotyczy grupowych czatów WhatsApp, Telegram, Discord, Google Chat i iMessage.

**Typy wzmianek:**

- **Wzmianki w metadanych**: natywne platformowe @-wzmianki. Ignorowane w trybie self-chat WhatsApp.
- **Wzorce tekstowe**: bezpieczne wzorce regex w `agents.list[].groupChat.mentionPatterns`. Nieprawidłowe wzorce i niebezpieczne zagnieżdżone powtórzenia są ignorowane.
- Blokowanie przez wzmianki jest egzekwowane tylko wtedy, gdy wykrywanie jest możliwe (natywne wzmianki lub co najmniej jeden wzorzec).

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

`messages.groupChat.historyLimit` ustawia globalną wartość domyślną. Kanały mogą ją nadpisać przez `channels.<channel>.historyLimit` (lub per konto). Ustaw `0`, aby wyłączyć.

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

Rozwiązywanie: nadpisanie per DM → domyślne dostawcy → brak limitu (wszystko zachowane).

Obsługiwane: `telegram`, `whatsapp`, `discord`, `slack`, `signal`, `imessage`, `msteams`.

#### Tryb self-chat

Dodaj własny numer do `allowFrom`, aby włączyć tryb self-chat (ignoruje natywne @-wzmianki, odpowiada tylko na wzorce tekstowe):

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

### Commands (obsługa poleceń czatu)

```json5
{
  commands: {
    native: "auto", // rejestruj natywne polecenia, gdy są obsługiwane
    text: true, // parsuj /commands w wiadomościach czatu
    bash: false, // zezwalaj na ! (alias: /bash)
    bashForegroundMs: 2000,
    config: false, // zezwalaj na /config
    debug: false, // zezwalaj na /debug
    restart: false, // zezwalaj na /restart + narzędzie restartu gateway
    allowFrom: {
      "*": ["user1"],
      discord: ["user:123"],
    },
    useAccessGroups: true,
  },
}
```

<Accordion title="Szczegóły poleceń">

- Polecenia tekstowe muszą być **samodzielnymi** wiadomościami zaczynającymi się od `/`.
- `native: "auto"` włącza natywne polecenia dla Discord/Telegram, pozostawia Slack wyłączony.
- Nadpisanie per kanał: `channels.discord.commands.native` (bool lub `"auto"`). `false` czyści wcześniej zarejestrowane polecenia.
- `channels.telegram.customCommands` dodaje dodatkowe wpisy menu bota Telegram.
- `bash: true` włącza `! <cmd>` dla powłoki hosta. Wymaga `tools.elevated.enabled` oraz nadawcy obecnego w `tools.elevated.allowFrom.<channel>`.
- `config: true` włącza `/config` (odczyt/zapis `openclaw.json`). Dla klientów gateway `chat.send` trwałe zapisy `/config set|unset` wymagają także `operator.admin`; tylko do odczytu `/config show` pozostaje dostępne dla zwykłych klientów operatora z zakresem zapisu.
- `channels.<provider>.configWrites` kontroluje mutacje konfiguracji per kanał (domyślnie: true).
- Dla kanałów wielo-kontowych `channels.<provider>.accounts.<id>.configWrites` kontroluje również zapisy kierowane do tego konta (na przykład `/allowlist --config --account <id>` lub `/config set channels.<provider>.accounts.<id>...`).
- `allowFrom` jest per dostawca. Gdy jest ustawione, stanowi **jedyne** źródło autoryzacji (listy zezwoleń kanału/parowanie i `useAccessGroups` są ignorowane).
- `useAccessGroups: false` pozwala poleceniom omijać zasady grup dostępu, gdy `allowFrom` nie jest ustawione.

</Accordion>

---

## Domyślne ustawienia agenta

### `agents.defaults.workspace`

Domyślnie: `~/.openclaw/workspace`.

```json5
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
}
```

### `agents.defaults.repoRoot`

Opcjonalny katalog główny repozytorium pokazywany w wierszu Runtime system promptu. Jeśli nie jest ustawiony, OpenClaw wykrywa go automatycznie, idąc w górę od workspace.

```json5
{
  agents: { defaults: { repoRoot: "~/Projects/openclaw" } },
}
```

### `agents.defaults.skills`

Opcjonalna domyślna lista zezwoleń Skills dla agentów, które nie ustawiają
`agents.list[].skills`.

```json5
{
  agents: {
    defaults: { skills: ["github", "weather"] },
    list: [
      { id: "writer" }, // dziedziczy github, weather
      { id: "docs", skills: ["docs-search"] }, // zastępuje wartości domyślne
      { id: "locked-down", skills: [] }, // bez skills
    ],
  },
}
```

- Pomiń `agents.defaults.skills`, aby domyślnie nie ograniczać Skills.
- Pomiń `agents.list[].skills`, aby dziedziczyć wartości domyślne.
- Ustaw `agents.list[].skills: []`, aby nie mieć żadnych Skills.
- Niepusta lista `agents.list[].skills` jest ostatecznym zestawem dla tego agenta;
  nie jest łączona z wartościami domyślnymi.

### `agents.defaults.skipBootstrap`

Wyłącza automatyczne tworzenie plików bootstrap workspace (`AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`, `BOOTSTRAP.md`).

```json5
{
  agents: { defaults: { skipBootstrap: true } },
}
```

### `agents.defaults.bootstrapMaxChars`

Maksymalna liczba znaków na plik bootstrap workspace przed obcięciem. Domyślnie: `20000`.

```json5
{
  agents: { defaults: { bootstrapMaxChars: 20000 } },
}
```

### `agents.defaults.bootstrapTotalMaxChars`

Maksymalna łączna liczba znaków wstrzykniętych ze wszystkich plików bootstrap workspace. Domyślnie: `150000`.

```json5
{
  agents: { defaults: { bootstrapTotalMaxChars: 150000 } },
}
```

### `agents.defaults.bootstrapPromptTruncationWarning`

Kontroluje widoczny dla agenta tekst ostrzeżenia, gdy kontekst bootstrap zostaje obcięty.
Domyślnie: `"once"`.

- `"off"`: nigdy nie wstrzykuje tekstu ostrzeżenia do system promptu.
- `"once"`: wstrzykuje ostrzeżenie raz dla każdej unikalnej sygnatury obcięcia (zalecane).
- `"always"`: wstrzykuje ostrzeżenie przy każdym uruchomieniu, gdy istnieje obcięcie.

```json5
{
  agents: { defaults: { bootstrapPromptTruncationWarning: "once" } }, // off | once | always
}
```

### `agents.defaults.imageMaxDimensionPx`

Maksymalny rozmiar w pikselach dłuższego boku obrazu w blokach obrazu transkryptu/narzędzia przed wywołaniami dostawcy.
Domyślnie: `1200`.

Niższe wartości zwykle zmniejszają zużycie tokenów vision i rozmiar payloadu żądania przy uruchomieniach z dużą liczbą zrzutów ekranu.
Wyższe wartości zachowują więcej szczegółów wizualnych.

```json5
{
  agents: { defaults: { imageMaxDimensionPx: 1200 } },
}
```

### `agents.defaults.userTimezone`

Strefa czasowa dla kontekstu system promptu (nie dla znaczników czasu wiadomości). Zapasowo używana jest strefa czasowa hosta.

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

- `model`: akceptuje albo ciąg (`"provider/model"`), albo obiekt (`{ primary, fallbacks }`).
  - Forma ciągu ustawia tylko model główny.
  - Forma obiektu ustawia model główny oraz uporządkowane modele przełączenia awaryjnego.
- `imageModel`: akceptuje albo ciąg (`"provider/model"`), albo obiekt (`{ primary, fallbacks }`).
  - Używany przez ścieżkę narzędzia `image` jako konfiguracja modelu vision.
  - Używany także jako routing zapasowy, gdy wybrany/domyslny model nie może przyjmować obrazów.
- `imageGenerationModel`: akceptuje albo ciąg (`"provider/model"`), albo obiekt (`{ primary, fallbacks }`).
  - Używany przez współdzieloną funkcję generowania obrazów i każdą przyszłą powierzchnię narzędzia/plugin, która generuje obrazy.
  - Typowe wartości: `google/gemini-3.1-flash-image-preview` dla natywnego generowania obrazów Gemini, `fal/fal-ai/flux/dev` dla fal lub `openai/gpt-image-1` dla OpenAI Images.
  - Jeśli wybierzesz bezpośrednio dostawcę/model, skonfiguruj także pasujące uwierzytelnienie/klucz API dostawcy (na przykład `GEMINI_API_KEY` lub `GOOGLE_API_KEY` dla `google/*`, `OPENAI_API_KEY` dla `openai/*`, `FAL_KEY` dla `fal/*`).
  - Jeśli pole zostanie pominięte, `image_generate` nadal może wywnioskować domyślnego dostawcę z uwierzytelnieniem. Najpierw próbuje bieżącego dostawcy domyślnego, a następnie pozostałych zarejestrowanych dostawców generowania obrazów w kolejności identyfikatorów dostawców.
- `musicGenerationModel`: akceptuje albo ciąg (`"provider/model"`), albo obiekt (`{ primary, fallbacks }`).
  - Używany przez współdzieloną funkcję generowania muzyki i wbudowane narzędzie `music_generate`.
  - Typowe wartości: `google/lyria-3-clip-preview`, `google/lyria-3-pro-preview` lub `minimax/music-2.5+`.
  - Jeśli pole zostanie pominięte, `music_generate` nadal może wywnioskować domyślnego dostawcę z uwierzytelnieniem. Najpierw próbuje bieżącego dostawcy domyślnego, a następnie pozostałych zarejestrowanych dostawców generowania muzyki w kolejności identyfikatorów dostawców.
  - Jeśli wybierzesz bezpośrednio dostawcę/model, skonfiguruj także pasujące uwierzytelnienie/klucz API dostawcy.
- `videoGenerationModel`: akceptuje albo ciąg (`"provider/model"`), albo obiekt (`{ primary, fallbacks }`).
  - Używany przez współdzieloną funkcję generowania wideo i wbudowane narzędzie `video_generate`.
  - Typowe wartości: `qwen/wan2.6-t2v`, `qwen/wan2.6-i2v`, `qwen/wan2.6-r2v`, `qwen/wan2.6-r2v-flash` lub `qwen/wan2.7-r2v`.
  - Jeśli pole zostanie pominięte, `video_generate` nadal może wywnioskować domyślnego dostawcę z uwierzytelnieniem. Najpierw próbuje bieżącego dostawcy domyślnego, a następnie pozostałych zarejestrowanych dostawców generowania wideo w kolejności identyfikatorów dostawców.
  - Jeśli wybierzesz bezpośrednio dostawcę/model, skonfiguruj także pasujące uwierzytelnienie/klucz API dostawcy.
  - Dołączony dostawca generowania wideo Qwen obsługuje obecnie maksymalnie 1 wyjściowe wideo, 1 wejściowy obraz, 4 wejściowe wideo, czas trwania 10 sekund oraz opcje na poziomie dostawcy `size`, `aspectRatio`, `resolution`, `audio` i `watermark`.
- `pdfModel`: akceptuje albo ciąg (`"provider/model"`), albo obiekt (`{ primary, fallbacks }`).
  - Używany przez narzędzie `pdf` do routingu modelu.
  - Jeśli pole zostanie pominięte, narzędzie PDF wraca kolejno do `imageModel`, a następnie do rozwiązanego modelu sesji/domyslnego.
- `pdfMaxBytesMb`: domyślny limit rozmiaru PDF dla narzędzia `pdf`, gdy `maxBytesMb` nie jest przekazane w chwili wywołania.
- `pdfMaxPages`: domyślna maksymalna liczba stron uwzględnianych przez tryb zapasowego wyodrębniania w narzędziu `pdf`.
- `verboseDefault`: domyślny poziom verbose dla agentów. Wartości: `"off"`, `"on"`, `"full"`. Domyślnie: `"off"`.
- `elevatedDefault`: domyślny poziom elevated-output dla agentów. Wartości: `"off"`, `"on"`, `"ask"`, `"full"`. Domyślnie: `"on"`.
- `model.primary`: format `provider/model` (np. `openai/gpt-5.4`). Jeśli pominiesz dostawcę, OpenClaw najpierw próbuje aliasu, potem unikalnego dopasowania dokładnego identyfikatora modelu wśród skonfigurowanych dostawców, a dopiero potem wraca do skonfigurowanego dostawcy domyślnego (przestarzałe zachowanie kompatybilności, więc preferuj jawne `provider/model`). Jeśli ten dostawca nie udostępnia już skonfigurowanego modelu domyślnego, OpenClaw wraca do pierwszego skonfigurowanego dostawcy/modelu zamiast zgłaszać nieaktualny domyślny model usuniętego dostawcy.
- `models`: skonfigurowany katalog modeli i lista zezwoleń dla `/model`. Każdy wpis może zawierać `alias` (skrót) oraz `params` (parametry zależne od dostawcy, np. `temperature`, `maxTokens`, `cacheRetention`, `context1m`).
- `params`: globalne domyślne parametry dostawcy stosowane do wszystkich modeli. Ustawiane w `agents.defaults.params` (np. `{ cacheRetention: "long" }`).
- Kolejność scalania `params` (konfiguracja): `agents.defaults.params` (globalna baza) jest nadpisywane przez `agents.defaults.models["provider/model"].params` (per model), a następnie `agents.list[].params` (dla pasującego identyfikatora agenta) nadpisuje po kluczu. Szczegóły znajdziesz w [Prompt Caching](/pl/reference/prompt-caching).
- Narzędzia zapisujące konfigurację, które modyfikują te pola (na przykład `/models set`, `/models set-image` oraz polecenia dodawania/usuwania fallback), zapisują kanoniczną formę obiektu i w miarę możliwości zachowują istniejące listy fallback.
- `maxConcurrent`: maksymalna liczba równoległych uruchomień agentów między sesjami (każda sesja nadal jest serializowana). Domyślnie: 4.

**Wbudowane skróty aliasów** (mają zastosowanie tylko wtedy, gdy model jest w `agents.defaults.models`):

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

Twoje skonfigurowane aliasy zawsze mają pierwszeństwo przed domyślnymi.

Modele Z.AI GLM-4.x automatycznie włączają tryb thinking, chyba że ustawisz `--thinking off` lub samodzielnie zdefiniujesz `agents.defaults.models["zai/<model>"].params.thinking`.
Modele Z.AI domyślnie włączają `tool_stream` dla strumieniowania wywołań narzędzi. Ustaw `agents.defaults.models["zai/<model>"].params.tool_stream` na `false`, aby to wyłączyć.
Modele Anthropic Claude 4.6 domyślnie używają trybu thinking `adaptive`, gdy nie ustawiono jawnego poziomu thinking.

- Sesje są obsługiwane, gdy ustawiono `sessionArg`.
- Przekazywanie obrazów jest obsługiwane, gdy `imageArg` akceptuje ścieżki plików.

### `agents.defaults.heartbeat`

Okresowe uruchomienia heartbeat.

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m", // 0m wyłącza
        model: "openai/gpt-5.4-mini",
        includeReasoning: false,
        lightContext: false, // domyślnie: false; true zachowuje tylko HEARTBEAT.md z plików bootstrap workspace
        isolatedSession: false, // domyślnie: false; true uruchamia każdy heartbeat w świeżej sesji (bez historii rozmowy)
        session: "main",
        to: "+15555550123",
        directPolicy: "allow", // allow (domyślnie) | block
        target: "none", // domyślnie: none | opcje: last | whatsapp | telegram | discord | ...
        prompt: "Read HEARTBEAT.md if it exists...",
        ackMaxChars: 300,
        suppressToolErrorWarnings: false,
      },
    },
  },
}
```

- `every`: ciąg czasu trwania (ms/s/m/h). Domyślnie: `30m` (uwierzytelnianie kluczem API) lub `1h` (uwierzytelnianie OAuth). Ustaw `0m`, aby wyłączyć.
- `suppressToolErrorWarnings`: gdy true, ukrywa payloady ostrzeżeń o błędach narzędzi podczas uruchomień heartbeat.
- `directPolicy`: zasada dostarczania bezpośredniego/DM. `allow` (domyślnie) zezwala na dostarczanie do celu bezpośredniego. `block` blokuje dostarczanie do celu bezpośredniego i emituje `reason=dm-blocked`.
- `lightContext`: gdy true, uruchomienia heartbeat używają lekkiego kontekstu bootstrap i zachowują tylko `HEARTBEAT.md` z plików bootstrap workspace.
- `isolatedSession`: gdy true, każde uruchomienie heartbeat działa w świeżej sesji bez wcześniejszej historii rozmowy. Ten sam wzorzec izolacji co cron `sessionTarget: "isolated"`. Zmniejsza koszt tokenów na heartbeat z około 100K do około 2–5K tokenów.
- Per agent: ustaw `agents.list[].heartbeat`. Gdy dowolny agent definiuje `heartbeat`, heartbeat uruchamiają **tylko te agenty**.
- Heartbeat uruchamia pełne tury agenta — krótsze interwały zużywają więcej tokenów.

### `agents.defaults.compaction`

```json5
{
  agents: {
    defaults: {
      compaction: {
        mode: "safeguard", // default | safeguard
        timeoutSeconds: 900,
        reserveTokensFloor: 24000,
        identifierPolicy: "strict", // strict | off | custom
        identifierInstructions: "Preserve deployment IDs, ticket IDs, and host:port pairs exactly.", // używane, gdy identifierPolicy=custom
        postCompactionSections: ["Session Startup", "Red Lines"], // [] wyłącza ponowne wstrzyknięcie
        model: "openrouter/anthropic/claude-sonnet-4-6", // opcjonalne nadpisanie modelu tylko dla compaction
        notifyUser: true, // wyślij krótką informację, gdy zaczyna się compaction (domyślnie: false)
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

- `mode`: `default` lub `safeguard` (sumaryzacja fragmentami dla długich historii). Zobacz [Compaction](/pl/concepts/compaction).
- `timeoutSeconds`: maksymalna liczba sekund dozwolona dla pojedynczej operacji compaction, po której OpenClaw ją przerywa. Domyślnie: `900`.
- `identifierPolicy`: `strict` (domyślnie), `off` lub `custom`. `strict` poprzedza sumaryzację compaction wbudowanymi wytycznymi dotyczącymi zachowania nieprzezroczystych identyfikatorów.
- `identifierInstructions`: opcjonalny niestandardowy tekst zachowania identyfikatorów używany, gdy `identifierPolicy=custom`.
- `postCompactionSections`: opcjonalne nazwy sekcji H2/H3 z AGENTS.md do ponownego wstrzyknięcia po compaction. Domyślnie `["Session Startup", "Red Lines"]`; ustaw `[]`, aby wyłączyć ponowne wstrzyknięcie. Gdy nie jest ustawione lub jawnie ustawione na tę domyślną parę, starsze nagłówki `Every Session`/`Safety` są również akceptowane jako zapas zgodności.
- `model`: opcjonalne nadpisanie `provider/model-id` tylko dla sumaryzacji compaction. Użyj tego, gdy główna sesja powinna pozostać na jednym modelu, ale podsumowania compaction powinny działać na innym; gdy pole nie jest ustawione, compaction używa modelu głównego sesji.
- `notifyUser`: gdy `true`, wysyła krótką informację użytkownikowi, gdy zaczyna się compaction (na przykład „Compacting context...”). Domyślnie wyłączone, aby compaction pozostał cichy.
- `memoryFlush`: cicha tura agentowa przed automatycznym compaction w celu zapisania trwałych wspomnień. Pomijana, gdy workspace jest tylko do odczytu.

### `agents.defaults.contextPruning`

Usuwa **stare wyniki narzędzi** z kontekstu w pamięci przed wysłaniem do LLM. **Nie** modyfikuje historii sesji na dysku.

```json5
{
  agents: {
    defaults: {
      contextPruning: {
        mode: "cache-ttl", // off | cache-ttl
        ttl: "1h", // czas trwania (ms/s/m/h), domyślna jednostka: minuty
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
- `ttl` kontroluje, jak często przycinanie może zostać uruchomione ponownie (po ostatnim dotknięciu cache).
- Przycinanie najpierw miękko skraca zbyt duże wyniki narzędzi, a następnie w razie potrzeby twardo czyści starsze wyniki narzędzi.

**Miękkie skracanie** zachowuje początek i koniec oraz wstawia `...` pośrodku.

**Twarde czyszczenie** zastępuje cały wynik narzędzia placeholderem.

Uwagi:

- Bloki obrazów nigdy nie są skracane/czyszczone.
- Współczynniki są oparte na znakach (w przybliżeniu), a nie na dokładnej liczbie tokenów.
- Jeśli istnieje mniej niż `keepLastAssistants` wiadomości asystenta, przycinanie jest pomijane.

</Accordion>

Szczegóły zachowania znajdziesz w [Session Pruning](/pl/concepts/session-pruning).

### Block streaming

```json5
{
  agents: {
    defaults: {
      blockStreamingDefault: "off", // on | off
      blockStreamingBreak: "text_end", // text_end | message_end
      blockStreamingChunk: { minChars: 800, maxChars: 1200 },
      blockStreamingCoalesce: { idleMs: 1000 },
      humanDelay: { mode: "natural" }, // off | natural | custom (użyj minMs/maxMs)
    },
  },
}
```

- Kanały inne niż Telegram wymagają jawnego `*.blockStreaming: true`, aby włączyć odpowiedzi blokowe.
- Nadpisania kanałów: `channels.<channel>.blockStreamingCoalesce` (oraz warianty per konto). Signal/Slack/Discord/Google Chat domyślnie używają `minChars: 1500`.
- `humanDelay`: losowa przerwa między odpowiedziami blokowymi. `natural` = 800–2500 ms. Nadpisanie per agent: `agents.list[].humanDelay`.

Szczegóły zachowania i chunkowania znajdziesz w [Streaming](/pl/concepts/streaming).

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

- Domyślnie: `instant` dla czatów bezpośrednich/wzmianek, `message` dla niewspomnianych czatów grupowych.
- Nadpisania per sesja: `session.typingMode`, `session.typingIntervalSeconds`.

Zobacz [Typing Indicators](/pl/concepts/typing-indicators).

<a id="agentsdefaultssandbox"></a>

### `agents.defaults.sandbox`

Opcjonalne sandboxing dla osadzonego agenta. Zobacz pełny przewodnik: [Sandboxing](/pl/gateway/sandboxing).

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
          // Obsługiwane są też SecretRef / treści inline:
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

- `docker`: lokalne środowisko uruchomieniowe Docker (domyślnie)
- `ssh`: generyczne zdalne środowisko uruchomieniowe oparte na SSH
- `openshell`: środowisko uruchomieniowe OpenShell

Gdy wybrane jest `backend: "openshell"`, ustawienia specyficzne dla środowiska uruchomieniowego są przenoszone do
`plugins.entries.openshell.config`.

**Konfiguracja backendu SSH:**

- `target`: cel SSH w formacie `user@host[:port]`
- `command`: polecenie klienta SSH (domyślnie: `ssh`)
- `workspaceRoot`: bezwzględny zdalny katalog główny używany dla workspace per zakres
- `identityFile` / `certificateFile` / `knownHostsFile`: istniejące lokalne pliki przekazywane do OpenSSH
- `identityData` / `certificateData` / `knownHostsData`: treści inline lub SecretRef, które OpenClaw materializuje do plików tymczasowych w czasie wykonywania
- `strictHostKeyChecking` / `updateHostKeys`: przełączniki zasad klucza hosta OpenSSH

**Priorytet uwierzytelniania SSH:**

- `identityData` ma pierwszeństwo przed `identityFile`
- `certificateData` ma pierwszeństwo przed `certificateFile`
- `knownHostsData` ma pierwszeństwo przed `knownHostsFile`
- Wartości `*Data` oparte na SecretRef są rozwiązywane z aktywnej migawki środowiska uruchomieniowego sekretów przed rozpoczęciem sesji sandbox

**Zachowanie backendu SSH:**

- inicjuje zdalny workspace raz po utworzeniu lub odtworzeniu
- następnie utrzymuje zdalny workspace SSH jako kanoniczny
- kieruje `exec`, narzędzia plikowe i ścieżki mediów przez SSH
- nie synchronizuje automatycznie zmian zdalnych z powrotem do hosta
- nie obsługuje kontenerów przeglądarki w sandboxie

**Dostęp do workspace:**

- `none`: workspace sandbox per zakres w `~/.openclaw/sandboxes`
- `ro`: workspace sandbox w `/workspace`, workspace agenta montowany tylko do odczytu w `/agent`
- `rw`: workspace agenta montowany do odczytu/zapisu w `/workspace`

**Zakres:**

- `session`: kontener + workspace per sesja
- `agent`: jeden kontener + workspace na agenta (domyślnie)
- `shared`: współdzielony kontener i workspace (bez izolacji między sesjami)

**Konfiguracja plugin OpenShell:**

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
          gateway: "lab", // opcjonalne
          gatewayEndpoint: "https://lab.example", // opcjonalne
          policy: "strict", // opcjonalny identyfikator polityki OpenShell
          providers: ["openai"], // opcjonalne
          autoProviders: true,
          timeoutSeconds: 120,
        },
      },
    },
  },
}
```

**Tryb OpenShell:**

- `mirror`: inicjalizuje zdalny z lokalnego przed exec, synchronizuje z powrotem po exec; lokalny workspace pozostaje kanoniczny
- `remote`: inicjalizuje zdalny raz podczas tworzenia sandbox, następnie utrzymuje zdalny workspace jako kanoniczny

W trybie `remote` lokalne edycje hosta wykonane poza OpenClaw nie są automatycznie synchronizowane do sandbox po kroku inicjalizacji.
Transport odbywa się przez SSH do sandbox OpenShell, ale plugin jest właścicielem cyklu życia sandbox i opcjonalnej synchronizacji mirror.

**`setupCommand`** uruchamia się raz po utworzeniu kontenera (przez `sh -lc`). Wymaga wychodzącego połączenia sieciowego, zapisywalnego katalogu głównego i użytkownika root.

**Kontenery domyślnie używają `network: "none"`** — ustaw `"bridge"` (lub niestandardową sieć bridge), jeśli agent potrzebuje dostępu wychodzącego.
`"host"` jest blokowane. `"container:<id>"` jest domyślnie blokowane, chyba że jawnie ustawisz
`sandbox.docker.dangerouslyAllowContainerNamespaceJoin: true` (break-glass).

**Przychodzące załączniki** są umieszczane w `media/inbound/*` w aktywnym workspace.

**`docker.binds`** montuje dodatkowe katalogi hosta; globalne i per-agent binds są scalane.

**Przeglądarka w sandboxie** (`sandbox.browser.enabled`): Chromium + CDP w kontenerze. URL noVNC jest wstrzykiwany do system promptu. Nie wymaga `browser.enabled` w `openclaw.json`.
Dostęp obserwatora noVNC domyślnie używa uwierzytelniania VNC, a OpenClaw emituje URL z krótkotrwałym tokenem (zamiast ujawniać hasło we współdzielonym URL).

- `allowHostControl: false` (domyślnie) blokuje sesjom sandbox targetowanie przeglądarki hosta.
- `network` domyślnie ma wartość `openclaw-sandbox-browser` (dedykowana sieć bridge). Ustaw `bridge` tylko wtedy, gdy jawnie chcesz globalnej łączności bridge.
- `cdpSourceRange` opcjonalnie ogranicza wejście CDP na brzegu kontenera do zakresu CIDR (na przykład `172.21.0.1/32`).
- `sandbox.browser.binds` montuje dodatkowe katalogi hosta tylko do kontenera przeglądarki sandbox. Gdy jest ustawione (w tym `[]`), zastępuje `docker.binds` dla kontenera przeglądarki.
- Domyślne parametry uruchamiania są zdefiniowane w `scripts/sandbox-browser-entrypoint.sh` i dostrojone dla hostów kontenerowych:
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
  - `--disable-3d-apis`, `--disable-software-rasterizer` oraz `--disable-gpu` są
    domyślnie włączone i można je wyłączyć przez
    `OPENCLAW_BROWSER_DISABLE_GRAPHICS_FLAGS=0`, jeśli użycie WebGL/3D tego wymaga.
  - `OPENCLAW_BROWSER_DISABLE_EXTENSIONS=0` ponownie włącza rozszerzenia, jeśli Twój workflow
    od nich zależy.
  - `--renderer-process-limit=2` można zmienić przez
    `OPENCLAW_BROWSER_RENDERER_PROCESS_LIMIT=<N>`; ustaw `0`, aby użyć
    domyślnego limitu procesów Chromium.
  - oraz `--no-sandbox` i `--disable-setuid-sandbox`, gdy `noSandbox` jest włączone.
  - Domyślne wartości są bazą obrazu kontenera; użyj niestandardowego obrazu przeglądarki z niestandardowym
    entrypointem, aby zmienić domyślne ustawienia kontenera.

</Accordion>

Sandboxing przeglądarki i `sandbox.docker.binds` są obecnie obsługiwane tylko przez Docker.

Zbuduj obrazy:

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
        model: "anthropic/claude-opus-4-6", // lub { primary, fallbacks }
        thinkingDefault: "high", // nadpisanie domyślnego poziomu thinking per agent
        reasoningDefault: "on", // nadpisanie domyślnej widoczności reasoning per agent
        fastModeDefault: false, // nadpisanie domyślnego fast mode per agent
        params: { cacheRetention: "none" }, // nadpisuje pasujące defaults.models params po kluczu
        skills: ["docs-search"], // zastępuje agents.defaults.skills, gdy ustawione
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
- `default`: gdy ustawiono wiele, wygrywa pierwszy (zapisywane jest ostrzeżenie). Jeśli żaden nie jest ustawiony, domyślny jest pierwszy wpis listy.
- `model`: forma ciągu nadpisuje tylko `primary`; forma obiektu `{ primary, fallbacks }` nadpisuje oba (`[]` wyłącza globalne fallbacki). Zadania cron, które nadpisują tylko `primary`, nadal dziedziczą domyślne fallbacki, chyba że ustawisz `fallbacks: []`.
- `params`: parametry strumienia per agent scalane ponad wybranym wpisem modelu w `agents.defaults.models`. Użyj tego do nadpisań specyficznych dla agenta, takich jak `cacheRetention`, `temperature` lub `maxTokens`, bez duplikowania całego katalogu modeli.
- `skills`: opcjonalna lista zezwoleń Skills per agent. Jeśli pominięta, agent dziedziczy `agents.defaults.skills`, gdy są ustawione; jawna lista zastępuje wartości domyślne zamiast się z nimi łączyć, a `[]` oznacza brak Skills.
- `thinkingDefault`: opcjonalny domyślny poziom thinking per agent (`off | minimal | low | medium | high | xhigh | adaptive`). Nadpisuje `agents.defaults.thinkingDefault` dla tego agenta, gdy nie ustawiono nadpisania per wiadomość ani per sesja.
- `reasoningDefault`: opcjonalna domyślna widoczność reasoning per agent (`on | off | stream`). Ma zastosowanie, gdy nie ustawiono nadpisania reasoning per wiadomość ani per sesja.
- `fastModeDefault`: opcjonalna domyślna wartość fast mode per agent (`true | false`). Ma zastosowanie, gdy nie ustawiono nadpisania fast mode per wiadomość ani per sesja.
- `runtime`: opcjonalny deskryptor środowiska uruchomieniowego per agent. Użyj `type: "acp"` z domyślnymi `runtime.acp` (`agent`, `backend`, `mode`, `cwd`), gdy agent ma domyślnie używać sesji harness ACP.
- `identity.avatar`: ścieżka względna do workspace, URL `http(s)` lub URI `data:`.
- `identity` wyprowadza wartości domyślne: `ackReaction` z `emoji`, `mentionPatterns` z `name`/`emoji`.
- `subagents.allowAgents`: lista zezwoleń identyfikatorów agentów dla `sessions_spawn` (`["*"]` = dowolny; domyślnie: tylko ten sam agent).
- Ochrona dziedziczenia sandbox: jeśli sesja żądająca jest w sandboxie, `sessions_spawn` odrzuca cele, które działałyby poza sandboxem.
- `subagents.requireAgentId`: gdy true, blokuje wywołania `sessions_spawn`, które pomijają `agentId` (wymusza jawny wybór profilu; domyślnie: false).

---

## Routing wielu agentów

Uruchamiaj wielu izolowanych agentów w jednym Gateway. Zobacz [Multi-Agent](/pl/concepts/multi-agent).

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

### Pola dopasowania powiązań

- `type` (opcjonalne): `route` dla normalnego routingu (brak typu domyślnie oznacza route), `acp` dla trwałych powiązań rozmów ACP.
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
5. `match.accountId: "*"` (w skali kanału)
6. Agent domyślny

W obrębie każdego poziomu wygrywa pierwszy pasujący wpis `bindings`.

Dla wpisów `type: "acp"` OpenClaw rozwiązuje po dokładnej tożsamości rozmowy (`match.channel` + konto + `match.peer.id`) i nie używa powyższej kolejności poziomów powiązań route.

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

<Accordion title="Narzędzia tylko do odczytu + workspace">

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

## Session

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
    parentForkMaxTokens: 100000, // pomiń fork wątku nadrzędnego powyżej tej liczby tokenów (0 wyłącza)
    maintenance: {
      mode: "warn", // warn | enforce
      pruneAfter: "30d",
      maxEntries: 500,
      rotateBytes: "10mb",
      resetArchiveRetention: "30d", // czas trwania lub false
      maxDiskBytes: "500mb", // opcjonalny twardy budżet
      highWaterBytes: "400mb", // opcjonalny cel po czyszczeniu
    },
    threadBindings: {
      enabled: true,
      idleHours: 24, // domyślne automatyczne odfokusowanie po bezczynności w godzinach (`0` wyłącza)
      maxAgeHours: 0, // domyślny twardy maksymalny wiek w godzinach (`0` wyłącza)
    },
    mainKey: "main", // starsze (środowisko uruchomieniowe zawsze używa "main")
    agentToAgent: { maxPingPongTurns: 5 },
    sendPolicy: {
      rules: [{ action: "deny", match: { channel: "discord", chatType: "group" } }],
      default: "allow",
    },
  },
}
```

<Accordion title="Szczegóły pól Session">

- **`scope`**: bazowa strategia grupowania sesji dla kontekstów czatów grupowych.
  - `per-sender` (domyślnie): każdy nadawca otrzymuje izolowaną sesję w kontekście kanału.
  - `global`: wszyscy uczestnicy w kontekście kanału współdzielą jedną sesję (używaj tylko wtedy, gdy zamierzony jest współdzielony kontekst).
- **`dmScope`**: sposób grupowania DM.
  - `main`: wszystkie DM współdzielą sesję główną.
  - `per-peer`: izolacja według identyfikatora nadawcy między kanałami.
  - `per-channel-peer`: izolacja per kanał + nadawca (zalecane dla skrzynek wielo-użytkownikowych).
  - `per-account-channel-peer`: izolacja per konto + kanał + nadawca (zalecane dla wielu kont).
- **`identityLinks`**: mapuje identyfikatory kanoniczne do peerów z prefiksem dostawcy dla współdzielenia sesji między kanałami.
- **`reset`**: podstawowa zasada resetu. `daily` resetuje o `atHour` czasu lokalnego; `idle` resetuje po `idleMinutes`. Gdy skonfigurowane są oba, wygrywa to, co wygaśnie wcześniej.
- **`resetByType`**: nadpisania per typ (`direct`, `group`, `thread`). Starsze `dm` jest akceptowane jako alias `direct`.
- **`parentForkMaxTokens`**: maksymalna wartość `totalTokens` sesji nadrzędnej dozwolona przy tworzeniu rozwidlonej sesji wątku (domyślnie `100000`).
  - Jeśli nadrzędne `totalTokens` jest powyżej tej wartości, OpenClaw rozpoczyna świeżą sesję wątku zamiast dziedziczyć historię transkryptu sesji nadrzędnej.
  - Ustaw `0`, aby wyłączyć tę ochronę i zawsze zezwalać na fork od rodzica.
- **`mainKey`**: starsze pole. Środowisko uruchomieniowe teraz zawsze używa `"main"` dla głównego zasobnika czatów bezpośrednich.
- **`agentToAgent.maxPingPongTurns`**: maksymalna liczba tur odpowiedzi zwrotnej między agentami podczas wymiany agent-do-agenta (liczba całkowita, zakres: `0`–`5`). `0` wyłącza łańcuch ping-pong.
- **`sendPolicy`**: dopasowanie po `channel`, `chatType` (`direct|group|channel`, ze starszym aliasem `dm`), `keyPrefix` lub `rawKeyPrefix`. Pierwsze deny wygrywa.
- **`maintenance`**: kontrola czyszczenia i retencji magazynu sesji.
  - `mode`: `warn` emituje tylko ostrzeżenia; `enforce` stosuje czyszczenie.
  - `pruneAfter`: granica wieku dla nieaktualnych wpisów (domyślnie `30d`).
  - `maxEntries`: maksymalna liczba wpisów w `sessions.json` (domyślnie `500`).
  - `rotateBytes`: obraca `sessions.json`, gdy przekroczy ten rozmiar (domyślnie `10mb`).
  - `resetArchiveRetention`: retencja dla archiwów transkryptów `*.reset.<timestamp>`. Domyślnie taka sama jak `pruneAfter`; ustaw `false`, aby wyłączyć.
  - `maxDiskBytes`: opcjonalny budżet miejsca na dysku dla katalogu sesji. W trybie `warn` zapisuje ostrzeżenia; w trybie `enforce` najpierw usuwa najstarsze artefakty/sesje.
  - `highWaterBytes`: opcjonalny cel po czyszczeniu budżetu. Domyślnie `80%` wartości `maxDiskBytes`.
- **`threadBindings`**: globalne wartości domyślne dla funkcji sesji związanych z wątkami.
  - `enabled`: główny domyślny przełącznik (dostawcy mogą nadpisywać; Discord używa `channels.discord.threadBindings.enabled`)
  - `idleHours`: domyślne automatyczne odfokusowanie po bezczynności w godzinach (`0` wyłącza; dostawcy mogą nadpisywać)
  - `maxAgeHours`: domyślny twardy maksymalny wiek w godzinach (`0` wyłącza; dostawcy mogą nadpisywać)

</Accordion>

---

## Wiadomości

```json5
{
  messages: {
    responsePrefix: "🦞", // lub "auto"
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
      debounceMs: 2000, // 0 wyłącza
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

Rozwiązywanie (najbardziej szczegółowe wygrywa): konto → kanał → globalne. `""` wyłącza i zatrzymuje kaskadę. `"auto"` wyprowadza `[{identity.name}]`.

**Zmienne szablonu:**

| Zmienna          | Opis                   | Przykład                    |
| ---------------- | ---------------------- | --------------------------- |
| `{model}`        | Krótka nazwa modelu    | `claude-opus-4-6`           |
| `{modelFull}`    | Pełny identyfikator modelu | `anthropic/claude-opus-4-6` |
| `{provider}`     | Nazwa dostawcy         | `anthropic`                 |
| `{thinkingLevel}` | Bieżący poziom thinking | `high`, `low`, `off`        |
| `{identity.name}` | Nazwa tożsamości agenta | (to samo co `"auto"`)       |

Zmienne są niewrażliwe na wielkość liter. `{think}` jest aliasem dla `{thinkingLevel}`.

### Reakcja ack

- Domyślnie przyjmuje `identity.emoji` aktywnego agenta, w przeciwnym razie `"👀"`. Ustaw `""`, aby wyłączyć.
- Nadpisania per kanał: `channels.<channel>.ackReaction`, `channels.<channel>.accounts.<id>.ackReaction`.
- Kolejność rozwiązywania: konto → kanał → `messages.ackReaction` → zapas z identity.
- Zakres: `group-mentions` (domyślnie), `group-all`, `direct`, `all`.
- `removeAckAfterReply`: usuwa ack po odpowiedzi w Slack, Discord i Telegram.
- `messages.statusReactions.enabled`: włącza reakcje statusu cyklu życia w Slack, Discord i Telegram.
  W Slack i Discord brak ustawienia utrzymuje reakcje statusu włączone, gdy aktywne są reakcje ack.
  W Telegram ustaw jawnie `true`, aby włączyć reakcje statusu cyklu życia.

### Debounce przychodzących wiadomości

Łączy szybkie wiadomości tekstowe od tego samego nadawcy w jedną turę agenta. Media/załączniki są opróżniane natychmiast. Polecenia sterujące omijają debounce.

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

- `auto` kontroluje automatyczny TTS. `/tts off|always|inbound|tagged` nadpisuje ustawienie per sesja.
- `summaryModel` nadpisuje `agents.defaults.model.primary` dla auto-podsumowania.
- `modelOverrides` jest domyślnie włączone; `modelOverrides.allowProvider` domyślnie ma wartość `false` (opt-in).
- Klucze API mają zapas w `ELEVENLABS_API_KEY`/`XI_API_KEY` oraz `OPENAI_API_KEY`.
- `openai.baseUrl` nadpisuje endpoint OpenAI TTS. Kolejność rozwiązywania to konfiguracja, potem `OPENAI_TTS_BASE_URL`, a następnie `https://api.openai.com/v1`.
- Gdy `openai.baseUrl` wskazuje endpoint inny niż OpenAI, OpenClaw traktuje go jako serwer TTS zgodny z OpenAI i łagodzi walidację modelu/głosu.

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
- Starsze płaskie klucze Talk (`talk.voiceId`, `talk.voiceAliases`, `talk.modelId`, `talk.outputFormat`, `talk.apiKey`) są przeznaczone wyłącznie do kompatybilności i są automatycznie migrowane do `talk.providers.<provider>`.
- Voice ID mają zapas w `ELEVENLABS_VOICE_ID` lub `SAG_VOICE_ID`.
- `providers.*.apiKey` akceptuje zwykłe ciągi tekstowe lub obiekty SecretRef.
- Zapas `ELEVENLABS_API_KEY` ma zastosowanie tylko wtedy, gdy nie skonfigurowano klucza API dla Talk.
- `providers.*.voiceAliases` pozwala dyrektywom Talk używać przyjaznych nazw.
- `silenceTimeoutMs` kontroluje, jak długo tryb Talk czeka po ciszy użytkownika, zanim wyśle transkrypt. Brak ustawienia zachowuje domyślne okno pauzy platformy (`700 ms na macOS i Androidzie, 900 ms na iOS`).

---

## Narzędzia

### Profile narzędzi

`tools.profile` ustawia bazową listę zezwoleń przed `tools.allow`/`tools.deny`:

Lokalny onboarding domyślnie ustawia nowe lokalne konfiguracje na `tools.profile: "coding"`, gdy pole nie jest ustawione (istniejące jawne profile są zachowywane).

| Profil      | Obejmuje                                                                                                                         |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `minimal`   | tylko `session_status`                                                                                                           |
| `coding`    | `group:fs`, `group:runtime`, `group:web`, `group:sessions`, `group:memory`, `cron`, `image`, `image_generate`, `video_generate` |
| `messaging` | `group:messaging`, `sessions_list`, `sessions_history`, `sessions_send`, `session_status`                                       |
| `full`      | Brak ograniczeń (to samo co brak ustawienia)                                                                                     |

### Grupy narzędzi

| Grupa             | Narzędzia                                                                                                                |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `group:runtime`   | `exec`, `process`, `code_execution` (`bash` jest akceptowany jako alias `exec`)                                         |
| `group:fs`        | `read`, `write`, `edit`, `apply_patch`                                                                                   |
| `group:sessions`  | `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`, `sessions_yield`, `subagents`, `session_status` |
| `group:memory`    | `memory_search`, `memory_get`                                                                                            |
| `group:web`       | `web_search`, `x_search`, `web_fetch`                                                                                    |
| `group:ui`        | `browser`, `canvas`                                                                                                      |
| `group:automation` | `cron`, `gateway`                                                                                                       |
| `group:messaging` | `message`                                                                                                                |
| `group:nodes`     | `nodes`                                                                                                                  |
| `group:agents`    | `agents_list`                                                                                                            |
| `group:media`     | `image`, `image_generate`, `video_generate`, `tts`                                                                       |
| `group:openclaw`  | Wszystkie wbudowane narzędzia (bez pluginów dostawców)                                                                   |

### `tools.allow` / `tools.deny`

Globalne zasady allow/deny dla narzędzi (deny wygrywa). Niewrażliwe na wielkość liter, obsługują wildcardy `*`. Stosowane nawet wtedy, gdy sandbox Docker jest wyłączony.

```json5
{
  tools: { deny: ["browser", "canvas"] },
}
```

### `tools.byProvider`

Dalsze ograniczenia narzędzi dla określonych dostawców lub modeli. Kolejność: profil bazowy → profil dostawcy → allow/deny.

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

Kontroluje podniesiony dostęp exec poza sandboxem:

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

- Nadpisanie per agent (`agents.list[].tools.elevated`) może tylko dodatkowo ograniczać.
- `/elevated on|off|ask|full` zapisuje stan per sesja; dyrektywy inline mają zastosowanie do pojedynczej wiadomości.
- Podniesione `exec` omija sandboxing i używa skonfigurowanej ścieżki ucieczki (`gateway` domyślnie lub `node`, gdy cel exec to `node`).

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

Kontrole bezpieczeństwa pętli narzędzi są **domyślnie wyłączone**. Ustaw `enabled: true`, aby aktywować wykrywanie.
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

- `historySize`: maksymalna historia wywołań narzędzi przechowywana do analizy pętli.
- `warningThreshold`: próg ostrzeżeń dla powtarzających się wzorców bez postępu.
- `criticalThreshold`: wyższy próg dla blokowania krytycznych pętli.
- `globalCircuitBreakerThreshold`: próg twardego zatrzymania dla dowolnego uruchomienia bez postępu.
- `detectors.genericRepeat`: ostrzega o powtarzanych wywołaniach tego samego narzędzia z tymi samymi argumentami.
- `detectors.knownPollNoProgress`: ostrzega/blokuje znane narzędzia pollingowe (`process.poll`, `command_status` itp.).
- `detectors.pingPong`: ostrzega/blokuje naprzemienne wzorce par bez postępu.
- Jeśli `warningThreshold >= criticalThreshold` lub `criticalThreshold >= globalCircuitBreakerThreshold`, walidacja kończy się niepowodzeniem.

### `tools.web`

```json5
{
  tools: {
    web: {
      search: {
        enabled: true,
        apiKey: "brave_api_key", // lub BRAVE_API_KEY env
        maxResults: 5,
        timeoutSeconds: 30,
        cacheTtlMinutes: 15,
      },
      fetch: {
        enabled: true,
        provider: "firecrawl", // opcjonalne; pomiń dla automatycznego wykrywania
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
        directSend: false, // opt-in: wyślij gotowe async music/video bezpośrednio do kanału
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

<Accordion title="Pola wpisu modelu mediów">

**Wpis dostawcy** (`type: "provider"` lub pominięte):

- `provider`: identyfikator dostawcy API (`openai`, `anthropic`, `google`/`gemini`, `groq` itp.)
- `model`: nadpisanie identyfikatora modelu
- `profile` / `preferredProfile`: wybór profilu `auth-profiles.json`

**Wpis CLI** (`type: "cli"`):

- `command`: wykonywalne polecenie do uruchomienia
- `args`: argumenty szablonowane (obsługuje `{{MediaPath}}`, `{{Prompt}}`, `{{MaxChars}}` itp.)

**Pola wspólne:**

- `capabilities`: opcjonalna lista (`image`, `audio`, `video`). Domyślnie: `openai`/`anthropic`/`minimax` → image, `google` → image+audio+video, `groq` → audio.
- `prompt`, `maxChars`, `maxBytes`, `timeoutSeconds`, `language`: nadpisania per wpis.
- Po błędach następuje przejście do następnego wpisu.

Uwierzytelnianie dostawcy korzysta ze standardowej kolejności: `auth-profiles.json` → zmienne środowiskowe → `models.providers.*.apiKey`.

**Pola async completion:**

- `asyncCompletion.directSend`: gdy `true`, ukończone zadania async `music_generate`
  i `video_generate` najpierw próbują bezpośredniego dostarczenia do kanału. Domyślnie: `false`
  (starsza ścieżka wybudzenia sesji żądającej/dostarczania przez model).

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

Kontroluje, które sesje mogą być targetowane przez narzędzia sesji (`sessions_list`, `sessions_history`, `sessions_send`).

Domyślnie: `tree` (bieżąca sesja + sesje uruchomione przez nią, takie jak subagenty).

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
- `tree`: bieżąca sesja + sesje uruchomione przez bieżącą sesję (subagenty).
- `agent`: dowolna sesja należąca do bieżącego identyfikatora agenta (może obejmować innych użytkowników, jeśli uruchamiasz sesje per nadawca pod tym samym identyfikatorem agenta).
- `all`: dowolna sesja. Targetowanie między agentami nadal wymaga `tools.agentToAgent`.
- Ograniczenie sandbox: gdy bieżąca sesja jest w sandboxie, a `agents.defaults.sandbox.sessionToolsVisibility="spawned"`, widoczność jest wymuszana na `tree`, nawet jeśli `tools.sessions.visibility="all"`.

### `tools.sessions_spawn`

Kontroluje obsługę załączników inline dla `sessions_spawn`.

```json5
{
  tools: {
    sessions_spawn: {
      attachments: {
        enabled: false, // opt-in: ustaw true, aby zezwolić na załączniki plikowe inline
        maxTotalBytes: 5242880, // 5 MB łącznie dla wszystkich plików
        maxFiles: 50,
        maxFileBytes: 1048576, // 1 MB na plik
        retainOnSessionKeep: false, // zachowaj załączniki, gdy cleanup="keep"
      },
    },
  },
}
```

Uwagi:

- Załączniki są obsługiwane tylko dla `runtime: "subagent"`. Środowisko uruchomieniowe ACP je odrzuca.
- Pliki są materializowane w podrzędnym workspace w `.openclaw/attachments/<uuid>/` wraz z `.manifest.json`.
- Zawartość załączników jest automatycznie redagowana przy utrwalaniu transkryptu.
- Wejścia base64 są walidowane z rygorystycznym sprawdzaniem alfabetu/dopełnienia i ochroną rozmiaru przed dekodowaniem.
- Uprawnienia plików to `0700` dla katalogów i `0600` dla plików.
- Czyszczenie jest zgodne z polityką `cleanup`: `delete` zawsze usuwa załączniki; `keep` zachowuje je tylko wtedy, gdy `retainOnSessionKeep: true`.

### `tools.experimental`

Eksperymentalne flagi wbudowanych narzędzi. Domyślnie wyłączone, chyba że obowiązuje reguła automatycznego włączenia specyficzna dla środowiska uruchomieniowego.

```json5
{
  tools: {
    experimental: {
      planTool: true, // włącza eksperymentalne update_plan
    },
  },
}
```

Uwagi:

- `planTool`: włącza strukturalne narzędzie `update_plan` do śledzenia nietrywialnej pracy wieloetapowej.
- Domyślnie: `false` dla dostawców innych niż OpenAI. Uruchomienia OpenAI i OpenAI Codex włączają je automatycznie.
- Gdy jest włączone, system prompt dodaje również wskazówki użycia, tak aby model korzystał z niego tylko przy większej pracy i utrzymywał co najwyżej jeden krok `in_progress`.

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

- `model`: domyślny model dla uruchamianych subagentów. Jeśli pole zostanie pominięte, subagenty dziedziczą model wywołującego.
- `allowAgents`: domyślna lista zezwoleń docelowych identyfikatorów agentów dla `sessions_spawn`, gdy agent żądający nie ustawia własnego `subagents.allowAgents` (`["*"]` = dowolny; domyślnie: tylko ten sam agent).
- `runTimeoutSeconds`: domyślny timeout (sekundy) dla `sessions_spawn`, gdy wywołanie narzędzia pomija `runTimeoutSeconds`. `0` oznacza brak timeoutu.
- Zasady narzędzi per subagent: `tools.subagents.tools.allow` / `tools.subagents.tools.deny`.

---

## Niestandardowi dostawcy i base URL

OpenClaw używa wbudowanego katalogu modeli. Dodaj niestandardowych dostawców przez `models.providers` w konfiguracji lub `~/.openclaw/agents/<agentId>/agent/models.json`.

```json5
{
  models: {
    mode: "merge", // merge (domyślnie) | replace
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
  - Niepuste wartości `baseUrl` z `models.json` agenta mają pierwszeństwo.
  - Niepuste wartości `apiKey` agenta mają pierwszeństwo tylko wtedy, gdy ten dostawca nie jest zarządzany przez SecretRef w bieżącym kontekście konfiguracji/profilu auth.
  - Wartości `apiKey` dostawcy zarządzane przez SecretRef są odświeżane na podstawie znaczników źródła (`ENV_VAR_NAME` dla odwołań env, `secretref-managed` dla odwołań file/exec) zamiast utrwalać rozwiązane sekrety.
  - Wartości nagłówków dostawcy zarządzane przez SecretRef są odświeżane na podstawie znaczników źródła (`secretref-env:ENV_VAR_NAME` dla odwołań env, `secretref-managed` dla odwołań file/exec).
  - Puste lub brakujące `apiKey`/`baseUrl` agenta wracają do `models.providers` w konfiguracji.
  - Pasujące wartości `contextWindow`/`maxTokens` modelu używają wyższej wartości pomiędzy jawną konfiguracją a niejawnymi wartościami katalogu.
  - Pasujące `contextTokens` modelu zachowuje jawny runtime cap, gdy jest obecny; użyj go, aby ograniczyć efektywny kontekst bez zmieniania natywnych metadanych modelu.
  - Użyj `models.mode: "replace"`, gdy chcesz, aby konfiguracja całkowicie przepisała `models.json`.
  - Utrwalanie znaczników jest autorytatywne względem źródła: znaczniki są zapisywane z aktywnej migawki źródłowej konfiguracji (przed rozwiązywaniem), a nie z rozwiązanych wartości sekretów środowiska uruchomieniowego.

### Szczegóły pól dostawcy

- `models.mode`: zachowanie katalogu dostawców (`merge` lub `replace`).
- `models.providers`: mapa niestandardowych dostawców kluczowana identyfikatorem dostawcy.
- `models.providers.*.api`: adapter żądań (`openai-completions`, `openai-responses`, `anthropic-messages`, `google-generative-ai` itp.).
- `models.providers.*.apiKey`: poświadczenie dostawcy (preferuj SecretRef/podstawienie z env).
- `models.providers.*.auth`: strategia uwierzytelniania (`api-key`, `token`, `oauth`, `aws-sdk`).
- `models.providers.*.injectNumCtxForOpenAICompat`: dla Ollama + `openai-completions` wstrzykuje `options.num_ctx` do żądań (domyślnie: `true`).
- `models.providers.*.authHeader`: wymusza transport poświadczenia w nagłówku `Authorization`, gdy jest wymagany.
- `models.providers.*.baseUrl`: bazowy URL nadrzędnego API.
- `models.providers.*.headers`: dodatkowe statyczne nagłówki dla routingu proxy/dzierżawy.
- `models.providers.*.request`: nadpisania transportu dla żądań HTTP dostawcy modelu.
  - `request.headers`: dodatkowe nagłówki (scalane z domyślnymi dostawcy). Wartości akceptują SecretRef.
  - `request.auth`: nadpisanie strategii uwierzytelniania. Tryby: `"provider-default"` (użyj wbudowanego uwierzytelniania dostawcy), `"authorization-bearer"` (z `token`), `"header"` (z `headerName`, `value`, opcjonalnym `prefix`).
  - `request.proxy`: nadpisanie proxy HTTP. Tryby: `"env-proxy"` (użyj zmiennych środowiskowych `HTTP_PROXY`/`HTTPS_PROXY`), `"explicit-proxy"` (z `url`). Oba tryby akceptują opcjonalny pod-obiekt `tls`.
  - `request.tls`: nadpisanie TLS dla połączeń bezpośrednich. Pola: `ca`, `cert`, `key`, `passphrase` (wszystkie akceptują SecretRef), `serverName`, `insecureSkipVerify`.
- `models.providers.*.models`: jawne wpisy katalogu modeli dostawcy.
- `models.providers.*.models.*.contextWindow`: natywne metadane okna kontekstu modelu.
- `models.providers.*.models.*.contextTokens`: opcjonalny runtime cap kontekstu. Użyj tego, gdy chcesz mniejszego efektywnego budżetu kontekstu niż natywne `contextWindow` modelu.
- `models.providers.*.models.*.compat.supportsDeveloperRole`: opcjonalna wskazówka kompatybilności. Dla `api: "openai-completions"` z niepustym nienatywnym `baseUrl` (host inny niż `api.openai.com`) OpenClaw wymusza to na `false` w czasie wykonywania. Puste/pominięte `baseUrl` zachowuje domyślne zachowanie OpenAI.
- `plugins.entries.amazon-bedrock.config.discovery`: katalog główny ustawień auto-discovery Bedrock.
- `plugins.entries.amazon-bedrock.config.discovery.enabled`: włącza/wyłącza niejawne discovery.
- `plugins.entries.amazon-bedrock.config.discovery.region`: region AWS dla discovery.
- `plugins.entries.amazon-bedrock.config.discovery.providerFilter`: opcjonalny filtr identyfikatora dostawcy dla ukierunkowanego discovery.
- `plugins.entries.amazon-bedrock.config.discovery.refreshInterval`: interwał odpytywania dla odświeżania discovery.
- `plugins.entries.amazon-bedrock.config.discovery.defaultContextWindow`: zapasowe okno kontekstu dla odkrytych modeli.
- `plugins.entries.amazon-bedrock.config.discovery.defaultMaxTokens`: zapasowe maksymalne tokeny wyjściowe dla odkrytych modeli.

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

Ustaw `OPENCODE_API_KEY` (lub `OPENCODE_ZEN_API_KEY`). Używaj odwołań `opencode/...` dla katalogu Zen lub `opencode-go/...` dla katalogu Go. Skrót: `openclaw onboard --auth-choice opencode-zen` lub `openclaw onboard --auth-choice opencode-go`.

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

- Ogólny endpoint: `https://api.z.ai/api/paas/v4`
- Endpoint do kodowania (domyślny): `https://api.z.ai/api/coding/paas/v4`
- Dla ogólnego endpointu zdefiniuj niestandardowego dostawcę z nadpisaniem base URL.

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

Dla endpointu Chiny: `baseUrl: "https://api.moonshot.cn/v1"` lub `openclaw onboard --auth-choice moonshot-api-key-cn`.

Natywne endpointy Moonshot reklamują kompatybilność użycia strumieniowania na współdzielonym
transporcie `openai-completions`, a OpenClaw teraz opiera to na możliwościach endpointu,
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

Base URL powinien pomijać `/v1` (klient Anthropic sam go dopisuje). Skrót: `openclaw onboard --auth-choice synthetic-api-key`.

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
`openclaw onboard --auth-choice minimax-global-api` lub
`openclaw onboard --auth-choice minimax-cn-api`.
Katalog modeli domyślnie zawiera teraz tylko M2.7.
Na ścieżce strumieniowania zgodnej z Anthropic OpenClaw domyślnie wyłącza thinking MiniMax,
chyba że jawnie ustawisz `thinking`. `/fast on` lub
`params.fastMode: true` przepisuje `MiniMax-M2.7` na
`MiniMax-M2.7-highspeed`.

</Accordion>

<Accordion title="Modele lokalne (LM Studio)">

Zobacz [Local Models](/pl/gateway/local-models). TL;DR: uruchom duży model lokalny przez LM Studio Responses API na wydajnym sprzęcie; zachowaj modele hostowane scalone jako fallback.

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
        apiKey: { source: "env", provider: "default", id: "GEMINI_API_KEY" }, // lub zwykły ciąg tekstowy
        env: { GEMINI_API_KEY: "GEMINI_KEY_HERE" },
      },
      peekaboo: { enabled: true },
      sag: { enabled: false },
    },
  },
}
```

- `allowBundled`: opcjonalna lista zezwoleń tylko dla bundled Skills (managed/workspace Skills pozostają bez zmian).
- `load.extraDirs`: dodatkowe współdzielone katalogi główne Skills (najniższy priorytet).
- `install.preferBrew`: gdy true, preferuje instalatory Homebrew, gdy `brew` jest
  dostępne, zanim przejdzie do innych rodzajów instalatorów.
- `install.nodeManager`: preferencja instalatora node dla specyfikacji `metadata.openclaw.install`
  (`npm` | `pnpm` | `yarn` | `bun`).
- `entries.<skillKey>.enabled: false` wyłącza Skill nawet jeśli jest bundled/zainstalowany.
- `entries.<skillKey>.apiKey`: wygodne pole klucza API dla Skills deklarujących podstawową zmienną env (zwykły ciąg tekstowy lub obiekt SecretRef).

---

## Plugins

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
- Discovery akceptuje natywne pluginy OpenClaw oraz kompatybilne bundle Codex i Claude, w tym bundle Claude o domyślnym układzie bez manifestu.
- **Zmiany konfiguracji wymagają restartu gateway.**
- `allow`: opcjonalna lista zezwoleń (ładują się tylko wymienione pluginy). `deny` ma pierwszeństwo.
- `plugins.entries.<id>.apiKey`: wygodne pole klucza API na poziomie plugin (gdy plugin to obsługuje).
- `plugins.entries.<id>.env`: mapa zmiennych środowiskowych ograniczona do plugin.
- `plugins.entries.<id>.hooks.allowPromptInjection`: gdy `false`, rdzeń blokuje `before_prompt_build` i ignoruje pola mutujące prompt ze starszego `before_agent_start`, zachowując starsze `modelOverride` i `providerOverride`. Dotyczy natywnych hooków plugin i obsługiwanych katalogów hooków dostarczanych przez bundle.
- `plugins.entries.<id>.subagent.allowModelOverride`: jawnie ufa temu pluginowi w żądaniu nadpisań `provider` i `model` per uruchomienie dla uruchomień subagentów w tle.
- `plugins.entries.<id>.subagent.allowedModels`: opcjonalna lista zezwoleń kanonicznych celów `provider/model` dla zaufanych nadpisań subagentów. Użyj `"*"` tylko wtedy, gdy świadomie chcesz zezwolić na dowolny model.
- `plugins.entries.<id>.config`: obiekt konfiguracji zdefiniowany przez plugin (walidowany przez schemat natywnego pluginu OpenClaw, jeśli jest dostępny).
- `plugins.entries.firecrawl.config.webFetch`: ustawienia dostawcy web-fetch Firecrawl.
  - `apiKey`: klucz API Firecrawl (akceptuje SecretRef). Zapasowo używa `plugins.entries.firecrawl.config.webSearch.apiKey`, starszego `tools.web.fetch.firecrawl.apiKey` lub zmiennej środowiskowej `FIRECRAWL_API_KEY`.
  - `baseUrl`: bazowy URL API Firecrawl (domyślnie: `https://api.firecrawl.dev`).
  - `onlyMainContent`: wyodrębnia tylko główną treść ze stron (domyślnie: `true`).
  - `