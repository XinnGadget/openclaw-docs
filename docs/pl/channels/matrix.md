---
read_when:
    - Konfigurowanie Matrix w OpenClaw
    - Konfigurowanie E2EE i weryfikacji Matrix
summary: Stan obsługi Matrix, konfiguracja i przykłady ustawień
title: Matrix
x-i18n:
    generated_at: "2026-04-06T03:08:38Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3e2d84c08d7d5b96db14b914e54f08d25334401cdd92eb890bc8dfb37b0ca2dc
    source_path: channels/matrix.md
    workflow: 15
---

# Matrix

Matrix to dołączona w pakiecie wtyczka kanału Matrix dla OpenClaw.
Korzysta z oficjalnego `matrix-js-sdk` i obsługuje wiadomości prywatne, pokoje, wątki, multimedia, reakcje, ankiety, lokalizację oraz E2EE.

## Dołączona wtyczka

Matrix jest dostarczany jako dołączona wtyczka w bieżących wydaniach OpenClaw, więc zwykłe
spakowane buildy nie wymagają osobnej instalacji.

Jeśli używasz starszego buildu lub niestandardowej instalacji, która nie zawiera Matrix, zainstaluj
go ręcznie:

Instalacja z npm:

```bash
openclaw plugins install @openclaw/matrix
```

Instalacja z lokalnego checkoutu:

```bash
openclaw plugins install ./path/to/local/matrix-plugin
```

Zobacz [Wtyczki](/pl/tools/plugin), aby poznać zachowanie wtyczek i zasady instalacji.

## Konfiguracja

1. Upewnij się, że wtyczka Matrix jest dostępna.
   - Jest już dołączona do obecnych spakowanych wydań OpenClaw.
   - Starsze/niestandardowe instalacje mogą dodać ją ręcznie za pomocą powyższych poleceń.
2. Utwórz konto Matrix na swoim homeserverze.
3. Skonfiguruj `channels.matrix`, używając jednego z wariantów:
   - `homeserver` + `accessToken`, lub
   - `homeserver` + `userId` + `password`.
4. Uruchom ponownie gateway.
5. Rozpocznij wiadomość prywatną z botem lub zaproś go do pokoju.

Ścieżki konfiguracji interaktywnej:

```bash
openclaw channels add
openclaw configure --section channels
```

O co dokładnie pyta kreator Matrix:

- URL homeservera
- metoda uwierzytelniania: token dostępu lub hasło
- identyfikator użytkownika tylko wtedy, gdy wybierzesz uwierzytelnianie hasłem
- opcjonalna nazwa urządzenia
- czy włączyć E2EE
- czy skonfigurować teraz dostęp do pokoi Matrix

Istotne zachowanie kreatora:

- Jeśli zmienne środowiskowe uwierzytelniania Matrix już istnieją dla wybranego konta, a to konto nie ma jeszcze zapisanego uwierzytelniania w konfiguracji, kreator oferuje skrót ze zmiennymi środowiskowymi i zapisuje dla tego konta tylko `enabled: true`.
- Gdy interaktywnie dodajesz kolejne konto Matrix, wpisana nazwa konta jest normalizowana do identyfikatora konta używanego w konfiguracji i zmiennych środowiskowych. Na przykład `Ops Bot` staje się `ops-bot`.
- Podpowiedzi allowlisty wiadomości prywatnych od razu akceptują pełne wartości `@user:server`. Nazwy wyświetlane działają tylko wtedy, gdy wyszukiwanie w katalogu na żywo znajdzie dokładnie jedno dopasowanie; w przeciwnym razie kreator poprosi o ponowną próbę z pełnym identyfikatorem Matrix.
- Podpowiedzi allowlisty pokoi akceptują bezpośrednio identyfikatory pokoi i aliasy. Mogą też rozpoznawać nazwy dołączonych pokoi na żywo, ale nierozpoznane nazwy są podczas konfiguracji zachowywane tylko w wpisanej postaci i później ignorowane przez rozpoznawanie allowlisty w czasie działania. Preferuj `!room:server` lub `#alias:server`.
- Tożsamość pokoju/sesji w czasie działania używa stabilnego identyfikatora pokoju Matrix. Aliasy zadeklarowane w pokoju są używane tylko jako dane wejściowe wyszukiwania, a nie jako długoterminowy klucz sesji ani stabilna tożsamość grupy.
- Aby rozpoznać nazwy pokoi przed ich zapisaniem, użyj `openclaw channels resolve --channel matrix "Project Room"`.

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

Matrix przechowuje zbuforowane poświadczenia w `~/.openclaw/credentials/matrix/`.
Konto domyślne używa `credentials.json`; nazwane konta używają `credentials-<account>.json`.
Gdy istnieją tam zbuforowane poświadczenia, OpenClaw traktuje Matrix jako skonfigurowany na potrzeby konfiguracji, doctor oraz wykrywania stanu kanału, nawet jeśli bieżące uwierzytelnianie nie jest ustawione bezpośrednio w konfiguracji.

Odpowiedniki w zmiennych środowiskowych (używane, gdy klucz konfiguracyjny nie jest ustawiony):

- `MATRIX_HOMESERVER`
- `MATRIX_ACCESS_TOKEN`
- `MATRIX_USER_ID`
- `MATRIX_PASSWORD`
- `MATRIX_DEVICE_ID`
- `MATRIX_DEVICE_NAME`

Dla kont innych niż domyślne użyj zmiennych środowiskowych przypisanych do konta:

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

Matrix ucieka znaki interpunkcyjne w identyfikatorach kont, aby uniknąć kolizji zmiennych środowiskowych przypisanych do kont.
Na przykład `-` staje się `_X2D_`, więc `ops-prod` mapuje się na `MATRIX_OPS_X2D_PROD_*`.

Interaktywny kreator oferuje skrót ze zmiennymi środowiskowymi tylko wtedy, gdy te zmienne uwierzytelniania są już obecne, a wybrane konto nie ma jeszcze zapisanego uwierzytelniania Matrix w konfiguracji.

## Przykład konfiguracji

To praktyczna bazowa konfiguracja z parowaniem wiadomości prywatnych, allowlistą pokoi i włączonym E2EE:

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

## Podglądy strumieniowania

Strumieniowanie odpowiedzi Matrix jest opcjonalne.

Ustaw `channels.matrix.streaming` na `"partial"`, jeśli chcesz, aby OpenClaw wysłał pojedynczą podglądową
odpowiedź na żywo, edytował ten podgląd w miejscu podczas generowania tekstu przez model, a następnie sfinalizował go po
zakończeniu odpowiedzi:

```json5
{
  channels: {
    matrix: {
      streaming: "partial",
    },
  },
}
```

