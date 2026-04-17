---
read_when:
    - Konfigurowanie Matrix w OpenClaw
    - Konfigurowanie Matrix E2EE i weryfikacji
summary: Status obsługi Matrix, konfiguracja i przykłady konfiguracji
title: Matrix
x-i18n:
    generated_at: "2026-04-15T19:41:38Z"
    model: gpt-5.4
    provider: openai
    source_hash: bd730bb9d0c8a548ee48b20931b3222e9aa1e6e95f1390b0c236645e03f3576d
    source_path: channels/matrix.md
    workflow: 15
---

# Matrix

Matrix to dołączony Plugin kanału dla OpenClaw.
Używa oficjalnego `matrix-js-sdk` i obsługuje wiadomości prywatne, pokoje, wątki, multimedia, reakcje, ankiety, lokalizację oraz E2EE.

## Dołączony Plugin

Matrix jest dostarczany jako dołączony Plugin w obecnych wydaniach OpenClaw, więc zwykłe
spakowane kompilacje nie wymagają osobnej instalacji.

Jeśli używasz starszej kompilacji lub niestandardowej instalacji, która nie zawiera Matrix, zainstaluj
go ręcznie:

Zainstaluj z npm:

```bash
openclaw plugins install @openclaw/matrix
```

Zainstaluj z lokalnego checkoutu:

```bash
openclaw plugins install ./path/to/local/matrix-plugin
```

Zobacz [Plugins](/pl/tools/plugin), aby poznać zachowanie Pluginów i zasady instalacji.

## Konfiguracja

1. Upewnij się, że Plugin Matrix jest dostępny.
   - Obecne spakowane wydania OpenClaw już go zawierają.
   - Starsze/niestandardowe instalacje mogą dodać go ręcznie za pomocą powyższych poleceń.
2. Utwórz konto Matrix na swoim homeserverze.
3. Skonfiguruj `channels.matrix`, używając jednego z wariantów:
   - `homeserver` + `accessToken`, albo
   - `homeserver` + `userId` + `password`.
4. Uruchom ponownie Gateway.
5. Rozpocznij wiadomość prywatną z botem albo zaproś go do pokoju.
   - Nowe zaproszenia Matrix działają tylko wtedy, gdy `channels.matrix.autoJoin` na to pozwala.

Interaktywne ścieżki konfiguracji:

```bash
openclaw channels add
openclaw configure --section channels
```

Kreator Matrix pyta o:

- URL homeservera
- metodę uwierzytelniania: token dostępu lub hasło
- identyfikator użytkownika (tylko przy uwierzytelnianiu hasłem)
- opcjonalną nazwę urządzenia
- czy włączyć E2EE
- czy skonfigurować dostęp do pokoi i automatyczne dołączanie do zaproszeń

Najważniejsze zachowania kreatora:

- Jeśli zmienne środowiskowe uwierzytelniania Matrix już istnieją, a to konto nie ma jeszcze zapisanego uwierzytelniania w konfiguracji, kreator oferuje skrót do użycia zmiennych środowiskowych, aby zachować uwierzytelnianie w zmiennych środowiskowych.
- Nazwy kont są normalizowane do identyfikatora konta. Na przykład `Ops Bot` staje się `ops-bot`.
- Wpisy listy dozwolonych dla wiadomości prywatnych akceptują bezpośrednio `@user:server`; nazwy wyświetlane działają tylko wtedy, gdy wyszukiwanie w katalogu na żywo znajdzie dokładnie jedno dopasowanie.
- Wpisy listy dozwolonych dla pokoi akceptują bezpośrednio identyfikatory pokoi i aliasy. Preferuj `!room:server` albo `#alias:server`; nierozwiązane nazwy są ignorowane w czasie działania podczas rozwiązywania listy dozwolonych.
- W trybie listy dozwolonych dla automatycznego dołączania do zaproszeń używaj tylko stabilnych celów zaproszeń: `!roomId:server`, `#alias:server` albo `*`. Zwykłe nazwy pokoi są odrzucane.
- Aby rozwiązać nazwy pokoi przed zapisaniem, użyj `openclaw channels resolve --channel matrix "Project Room"`.

<Warning>
`channels.matrix.autoJoin` domyślnie ma wartość `off`.

Jeśli pozostawisz ją nieustawioną, bot nie dołączy do zaproszonych pokoi ani nowych zaproszeń w stylu wiadomości prywatnych, więc nie pojawi się w nowych grupach ani zaproszonych wiadomościach prywatnych, chyba że najpierw dołączysz ręcznie.

Ustaw `autoJoin: "allowlist"` razem z `autoJoinAllowlist`, aby ograniczyć, które zaproszenia będą akceptowane, albo ustaw `autoJoin: "always"`, jeśli chcesz, aby dołączał do każdego zaproszenia.

W trybie `allowlist` `autoJoinAllowlist` akceptuje tylko `!roomId:server`, `#alias:server` albo `*`.
</Warning>

Przykład listy dozwolonych:

```json5
{
  channels: {
    matrix: {
      autoJoin: "allowlist",
      autoJoinAllowlist: ["!ops:example.org", "#support:example.org"],
      groups: {
        "!ops:example.org": {
          requireMention: true,
        },
      },
    },
  },
}
```

Dołączaj do każdego zaproszenia:

```json5
{
  channels: {
    matrix: {
      autoJoin: "always",
    },
  },
}
```

Minimalna konfiguracja oparta na tokenie:

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_xxx",
      dm: { policy: "pairing" },
    },
  },
}
```

Konfiguracja oparta na haśle (token jest buforowany po zalogowaniu):

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      userId: "@bot:example.org",
      password: "replace-me", // pragma: allowlist secret
      deviceName: "OpenClaw Gateway",
    },
  },
}
```

Matrix przechowuje zapisane w pamięci podręcznej poświadczenia w `~/.openclaw/credentials/matrix/`.
Domyślne konto używa `credentials.json`; nazwane konta używają `credentials-<account>.json`.
Gdy istnieją tam zapisane w pamięci podręcznej poświadczenia, OpenClaw traktuje Matrix jako skonfigurowany na potrzeby konfiguracji, doctor i wykrywania statusu kanału, nawet jeśli bieżące uwierzytelnianie nie jest ustawione bezpośrednio w konfiguracji.

Odpowiedniki zmiennych środowiskowych (używane, gdy klucz konfiguracyjny nie jest ustawiony):

- `MATRIX_HOMESERVER`
- `MATRIX_ACCESS_TOKEN`
- `MATRIX_USER_ID`
- `MATRIX_PASSWORD`
- `MATRIX_DEVICE_ID`
- `MATRIX_DEVICE_NAME`

Dla kont innych niż domyślne użyj zmiennych środowiskowych z zakresem konta:

- `MATRIX_<ACCOUNT_ID>_HOMESERVER`
- `MATRIX_<ACCOUNT_ID>_ACCESS_TOKEN`
- `MATRIX_<ACCOUNT_ID>_USER_ID`
- `MATRIX_<ACCOUNT_ID>_PASSWORD`
- `MATRIX_<ACCOUNT_ID>_DEVICE_ID`
- `MATRIX_<ACCOUNT_ID>_DEVICE_NAME`

Przykład dla konta `ops`:

- `MATRIX_OPS_HOMESERVER`
- `MATRIX_OPS_ACCESS_TOKEN`

Dla znormalizowanego identyfikatora konta `ops-bot` użyj:

- `MATRIX_OPS_X2D_BOT_HOMESERVER`
- `MATRIX_OPS_X2D_BOT_ACCESS_TOKEN`

Matrix zmienia interpunkcję w identyfikatorach kont, aby zmienne środowiskowe z zakresem konta nie kolidowały ze sobą.
Na przykład `-` staje się `_X2D_`, więc `ops-prod` mapuje się na `MATRIX_OPS_X2D_PROD_*`.

Interaktywny kreator oferuje skrót do zmiennych środowiskowych tylko wtedy, gdy te zmienne środowiskowe uwierzytelniania już istnieją, a wybrane konto nie ma jeszcze zapisanego uwierzytelniania Matrix w konfiguracji.

## Przykład konfiguracji