- `streaming: "off"` jest ustawieniem domyślnym. OpenClaw czeka na końcową odpowiedź i wysyła ją jednorazowo.
- `streaming: "partial"` tworzy jedną edytowalną wiadomość podglądu dla bieżącego bloku odpowiedzi asystenta przy użyciu zwykłych wiadomości tekstowych Matrix. Zachowuje to starsze zachowanie Matrix polegające na powiadamianiu najpierw o podglądzie, więc standardowe klienty mogą powiadamiać na podstawie pierwszego strumieniowanego tekstu podglądu zamiast gotowego bloku.
- `streaming: "quiet"` tworzy jeden edytowalny cichy podgląd-notice dla bieżącego bloku odpowiedzi asystenta. Używaj tego tylko wtedy, gdy skonfigurujesz także reguły push odbiorców dla sfinalizowanych edycji podglądu.
- `blockStreaming: true` włącza osobne komunikaty postępu Matrix. Gdy strumieniowanie podglądu jest włączone, Matrix zachowuje bieżący szkic dla aktualnego bloku i pozostawia ukończone bloki jako osobne wiadomości.
- Gdy podgląd strumieniowania jest włączony, a `blockStreaming` jest wyłączone, Matrix edytuje szkic na żywo w miejscu i finalizuje to samo zdarzenie po zakończeniu bloku lub całej tury.
- Jeśli podgląd przestanie mieścić się w jednym zdarzeniu Matrix, OpenClaw zatrzymuje strumieniowanie podglądu i wraca do zwykłego końcowego dostarczenia.
- Odpowiedzi multimedialne nadal wysyłają załączniki normalnie. Jeśli nie można już bezpiecznie ponownie użyć starego podglądu, OpenClaw redaguje go przed wysłaniem końcowej odpowiedzi multimedialnej.
- Edycje podglądu powodują dodatkowe wywołania API Matrix. Pozostaw strumieniowanie wyłączone, jeśli chcesz zachować najbardziej konserwatywne zachowanie względem limitów szybkości.

Samo `blockStreaming` nie włącza szkiców podglądu.
Użyj `streaming: "partial"` lub `streaming: "quiet"` do edycji podglądu; następnie dodaj `blockStreaming: true` tylko wtedy, gdy chcesz również, aby ukończone bloki asystenta pozostały widoczne jako osobne komunikaty postępu.

Jeśli potrzebujesz standardowych powiadomień Matrix bez niestandardowych reguł push, użyj `streaming: "partial"` dla zachowania „najpierw podgląd” albo pozostaw `streaming` wyłączone dla dostarczania tylko gotowej odpowiedzi. Gdy `streaming: "off"`:

- `blockStreaming: true` wysyła każdy ukończony blok jako zwykłą powiadamiającą wiadomość Matrix.
- `blockStreaming: false` wysyła tylko końcową ukończoną odpowiedź jako zwykłą powiadamiającą wiadomość Matrix.

### Samohostowane reguły push dla cichych sfinalizowanych podglądów

Jeśli używasz własnej infrastruktury Matrix i chcesz, aby ciche podglądy powiadamiały tylko wtedy, gdy blok lub
końcowa odpowiedź są gotowe, ustaw `streaming: "quiet"` i dodaj regułę push per użytkownik dla sfinalizowanych edycji podglądu.

Zwykle jest to konfiguracja po stronie użytkownika-odbiorcy, a nie globalna zmiana konfiguracji homeservera:

Szybka mapa przed rozpoczęciem:

- użytkownik odbiorca = osoba, która powinna otrzymać powiadomienie
- użytkownik bot = konto Matrix OpenClaw wysyłające odpowiedź
- do poniższych wywołań API użyj tokenu dostępu użytkownika odbiorcy
- w regule push dopasuj `sender` do pełnego MXID użytkownika bota

1. Skonfiguruj OpenClaw tak, aby używał cichych podglądów:

```json5
{
  channels: {
    matrix: {
      streaming: "quiet",
    },
  },
}
```

2. Upewnij się, że konto odbiorcy już otrzymuje zwykłe powiadomienia push Matrix. Reguły cichych podglądów
   działają tylko wtedy, gdy ten użytkownik ma już działające pushery/urządzenia.

3. Pobierz token dostępu użytkownika odbiorcy.
   - Użyj tokenu użytkownika odbierającego, a nie tokenu bota.
   - Najłatwiej jest zwykle użyć ponownie tokenu istniejącej sesji klienta.
   - Jeśli potrzebujesz wygenerować nowy token, możesz zalogować się przez standardowe API Client-Server Matrix:

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

Jeśli to zwróci brak aktywnych pusherów/urządzeń, najpierw napraw zwykłe powiadomienia Matrix, a dopiero potem dodaj
poniższą regułę OpenClaw.

OpenClaw oznacza sfinalizowane edycje podglądu zawierające wyłącznie tekst za pomocą:

```json
{
  "com.openclaw.finalized_preview": true
}
```

5. Utwórz regułę push override dla każdego konta odbiorcy, które ma otrzymywać te powiadomienia:

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

- `https://matrix.example.org`: podstawowy URL twojego homeservera
- `$USER_ACCESS_TOKEN`: token dostępu użytkownika odbierającego
- `openclaw-finalized-preview-botname`: identyfikator reguły unikalny dla tego bota i tego użytkownika odbierającego
- `@bot:example.org`: MXID twojego bota Matrix OpenClaw, a nie MXID użytkownika odbierającego

Ważne w konfiguracjach z wieloma botami:

- Reguły push są kluczowane przez `ruleId`. Ponowne wykonanie `PUT` dla tego samego identyfikatora reguły aktualizuje tę jedną regułę.
- Jeśli jeden użytkownik odbierający ma otrzymywać powiadomienia od wielu kont botów Matrix OpenClaw, utwórz jedną regułę na bota z unikalnym identyfikatorem reguły dla każdego dopasowania nadawcy.
- Prosty wzorzec to `openclaw-finalized-preview-<botname>`, na przykład `openclaw-finalized-preview-ops` lub `openclaw-finalized-preview-support`.

Reguła jest oceniana względem nadawcy zdarzenia:

- uwierzytelnij się tokenem użytkownika odbierającego
- dopasuj `sender` do MXID bota OpenClaw

6. Sprawdź, czy reguła istnieje:

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

7. Przetestuj strumieniowaną odpowiedź. W trybie cichym pokój powinien pokazywać cichy szkic podglądu, a końcowa
   edycja w miejscu powinna wysłać powiadomienie po zakończeniu bloku lub tury.

Jeśli później trzeba będzie usunąć regułę, usuń ten sam identyfikator reguły przy użyciu tokenu użytkownika odbierającego:

```bash
curl -sS -X DELETE \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

Uwagi:

- Utwórz regułę przy użyciu tokenu dostępu użytkownika odbierającego, a nie tokenu bota.
- Nowe zdefiniowane przez użytkownika reguły `override` są wstawiane przed domyślnymi regułami wyciszającymi, więc nie jest potrzebny dodatkowy parametr kolejności.
- Dotyczy to tylko edycji podglądu zawierających wyłącznie tekst, które OpenClaw może bezpiecznie sfinalizować w miejscu. Fallbacki dla multimediów i fallbacki dla starych podglądów nadal używają zwykłego dostarczania Matrix.
- Jeśli `GET /_matrix/client/v3/pushers` nie pokazuje żadnych pusherów, użytkownik nie ma jeszcze działającego dostarczania powiadomień push Matrix dla tego konta/urządzenia.

#### Synapse

W przypadku Synapse powyższa konfiguracja zwykle sama w sobie wystarcza:

- Nie jest wymagana żadna specjalna zmiana `homeserver.yaml` dla sfinalizowanych powiadomień podglądu OpenClaw.
- Jeśli twoje wdrożenie Synapse już wysyła zwykłe powiadomienia push Matrix, token użytkownika + wywołanie `pushrules` powyżej to główny krok konfiguracji.
- Jeśli uruchamiasz Synapse za reverse proxy lub workerami, upewnij się, że `/_matrix/client/.../pushrules/` poprawnie trafia do Synapse.
- Jeśli używasz workerów Synapse, upewnij się, że pushery działają prawidłowo. Dostarczanie push jest obsługiwane przez proces główny albo `synapse.app.pusher` / skonfigurowane workery pusherów.

#### Tuwunel

W przypadku Tuwunel użyj tego samego przepływu konfiguracji i wywołania API `pushrules`, które pokazano powyżej:

- Nie jest wymagana żadna konfiguracja specyficzna dla Tuwunel dla samego znacznika sfinalizowanego podglądu.
- Jeśli zwykłe powiadomienia Matrix już działają dla tego użytkownika, token użytkownika + wywołanie `pushrules` powyżej to główny krok konfiguracji.
- Jeśli wygląda na to, że powiadomienia znikają, gdy użytkownik jest aktywny na innym urządzeniu, sprawdź, czy włączono `suppress_push_when_active`. Tuwunel dodał tę opcję w Tuwunel 1.4.2 12 września 2025 r. i może ona celowo wyciszać powiadomienia push na innych urządzeniach, gdy jedno urządzenie jest aktywne.

## Szyfrowanie i weryfikacja

W zaszyfrowanych pokojach (E2EE) wychodzące zdarzenia obrazów używają `thumbnail_file`, dzięki czemu podglądy obrazów są szyfrowane razem z pełnym załącznikiem. Niezaszyfrowane pokoje nadal używają zwykłego `thumbnail_url`. Nie jest wymagana żadna konfiguracja — wtyczka automatycznie wykrywa stan E2EE.

### Pokoje bot-do-bot

Domyślnie wiadomości Matrix od innych skonfigurowanych kont Matrix OpenClaw są ignorowane.

Użyj `allowBots`, jeśli celowo chcesz zezwolić na ruch Matrix między agentami:

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

- `allowBots: true` akceptuje wiadomości od innych skonfigurowanych kont botów Matrix w dozwolonych pokojach i wiadomościach prywatnych.
- `allowBots: "mentions"` akceptuje te wiadomości tylko wtedy, gdy w pokojach wyraźnie wspominają tego bota. Wiadomości prywatne są nadal dozwolone.
- `groups.<room>.allowBots` nadpisuje ustawienie na poziomie konta dla jednego pokoju.
- OpenClaw nadal ignoruje wiadomości od tego samego identyfikatora użytkownika Matrix, aby uniknąć pętli odpowiedzi do samego siebie.
- Matrix nie udostępnia tu natywnej flagi bota; OpenClaw traktuje „autorstwo bota” jako „wysłane przez inne skonfigurowane konto Matrix na tym gateway OpenClaw”.

Włączając ruch bot-do-bot we współdzielonych pokojach, używaj ścisłych allowlist pokoi i wymogów wzmianki.

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

Sprawdź stan weryfikacji:

```bash
openclaw matrix verify status
```

Szczegółowy stan (pełna diagnostyka):

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

Obsługa wielu kont: użyj `channels.matrix.accounts` z poświadczeniami per konto i opcjonalnym `name`. Zobacz [Dokumentacja konfiguracji](/pl/gateway/configuration-reference#multi-account-all-channels), aby poznać wspólny wzorzec.

Szczegółowa diagnostyka bootstrap:

```bash
openclaw matrix verify bootstrap --verbose
```

Wymuś reset tożsamości cross-signing przed bootstrapem:

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

Sprawdź stan kopii zapasowej kluczy pokojów:

```bash
openclaw matrix verify backup status
```

Szczegółowa diagnostyka stanu kopii zapasowej:

```bash
openclaw matrix verify backup status --verbose
```

Przywróć klucze pokoi z kopii zapasowej na serwerze:

```bash
openclaw matrix verify backup restore
```

Szczegółowa diagnostyka przywracania:

```bash
openclaw matrix verify backup restore --verbose
```

Usuń bieżącą kopię zapasową na serwerze i utwórz nową bazę kopii zapasowej. Jeśli zapisany
klucz kopii zapasowej nie może zostać poprawnie załadowany, ten reset może również odtworzyć tajny magazyn, aby
przyszłe zimne starty mogły załadować nowy klucz kopii zapasowej:

```bash
openclaw matrix verify backup reset --yes
```

Wszystkie polecenia `verify` są domyślnie zwięzłe (łącznie z cichym wewnętrznym logowaniem SDK) i pokazują szczegółową diagnostykę tylko z `--verbose`.
Do skryptów użyj `--json`, aby uzyskać pełne dane wyjściowe czytelne maszynowo.

W konfiguracjach wielokontowych polecenia Matrix CLI używają niejawnego domyślnego konta Matrix, chyba że przekażesz `--account <id>`.
Jeśli skonfigurujesz wiele nazwanych kont, najpierw ustaw `channels.matrix.defaultAccount`, w przeciwnym razie te niejawne operacje CLI zatrzymają się i poproszą o jawny wybór konta.
Używaj `--account`, gdy chcesz, aby operacje weryfikacji lub urządzenia jawnie kierowały się na nazwane konto:

```bash
openclaw matrix verify status --account assistant
openclaw matrix verify backup restore --account assistant
openclaw matrix devices list --account assistant
```

Gdy szyfrowanie jest wyłączone lub niedostępne dla nazwanego konta, ostrzeżenia Matrix i błędy weryfikacji wskazują klucz konfiguracji tego konta, na przykład `channels.matrix.accounts.assistant.encryption`.

### Co oznacza „zweryfikowane”

OpenClaw traktuje to urządzenie Matrix jako zweryfikowane tylko wtedy, gdy zostało zweryfikowane przez twoją własną tożsamość cross-signing.
W praktyce `openclaw matrix verify status --verbose` pokazuje trzy sygnały zaufania:

- `Locally trusted`: to urządzenie jest zaufane tylko przez bieżącego klienta
- `Cross-signing verified`: SDK zgłasza to urządzenie jako zweryfikowane przez cross-signing
- `Signed by owner`: urządzenie jest podpisane przez twój własny klucz self-signing

`Verified by owner` przyjmuje wartość `yes` tylko wtedy, gdy obecna jest weryfikacja cross-signing lub podpis właściciela.
Samo lokalne zaufanie nie wystarcza, aby OpenClaw traktował urządzenie jako w pełni zweryfikowane.

### Co robi bootstrap

`openclaw matrix verify bootstrap` to polecenie naprawy i konfiguracji dla zaszyfrowanych kont Matrix.
Wykonuje kolejno wszystkie poniższe czynności:

- inicjuje tajny magazyn, ponownie używając istniejącego klucza odzyskiwania, jeśli to możliwe
- inicjuje cross-signing i przesyła brakujące publiczne klucze cross-signing
- próbuje oznaczyć i podpisać przez cross-signing bieżące urządzenie
- tworzy nową serwerową kopię zapasową kluczy pokoi, jeśli jeszcze nie istnieje

Jeśli homeserver wymaga interaktywnego uwierzytelniania do przesłania kluczy cross-signing, OpenClaw najpierw próbuje przesłania bez uwierzytelniania, potem z `m.login.dummy`, a następnie z `m.login.password`, gdy skonfigurowano `channels.matrix.password`.

Używaj `--force-reset-cross-signing` tylko wtedy, gdy celowo chcesz porzucić bieżącą tożsamość cross-signing i utworzyć nową.

Jeśli celowo chcesz porzucić bieżącą kopię zapasową kluczy pokoi i rozpocząć nową
bazę kopii zapasowej dla przyszłych wiadomości, użyj `openclaw matrix verify backup reset --yes`.
Rób to tylko wtedy, gdy akceptujesz, że niemożliwa do odzyskania stara zaszyfrowana historia pozostanie
niedostępna i że OpenClaw może odtworzyć tajny magazyn, jeśli nie da się bezpiecznie załadować
bieżącego sekretu kopii zapasowej.

### Świeża baza kopii zapasowej

Jeśli chcesz zachować działanie przyszłych zaszyfrowanych wiadomości i akceptujesz utratę nieodzyskiwalnej starej historii, uruchom po kolei te polecenia:

```bash
openclaw matrix verify backup reset --yes
openclaw matrix verify backup status --verbose
openclaw matrix verify status
```

Dodaj `--account <id>` do każdego polecenia, jeśli chcesz jawnie wskazać nazwane konto Matrix.

### Zachowanie przy uruchamianiu

Gdy `encryption: true`, Matrix domyślnie ustawia `startupVerification` na `"if-unverified"`.
Przy uruchamianiu, jeśli to urządzenie nadal nie jest zweryfikowane, Matrix poprosi o samoweryfikację w innym kliencie Matrix,
pominie duplikaty próśb, gdy jedna już oczekuje, i zastosuje lokalny cooldown przed ponowną próbą po restartach.
Domyślnie nieudane próby wysłania żądania są ponawiane szybciej niż udane utworzenie żądania.
Ustaw `startupVerification: "off"`, aby wyłączyć automatyczne żądania przy uruchamianiu, albo dostosuj `startupVerificationCooldownHours`,
jeśli chcesz krótsze lub dłuższe okno ponawiania.

Uruchamianie automatycznie wykonuje też konserwatywne przejście bootstrapu kryptograficznego.
To przejście najpierw próbuje ponownie użyć bieżącego tajnego magazynu i tożsamości cross-signing oraz unika resetowania cross-signing, chyba że uruchomisz jawny przepływ naprawy bootstrap.

Jeśli podczas uruchamiania zostanie wykryty uszkodzony stan bootstrapu i skonfigurowano `channels.matrix.password`, OpenClaw może spróbować bardziej rygorystycznej ścieżki naprawy.
Jeśli bieżące urządzenie jest już podpisane przez właściciela, OpenClaw zachowuje tę tożsamość zamiast resetować ją automatycznie.

Aktualizacja z poprzedniej publicznej wtyczki Matrix:

- OpenClaw automatycznie ponownie używa tego samego konta Matrix, tokenu dostępu i tożsamości urządzenia, jeśli to możliwe.
- Przed uruchomieniem jakichkolwiek zmian migracyjnych Matrix wymagających działania OpenClaw tworzy lub ponownie używa migawki odzyskiwania w `~/Backups/openclaw-migrations/`.
- Jeśli używasz wielu kont Matrix, ustaw `channels.matrix.defaultAccount` przed aktualizacją ze starego płaskiego układu store, aby OpenClaw wiedział, które konto ma otrzymać ten współdzielony starszy stan.
- Jeśli poprzednia wtyczka przechowywała lokalnie klucz odszyfrowywania kopii zapasowej kluczy pokoi Matrix, uruchamianie lub `openclaw doctor --fix` automatycznie zaimportują go do nowego przepływu klucza odzyskiwania.
- Jeśli token dostępu Matrix zmienił się po przygotowaniu migracji, uruchamianie skanuje teraz sąsiednie katalogi główne store haszowane tokenem w poszukiwaniu oczekującego starszego stanu przywracania, zanim zrezygnuje z automatycznego przywracania kopii zapasowej.
- Jeśli token dostępu Matrix zmieni się później dla tego samego konta, homeservera i użytkownika, OpenClaw będzie teraz preferował ponowne użycie najbardziej kompletnego istniejącego katalogu głównego store haszowanego tokenem zamiast rozpoczynać od pustego katalogu stanu Matrix.
- Przy następnym uruchomieniu gateway klucze pokoi z kopii zapasowej zostaną automatycznie przywrócone do nowego store kryptograficznego.
- Jeśli stara wtyczka miała tylko lokalne klucze pokoi, które nigdy nie zostały objęte kopią zapasową, OpenClaw wyświetli wyraźne ostrzeżenie. Tych kluczy nie można automatycznie wyeksportować z poprzedniego rust crypto store, więc część starej zaszyfrowanej historii może pozostać niedostępna do czasu ręcznego odzyskania.
- Zobacz [Migracja Matrix](/pl/install/migrating-matrix), aby poznać pełny przebieg aktualizacji, ograniczenia, polecenia odzyskiwania i typowe komunikaty migracyjne.

Zaszyfrowany stan środowiska wykonawczego jest zorganizowany w katalogach głównych haszowanych tokenem per konto i per użytkownik w
`~/.openclaw/matrix/accounts/<account>/<homeserver>__<user>/<token-hash>/`.
Ten katalog zawiera sync store (`bot-storage.json`), crypto store (`crypto/`),
plik klucza odzyskiwania (`recovery-key.json`), migawkę IndexedDB (`crypto-idb-snapshot.json`),
powiązania wątków (`thread-bindings.json`) oraz stan weryfikacji przy uruchamianiu (`startup-verification.json`),
gdy te funkcje są używane.
Gdy token się zmieni, ale tożsamość konta pozostaje taka sama, OpenClaw ponownie używa najlepszego istniejącego
katalogu głównego dla tej krotki konto/homeserver/użytkownik, dzięki czemu wcześniejszy stan synchronizacji, stan kryptograficzny, powiązania wątków
i stan weryfikacji przy uruchamianiu pozostają widoczne.

### Model Node crypto store

Matrix E2EE w tej wtyczce używa oficjalnej ścieżki Rust crypto `matrix-js-sdk` w Node.
Ta ścieżka oczekuje trwałości opartej na IndexedDB, jeśli chcesz, aby stan kryptograficzny przetrwał restarty.

OpenClaw obecnie zapewnia to w Node poprzez:

- użycie `fake-indexeddb` jako shimu API IndexedDB oczekiwanego przez SDK
- odtworzenie zawartości IndexedDB Rust crypto z `crypto-idb-snapshot.json` przed `initRustCrypto`
- zapis zaktualizowanej zawartości IndexedDB z powrotem do `crypto-idb-snapshot.json` po inicjalizacji i podczas działania
- serializowanie odtwarzania i zapisu migawki względem `crypto-idb-snapshot.json` przy użyciu doradczej blokady pliku, aby trwałość środowiska wykonawczego gateway i operacje konserwacyjne CLI nie ścigały się o ten sam plik migawki

To warstwa kompatybilności/przechowywania, a nie niestandardowa implementacja kryptografii.
Plik migawki zawiera wrażliwy stan środowiska wykonawczego i jest przechowywany z restrykcyjnymi uprawnieniami pliku.
W modelu bezpieczeństwa OpenClaw host gateway i lokalny katalog stanu OpenClaw już znajdują się wewnątrz granicy zaufanego operatora, więc jest to przede wszystkim kwestia trwałości operacyjnej, a nie osobna zdalna granica zaufania.

Planowane ulepszenie:

- dodać obsługę SecretRef dla trwałego materiału kluczy Matrix, tak aby klucze odzyskiwania i powiązane sekrety szyfrowania store mogły pochodzić z dostawców sekretów OpenClaw, a nie wyłącznie z plików lokalnych

## Zarządzanie profilem

Zaktualizuj własny profil Matrix dla wybranego konta za pomocą:

```bash
openclaw matrix profile set --name "OpenClaw Assistant"
openclaw matrix profile set --avatar-url https://cdn.example.org/avatar.png
```

Dodaj `--account <id>`, jeśli chcesz jawnie wskazać nazwane konto Matrix.

Matrix bezpośrednio akceptuje adresy URL awatarów `mxc://`. Gdy przekażesz adres URL awatara `http://` lub `https://`, OpenClaw najpierw prześle go do Matrix, a następnie zapisze rozpoznany adres `mxc://` z powrotem do `channels.matrix.avatarUrl` (lub do wybranego nadpisania konta).

## Automatyczne powiadomienia o weryfikacji

Matrix publikuje teraz powiadomienia o cyklu życia weryfikacji bezpośrednio w ścisłym pokoju DM weryfikacji jako wiadomości `m.notice`.
Obejmuje to:

- powiadomienia o żądaniu weryfikacji
- powiadomienia o gotowości do weryfikacji (z jawną wskazówką „Zweryfikuj przez emoji”)
- powiadomienia o rozpoczęciu i zakończeniu weryfikacji
- szczegóły SAS (emoji i liczby dziesiętne), gdy są dostępne

Przychodzące żądania weryfikacji z innego klienta Matrix są śledzone i automatycznie akceptowane przez OpenClaw.
W przepływach samoweryfikacji OpenClaw automatycznie uruchamia też przepływ SAS, gdy weryfikacja emoji staje się dostępna, i potwierdza swoją stronę.
W przypadku żądań weryfikacji z innego użytkownika/urządzenia Matrix OpenClaw automatycznie akceptuje żądanie, a następnie czeka, aż przepływ SAS będzie przebiegał normalnie.
Aby ukończyć weryfikację, nadal musisz porównać emoji lub dziesiętny SAS w swoim kliencie Matrix i tam potwierdzić „Są zgodne”.

OpenClaw nie akceptuje bezrefleksyjnie zduplikowanych przepływów zainicjowanych samodzielnie. Podczas uruchamiania pomijane jest tworzenie nowego żądania, jeśli żądanie samoweryfikacji już oczekuje.