To praktyczna bazowa konfiguracja z parowaniem wiadomości prywatnych, listą dozwolonych pokoi i włączonym E2EE:

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_xxx",
      encryption: true,

      dm: {
        policy: "pairing",
        sessionScope: "per-room",
        threadReplies: "off",
      },

      groupPolicy: "allowlist",
      groupAllowFrom: ["@admin:example.org"],
      groups: {
        "!roomid:example.org": {
          requireMention: true,
        },
      },

      autoJoin: "allowlist",
      autoJoinAllowlist: ["!roomid:example.org"],
      threadReplies: "inbound",
      replyToMode: "off",
      streaming: "partial",
    },
  },
}
```

`autoJoin` dotyczy wszystkich zaproszeń Matrix, w tym zaproszeń w stylu wiadomości prywatnych. OpenClaw nie może wiarygodnie
sklasyfikować zaproszonego pokoju jako wiadomości prywatnej lub grupy w momencie zaproszenia, dlatego wszystkie zaproszenia najpierw przechodzą przez `autoJoin`.
`dm.policy` ma zastosowanie po dołączeniu bota i sklasyfikowaniu pokoju jako wiadomości prywatnej.

## Podglądy strumieniowania

Strumieniowanie odpowiedzi Matrix jest opcjonalne.

Ustaw `channels.matrix.streaming` na `"partial"`, jeśli chcesz, aby OpenClaw wysyłał pojedynczą odpowiedź podglądu na żywo,
edytował ten podgląd na miejscu, gdy model generuje tekst, a następnie finalizował go, gdy
odpowiedź będzie gotowa:

```json5
{
  channels: {
    matrix: {
      streaming: "partial",
    },
  },
}
```

- `streaming: "off"` jest ustawieniem domyślnym. OpenClaw czeka na końcową odpowiedź i wysyła ją tylko raz.
- `streaming: "partial"` tworzy jedną edytowalną wiadomość podglądu dla bieżącego bloku asystenta przy użyciu zwykłych wiadomości tekstowych Matrix. Zachowuje to starsze zachowanie Matrix polegające na najpierw wysyłanym podglądzie w powiadomieniach, więc standardowe klienty mogą powiadamiać o pierwszym strumieniowanym tekście podglądu zamiast o ukończonym bloku.
- `streaming: "quiet"` tworzy jedną edytowalną cichą notatkę podglądu dla bieżącego bloku asystenta. Używaj tego tylko wtedy, gdy skonfigurujesz również reguły push odbiorcy dla sfinalizowanych edycji podglądu.
- `blockStreaming: true` włącza osobne wiadomości postępu Matrix. Gdy podgląd strumieniowania jest włączony, Matrix zachowuje szkic na żywo dla bieżącego bloku i pozostawia ukończone bloki jako oddzielne wiadomości.
- Gdy podgląd strumieniowania jest włączony i `blockStreaming` jest wyłączone, Matrix edytuje szkic na żywo na miejscu i finalizuje to samo zdarzenie po zakończeniu bloku lub całej tury.
- Jeśli podgląd przestanie mieścić się w jednym zdarzeniu Matrix, OpenClaw zatrzyma strumieniowanie podglądu i wróci do normalnego końcowego dostarczania.
- Odpowiedzi multimedialne nadal wysyłają załączniki normalnie. Jeśli nieaktualnego podglądu nie da się już bezpiecznie ponownie użyć, OpenClaw zredaguje go przed wysłaniem końcowej odpowiedzi multimedialnej.
- Edycje podglądu powodują dodatkowe wywołania API Matrix. Pozostaw strumieniowanie wyłączone, jeśli chcesz zachować najbardziej zachowawcze zachowanie względem limitów szybkości.

`blockStreaming` samo w sobie nie włącza roboczych podglądów.
Użyj `streaming: "partial"` albo `streaming: "quiet"` do edycji podglądu; następnie dodaj `blockStreaming: true` tylko wtedy, gdy chcesz również, aby ukończone bloki asystenta pozostały widoczne jako oddzielne wiadomości postępu.

Jeśli potrzebujesz standardowych powiadomień Matrix bez niestandardowych reguł push, użyj `streaming: "partial"` dla zachowania z podglądem najpierw albo pozostaw `streaming` wyłączone dla dostarczania tylko końcowej odpowiedzi. Przy `streaming: "off"`:

- `blockStreaming: true` wysyła każdy ukończony blok jako zwykłą powiadamiającą wiadomość Matrix.
- `blockStreaming: false` wysyła tylko końcową ukończoną odpowiedź jako zwykłą powiadamiającą wiadomość Matrix.

### Samodzielnie hostowane reguły push dla cichych sfinalizowanych podglądów

Jeśli utrzymujesz własną infrastrukturę Matrix i chcesz, aby ciche podglądy powiadamiały dopiero po ukończeniu bloku lub
końcowej odpowiedzi, ustaw `streaming: "quiet"` i dodaj regułę push per użytkownik dla sfinalizowanych edycji podglądu.

Zwykle jest to konfiguracja użytkownika-odbiorcy, a nie globalna zmiana konfiguracji homeservera:

Szybka mapa przed rozpoczęciem:

- użytkownik-odbiorca = osoba, która powinna otrzymać powiadomienie
- użytkownik-bot = konto Matrix OpenClaw, które wysyła odpowiedź
- użyj tokenu dostępu użytkownika-odbiorcy do poniższych wywołań API
- dopasuj `sender` w regule push do pełnego MXID użytkownika-bota

1. Skonfiguruj OpenClaw do używania cichych podglądów:

```json5
{
  channels: {
    matrix: {
      streaming: "quiet",
    },
  },
}
```

2. Upewnij się, że konto odbiorcy już otrzymuje normalne powiadomienia push Matrix. Reguły
   cichych podglądów działają tylko wtedy, gdy ten użytkownik ma już działające pushery/urządzenia.

3. Pobierz token dostępu użytkownika-odbiorcy.
   - Użyj tokenu użytkownika odbierającego, a nie tokenu bota.
   - Najłatwiej jest zwykle ponownie użyć tokenu istniejącej sesji klienta.
   - Jeśli musisz wygenerować nowy token, możesz zalogować się przez standardowe API klient-serwer Matrix:

```bash
curl -sS -X POST \
  "https://matrix.example.org/_matrix/client/v3/login" \
  -H "Content-Type: application/json" \
  --data '{
    "type": "m.login.password",
    "identifier": {
      "type": "m.id.user",
      "user": "@alice:example.org"
    },
    "password": "REDACTED"
  }'
```

4. Sprawdź, czy konto odbiorcy ma już pushery:

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushers"
```

Jeśli zwróci to brak aktywnych pusherów/urządzeń, najpierw napraw zwykłe powiadomienia Matrix przed dodaniem
poniższej reguły OpenClaw.

OpenClaw oznacza sfinalizowane edycje podglądu tylko tekstowego za pomocą:

```json
{
  "com.openclaw.finalized_preview": true
}
```

5. Utwórz regułę push typu override dla każdego konta odbiorcy, które powinno otrzymywać te powiadomienia:

```bash
curl -sS -X PUT \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname" \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "conditions": [
      { "kind": "event_match", "key": "type", "pattern": "m.room.message" },
      {
        "kind": "event_property_is",
        "key": "content.m\\.relates_to.rel_type",
        "value": "m.replace"
      },
      {
        "kind": "event_property_is",
        "key": "content.com\\.openclaw\\.finalized_preview",
        "value": true
      },
      { "kind": "event_match", "key": "sender", "pattern": "@bot:example.org" }
    ],
    "actions": [
      "notify",
      { "set_tweak": "sound", "value": "default" },
      { "set_tweak": "highlight", "value": false }
    ]
  }'
```

Zastąp te wartości przed uruchomieniem polecenia:

- `https://matrix.example.org`: podstawowy URL Twojego homeservera
- `$USER_ACCESS_TOKEN`: token dostępu użytkownika odbierającego
- `openclaw-finalized-preview-botname`: identyfikator reguły unikalny dla tego bota dla tego użytkownika odbierającego
- `@bot:example.org`: MXID Twojego bota Matrix OpenClaw, a nie MXID użytkownika odbierającego

Ważne w konfiguracjach z wieloma botami:

- Reguły push są kluczowane przez `ruleId`. Ponowne uruchomienie `PUT` względem tego samego identyfikatora reguły aktualizuje tę jedną regułę.
- Jeśli jeden użytkownik odbierający powinien otrzymywać powiadomienia dla wielu kont botów Matrix OpenClaw, utwórz jedną regułę na bota z unikalnym identyfikatorem reguły dla każdego dopasowania nadawcy.
- Prosty wzorzec to `openclaw-finalized-preview-<botname>`, na przykład `openclaw-finalized-preview-ops` albo `openclaw-finalized-preview-support`.

Reguła jest oceniana względem nadawcy zdarzenia:

- uwierzytelnij się tokenem użytkownika odbierającego
- dopasuj `sender` do MXID bota OpenClaw

6. Sprawdź, czy reguła istnieje:

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

7. Przetestuj odpowiedź strumieniowaną. W trybie cichym pokój powinien pokazać cichy roboczy podgląd, a końcowa
   edycja na miejscu powinna wysłać powiadomienie po zakończeniu bloku lub tury.

Jeśli później chcesz usunąć regułę, usuń ten sam identyfikator reguły za pomocą tokenu użytkownika odbierającego:

```bash
curl -sS -X DELETE \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

Uwagi:

- Utwórz regułę przy użyciu tokenu dostępu użytkownika odbierającego, a nie tokenu bota.
- Nowe zdefiniowane przez użytkownika reguły `override` są wstawiane przed domyślnymi regułami wyciszania, więc nie jest potrzebny dodatkowy parametr kolejności.
- Dotyczy to tylko edycji podglądu wyłącznie tekstowego, które OpenClaw może bezpiecznie sfinalizować na miejscu. Powroty awaryjne dla multimediów i nieaktualnych podglądów nadal używają zwykłego dostarczania Matrix.
- Jeśli `GET /_matrix/client/v3/pushers` pokazuje brak pusherów, użytkownik nie ma jeszcze działającego dostarczania powiadomień push Matrix dla tego konta/urządzenia.

#### Synapse

W przypadku Synapse powyższa konfiguracja zwykle sama w sobie wystarcza:

- Nie jest wymagana żadna specjalna zmiana w `homeserver.yaml` dla sfinalizowanych powiadomień podglądu OpenClaw.
- Jeśli Twoje wdrożenie Synapse już wysyła zwykłe powiadomienia push Matrix, token użytkownika i powyższe wywołanie `pushrules` są głównym krokiem konfiguracji.
- Jeśli uruchamiasz Synapse za reverse proxy lub workerami, upewnij się, że `/_matrix/client/.../pushrules/` poprawnie trafia do Synapse.
- Jeśli używasz workerów Synapse, upewnij się, że pushery działają prawidłowo. Dostarczanie push jest obsługiwane przez proces główny albo `synapse.app.pusher` / skonfigurowane workery pusherów.

#### Tuwunel

W przypadku Tuwunel użyj tego samego przepływu konfiguracji i wywołania API `pushrules`, które pokazano powyżej:

- Nie jest wymagana żadna konfiguracja specyficzna dla Tuwunel dla samego znacznika sfinalizowanego podglądu.
- Jeśli zwykłe powiadomienia Matrix już działają dla tego użytkownika, token użytkownika i powyższe wywołanie `pushrules` są głównym krokiem konfiguracji.
- Jeśli powiadomienia wydają się znikać, gdy użytkownik jest aktywny na innym urządzeniu, sprawdź, czy włączono `suppress_push_when_active`. Tuwunel dodał tę opcję w Tuwunel 1.4.2 12 września 2025 roku i może ona celowo wyciszać powiadomienia push na innych urządzeniach, gdy jedno urządzenie jest aktywne.

## Pokoje bot-do-bota

Domyślnie wiadomości Matrix z innych skonfigurowanych kont Matrix OpenClaw są ignorowane.

Użyj `allowBots`, jeśli celowo chcesz dopuścić ruch Matrix między agentami:

```json5
{
  channels: {
    matrix: {
      allowBots: "mentions", // true | "mentions"
      groups: {
        "!roomid:example.org": {
          requireMention: true,
        },
      },
    },
  },
}
```

- `allowBots: true` akceptuje wiadomości z innych skonfigurowanych kont botów Matrix w dozwolonych pokojach i wiadomościach prywatnych.
- `allowBots: "mentions"` akceptuje te wiadomości tylko wtedy, gdy wyraźnie wspominają tego bota w pokojach. Wiadomości prywatne nadal są dozwolone.
- `groups.<room>.allowBots` zastępuje ustawienie na poziomie konta dla jednego pokoju.
- OpenClaw nadal ignoruje wiadomości z tego samego identyfikatora użytkownika Matrix, aby uniknąć pętli odpowiedzi do samego siebie.
- Matrix nie udostępnia tutaj natywnej flagi bota; OpenClaw traktuje „wiadomość utworzoną przez bota” jako „wysłaną przez inne skonfigurowane konto Matrix na tym Gateway OpenClaw”.

Przy włączaniu ruchu bot-do-bota we współdzielonych pokojach używaj ścisłych list dozwolonych pokoi i wymagań wzmianki.

## Szyfrowanie i weryfikacja

W szyfrowanych pokojach (E2EE) wychodzące zdarzenia obrazów używają `thumbnail_file`, dzięki czemu podglądy obrazów są szyfrowane razem z pełnym załącznikiem. Nieszyfrowane pokoje nadal używają zwykłego `thumbnail_url`. Nie jest wymagana żadna konfiguracja — Plugin automatycznie wykrywa stan E2EE.

Włącz szyfrowanie:

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_xxx",
      encryption: true,
      dm: { policy: "pairing" },
    },
  },
}
```

Sprawdź status weryfikacji:

```bash
openclaw matrix verify status
```

Szczegółowy status (pełna diagnostyka):

```bash
openclaw matrix verify status --verbose
```

Uwzględnij zapisany klucz odzyskiwania w danych wyjściowych czytelnych maszynowo:

```bash
openclaw matrix verify status --include-recovery-key --json
```

Zainicjuj cross-signing i stan weryfikacji:

```bash
openclaw matrix verify bootstrap
```

Szczegółowa diagnostyka bootstrapu:

```bash
openclaw matrix verify bootstrap --verbose
```

Wymuś reset świeżej tożsamości cross-signing przed bootstrapem:

```bash
openclaw matrix verify bootstrap --force-reset-cross-signing
```

Zweryfikuj to urządzenie za pomocą klucza odzyskiwania:

```bash
openclaw matrix verify device "<your-recovery-key>"
```

Szczegółowe informacje o weryfikacji urządzenia:

```bash
openclaw matrix verify device "<your-recovery-key>" --verbose
```

Sprawdź stan kopii zapasowej kluczy pokoju:

```bash
openclaw matrix verify backup status
```

Szczegółowa diagnostyka stanu kopii zapasowej:

```bash
openclaw matrix verify backup status --verbose
```

Przywróć klucze pokoju z kopii zapasowej serwera:

```bash
openclaw matrix verify backup restore
```

Szczegółowa diagnostyka przywracania:

```bash
openclaw matrix verify backup restore --verbose
```

Usuń bieżącą kopię zapasową serwera i utwórz świeżą bazę odniesienia kopii zapasowej. Jeśli zapisany
klucz kopii zapasowej nie może zostać poprawnie załadowany, ten reset może także odtworzyć magazyn sekretów, aby
przyszłe zimne starty mogły załadować nowy klucz kopii zapasowej:

```bash
openclaw matrix verify backup reset --yes
```

Wszystkie polecenia `verify` są domyślnie zwięzłe (w tym ciche wewnętrzne logowanie SDK) i pokazują szczegółową diagnostykę tylko z `--verbose`.
Do skryptów używaj `--json`, aby uzyskać pełne dane wyjściowe czytelne maszynowo.