Powiadomienia protokołu/systemu weryfikacji nie są przekazywane do pipeline czatu agenta, więc nie powodują `NO_REPLY`.

### Higiena urządzeń

Stare urządzenia Matrix zarządzane przez OpenClaw mogą gromadzić się na koncie i utrudniać zrozumienie zaufania w zaszyfrowanych pokojach.
Wyświetl je za pomocą:

```bash
openclaw matrix devices list
```

Usuń nieaktualne urządzenia Matrix zarządzane przez OpenClaw za pomocą:

```bash
openclaw matrix devices prune-stale
```

### Naprawa Direct Room

Jeśli stan wiadomości prywatnych się rozjedzie, OpenClaw może skończyć ze starymi mapowaniami `m.direct`, które wskazują stare pokoje solo zamiast aktywnego DM. Aby sprawdzić bieżące mapowanie dla partnera, użyj:

```bash
openclaw matrix direct inspect --user-id @alice:example.org
```

Aby je naprawić, użyj:

```bash
openclaw matrix direct repair --user-id @alice:example.org
```

Naprawa utrzymuje logikę specyficzną dla Matrix wewnątrz wtyczki:

- preferuje ścisły DM 1:1, który jest już zmapowany w `m.direct`
- w przeciwnym razie przechodzi do dowolnego aktualnie dołączonego ścisłego DM 1:1 z tym użytkownikiem
- jeśli nie istnieje zdrowy DM, tworzy nowy pokój direct i przepisuje `m.direct`, aby wskazywał na niego

Przepływ naprawy nie usuwa automatycznie starych pokoi. Wybiera tylko zdrowy DM i aktualizuje mapowanie, aby nowe wysyłki Matrix, powiadomienia o weryfikacji i inne przepływy wiadomości prywatnych znów trafiały do właściwego pokoju.

## Wątki

Matrix obsługuje natywne wątki Matrix zarówno dla automatycznych odpowiedzi, jak i wysyłek przez narzędzie wiadomości.

- `dm.sessionScope: "per-user"` (domyślnie) utrzymuje trasowanie DM Matrix w zakresie nadawcy, dzięki czemu wiele pokoi DM może współdzielić jedną sesję, gdy rozpoznają tego samego rozmówcę.
- `dm.sessionScope: "per-room"` izoluje każdy pokój DM Matrix do własnego klucza sesji, nadal używając zwykłych kontroli uwierzytelniania DM i allowlisty.
- Jawne powiązania konwersacji Matrix nadal mają pierwszeństwo przed `dm.sessionScope`, więc powiązane pokoje i wątki zachowują wybrany docelowy klucz sesji.
- `threadReplies: "off"` utrzymuje odpowiedzi na poziomie głównym i pozostawia przychodzące wiadomości w wątkach w sesji nadrzędnej.
- `threadReplies: "inbound"` odpowiada wewnątrz wątku tylko wtedy, gdy wiadomość przychodząca już znajdowała się w tym wątku.
- `threadReplies: "always"` utrzymuje odpowiedzi pokojowe w wątku zakotwiczonym w wiadomości wyzwalającej i kieruje tę konwersację przez odpowiadającą sesję o zakresie wątku od pierwszej wiadomości wyzwalającej.
- `dm.threadReplies` nadpisuje ustawienie najwyższego poziomu tylko dla wiadomości prywatnych. Na przykład możesz utrzymać izolację wątków w pokojach, a jednocześnie zachować płaskie wiadomości prywatne.
- Przychodzące wiadomości w wątkach zawierają wiadomość główną wątku jako dodatkowy kontekst agenta.
- Wysyłki przez narzędzie wiadomości teraz automatycznie dziedziczą bieżący wątek Matrix, gdy cel jest tym samym pokojem lub tym samym celem użytkownika DM, chyba że podano jawne `threadId`.
- Ponowne użycie docelowego użytkownika DM w tej samej sesji następuje tylko wtedy, gdy bieżące metadane sesji potwierdzają tego samego partnera DM na tym samym koncie Matrix; w przeciwnym razie OpenClaw wraca do normalnego trasowania w zakresie użytkownika.
- Gdy OpenClaw wykryje kolizję pokoju DM Matrix z innym pokojem DM w tej samej współdzielonej sesji DM Matrix, publikuje w tym pokoju jednorazowe `m.notice` z furtką `/focus`, gdy powiązania wątków są włączone, oraz z podpowiedzią `dm.sessionScope`.
- Powiązania wątków w czasie działania są obsługiwane w Matrix. `/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age` oraz związane z wątkiem `/acp spawn` działają teraz w pokojach i wiadomościach prywatnych Matrix.
- Główne `/focus` w pokoju/DM Matrix tworzy nowy wątek Matrix i wiąże go z docelową sesją, gdy `threadBindings.spawnSubagentSessions=true`.
- Uruchomienie `/focus` lub `/acp spawn --thread here` wewnątrz istniejącego wątku Matrix wiąże zamiast tego ten bieżący wątek.

## Powiązania konwersacji ACP

Pokoje Matrix, wiadomości prywatne i istniejące wątki Matrix można przekształcać w trwałe obszary robocze ACP bez zmiany powierzchni czatu.

Szybki przepływ dla operatora:

- Uruchom `/acp spawn codex --bind here` wewnątrz wiadomości prywatnej Matrix, pokoju lub istniejącego wątku, którego chcesz dalej używać.
- W głównej wiadomości prywatnej lub pokoju Matrix bieżąca wiadomość prywatna/pokój pozostaje powierzchnią czatu, a przyszłe wiadomości są kierowane do uruchomionej sesji ACP.
- W istniejącym wątku Matrix `--bind here` wiąże bieżący wątek w miejscu.
- `/new` i `/reset` resetują tę samą powiązaną sesję ACP w miejscu.
- `/acp close` zamyka sesję ACP i usuwa powiązanie.

Uwagi:

- `--bind here` nie tworzy podrzędnego wątku Matrix.
- `threadBindings.spawnAcpSessions` jest wymagane tylko dla `/acp spawn --thread auto|here`, gdy OpenClaw musi utworzyć lub powiązać podrzędny wątek Matrix.

### Konfiguracja Thread Binding

Matrix dziedziczy globalne ustawienia domyślne z `session.threadBindings` i obsługuje także nadpisania per kanał:

- `threadBindings.enabled`
- `threadBindings.idleHours`
- `threadBindings.maxAgeHours`
- `threadBindings.spawnSubagentSessions`
- `threadBindings.spawnAcpSessions`

Flagi uruchamiania powiązane z wątkami Matrix są opcjonalne:

- Ustaw `threadBindings.spawnSubagentSessions: true`, aby zezwolić głównemu `/focus` na tworzenie i wiązanie nowych wątków Matrix.
- Ustaw `threadBindings.spawnAcpSessions: true`, aby zezwolić `/acp spawn --thread auto|here` na wiązanie sesji ACP z wątkami Matrix.

## Reakcje

Matrix obsługuje wychodzące akcje reakcji, przychodzące powiadomienia o reakcjach oraz przychodzące reakcje potwierdzające.

- Narzędzia wychodzących reakcji są kontrolowane przez `channels["matrix"].actions.reactions`.
- `react` dodaje reakcję do konkretnego zdarzenia Matrix.
- `reactions` wyświetla bieżące podsumowanie reakcji dla konkretnego zdarzenia Matrix.
- `emoji=""` usuwa własne reakcje konta bota na tym zdarzeniu.
- `remove: true` usuwa tylko reakcję z określonym emoji z konta bota.

Zakres reakcji potwierdzających jest rozstrzygany w standardowej kolejności OpenClaw:

- `channels["matrix"].accounts.<accountId>.ackReaction`
- `channels["matrix"].ackReaction`
- `messages.ackReaction`
- fallback emoji tożsamości agenta

Zakres reakcji potwierdzających jest rozstrzygany w tej kolejności:

- `channels["matrix"].accounts.<accountId>.ackReactionScope`
- `channels["matrix"].ackReactionScope`
- `messages.ackReactionScope`

Tryb powiadomień o reakcjach jest rozstrzygany w tej kolejności:

- `channels["matrix"].accounts.<accountId>.reactionNotifications`
- `channels["matrix"].reactionNotifications`
- domyślnie: `own`

Bieżące zachowanie:

- `reactionNotifications: "own"` przekazuje dodane zdarzenia `m.reaction`, gdy dotyczą wiadomości Matrix napisanych przez bota.
- `reactionNotifications: "off"` wyłącza systemowe zdarzenia reakcji.
- Usunięcia reakcji nadal nie są syntetyzowane do zdarzeń systemowych, ponieważ Matrix udostępnia je jako redactions, a nie jako osobne usunięcia `m.reaction`.

## Kontekst historii

- `channels.matrix.historyLimit` określa, ile ostatnich wiadomości z pokoju jest uwzględnianych jako `InboundHistory`, gdy wiadomość z pokoju Matrix wyzwala agenta.
- Wartość zapasowa pochodzi z `messages.groupChat.historyLimit`. Ustaw `0`, aby wyłączyć.
- Historia pokoju Matrix jest ograniczona do pokoju. Wiadomości prywatne nadal używają zwykłej historii sesji.
- Historia pokoju Matrix działa tylko dla oczekujących wiadomości: OpenClaw buforuje wiadomości z pokoju, które jeszcze nie wywołały odpowiedzi, a następnie robi migawkę tego okna, gdy pojawi się wzmianka lub inny wyzwalacz.
- Bieżąca wiadomość wyzwalająca nie jest uwzględniana w `InboundHistory`; pozostaje w głównej treści przychodzącej dla tej tury.
- Ponowne próby dla tego samego zdarzenia Matrix ponownie używają oryginalnej migawki historii zamiast przesuwać ją do nowszych wiadomości z pokoju.

## Widoczność kontekstu

Matrix obsługuje współdzieloną kontrolę `contextVisibility` dla uzupełniającego kontekstu pokoju, takiego jak pobrany tekst odpowiedzi, korzenie wątków i oczekująca historia.

- `contextVisibility: "all"` jest ustawieniem domyślnym. Kontekst uzupełniający jest zachowywany bez zmian.
- `contextVisibility: "allowlist"` filtruje kontekst uzupełniający do nadawców dozwolonych przez aktywne sprawdzenia allowlisty pokoju/użytkownika.
- `contextVisibility: "allowlist_quote"` działa jak `allowlist`, ale nadal zachowuje jedną jawną cytowaną odpowiedź.

To ustawienie wpływa na widoczność kontekstu uzupełniającego, a nie na to, czy sama wiadomość przychodząca może wywołać odpowiedź.
Autoryzacja wyzwalacza nadal wynika z ustawień `groupPolicy`, `groups`, `groupAllowFrom` oraz zasad DM.

## Przykład zasad dla wiadomości prywatnych i pokoi

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

Zobacz [Grupy](/pl/channels/groups), aby poznać zachowanie ograniczania do wzmianek i allowlist.

Przykład parowania dla wiadomości prywatnych Matrix:

```bash
openclaw pairing list matrix
openclaw pairing approve matrix <CODE>
```

Jeśli niezatwierdzony użytkownik Matrix nadal wysyła do ciebie wiadomości przed zatwierdzeniem, OpenClaw ponownie używa tego samego oczekującego kodu parowania i może ponownie wysłać odpowiedź przypominającą po krótkim czasie cooldown zamiast tworzyć nowy kod.

Zobacz [Parowanie](/pl/channels/pairing), aby poznać wspólny przepływ parowania wiadomości prywatnych i układ przechowywania.

## Zatwierdzenia exec

Matrix może działać jako klient zatwierdzania exec dla konta Matrix.

- `channels.matrix.execApprovals.enabled`
- `channels.matrix.execApprovals.approvers` (opcjonalne; fallback do `channels.matrix.dm.allowFrom`)
- `channels.matrix.execApprovals.target` (`dm` | `channel` | `both`, domyślnie: `dm`)
- `channels.matrix.execApprovals.agentFilter`
- `channels.matrix.execApprovals.sessionFilter`

Zatwierdzający muszą być identyfikatorami użytkowników Matrix, takimi jak `@owner:example.org`. Matrix automatycznie włącza natywne zatwierdzenia exec, gdy `enabled` nie jest ustawione albo ma wartość `"auto"` i można rozpoznać co najmniej jednego zatwierdzającego — albo z `execApprovals.approvers`, albo z `channels.matrix.dm.allowFrom`. Ustaw `enabled: false`, aby jawnie wyłączyć Matrix jako natywnego klienta zatwierdzania. W przeciwnym razie żądania zatwierdzenia wracają do innych skonfigurowanych ścieżek zatwierdzania albo do zasad fallback zatwierdzania exec.

Natywne trasowanie Matrix dotyczy obecnie tylko exec:

- `channels.matrix.execApprovals.*` kontroluje natywne trasowanie DM/kanału tylko dla zatwierdzeń exec.
- Zatwierdzenia wtyczek nadal używają współdzielonego `/approve` w tym samym czacie oraz ewentualnego skonfigurowanego przekazywania `approvals.plugin`.
- Matrix może nadal ponownie używać `channels.matrix.dm.allowFrom` do autoryzacji zatwierdzeń wtyczek, gdy może bezpiecznie rozpoznać zatwierdzających, ale nie udostępnia osobnej natywnej ścieżki rozsyłania zatwierdzeń wtyczek do DM/kanału.