W konfiguracjach wielokontowych polecenia Matrix CLI używają niejawnego domyślnego konta Matrix, chyba że przekażesz `--account <id>`.
Jeśli skonfigurujesz wiele nazwanych kont, najpierw ustaw `channels.matrix.defaultAccount`, w przeciwnym razie te niejawne operacje CLI zatrzymają się i poproszą o jawny wybór konta.
Używaj `--account`, gdy chcesz, aby operacje weryfikacji lub urządzeń były jawnie kierowane do nazwanego konta:

```bash
openclaw matrix verify status --account assistant
openclaw matrix verify backup restore --account assistant
openclaw matrix devices list --account assistant
```

Gdy szyfrowanie jest wyłączone lub niedostępne dla nazwanego konta, ostrzeżenia Matrix i błędy weryfikacji wskazują klucz konfiguracji tego konta, na przykład `channels.matrix.accounts.assistant.encryption`.

### Co oznacza „zweryfikowane”

OpenClaw traktuje to urządzenie Matrix jako zweryfikowane tylko wtedy, gdy jest ono zweryfikowane przez Twoją własną tożsamość cross-signing.
W praktyce `openclaw matrix verify status --verbose` ujawnia trzy sygnały zaufania:

- `Locally trusted`: to urządzenie jest zaufane tylko przez bieżącego klienta
- `Cross-signing verified`: SDK zgłasza urządzenie jako zweryfikowane przez cross-signing
- `Signed by owner`: urządzenie jest podpisane przez Twój własny klucz self-signing

`Verified by owner` przyjmuje wartość `yes` tylko wtedy, gdy obecna jest weryfikacja cross-signing lub podpis właściciela.
Samo lokalne zaufanie nie wystarcza, aby OpenClaw traktował urządzenie jako w pełni zweryfikowane.

### Co robi bootstrap

`openclaw matrix verify bootstrap` to polecenie naprawy i konfiguracji dla szyfrowanych kont Matrix.
Wykonuje ono wszystkie poniższe czynności w tej kolejności:

- inicjalizuje magazyn sekretów, ponownie używając istniejącego klucza odzyskiwania, gdy to możliwe
- inicjalizuje cross-signing i przesyła brakujące publiczne klucze cross-signing
- próbuje oznaczyć i podpisać cross-signing bieżącego urządzenia
- tworzy nową kopię zapasową kluczy pokoju po stronie serwera, jeśli jeszcze nie istnieje

Jeśli homeserver wymaga uwierzytelniania interaktywnego do przesłania kluczy cross-signing, OpenClaw najpierw próbuje przesłania bez uwierzytelnienia, następnie z `m.login.dummy`, a potem z `m.login.password`, gdy `channels.matrix.password` jest skonfigurowane.

Używaj `--force-reset-cross-signing` tylko wtedy, gdy celowo chcesz odrzucić bieżącą tożsamość cross-signing i utworzyć nową.

Jeśli celowo chcesz odrzucić bieżącą kopię zapasową kluczy pokoju i rozpocząć nową
bazę odniesienia kopii zapasowej dla przyszłych wiadomości, użyj `openclaw matrix verify backup reset --yes`.
Rób to tylko wtedy, gdy akceptujesz, że niemożliwa do odzyskania stara zaszyfrowana historia pozostanie
niedostępna i że OpenClaw może odtworzyć magazyn sekretów, jeśli bieżący sekret kopii zapasowej
nie może zostać bezpiecznie załadowany.

### Świeża baza odniesienia kopii zapasowej

Jeśli chcesz zachować działanie przyszłych zaszyfrowanych wiadomości i akceptujesz utratę nieodzyskiwalnej starej historii, uruchom te polecenia po kolei:

```bash
openclaw matrix verify backup reset --yes
openclaw matrix verify backup status --verbose
openclaw matrix verify status
```

Dodaj `--account <id>` do każdego polecenia, gdy chcesz jawnie kierować je do nazwanego konta Matrix.

### Zachowanie przy uruchamianiu

Gdy `encryption: true`, Matrix domyślnie ustawia `startupVerification` na `"if-unverified"`.
Przy uruchamianiu, jeśli to urządzenie nadal nie jest zweryfikowane, Matrix poprosi o samoweryfikację w innym kliencie Matrix,
pominie duplikaty żądań, gdy jedno jest już oczekujące, i zastosuje lokalny czas odczekania przed ponowną próbą po restartach.
Nieudane próby żądania są domyślnie ponawiane szybciej niż udane utworzenie żądania.
Ustaw `startupVerification: "off"`, aby wyłączyć automatyczne żądania przy uruchamianiu, albo dostosuj `startupVerificationCooldownHours`,
jeśli chcesz krótsze lub dłuższe okno ponawiania.

Uruchamianie automatycznie wykonuje też zachowawczy przebieg bootstrapu kryptograficznego.
Ten przebieg najpierw próbuje ponownie użyć bieżącego magazynu sekretów i tożsamości cross-signing oraz unika resetowania cross-signing, chyba że uruchomisz jawny przepływ naprawy bootstrapu.

Jeśli podczas uruchamiania nadal zostanie wykryty uszkodzony stan bootstrapu, OpenClaw może spróbować chronionej ścieżki naprawy nawet wtedy, gdy `channels.matrix.password` nie jest skonfigurowane.
Jeśli homeserver wymaga dla tej naprawy opartego na haśle UIA, OpenClaw zapisuje ostrzeżenie w logach i zachowuje niekrytyczny charakter uruchamiania zamiast przerywać działanie bota.
Jeśli bieżące urządzenie jest już podpisane przez właściciela, OpenClaw zachowuje tę tożsamość zamiast resetować ją automatycznie.

Zobacz [migrację Matrix](/pl/install/migrating-matrix), aby poznać pełny przepływ aktualizacji, ograniczenia, polecenia odzyskiwania i typowe komunikaty migracji.

### Powiadomienia o weryfikacji

Matrix publikuje powiadomienia o cyklu życia weryfikacji bezpośrednio w ścisłym pokoju wiadomości prywatnych do weryfikacji jako wiadomości `m.notice`.
Obejmuje to:

- powiadomienia o żądaniu weryfikacji
- powiadomienia o gotowości weryfikacji (z wyraźną instrukcją „Zweryfikuj za pomocą emoji”)
- powiadomienia o rozpoczęciu i zakończeniu weryfikacji
- szczegóły SAS (emoji i liczby dziesiętne), gdy są dostępne

Przychodzące żądania weryfikacji z innego klienta Matrix są śledzone i automatycznie akceptowane przez OpenClaw.
W przepływach samoweryfikacji OpenClaw automatycznie rozpoczyna też przepływ SAS, gdy weryfikacja emoji stanie się dostępna, i potwierdza własną stronę.
W przypadku żądań weryfikacji z innego użytkownika/urządzenia Matrix OpenClaw automatycznie akceptuje żądanie, a następnie czeka, aż przepływ SAS będzie kontynuowany normalnie.
Nadal musisz porównać emoji lub dziesiętny SAS w swoim kliencie Matrix i potwierdzić tam „Są zgodne”, aby ukończyć weryfikację.

OpenClaw nie akceptuje bezrefleksyjnie automatycznie samoinicjowanych zduplikowanych przepływów. Przy uruchamianiu pomija utworzenie nowego żądania, gdy żądanie samoweryfikacji jest już oczekujące.

Powiadomienia protokołu/systemu weryfikacji nie są przekazywane do potoku czatu agenta, więc nie powodują `NO_REPLY`.

### Higiena urządzeń

Na koncie mogą gromadzić się stare urządzenia Matrix zarządzane przez OpenClaw, co utrudnia ocenę zaufania w szyfrowanych pokojach.
Wyświetl je poleceniem:

```bash
openclaw matrix devices list
```

Usuń nieaktualne urządzenia zarządzane przez OpenClaw poleceniem:

```bash
openclaw matrix devices prune-stale
```

### Magazyn kryptograficzny

Matrix E2EE używa oficjalnej ścieżki kryptografii Rust z `matrix-js-sdk` w Node, z `fake-indexeddb` jako shimem IndexedDB. Stan kryptograficzny jest utrwalany w pliku migawki (`crypto-idb-snapshot.json`) i przywracany przy uruchamianiu. Plik migawki jest wrażliwym stanem środowiska uruchomieniowego przechowywanym z restrykcyjnymi uprawnieniami do pliku.