Zasady dostarczania:

- `target: "dm"` wysyła prośby o zatwierdzenie do wiadomości prywatnych zatwierdzających
- `target: "channel"` wysyła prośbę z powrotem do źródłowego pokoju lub wiadomości prywatnej Matrix
- `target: "both"` wysyła do wiadomości prywatnych zatwierdzających oraz do źródłowego pokoju lub wiadomości prywatnej Matrix

Prompty zatwierdzenia Matrix inicjalizują skróty reakcji na głównej wiadomości zatwierdzenia:

- `✅` = zezwól jednorazowo
- `❌` = odmów
- `♾️` = zezwól zawsze, gdy taka decyzja jest dozwolona przez obowiązującą politykę exec

Zatwierdzający mogą zareagować na tę wiadomość lub użyć zapasowych poleceń z ukośnikiem: `/approve <id> allow-once`, `/approve <id> allow-always` albo `/approve <id> deny`.

Tylko rozpoznani zatwierdzający mogą zatwierdzać lub odmawiać. Dostarczanie do kanału obejmuje tekst polecenia, więc włączaj `channel` lub `both` tylko w zaufanych pokojach.

Prompty zatwierdzenia Matrix ponownie używają współdzielonego planera zatwierdzeń rdzenia. Natywna powierzchnia specyficzna dla Matrix jest tylko transportem dla zatwierdzeń exec: trasowaniem pokoju/DM oraz zachowaniem wysyłania/aktualizacji/usuwania wiadomości.

Nadpisanie per konto:

- `channels.matrix.accounts.<account>.execApprovals`

Powiązana dokumentacja: [Zatwierdzenia exec](/pl/tools/exec-approvals)

## Przykład wielu kont

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

Wartości najwyższego poziomu `channels.matrix` działają jako ustawienia domyślne dla nazwanych kont, chyba że konto je nadpisze.
Możesz ograniczyć dziedziczone wpisy pokoi do jednego konta Matrix za pomocą `groups.<room>.account` (lub starszego `rooms.<room>.account`).
Wpisy bez `account` pozostają współdzielone przez wszystkie konta Matrix, a wpisy z `account: "default"` nadal działają, gdy konto domyślne jest skonfigurowane bezpośrednio na najwyższym poziomie `channels.matrix.*`.
Częściowe współdzielone domyślne ustawienia uwierzytelniania same w sobie nie tworzą osobnego niejawnego konta domyślnego. OpenClaw syntetyzuje najwyższy poziom konta `default` tylko wtedy, gdy to konto domyślne ma świeże uwierzytelnianie (`homeserver` plus `accessToken` albo `homeserver` plus `userId` i `password`); nazwane konta mogą nadal pozostać wykrywalne z `homeserver` plus `userId`, gdy zbuforowane poświadczenia później spełnią wymagania uwierzytelniania.
Jeśli Matrix ma już dokładnie jedno nazwane konto albo `defaultAccount` wskazuje istniejący klucz nazwanego konta, promowanie naprawy/konfiguracji z trybu jednego konta do wielu kont zachowuje to konto zamiast tworzyć nowy wpis `accounts.default`. Do promowanego konta przenoszone są tylko klucze uwierzytelniania/bootstrap Matrix; współdzielone klucze polityk dostarczania pozostają na najwyższym poziomie.
Ustaw `defaultAccount`, jeśli chcesz, aby OpenClaw preferował jedno nazwane konto Matrix do niejawnego trasowania, sondowania i operacji CLI.
Jeśli skonfigurujesz wiele nazwanych kont, ustaw `defaultAccount` albo przekazuj `--account <id>` dla poleceń CLI, które opierają się na niejawnym wyborze konta.
Przekaż `--account <id>` do `openclaw matrix verify ...` i `openclaw matrix devices ...`, gdy chcesz nadpisać ten niejawny wybór dla pojedynczego polecenia.

## Prywatne/LAN homeservery

Domyślnie OpenClaw blokuje prywatne/wewnętrzne homeservery Matrix dla ochrony SSRF, chyba że
jawnie włączysz to per konto.

Jeśli twój homeserver działa na localhost, adresie IP LAN/Tailscale lub wewnętrznej nazwie hosta, włącz
`allowPrivateNetwork` dla tego konta Matrix:

```json5
{
  channels: {
    matrix: {
      homeserver: "http://matrix-synapse:8008",
      allowPrivateNetwork: true,
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

To włączenie dotyczy tylko zaufanych prywatnych/wewnętrznych celów. Publiczne nieszyfrowane homeservery, takie jak
`http://matrix.example.org:8008`, nadal są blokowane. Gdy to możliwe, preferuj `https://`.

## Proxy dla ruchu Matrix

Jeśli twoje wdrożenie Matrix wymaga jawnego wychodzącego proxy HTTP(S), ustaw `channels.matrix.proxy`:

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

Nazwane konta mogą nadpisywać domyślne ustawienie najwyższego poziomu przez `channels.matrix.accounts.<id>.proxy`.
OpenClaw używa tego samego ustawienia proxy dla ruchu Matrix w czasie działania i dla sond stanu konta.

## Rozpoznawanie celów

Matrix akceptuje następujące formy celu wszędzie tam, gdzie OpenClaw prosi o cel pokoju lub użytkownika:

- Użytkownicy: `@user:server`, `user:@user:server` lub `matrix:user:@user:server`
- Pokoje: `!room:server`, `room:!room:server` lub `matrix:room:!room:server`
- Aliasy: `#alias:server`, `channel:#alias:server` lub `matrix:channel:#alias:server`

Wyszukiwanie w katalogu na żywo używa zalogowanego konta Matrix:

- Wyszukiwanie użytkowników odpytuje katalog użytkowników Matrix na tym homeserverze.
- Wyszukiwanie pokoi bezpośrednio akceptuje jawne identyfikatory pokoi i aliasy, a następnie przechodzi do wyszukiwania nazw dołączonych pokoi dla tego konta.
- Wyszukiwanie nazw dołączonych pokoi jest oparte na best-effort. Jeśli nie da się rozpoznać nazwy pokoju do identyfikatora lub aliasu, jest ignorowana przez rozpoznawanie allowlisty w czasie działania.

## Dokumentacja konfiguracji