Zaszyfrowany stan środowiska uruchomieniowego znajduje się pod katalogami per konto i per użytkownik, haszowanymi tokenem, w
`~/.openclaw/matrix/accounts/<account>/<homeserver>__<user>/<token-hash>/`.
Ten katalog zawiera magazyn synchronizacji (`bot-storage.json`), magazyn kryptograficzny (`crypto/`),
plik klucza odzyskiwania (`recovery-key.json`), migawkę IndexedDB (`crypto-idb-snapshot.json`),
powiązania wątków (`thread-bindings.json`) oraz stan weryfikacji przy uruchamianiu (`startup-verification.json`).
Gdy token się zmienia, ale tożsamość konta pozostaje taka sama, OpenClaw ponownie używa najlepszego istniejącego
katalogu głównego dla tej krotki konto/homeserver/użytkownik, dzięki czemu wcześniejszy stan synchronizacji, stan kryptograficzny, powiązania wątków
oraz stan weryfikacji przy uruchamianiu pozostają widoczne.

## Zarządzanie profilem

Zaktualizuj własny profil Matrix dla wybranego konta za pomocą:

```bash
openclaw matrix profile set --name "OpenClaw Assistant"
openclaw matrix profile set --avatar-url https://cdn.example.org/avatar.png
```

Dodaj `--account <id>`, jeśli chcesz jawnie kierować operację do nazwanego konta Matrix.

Matrix akceptuje bezpośrednio adresy URL awatarów `mxc://`. Gdy przekażesz adres URL awatara `http://` lub `https://`, OpenClaw najpierw prześle go do Matrix i zapisze rozwiązany adres URL `mxc://` z powrotem do `channels.matrix.avatarUrl` (lub do wybranego nadpisania konta).

## Wątki

Matrix obsługuje natywne wątki Matrix zarówno dla odpowiedzi automatycznych, jak i dla wysyłek przez narzędzie wiadomości.

- `dm.sessionScope: "per-user"` (domyślnie) utrzymuje routowanie wiadomości prywatnych Matrix w zakresie nadawcy, więc wiele pokoi wiadomości prywatnych może współdzielić jedną sesję, jeśli zostaną rozwiązane do tego samego peera.
- `dm.sessionScope: "per-room"` izoluje każdy pokój wiadomości prywatnych Matrix do własnego klucza sesji, nadal używając zwykłego uwierzytelniania wiadomości prywatnych i sprawdzeń listy dozwolonych.
- Jawne powiązania konwersacji Matrix nadal mają pierwszeństwo przed `dm.sessionScope`, więc powiązane pokoje i wątki zachowują wybraną sesję docelową.
- `threadReplies: "off"` utrzymuje odpowiedzi na poziomie głównym i utrzymuje przychodzące wiadomości wątkowe w sesji nadrzędnej.
- `threadReplies: "inbound"` odpowiada wewnątrz wątku tylko wtedy, gdy wiadomość przychodząca już była w tym wątku.
- `threadReplies: "always"` utrzymuje odpowiedzi pokojowe w wątku zakorzenionym w wiadomości wyzwalającej i kieruje tę konwersację przez odpowiadającą sesję w zakresie wątku od pierwszej wiadomości wyzwalającej.
- `dm.threadReplies` nadpisuje ustawienie najwyższego poziomu tylko dla wiadomości prywatnych. Na przykład możesz utrzymać izolację wątków pokojowych, pozostawiając wiadomości prywatne płaskie.
- Przychodzące wiadomości wątkowe zawierają wiadomość główną wątku jako dodatkowy kontekst agenta.
- Wysyłki przez narzędzie wiadomości automatycznie dziedziczą bieżący wątek Matrix, gdy celem jest ten sam pokój lub ten sam docelowy użytkownik wiadomości prywatnych, chyba że podano jawne `threadId`.
- Ponowne użycie tego samego celu użytkownika wiadomości prywatnych w tej samej sesji uruchamia się tylko wtedy, gdy bieżące metadane sesji potwierdzają tego samego peera wiadomości prywatnych na tym samym koncie Matrix; w przeciwnym razie OpenClaw wraca do normalnego routowania w zakresie użytkownika.
- Gdy OpenClaw wykryje kolizję pokoju wiadomości prywatnych Matrix z innym pokojem wiadomości prywatnych w tej samej współdzielonej sesji wiadomości prywatnych Matrix, publikuje jednorazowe `m.notice` w tym pokoju z mechanizmem awaryjnym `/focus`, gdy powiązania wątków są włączone, oraz ze wskazówką `dm.sessionScope`.
- Powiązania wątków w środowisku uruchomieniowym są obsługiwane dla Matrix. `/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age` i powiązane z wątkiem `/acp spawn` działają w pokojach i wiadomościach prywatnych Matrix.
- Główne `/focus` w pokoju/wiadomości prywatnej Matrix tworzy nowy wątek Matrix i wiąże go z sesją docelową, gdy `threadBindings.spawnSubagentSessions=true`.
- Uruchomienie `/focus` lub `/acp spawn --thread here` wewnątrz istniejącego wątku Matrix wiąże zamiast tego ten bieżący wątek.

## Powiązania konwersacji ACP

Pokoje Matrix, wiadomości prywatne i istniejące wątki Matrix mogą zostać przekształcone w trwałe obszary robocze ACP bez zmiany powierzchni czatu.

Szybki przepływ pracy operatora:

- Uruchom `/acp spawn codex --bind here` wewnątrz wiadomości prywatnej Matrix, pokoju lub istniejącego wątku, którego chcesz nadal używać.
- W głównej wiadomości prywatnej lub pokoju Matrix bieżąca wiadomość prywatna/pokój pozostaje powierzchnią czatu, a przyszłe wiadomości są kierowane do uruchomionej sesji ACP.
- Wewnątrz istniejącego wątku Matrix `--bind here` wiąże ten bieżący wątek na miejscu.
- `/new` i `/reset` resetują tę samą powiązaną sesję ACP na miejscu.
- `/acp close` zamyka sesję ACP i usuwa powiązanie.

Uwagi:

- `--bind here` nie tworzy podrzędnego wątku Matrix.
- `threadBindings.spawnAcpSessions` jest wymagane tylko dla `/acp spawn --thread auto|here`, gdzie OpenClaw musi utworzyć lub powiązać podrzędny wątek Matrix.

### Konfiguracja powiązań wątków

Matrix dziedziczy globalne wartości domyślne z `session.threadBindings`, a także obsługuje nadpisania per kanał:

- `threadBindings.enabled`
- `threadBindings.idleHours`
- `threadBindings.maxAgeHours`
- `threadBindings.spawnSubagentSessions`
- `threadBindings.spawnAcpSessions`

Flagi uruchamiania powiązanego z wątkiem Matrix są typu opt-in:

- Ustaw `threadBindings.spawnSubagentSessions: true`, aby pozwolić głównemu `/focus` tworzyć i wiązać nowe wątki Matrix.
- Ustaw `threadBindings.spawnAcpSessions: true`, aby pozwolić `/acp spawn --thread auto|here` wiązać sesje ACP z wątkami Matrix.

## Reakcje

Matrix obsługuje wychodzące akcje reakcji, przychodzące powiadomienia o reakcjach oraz przychodzące reakcje potwierdzające.

- Narzędzia wychodzących reakcji są kontrolowane przez `channels["matrix"].actions.reactions`.
- `react` dodaje reakcję do konkretnego zdarzenia Matrix.
- `reactions` wyświetla bieżące podsumowanie reakcji dla konkretnego zdarzenia Matrix.
- `emoji=""` usuwa własne reakcje konta bota na tym zdarzeniu.
- `remove: true` usuwa tylko określoną reakcję emoji z konta bota.

Zakres reakcji potwierdzających jest rozwiązywany w standardowej kolejności OpenClaw:

- `channels["matrix"].accounts.<accountId>.ackReaction`
- `channels["matrix"].ackReaction`
- `messages.ackReaction`
- zapasowe emoji tożsamości agenta