- `enabled`: włącza lub wyłącza kanał.
- `name`: opcjonalna etykieta konta.
- `defaultAccount`: preferowany identyfikator konta, gdy skonfigurowano wiele kont Matrix.
- `homeserver`: URL homeservera, na przykład `https://matrix.example.org`.
- `allowPrivateNetwork`: zezwala temu kontu Matrix na łączenie się z prywatnymi/wewnętrznymi homeserverami. Włącz to, gdy homeserver rozpoznaje się do `localhost`, adresu IP LAN/Tailscale albo wewnętrznego hosta, takiego jak `matrix-synapse`.
- `proxy`: opcjonalny URL proxy HTTP(S) dla ruchu Matrix. Nazwane konta mogą nadpisywać domyślne ustawienie najwyższego poziomu własnym `proxy`.
- `userId`: pełny identyfikator użytkownika Matrix, na przykład `@bot:example.org`.
- `accessToken`: token dostępu do uwierzytelniania opartego na tokenie. Zarówno wartości w postaci zwykłego tekstu, jak i wartości SecretRef są obsługiwane dla `channels.matrix.accessToken` oraz `channels.matrix.accounts.<id>.accessToken` w dostawcach env/file/exec. Zobacz [Zarządzanie sekretami](/pl/gateway/secrets).
- `password`: hasło do logowania opartego na haśle. Obsługiwane są wartości zwykłego tekstu i SecretRef.
- `deviceId`: jawny identyfikator urządzenia Matrix.
- `deviceName`: nazwa wyświetlana urządzenia przy logowaniu hasłem.
- `avatarUrl`: zapisany URL własnego awatara do synchronizacji profilu i aktualizacji `set-profile`.
- `initialSyncLimit`: limit zdarzeń synchronizacji przy uruchamianiu.
- `encryption`: włącza E2EE.
- `allowlistOnly`: wymusza zachowanie tylko według allowlisty dla wiadomości prywatnych i pokoi.
- `allowBots`: zezwala na wiadomości od innych skonfigurowanych kont Matrix OpenClaw (`true` lub `"mentions"`).
- `groupPolicy`: `open`, `allowlist` lub `disabled`.
- `contextVisibility`: tryb widoczności uzupełniającego kontekstu pokoju (`all`, `allowlist`, `allowlist_quote`).
- `groupAllowFrom`: allowlista identyfikatorów użytkowników dla ruchu w pokojach.
- Wpisy `groupAllowFrom` powinny być pełnymi identyfikatorami użytkowników Matrix. Nierozpoznane nazwy są ignorowane w czasie działania.
- `historyLimit`: maksymalna liczba wiadomości z pokoju uwzględnianych jako kontekst historii grupy. Fallback do `messages.groupChat.historyLimit`. Ustaw `0`, aby wyłączyć.
- `replyToMode`: `off`, `first` lub `all`.
- `markdown`: opcjonalna konfiguracja renderowania Markdown dla wychodzącego tekstu Matrix.
- `streaming`: `off` (domyślnie), `partial`, `quiet`, `true` lub `false`. `partial` i `true` włączają aktualizacje szkicu „najpierw podgląd” przy użyciu zwykłych wiadomości tekstowych Matrix. `quiet` używa niepowiadamiających notice podglądu dla samohostowanych konfiguracji reguł push.
- `blockStreaming`: `true` włącza osobne komunikaty postępu dla ukończonych bloków asystenta, gdy aktywne jest strumieniowanie szkicu podglądu.
- `threadReplies`: `off`, `inbound` lub `always`.
- `threadBindings`: nadpisania per kanał dla trasowania i cyklu życia sesji związanych z wątkami.
- `startupVerification`: tryb automatycznego żądania samoweryfikacji przy uruchamianiu (`if-unverified`, `off`).
- `startupVerificationCooldownHours`: czas cooldown przed ponowną próbą automatycznych żądań weryfikacji przy uruchamianiu.
- `textChunkLimit`: rozmiar fragmentu wiadomości wychodzącej.
- `chunkMode`: `length` lub `newline`.
- `responsePrefix`: opcjonalny prefiks wiadomości dla odpowiedzi wychodzących.
- `ackReaction`: opcjonalne nadpisanie reakcji potwierdzającej dla tego kanału/konta.
- `ackReactionScope`: opcjonalne nadpisanie zakresu reakcji potwierdzającej (`group-mentions`, `group-all`, `direct`, `all`, `none`, `off`).
- `reactionNotifications`: tryb powiadomień o reakcjach przychodzących (`own`, `off`).
- `mediaMaxMb`: limit rozmiaru multimediów w MB dla obsługi multimediów Matrix. Dotyczy wysyłek wychodzących i przetwarzania multimediów przychodzących.
- `autoJoin`: zasada automatycznego dołączania do zaproszeń (`always`, `allowlist`, `off`). Domyślnie: `off`.
- `autoJoinAllowlist`: pokoje/aliasy dozwolone, gdy `autoJoin` ma wartość `allowlist`. Wpisy aliasów są podczas obsługi zaproszeń rozpoznawane do identyfikatorów pokoi; OpenClaw nie ufa stanowi aliasu deklarowanemu przez zapraszający pokój.
- `dm`: blok zasad DM (`enabled`, `policy`, `allowFrom`, `sessionScope`, `threadReplies`).
- Wpisy `dm.allowFrom` powinny być pełnymi identyfikatorami użytkowników Matrix, chyba że zostały już rozpoznane przez wyszukiwanie w katalogu na żywo.
- `dm.sessionScope`: `per-user` (domyślnie) lub `per-room`. Użyj `per-room`, jeśli chcesz, aby każdy pokój DM Matrix zachowywał oddzielny kontekst, nawet jeśli rozmówca jest ten sam.
- `dm.threadReplies`: nadpisanie zasad wątków tylko dla DM (`off`, `inbound`, `always`). Nadpisuje ustawienie najwyższego poziomu `threadReplies` zarówno dla umiejscowienia odpowiedzi, jak i izolacji sesji w wiadomościach prywatnych.
- `execApprovals`: natywne dostarczanie zatwierdzeń exec w Matrix (`enabled`, `approvers`, `target`, `agentFilter`, `sessionFilter`).
- `execApprovals.approvers`: identyfikatory użytkowników Matrix uprawnionych do zatwierdzania żądań exec. Opcjonalne, gdy `dm.allowFrom` już identyfikuje zatwierdzających.
- `execApprovals.target`: `dm | channel | both` (domyślnie: `dm`).
- `accounts`: nazwane nadpisania per konto. Wartości najwyższego poziomu `channels.matrix` działają jako ustawienia domyślne dla tych wpisów.
- `groups`: mapa zasad per pokój. Preferuj identyfikatory pokoi lub aliasy; nierozpoznane nazwy pokoi są ignorowane w czasie działania. Tożsamość sesji/grupy używa po rozpoznaniu stabilnego identyfikatora pokoju, podczas gdy etykiety czytelne dla człowieka nadal pochodzą z nazw pokoi.
- `groups.<room>.account`: ogranicza jeden dziedziczony wpis pokoju do konkretnego konta Matrix w konfiguracjach wielokontowych.
- `groups.<room>.allowBots`: nadpisanie na poziomie pokoju dla nadawców będących skonfigurowanymi botami (`true` lub `"mentions"`).
- `groups.<room>.users`: allowlista nadawców per pokój.
- `groups.<room>.tools`: nadpisania zezwalania/blokowania narzędzi per pokój.
- `groups.<room>.autoReply`: nadpisanie ograniczania do wzmianek na poziomie pokoju. `true` wyłącza wymóg wzmianki dla tego pokoju; `false` wymusza go ponownie.
- `groups.<room>.skills`: opcjonalny filtr Skills na poziomie pokoju.
- `groups.<room>.systemPrompt`: opcjonalny fragment system promptu na poziomie pokoju.
- `rooms`: starszy alias dla `groups`.
- `actions`: kontrola dostępu narzędzi per akcja (`messages`, `reactions`, `pins`, `profile`, `memberInfo`, `channelInfo`, `verification`).

## Powiązane

- [Przegląd kanałów](/pl/channels) — wszystkie obsługiwane kanały
- [Parowanie](/pl/channels/pairing) — uwierzytelnianie wiadomości prywatnych i przepływ parowania
- [Grupy](/pl/channels/groups) — zachowanie czatu grupowego i ograniczanie do wzmianek
- [Trasowanie kanałów](/pl/channels/channel-routing) — trasowanie sesji dla wiadomości
- [Bezpieczeństwo](/pl/gateway/security) — model dostępu i utwardzanie