Zakres reakcji potwierdzających jest rozwiązywany w tej kolejności:

- `channels["matrix"].accounts.<accountId>.ackReactionScope`
- `channels["matrix"].ackReactionScope`
- `messages.ackReactionScope`

Tryb powiadomień o reakcjach jest rozwiązywany w tej kolejności:

- `channels["matrix"].accounts.<accountId>.reactionNotifications`
- `channels["matrix"].reactionNotifications`
- domyślnie: `own`

Zachowanie:

- `reactionNotifications: "own"` przekazuje dodane zdarzenia `m.reaction`, gdy są skierowane do wiadomości Matrix utworzonych przez bota.
- `reactionNotifications: "off"` wyłącza zdarzenia systemowe reakcji.
- Usunięcia reakcji nie są syntetyzowane do zdarzeń systemowych, ponieważ Matrix udostępnia je jako redakcje, a nie jako samodzielne usunięcia `m.reaction`.

## Kontekst historii

- `channels.matrix.historyLimit` kontroluje, ile ostatnich wiadomości pokoju jest dołączanych jako `InboundHistory`, gdy wiadomość w pokoju Matrix wyzwala agenta. Wartość zapasowa to `messages.groupChat.historyLimit`; jeśli oba ustawienia są nieustawione, efektywną wartością domyślną jest `0`. Ustaw `0`, aby wyłączyć.
- Historia pokoju Matrix jest tylko pokojowa. Wiadomości prywatne nadal używają normalnej historii sesji.
- Historia pokoju Matrix ma charakter tylko oczekujący: OpenClaw buforuje wiadomości pokojowe, które jeszcze nie wyzwoliły odpowiedzi, a następnie zapisuje migawkę tego okna, gdy nadejdzie wzmianka lub inny wyzwalacz.
- Bieżąca wiadomość wyzwalająca nie jest uwzględniana w `InboundHistory`; pozostaje w głównej treści przychodzącej dla tej tury.
- Ponowienia tego samego zdarzenia Matrix używają ponownie oryginalnej migawki historii zamiast przesuwać się do nowszych wiadomości pokojowych.

## Widoczność kontekstu

Matrix obsługuje współdzieloną kontrolę `contextVisibility` dla uzupełniającego kontekstu pokoju, takiego jak pobrana treść odpowiedzi, główne wiadomości wątków i oczekująca historia.

- `contextVisibility: "all"` jest ustawieniem domyślnym. Uzupełniający kontekst jest zachowywany w otrzymanej postaci.
- `contextVisibility: "allowlist"` filtruje uzupełniający kontekst do nadawców dozwolonych przez aktywne sprawdzenia list dozwolonych pokoju/użytkownika.
- `contextVisibility: "allowlist_quote"` działa jak `allowlist`, ale nadal zachowuje jedną jawną cytowaną odpowiedź.

To ustawienie wpływa na widoczność uzupełniającego kontekstu, a nie na to, czy sama wiadomość przychodząca może wyzwolić odpowiedź.
Autoryzacja wyzwalacza nadal pochodzi z ustawień `groupPolicy`, `groups`, `groupAllowFrom` i zasad wiadomości prywatnych.

## Zasady wiadomości prywatnych i pokoi

```json5
{
  channels: {
    matrix: {
      dm: {
        policy: "allowlist",
        allowFrom: ["@admin:example.org"],
        threadReplies: "off",
      },
      groupPolicy: "allowlist",
      groupAllowFrom: ["@admin:example.org"],
      groups: {
        "!roomid:example.org": {
          requireMention: true,
        },
      },
    },
  },
}
```

Zobacz [Groups](/pl/channels/groups), aby poznać zachowanie bramkowania wzmiankami i list dozwolonych.

Przykład parowania dla wiadomości prywatnych Matrix:

```bash
openclaw pairing list matrix
openclaw pairing approve matrix <CODE>
```

Jeśli niezatwierdzony użytkownik Matrix nadal wysyła Ci wiadomości przed zatwierdzeniem, OpenClaw ponownie użyje tego samego oczekującego kodu parowania i może ponownie wysłać przypomnienie po krótkim czasie odczekania zamiast generować nowy kod.

Zobacz [Pairing](/pl/channels/pairing), aby poznać współdzielony przepływ parowania wiadomości prywatnych i układ przechowywania.

## Naprawa pokoju bezpośredniego

Jeśli stan wiadomości bezpośrednich się rozjedzie, OpenClaw może skończyć ze starymi mapowaniami `m.direct`, które wskazują stare pokoje solo zamiast aktywnej wiadomości prywatnej. Sprawdź bieżące mapowanie dla peera za pomocą:

```bash
openclaw matrix direct inspect --user-id @alice:example.org
```

Napraw je za pomocą:

```bash
openclaw matrix direct repair --user-id @alice:example.org
```

Przepływ naprawy:

- preferuje ścisłą wiadomość prywatną 1:1, która jest już zmapowana w `m.direct`
- w razie potrzeby przechodzi do dowolnej aktualnie dołączonej ścisłej wiadomości prywatnej 1:1 z tym użytkownikiem
- tworzy nowy pokój bezpośredni i przepisuje `m.direct`, jeśli nie istnieje zdrowa wiadomość prywatna

Przepływ naprawy nie usuwa automatycznie starych pokoi. Wybiera tylko zdrową wiadomość prywatną i aktualizuje mapowanie, aby nowe wysyłki Matrix, powiadomienia weryfikacyjne i inne przepływy wiadomości bezpośrednich znów trafiały do właściwego pokoju.

## Zatwierdzenia exec

Matrix może działać jako natywny klient zatwierdzeń dla konta Matrix. Natywne
pokrętła routowania wiadomości prywatnych/kanałów nadal znajdują się pod konfiguracją zatwierdzeń exec:

- `channels.matrix.execApprovals.enabled`
- `channels.matrix.execApprovals.approvers` (opcjonalne; wartość zapasowa to `channels.matrix.dm.allowFrom`)
- `channels.matrix.execApprovals.target` (`dm` | `channel` | `both`, domyślnie: `dm`)
- `channels.matrix.execApprovals.agentFilter`
- `channels.matrix.execApprovals.sessionFilter`

Zatwierdzający muszą być identyfikatorami użytkowników Matrix, takimi jak `@owner:example.org`. Matrix automatycznie włącza natywne zatwierdzenia, gdy `enabled` jest nieustawione lub ma wartość `"auto"` i można rozwiązać co najmniej jednego zatwierdzającego. Zatwierdzenia exec używają najpierw `execApprovals.approvers` i mogą wracać do `channels.matrix.dm.allowFrom`. Zatwierdzenia Pluginów autoryzują się przez `channels.matrix.dm.allowFrom`. Ustaw `enabled: false`, aby jawnie wyłączyć Matrix jako natywnego klienta zatwierdzeń. W przeciwnym razie żądania zatwierdzenia wracają do innych skonfigurowanych ścieżek zatwierdzania albo do zasad awaryjnych zatwierdzania.

Natywne routowanie Matrix obsługuje oba rodzaje zatwierdzeń:

- `channels.matrix.execApprovals.*` kontroluje natywny tryb rozsyłania do wiadomości prywatnych/kanałów dla promptów zatwierdzania Matrix.
- Zatwierdzenia exec używają zbioru zatwierdzających exec z `execApprovals.approvers` albo `channels.matrix.dm.allowFrom`.
- Zatwierdzenia Pluginów używają listy dozwolonych wiadomości prywatnych Matrix z `channels.matrix.dm.allowFrom`.
- Skróty reakcji Matrix i aktualizacje wiadomości mają zastosowanie zarówno do zatwierdzeń exec, jak i Pluginów.

Zasady dostarczania:

- `target: "dm"` wysyła prompty zatwierdzania do wiadomości prywatnych zatwierdzających
- `target: "channel"` wysyła prompt z powrotem do źródłowego pokoju lub wiadomości prywatnej Matrix
- `target: "both"` wysyła do wiadomości prywatnych zatwierdzających oraz do źródłowego pokoju lub wiadomości prywatnej Matrix

Prompty zatwierdzania Matrix inicjują skróty reakcji na głównej wiadomości zatwierdzania:

- `✅` = zezwól raz
- `❌` = odmów
- `♾️` = zezwól zawsze, gdy taka decyzja jest dozwolona przez efektywną politykę exec

Zatwierdzający mogą zareagować na tę wiadomość albo użyć zapasowych poleceń slash: `/approve <id> allow-once`, `/approve <id> allow-always` lub `/approve <id> deny`.

Tylko rozwiązani zatwierdzający mogą zatwierdzać lub odmawiać. W przypadku zatwierdzeń exec dostarczanie kanałowe zawiera treść polecenia, dlatego włączaj `channel` lub `both` tylko w zaufanych pokojach.

Nadpisanie per konto:

- `channels.matrix.accounts.<account>.execApprovals`

Powiązane dokumenty: [Exec approvals](/pl/tools/exec-approvals)

## Wiele kont

```json5
{
  channels: {
    matrix: {
      enabled: true,
      defaultAccount: "assistant",
      dm: { policy: "pairing" },
      accounts: {
        assistant: {
          homeserver: "https://matrix.example.org",
          accessToken: "syt_assistant_xxx",
          encryption: true,
        },
        alerts: {
          homeserver: "https://matrix.example.org",
          accessToken: "syt_alerts_xxx",
          dm: {
            policy: "allowlist",
            allowFrom: ["@ops:example.org"],
            threadReplies: "off",
          },
        },
      },
    },
  },
}
```

Wartości najwyższego poziomu `channels.matrix` działają jako wartości domyślne dla nazwanych kont, chyba że konto je nadpisze.
Możesz ograniczyć odziedziczone wpisy pokojów do jednego konta Matrix za pomocą `groups.<room>.account`.
Wpisy bez `account` pozostają współdzielone przez wszystkie konta Matrix, a wpisy z `account: "default"` nadal działają, gdy konto domyślne jest skonfigurowane bezpośrednio na najwyższym poziomie `channels.matrix.*`.
Częściowe współdzielone domyślne ustawienia uwierzytelniania same z siebie nie tworzą osobnego niejawnego konta domyślnego. OpenClaw syntetyzuje konto najwyższego poziomu `default` tylko wtedy, gdy to domyślne konto ma świeże uwierzytelnienie (`homeserver` plus `accessToken` albo `homeserver` plus `userId` i `password`); nazwane konta nadal mogą pozostać wykrywalne na podstawie `homeserver` plus `userId`, gdy zapisane poświadczenia spełnią wymagania uwierzytelniania później.
Jeśli Matrix ma już dokładnie jedno nazwane konto albo `defaultAccount` wskazuje istniejący klucz nazwanego konta, promocja naprawy/konfiguracji z jednego konta do wielu kont zachowuje to konto zamiast tworzyć świeży wpis `accounts.default`. Tylko klucze uwierzytelniania/bootstrapu Matrix są przenoszone do promowanego konta; współdzielone klucze polityki dostarczania pozostają na najwyższym poziomie.
Ustaw `defaultAccount`, gdy chcesz, aby OpenClaw preferował jedno nazwane konto Matrix do niejawnego routingu, sondowania i operacji CLI.
Jeśli skonfigurowano wiele kont Matrix i jedno z identyfikatorów kont to `default`, OpenClaw używa tego konta niejawnie nawet wtedy, gdy `defaultAccount` nie jest ustawione.
Jeśli skonfigurujesz wiele nazwanych kont, ustaw `defaultAccount` albo przekazuj `--account <id>` dla poleceń CLI, które opierają się na niejawnym wyborze konta.
Przekaż `--account <id>` do `openclaw matrix verify ...` i `openclaw matrix devices ...`, gdy chcesz nadpisać ten niejawny wybór dla jednego polecenia.

Zobacz [Configuration reference](/pl/gateway/configuration-reference#multi-account-all-channels), aby poznać współdzielony wzorzec wielu kont.

## Prywatne/LAN homeservery

Domyślnie OpenClaw blokuje prywatne/wewnętrzne homeservery Matrix dla ochrony SSRF, chyba że
jawnie włączysz to per konto.

Jeśli Twój homeserver działa na localhost, adresie IP LAN/Tailscale albo wewnętrznej nazwie hosta, włącz
`network.dangerouslyAllowPrivateNetwork` dla tego konta Matrix:

```json5
{
  channels: {
    matrix: {
      homeserver: "http://matrix-synapse:8008",
      network: {
        dangerouslyAllowPrivateNetwork: true,
      },
      accessToken: "syt_internal_xxx",
    },
  },
}
```

Przykład konfiguracji przez CLI:

```bash
openclaw matrix account add \
  --account ops \
  --homeserver http://matrix-synapse:8008 \
  --allow-private-network \
  --access-token syt_ops_xxx
```

To ustawienie opt-in pozwala tylko na zaufane cele prywatne/wewnętrzne. Publiczne homeservery działające po jawnym HTTP, takie jak
`http://matrix.example.org:8008`, nadal pozostają zablokowane. Gdy to możliwe, preferuj `https://`.

## Przekazywanie ruchu Matrix przez proxy

Jeśli Twoje wdrożenie Matrix wymaga jawnego wychodzącego proxy HTTP(S), ustaw `channels.matrix.proxy`:

```json5
{
  channels: {
    matrix: {
      homeserver: "https://matrix.example.org",
      accessToken: "syt_bot_xxx",
      proxy: "http://127.0.0.1:7890",
    },
  },
}
```

Nazwane konta mogą nadpisać domyślne ustawienie najwyższego poziomu przez `channels.matrix.accounts.<id>.proxy`.
OpenClaw używa tego samego ustawienia proxy zarówno dla ruchu Matrix w czasie działania, jak i dla sond statusu konta.

## Rozwiązywanie celów

Matrix akceptuje te formy celu wszędzie tam, gdzie OpenClaw prosi o cel pokoju lub użytkownika:

- Użytkownicy: `@user:server`, `user:@user:server` albo `matrix:user:@user:server`
- Pokoje: `!room:server`, `room:!room:server` albo `matrix:room:!room:server`
- Aliasy: `#alias:server`, `channel:#alias:server` albo `matrix:channel:#alias:server`

Wyszukiwanie katalogu na żywo używa zalogowanego konta Matrix:

- Wyszukiwania użytkowników odpytują katalog użytkowników Matrix na tym homeserverze.
- Wyszukiwania pokojów akceptują bezpośrednio jawne identyfikatory pokojów i aliasy, a następnie w razie potrzeby przechodzą do przeszukiwania nazw dołączonych pokojów dla tego konta.
- Wyszukiwanie nazw dołączonych pokojów jest podejściem best-effort. Jeśli nazwy pokoju nie da się rozwiązać do identyfikatora lub aliasu, zostaje ona zignorowana podczas rozwiązywania listy dozwolonych w czasie działania.

## Dokumentacja konfiguracji

- `enabled`: włącza lub wyłącza kanał.
- `name`: opcjonalna etykieta konta.
- `defaultAccount`: preferowany identyfikator konta, gdy skonfigurowano wiele kont Matrix.
- `homeserver`: adres URL homeservera, na przykład `https://matrix.example.org`.
- `network.dangerouslyAllowPrivateNetwork`: pozwala temu kontu Matrix łączyć się z prywatnymi/wewnętrznymi homeserverami. Włącz to, gdy homeserver rozwiązuje się do `localhost`, adresu IP LAN/Tailscale albo wewnętrznego hosta takiego jak `matrix-synapse`.
- `proxy`: opcjonalny adres URL proxy HTTP(S) dla ruchu Matrix. Nazwane konta mogą nadpisać domyślne ustawienie najwyższego poziomu własnym `proxy`.
- `userId`: pełny identyfikator użytkownika Matrix, na przykład `@bot:example.org`.
- `accessToken`: token dostępu do uwierzytelniania opartego na tokenie. Zwykłe wartości tekstowe i wartości SecretRef są obsługiwane dla `channels.matrix.accessToken` oraz `channels.matrix.accounts.<id>.accessToken` w dostawcach env/file/exec. Zobacz [Secrets Management](/pl/gateway/secrets).
- `password`: hasło do logowania opartego na haśle. Obsługiwane są zwykłe wartości tekstowe i wartości SecretRef.
- `deviceId`: jawny identyfikator urządzenia Matrix.
- `deviceName`: wyświetlana nazwa urządzenia dla logowania hasłem.
- `avatarUrl`: zapisany adres URL własnego awatara do synchronizacji profilu i aktualizacji `profile set`.
- `initialSyncLimit`: maksymalna liczba zdarzeń pobieranych podczas synchronizacji przy uruchamianiu.
- `encryption`: włącza E2EE.
- `allowlistOnly`: gdy ma wartość `true`, podnosi politykę pokoju `open` do `allowlist` i wymusza `allowlist` dla wszystkich aktywnych polityk wiadomości prywatnych z wyjątkiem `disabled` (w tym `pairing` i `open`). Nie wpływa na polityki `disabled`.
- `allowBots`: pozwala na wiadomości z innych skonfigurowanych kont Matrix OpenClaw (`true` albo `"mentions"`).
- `groupPolicy`: `open`, `allowlist` albo `disabled`.
- `contextVisibility`: tryb widoczności uzupełniającego kontekstu pokoju (`all`, `allowlist`, `allowlist_quote`).
- `groupAllowFrom`: lista dozwolonych identyfikatorów użytkowników dla ruchu pokojowego. Wpisy powinny być pełnymi identyfikatorami użytkowników Matrix; nierozwiązane nazwy są ignorowane w czasie działania.
- `historyLimit`: maksymalna liczba wiadomości pokoju do uwzględnienia jako kontekst historii grupy. Wartość zapasowa to `messages.groupChat.historyLimit`; jeśli oba ustawienia są nieustawione, efektywną wartością domyślną jest `0`. Ustaw `0`, aby wyłączyć.
- `replyToMode`: `off`, `first`, `all` albo `batched`.
- `markdown`: opcjonalna konfiguracja renderowania Markdown dla wychodzącego tekstu Matrix.
- `streaming`: `off` (domyślnie), `"partial"`, `"quiet"`, `true` albo `false`. `"partial"` i `true` włączają aktualizacje szkicu typu preview-first przy użyciu zwykłych wiadomości tekstowych Matrix. `"quiet"` używa niepowiadamiających powiadomień podglądu dla samodzielnie hostowanych konfiguracji reguł push. `false` jest równoważne `"off"`.
- `blockStreaming`: `true` włącza osobne wiadomości postępu dla ukończonych bloków asystenta, gdy aktywne jest strumieniowanie szkicu podglądu.
- `threadReplies`: `off`, `inbound` albo `always`.
- `threadBindings`: nadpisania per kanał dla routingu i cyklu życia sesji powiązanych z wątkami.
- `startupVerification`: tryb automatycznego żądania samoweryfikacji przy uruchamianiu (`if-unverified`, `off`).
- `startupVerificationCooldownHours`: czas odczekania przed ponowną próbą automatycznych żądań weryfikacji przy uruchamianiu.
- `textChunkLimit`: rozmiar fragmentu wiadomości wychodzącej w znakach (ma zastosowanie, gdy `chunkMode` ma wartość `length`).
- `chunkMode`: `length` dzieli wiadomości według liczby znaków; `newline` dzieli na granicach linii.
- `responsePrefix`: opcjonalny ciąg znaków dodawany na początku wszystkich odpowiedzi wychodzących dla tego kanału.
- `ackReaction`: opcjonalne nadpisanie reakcji potwierdzającej dla tego kanału/konta.
- `ackReactionScope`: opcjonalne nadpisanie zakresu reakcji potwierdzającej (`group-mentions`, `group-all`, `direct`, `all`, `none`, `off`).
- `reactionNotifications`: tryb przychodzących powiadomień o reakcjach (`own`, `off`).
- `mediaMaxMb`: limit rozmiaru multimediów w MB dla wysyłek wychodzących i przetwarzania multimediów przychodzących.
- `autoJoin`: polityka automatycznego dołączania do zaproszeń (`always`, `allowlist`, `off`). Domyślnie: `off`. Dotyczy wszystkich zaproszeń Matrix, w tym zaproszeń w stylu wiadomości prywatnych.
- `autoJoinAllowlist`: pokoje/aliasy dozwolone, gdy `autoJoin` ma wartość `allowlist`. Wpisy aliasów są rozwiązywane do identyfikatorów pokojów podczas obsługi zaproszeń; OpenClaw nie ufa stanowi aliasu deklarowanemu przez zaproszony pokój.
- `dm`: blok zasad wiadomości prywatnych (`enabled`, `policy`, `allowFrom`, `sessionScope`, `threadReplies`).
- `dm.policy`: kontroluje dostęp do wiadomości prywatnych po tym, jak OpenClaw dołączył do pokoju i sklasyfikował go jako wiadomość prywatną. Nie zmienia tego, czy zaproszenie zostanie automatycznie przyjęte.
- `dm.allowFrom`: wpisy powinny być pełnymi identyfikatorami użytkowników Matrix, chyba że zostały już rozwiązane przez wyszukiwanie katalogu na żywo.
- `dm.sessionScope`: `per-user` (domyślnie) albo `per-room`. Użyj `per-room`, gdy chcesz, aby każdy pokój wiadomości prywatnych Matrix zachowywał oddzielny kontekst, nawet jeśli peer jest ten sam.
- `dm.threadReplies`: nadpisanie polityki wątków tylko dla wiadomości prywatnych (`off`, `inbound`, `always`). Nadpisuje ustawienie najwyższego poziomu `threadReplies` zarówno dla umiejscowienia odpowiedzi, jak i izolacji sesji w wiadomościach prywatnych.
- `execApprovals`: natywne dostarczanie zatwierdzeń exec w Matrix (`enabled`, `approvers`, `target`, `agentFilter`, `sessionFilter`).
- `execApprovals.approvers`: identyfikatory użytkowników Matrix uprawnionych do zatwierdzania żądań exec. Opcjonalne, gdy `dm.allowFrom` już identyfikuje zatwierdzających.
- `execApprovals.target`: `dm | channel | both` (domyślnie: `dm`).
- `accounts`: nazwane nadpisania per konto. Wartości najwyższego poziomu `channels.matrix` działają jako wartości domyślne dla tych wpisów.
- `groups`: mapa zasad per pokój. Preferuj identyfikatory pokojów lub aliasy; nierozwiązane nazwy pokojów są ignorowane w czasie działania. Tożsamość sesji/grupy używa stabilnego identyfikatora pokoju po rozwiązaniu.
- `groups.<room>.account`: ogranicza jeden odziedziczony wpis pokoju do konkretnego konta Matrix w konfiguracjach wielokontowych.
- `groups.<room>.allowBots`: nadpisanie na poziomie pokoju dla nadawców będących skonfigurowanymi botami (`true` albo `"mentions"`).
- `groups.<room>.users`: lista dozwolonych nadawców per pokój.
- `groups.<room>.tools`: nadpisania per pokój dla zezwoleń/odmów narzędzi.
- `groups.<room>.autoReply`: nadpisanie bramkowania wzmiankami na poziomie pokoju. `true` wyłącza wymagania wzmianki dla tego pokoju; `false` wymusza ich ponowne włączenie.
- `groups.<room>.skills`: opcjonalny filtr Skills na poziomie pokoju.
- `groups.<room>.systemPrompt`: opcjonalny fragment system promptu na poziomie pokoju.
- `rooms`: starszy alias dla `groups`.
- `actions`: kontrola dostępu do narzędzi per akcja (`messages`, `reactions`, `pins`, `profile`, `memberInfo`, `channelInfo`, `verification`).

## Powiązane

- [Channels Overview](/pl/channels) — wszystkie obsługiwane kanały
- [Pairing](/pl/channels/pairing) — uwierzytelnianie wiadomości prywatnych i przepływ parowania
- [Groups](/pl/channels/groups) — zachowanie czatu grupowego i bramkowanie wzmiankami
- [Channel Routing](/pl/channels/channel-routing) — routowanie sesji dla wiadomości
- [Security](/pl/gateway/security) — model dostępu i utwardzanie
