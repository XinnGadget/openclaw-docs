---
read_when:
    - Uruchamiasz harnessy programistyczne przez ACP
    - Konfigurujesz sesje ACP powiązane z konwersacją na kanałach wiadomości
    - Wiążesz konwersację w kanale wiadomości z trwałą sesją ACP
    - Rozwiązujesz problemy z backendem ACP i podłączeniem pluginów
    - Obsługujesz polecenia /acp z poziomu czatu
summary: Używaj sesji runtime ACP dla Codex, Claude Code, Cursor, Gemini CLI, OpenClaw ACP i innych agentów harness
title: Agenci ACP
x-i18n:
    generated_at: "2026-04-06T03:15:07Z"
    model: gpt-5.4
    provider: openai
    source_hash: 302f3fe25b1ffe0576592b6e0ad9e8a5781fa5702b31d508d9ba8908f7df33bd
    source_path: tools/acp-agents.md
    workflow: 15
---

# Agenci ACP

Sesje [Agent Client Protocol (ACP)](https://agentclientprotocol.com/) pozwalają OpenClaw uruchamiać zewnętrzne harnessy programistyczne (na przykład Pi, Claude Code, Codex, Cursor, Copilot, OpenClaw ACP, OpenCode, Gemini CLI i inne obsługiwane harnessy ACPX) przez plugin backendu ACP.

Jeśli poprosisz OpenClaw zwykłym językiem, aby „uruchomił to w Codex” albo „wystartował Claude Code w wątku”, OpenClaw powinien skierować takie żądanie do runtime ACP (a nie do natywnego runtime subagenta). Każde uruchomienie sesji ACP jest śledzone jako [zadanie w tle](/pl/automation/tasks).

Jeśli chcesz, aby Codex lub Claude Code łączyły się bezpośrednio jako zewnętrzny klient MCP
z istniejącymi konwersacjami kanałów OpenClaw, użyj
[`openclaw mcp serve`](/cli/mcp) zamiast ACP.

## Której strony potrzebuję?

W pobliżu są trzy powierzchnie, które łatwo pomylić:

| Chcesz...                                                                     | Użyj tego                   | Uwagi                                                                                                       |
| ---------------------------------------------------------------------------------- | -------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Uruchomić Codex, Claude Code, Gemini CLI lub inny zewnętrzny harness _przez_ OpenClaw | Ta strona: agenci ACP      | Sesje powiązane z czatem, `/acp spawn`, `sessions_spawn({ runtime: "acp" })`, zadania w tle, sterowanie runtime |
| Udostępnić sesję OpenClaw Gateway _jako_ serwer ACP dla edytora lub klienta      | [`openclaw acp`](/cli/acp) | Tryb mostu. IDE/klient komunikuje się z OpenClaw przez ACP przez stdio/WebSocket                                          |

## Czy to działa od razu po instalacji?

Zwykle tak.

- Świeże instalacje są teraz dostarczane z włączonym domyślnie wbudowanym pluginem runtime `acpx`.
- Wbudowany plugin `acpx` preferuje własne, przypięte binarium `acpx` lokalne dla pluginu.
- Przy uruchomieniu OpenClaw sprawdza to binarium i samodzielnie je naprawia, jeśli trzeba.
- Zacznij od `/acp doctor`, jeśli chcesz szybko sprawdzić gotowość.

Co nadal może się zdarzyć przy pierwszym użyciu:

- Adapter docelowego harnessu może zostać pobrany na żądanie przez `npx` przy pierwszym użyciu tego harnessu.
- Uwierzytelnianie dostawcy nadal musi istnieć na hoście dla tego harnessu.
- Jeśli host nie ma dostępu do npm/sieci, pobieranie adapterów przy pierwszym uruchomieniu może się nie udać, dopóki cache nie zostanie rozgrzany albo adapter nie zostanie zainstalowany w inny sposób.

Przykłady:

- `/acp spawn codex`: OpenClaw powinien być gotowy do uruchomienia `acpx`, ale adapter ACP dla Codex może nadal wymagać pobrania przy pierwszym użyciu.
- `/acp spawn claude`: podobnie z adapterem ACP dla Claude oraz uwierzytelnianiem po stronie Claude na tym hoście.

## Szybki przepływ dla operatora

Użyj tego, gdy chcesz praktycznego podręcznika `/acp`:

1. Uruchom sesję:
   - `/acp spawn codex --bind here`
   - `/acp spawn codex --mode persistent --thread auto`
2. Pracuj w powiązanej konwersacji lub wątku (albo wskaż jawnie klucz tej sesji).
3. Sprawdź stan runtime:
   - `/acp status`
4. Dostosuj opcje runtime według potrzeb:
   - `/acp model <provider/model>`
   - `/acp permissions <profile>`
   - `/acp timeout <seconds>`
5. Popchnij aktywną sesję bez zastępowania kontekstu:
   - `/acp steer tighten logging and continue`
6. Zatrzymaj pracę:
   - `/acp cancel` (zatrzymaj bieżącą turę), albo
   - `/acp close` (zamknij sesję i usuń powiązania)

## Szybki start dla ludzi

Przykłady naturalnych próśb:

- „Powiąż ten kanał Discord z Codex.”
- „Uruchom trwałą sesję Codex w wątku tutaj i utrzymuj skupienie.”
- „Uruchom to jako jednorazową sesję Claude Code ACP i podsumuj wynik.”
- „Powiąż ten czat iMessage z Codex i utrzymuj kolejne wiadomości w tym samym workspace.”
- „Użyj Gemini CLI do tego zadania w wątku, a potem utrzymuj kolejne wiadomości w tym samym wątku.”

Co OpenClaw powinien zrobić:

1. Wybrać `runtime: "acp"`.
2. Rozwiązać żądany cel harnessu (`agentId`, na przykład `codex`).
3. Jeśli żądane jest powiązanie bieżącej konwersacji, a aktywny kanał to obsługuje, powiązać sesję ACP z tą konwersacją.
4. W przeciwnym razie, jeśli żądane jest powiązanie z wątkiem, a bieżący kanał to obsługuje, powiązać sesję ACP z wątkiem.
5. Kierować kolejne powiązane wiadomości do tej samej sesji ACP aż do wycofania fokusu/zamknięcia/wygaśnięcia.

## ACP a subagenci

Używaj ACP, gdy chcesz zewnętrznego runtime harnessu. Używaj subagentów, gdy chcesz natywnych, delegowanych uruchomień OpenClaw.

| Obszar          | Sesja ACP                           | Uruchomienie subagenta                      |
| ------------- | ------------------------------------- | ---------------------------------- |
| Runtime       | Plugin backendu ACP (na przykład acpx) | Natywny runtime subagenta OpenClaw  |
| Klucz sesji   | `agent:<agentId>:acp:<uuid>`          | `agent:<agentId>:subagent:<uuid>`  |
| Główne polecenia | `/acp ...`                            | `/subagents ...`                   |
| Narzędzie uruchamiania    | `sessions_spawn` z `runtime:"acp"` | `sessions_spawn` (domyślny runtime) |

Zobacz też [Subagenci](/pl/tools/subagents).

## Jak ACP uruchamia Claude Code

Dla Claude Code przez ACP stos wygląda następująco:

1. Płaszczyzna sterowania sesją ACP OpenClaw
2. wbudowany plugin runtime `acpx`
3. Adapter Claude ACP
4. Mechanizmy runtime/sesji po stronie Claude

Ważne rozróżnienie:

- ACP Claude to sesja harnessu z kontrolkami ACP, wznawianiem sesji, śledzeniem zadań w tle i opcjonalnym powiązaniem z konwersacją/wątkiem.
  Dla operatorów praktyczna zasada jest taka:

- jeśli chcesz `/acp spawn`, sesji, które można powiązać, kontrolek runtime lub trwałej pracy harnessu: użyj ACP

## Sesje powiązane

### Powiązania bieżącej konwersacji

Użyj `/acp spawn <harness> --bind here`, gdy chcesz, aby bieżąca konwersacja stała się trwałym workspace ACP bez tworzenia podrzędnego wątku.

Zachowanie:

- OpenClaw nadal zarządza transportem kanału, uwierzytelnianiem, bezpieczeństwem i dostarczaniem.
- Bieżąca konwersacja jest przypinana do uruchomionego klucza sesji ACP.
- Kolejne wiadomości w tej konwersacji są kierowane do tej samej sesji ACP.
- `/new` i `/reset` resetują tę samą powiązaną sesję ACP w miejscu.
- `/acp close` zamyka sesję i usuwa powiązanie bieżącej konwersacji.

Co to oznacza w praktyce:

- `--bind here` zachowuje tę samą powierzchnię czatu. Na Discord bieżący kanał pozostaje bieżącym kanałem.
- `--bind here` może nadal utworzyć nową sesję ACP, jeśli uruchamiasz nową pracę. Powiązanie dołącza tę sesję do bieżącej konwersacji.
- `--bind here` samo w sobie nie tworzy podrzędnego wątku Discord ani tematu Telegram.
- Runtime ACP nadal może mieć własny katalog roboczy (`cwd`) lub workspace na dysku zarządzany przez backend. Ten runtime workspace jest oddzielny od powierzchni czatu i nie oznacza nowego wątku wiadomości.
- Jeśli uruchamiasz do innego agenta ACP i nie przekażesz `--cwd`, OpenClaw domyślnie dziedziczy workspace **agenta docelowego**, a nie żądającego.
- Jeśli ta dziedziczona ścieżka workspace nie istnieje (`ENOENT`/`ENOTDIR`), OpenClaw przechodzi na domyślny `cwd` backendu zamiast po cichu użyć niewłaściwego drzewa.
- Jeśli dziedziczony workspace istnieje, ale nie można uzyskać do niego dostępu (na przykład `EACCES`), uruchomienie zwraca rzeczywisty błąd dostępu zamiast odrzucać `cwd`.

Model mentalny:

- powierzchnia czatu: miejsce, w którym ludzie dalej rozmawiają (`kanał Discord`, `temat Telegram`, `czat iMessage`)
- sesja ACP: trwały stan runtime Codex/Claude/Gemini, do którego kieruje OpenClaw
- podrzędny wątek/temat: opcjonalna dodatkowa powierzchnia wiadomości tworzona tylko przez `--thread ...`
- runtime workspace: lokalizacja systemu plików, w której działa harness (`cwd`, checkout repozytorium, workspace backendu)

Przykłady:

- `/acp spawn codex --bind here`: zachowaj ten czat, uruchom lub podłącz sesję Codex ACP i kieruj do niej przyszłe wiadomości stąd
- `/acp spawn codex --thread auto`: OpenClaw może utworzyć podrzędny wątek/temat i powiązać z nim sesję ACP
- `/acp spawn codex --bind here --cwd /workspace/repo`: to samo powiązanie z czatem co wyżej, ale Codex działa w `/workspace/repo`

Obsługa powiązań bieżącej konwersacji:

- Kanały czatu/wiadomości, które deklarują obsługę powiązania bieżącej konwersacji, mogą używać `--bind here` przez współdzieloną ścieżkę powiązań konwersacji.
- Kanały z własną semantyką wątków/tematów nadal mogą zapewniać specyficzną dla kanału kanonikalizację za tym samym współdzielonym interfejsem.
- `--bind here` zawsze oznacza „powiąż bieżącą konwersację w miejscu”.
- Ogólne powiązania bieżącej konwersacji używają współdzielonego magazynu powiązań OpenClaw i przetrwają zwykłe restarty gateway.

Uwagi:

- `--bind here` i `--thread ...` wzajemnie się wykluczają w `/acp spawn`.
- Na Discord `--bind here` wiąże bieżący kanał lub wątek w miejscu. `spawnAcpSessions` jest wymagane tylko wtedy, gdy OpenClaw musi utworzyć podrzędny wątek dla `--thread auto|here`.
- Jeśli aktywny kanał nie udostępnia powiązań ACP bieżącej konwersacji, OpenClaw zwraca jasny komunikat o braku obsługi.
- `resume` i pytania o „nową sesję” dotyczą sesji ACP, a nie kanału. Możesz ponownie użyć albo zastąpić stan runtime bez zmiany bieżącej powierzchni czatu.

### Sesje powiązane z wątkiem

Gdy powiązania z wątkiem są włączone dla adaptera kanału, sesje ACP mogą być wiązane z wątkami:

- OpenClaw wiąże wątek z docelową sesją ACP.
- Kolejne wiadomości w tym wątku są kierowane do powiązanej sesji ACP.
- Wyjście ACP jest dostarczane z powrotem do tego samego wątku.
- Wycofanie fokusu/zamknięcie/archiwizacja/przekroczenie czasu bezczynności lub maksymalnego wieku usuwa powiązanie.

Obsługa powiązań z wątkiem zależy od adaptera. Jeśli aktywny adapter kanału nie obsługuje powiązań z wątkiem, OpenClaw zwraca jasny komunikat o braku obsługi lub niedostępności.

Wymagane flagi funkcji dla ACP powiązanego z wątkiem:

- `acp.enabled=true`
- `acp.dispatch.enabled` jest domyślnie włączone (ustaw `false`, aby wstrzymać dispatch ACP)
- Włączona flaga uruchamiania wątku ACP adaptera kanału (zależna od adaptera)
  - Discord: `channels.discord.threadBindings.spawnAcpSessions=true`
  - Telegram: `channels.telegram.threadBindings.spawnAcpSessions=true`

### Kanały obsługujące wątki

- Dowolny adapter kanału, który udostępnia możliwość wiązania sesji/wątków.
- Obecne wbudowane wsparcie:
  - wątki/kanały Discord
  - tematy Telegram (tematy forum w grupach/supergrupach i tematy DM)
- Kanały pluginów mogą dodać obsługę przez ten sam interfejs powiązań.

## Ustawienia specyficzne dla kanału

Dla nieefemerycznych przepływów pracy skonfiguruj trwałe powiązania ACP w wpisach najwyższego poziomu `bindings[]`.

### Model powiązań

- `bindings[].type="acp"` oznacza trwałe powiązanie konwersacji ACP.
- `bindings[].match` identyfikuje docelową konwersację:
  - Kanał lub wątek Discord: `match.channel="discord"` + `match.peer.id="<channelOrThreadId>"`
  - Temat forum Telegram: `match.channel="telegram"` + `match.peer.id="<chatId>:topic:<topicId>"`
  - Czat DM/grupowy BlueBubbles: `match.channel="bluebubbles"` + `match.peer.id="<handle|chat_id:*|chat_guid:*|chat_identifier:*>"`
    Preferuj `chat_id:*` lub `chat_identifier:*` dla stabilnych powiązań grupowych.
  - Czat DM/grupowy iMessage: `match.channel="imessage"` + `match.peer.id="<handle|chat_id:*|chat_guid:*|chat_identifier:*>"`
    Preferuj `chat_id:*` dla stabilnych powiązań grupowych.
- `bindings[].agentId` to identyfikator właściciela agenta OpenClaw.
- Opcjonalne nadpisania ACP znajdują się pod `bindings[].acp`:
  - `mode` (`persistent` albo `oneshot`)
  - `label`
  - `cwd`
  - `backend`

### Domyślne ustawienia runtime per-agent

Użyj `agents.list[].runtime`, aby zdefiniować domyślne ACP raz na agenta:

- `agents.list[].runtime.type="acp"`
- `agents.list[].runtime.acp.agent` (identyfikator harnessu, na przykład `codex` albo `claude`)
- `agents.list[].runtime.acp.backend`
- `agents.list[].runtime.acp.mode`
- `agents.list[].runtime.acp.cwd`

Kolejność pierwszeństwa nadpisań dla sesji ACP powiązanych:

1. `bindings[].acp.*`
2. `agents.list[].runtime.acp.*`
3. globalne ustawienia domyślne ACP (na przykład `acp.backend`)

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
      {
        id: "claude",
        runtime: {
          type: "acp",
          acp: { agent: "claude", backend: "acpx", mode: "persistent" },
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
    {
      type: "acp",
      agentId: "claude",
      match: {
        channel: "telegram",
        accountId: "default",
        peer: { kind: "group", id: "-1001234567890:topic:42" },
      },
      acp: { cwd: "/workspace/repo-b" },
    },
    {
      type: "route",
      agentId: "main",
      match: { channel: "discord", accountId: "default" },
    },
    {
      type: "route",
      agentId: "main",
      match: { channel: "telegram", accountId: "default" },
    },
  ],
  channels: {
    discord: {
      guilds: {
        "111111111111111111": {
          channels: {
            "222222222222222222": { requireMention: false },
          },
        },
      },
    },
    telegram: {
      groups: {
        "-1001234567890": {
          topics: { "42": { requireMention: false } },
        },
      },
    },
  },
}
```

Zachowanie:

- OpenClaw zapewnia istnienie skonfigurowanej sesji ACP przed użyciem.
- Wiadomości w tym kanale lub temacie są kierowane do skonfigurowanej sesji ACP.
- W powiązanych konwersacjach `/new` i `/reset` resetują ten sam klucz sesji ACP w miejscu.
- Tymczasowe powiązania runtime (na przykład utworzone przez przepływy fokusowania wątku) nadal obowiązują tam, gdzie istnieją.
- Dla uruchomień ACP między agentami bez jawnego `cwd` OpenClaw dziedziczy workspace agenta docelowego z konfiguracji agenta.
- Brakujące dziedziczone ścieżki workspace powodują przejście na domyślny `cwd` backendu; rzeczywiste błędy dostępu są zwracane jako błędy uruchomienia.

## Uruchamianie sesji ACP (interfejsy)

### Z `sessions_spawn`

Użyj `runtime: "acp"`, aby uruchomić sesję ACP z tury agenta albo wywołania narzędzia.

```json
{
  "task": "Open the repo and summarize failing tests",
  "runtime": "acp",
  "agentId": "codex",
  "thread": true,
  "mode": "session"
}
```

Uwagi:

- `runtime` domyślnie ma wartość `subagent`, więc dla sesji ACP ustaw jawnie `runtime: "acp"`.
- Jeśli `agentId` zostanie pominięte, OpenClaw użyje `acp.defaultAgent`, gdy jest skonfigurowane.
- `mode: "session"` wymaga `thread: true`, aby zachować trwałą powiązaną konwersację.

Szczegóły interfejsu:

- `task` (wymagane): początkowy prompt wysyłany do sesji ACP.
- `runtime` (wymagane dla ACP): musi mieć wartość `"acp"`.
- `agentId` (opcjonalne): identyfikator docelowego harnessu ACP. Jeśli ustawiono, używany jest fallback do `acp.defaultAgent`.
- `thread` (opcjonalne, domyślnie `false`): żądanie przepływu powiązania z wątkiem tam, gdzie jest obsługiwane.
- `mode` (opcjonalne): `run` (jednorazowe) albo `session` (trwałe).
  - domyślnie jest to `run`
  - jeśli `thread: true` i `mode` pominięto, OpenClaw może domyślnie przejść do zachowania trwałego zależnie od ścieżki runtime
  - `mode: "session"` wymaga `thread: true`
- `cwd` (opcjonalne): żądany katalog roboczy runtime (walidowany przez politykę backendu/runtime). Jeśli zostanie pominięty, uruchomienie ACP dziedziczy workspace agenta docelowego, jeśli jest skonfigurowany; brakujące dziedziczone ścieżki przechodzą na ustawienia domyślne backendu, a rzeczywiste błędy dostępu są zwracane.
- `label` (opcjonalne): etykieta dla operatora używana w tekście sesji/banera.
- `resumeSessionId` (opcjonalne): wznowienie istniejącej sesji ACP zamiast tworzenia nowej. Agent odtwarza historię konwersacji przez `session/load`. Wymaga `runtime: "acp"`.
- `streamTo` (opcjonalne): `"parent"` strumieniuje podsumowania postępu początkowego uruchomienia ACP z powrotem do sesji żądającej jako zdarzenia systemowe.
  - Gdy dostępne, akceptowane odpowiedzi zawierają `streamLogPath` wskazujące na plik JSONL logu ograniczony do sesji (`<sessionId>.acp-stream.jsonl`), który możesz śledzić dla pełnej historii przekazywania.

### Wznawianie istniejącej sesji

Użyj `resumeSessionId`, aby kontynuować poprzednią sesję ACP zamiast zaczynać od nowa. Agent odtwarza historię konwersacji przez `session/load`, więc podejmuje pracę z pełnym kontekstem tego, co było wcześniej.

```json
{
  "task": "Continue where we left off — fix the remaining test failures",
  "runtime": "acp",
  "agentId": "codex",
  "resumeSessionId": "<previous-session-id>"
}
```

Typowe przypadki użycia:

- Przekazanie sesji Codex z laptopa na telefon — powiedz agentowi, aby podjął pracę tam, gdzie została przerwana
- Kontynuacja sesji programistycznej rozpoczętej interaktywnie w CLI, teraz bez interfejsu przez agenta
- Podjęcie pracy przerwanej przez restart gateway albo przekroczenie czasu bezczynności

Uwagi:

- `resumeSessionId` wymaga `runtime: "acp"` — zwraca błąd, jeśli zostanie użyte z runtime subagenta.
- `resumeSessionId` przywraca historię konwersacji upstream ACP; `thread` i `mode` nadal obowiązują normalnie dla nowej sesji OpenClaw, którą tworzysz, więc `mode: "session"` nadal wymaga `thread: true`.
- Agent docelowy musi obsługiwać `session/load` (obsługują to Codex i Claude Code).
- Jeśli identyfikator sesji nie zostanie znaleziony, uruchomienie kończy się jawnym błędem — bez cichego przejścia do nowej sesji.

### Test smoke dla operatora

Użyj tego po wdrożeniu gateway, gdy chcesz szybko sprawdzić na żywo, czy uruchamianie ACP
naprawdę działa end-to-end, a nie tylko przechodzi testy jednostkowe.

Zalecana bramka:

1. Zweryfikuj wersję/commit wdrożonego gateway na hoście docelowym.
2. Potwierdź, że wdrożone źródło zawiera akceptację linii ACP w
   `src/gateway/sessions-patch.ts` (`subagent:* or acp:* sessions`).
3. Otwórz tymczasową sesję mostu ACPX do aktywnego agenta (na przykład
   `razor(main)` na `jpclawhq`).
4. Poproś tego agenta o wywołanie `sessions_spawn` z:
   - `runtime: "acp"`
   - `agentId: "codex"`
   - `mode: "run"`
   - zadanie: `Reply with exactly LIVE-ACP-SPAWN-OK`
5. Zweryfikuj, że agent raportuje:
   - `accepted=yes`
   - prawdziwe `childSessionKey`
   - brak błędu walidatora
6. Wyczyść tymczasową sesję mostu ACPX.

Przykładowy prompt dla aktywnego agenta:

```text
Use the sessions_spawn tool now with runtime: "acp", agentId: "codex", and mode: "run".
Set the task to: "Reply with exactly LIVE-ACP-SPAWN-OK".
Then report only: accepted=<yes/no>; childSessionKey=<value or none>; error=<exact text or none>.
```

Uwagi:

- Utrzymuj ten test smoke w `mode: "run"`, chyba że celowo testujesz
  trwałe sesje ACP powiązane z wątkiem.
- Nie wymagaj `streamTo: "parent"` dla podstawowej bramki. Ta ścieżka zależy od
  możliwości sesji żądającej i jest osobnym testem integracyjnym.
- Traktuj testowanie `mode: "session"` powiązanego z wątkiem jako drugi, bogatszy
  przebieg integracyjny z prawdziwego wątku Discord albo tematu Telegram.

## Zgodność z sandboxem

Sesje ACP obecnie działają w runtime hosta, a nie wewnątrz sandboxa OpenClaw.

Obecne ograniczenia:

- Jeśli sesja żądająca jest objęta sandboxem, uruchomienia ACP są blokowane zarówno dla `sessions_spawn({ runtime: "acp" })`, jak i `/acp spawn`.
  - Błąd: `Sandboxed sessions cannot spawn ACP sessions because runtime="acp" runs on the host. Use runtime="subagent" from sandboxed sessions.`
- `sessions_spawn` z `runtime: "acp"` nie obsługuje `sandbox: "require"`.
  - Błąd: `sessions_spawn sandbox="require" is unsupported for runtime="acp" because ACP sessions run outside the sandbox. Use runtime="subagent" or sandbox="inherit".`

Używaj `runtime: "subagent"`, gdy potrzebujesz wykonania wymuszanego przez sandbox.

### Z polecenia `/acp`

Użyj `/acp spawn`, gdy potrzebujesz jawnej kontroli operatora z czatu.

```text
/acp spawn codex --mode persistent --thread auto
/acp spawn codex --mode oneshot --thread off
/acp spawn codex --bind here
/acp spawn codex --thread here
```

Kluczowe flagi:

- `--mode persistent|oneshot`
- `--bind here|off`
- `--thread auto|here|off`
- `--cwd <absolute-path>`
- `--label <name>`

Zobacz [Polecenia ukośnikowe](/pl/tools/slash-commands).

## Rozwiązywanie celu sesji

Większość działań `/acp` akceptuje opcjonalny cel sesji (`session-key`, `session-id` albo `session-label`).

Kolejność rozwiązywania:

1. Jawny argument celu (albo `--session` dla `/acp steer`)
   - najpierw próba jako klucz
   - potem jako identyfikator sesji w formacie UUID
   - potem jako etykieta
2. Bieżące powiązanie wątku (jeśli ta konwersacja/wątek jest powiązana z sesją ACP)
3. Fallback do bieżącej sesji żądającej

Powiązania bieżącej konwersacji i powiązania wątków biorą udział w kroku 2.

Jeśli żaden cel nie zostanie rozwiązany, OpenClaw zwraca jasny błąd (`Unable to resolve session target: ...`).

## Tryby powiązania przy uruchamianiu

`/acp spawn` obsługuje `--bind here|off`.

| Tryb   | Zachowanie                                                               |
| ------ | ---------------------------------------------------------------------- |
| `here` | Powiąż bieżącą aktywną konwersację w miejscu; nie powiedzie się, jeśli żadna nie jest aktywna. |
| `off`  | Nie twórz powiązania bieżącej konwersacji.                          |

Uwagi:

- `--bind here` to najprostsza ścieżka operatora dla „uczyń ten kanał lub czat wspieranym przez Codex”.
- `--bind here` nie tworzy podrzędnego wątku.
- `--bind here` jest dostępne tylko na kanałach, które udostępniają obsługę powiązania bieżącej konwersacji.
- `--bind` i `--thread` nie mogą być łączone w tym samym wywołaniu `/acp spawn`.

## Tryby wątków przy uruchamianiu

`/acp spawn` obsługuje `--thread auto|here|off`.

| Tryb   | Zachowanie                                                                                            |
| ------ | --------------------------------------------------------------------------------------------------- |
| `auto` | W aktywnym wątku: powiąż ten wątek. Poza wątkiem: utwórz/powiąż podrzędny wątek tam, gdzie jest obsługiwane. |
| `here` | Wymagaj bieżącego aktywnego wątku; nie powiedzie się, jeśli nie jesteś wewnątrz wątku.                                                  |
| `off`  | Brak powiązania. Sesja uruchamia się bez powiązania.                                                                 |

Uwagi:

- Na powierzchniach bez obsługi wiązania wątków domyślne zachowanie jest w praktyce równe `off`.
- Uruchamianie z powiązaniem z wątkiem wymaga wsparcia polityki kanału:
  - Discord: `channels.discord.threadBindings.spawnAcpSessions=true`
  - Telegram: `channels.telegram.threadBindings.spawnAcpSessions=true`
- Użyj `--bind here`, gdy chcesz przypiąć bieżącą konwersację bez tworzenia podrzędnego wątku.

## Kontrolki ACP

Dostępna rodzina poleceń:

- `/acp spawn`
- `/acp cancel`
- `/acp steer`
- `/acp close`
- `/acp status`
- `/acp set-mode`
- `/acp set`
- `/acp cwd`
- `/acp permissions`
- `/acp timeout`
- `/acp model`
- `/acp reset-options`
- `/acp sessions`
- `/acp doctor`
- `/acp install`

`/acp status` pokazuje efektywne opcje runtime i, gdy są dostępne, zarówno identyfikatory sesji na poziomie runtime, jak i backendu.

Niektóre kontrolki zależą od możliwości backendu. Jeśli backend nie obsługuje danej kontrolki, OpenClaw zwraca jasny błąd o nieobsługiwanej kontrolce.

## Książka kucharska poleceń ACP

| Polecenie              | Co robi                                              | Przykład                                                       |
| -------------------- | --------------------------------------------------------- | ------------------------------------------------------------- |
| `/acp spawn`         | Tworzy sesję ACP; opcjonalne bieżące powiązanie lub powiązanie z wątkiem. | `/acp spawn codex --bind here --cwd /repo`                    |
| `/acp cancel`        | Anuluje turę w locie dla docelowej sesji.                 | `/acp cancel agent:codex:acp:<uuid>`                          |
| `/acp steer`         | Wysyła instrukcję sterującą do działającej sesji.                | `/acp steer --session support inbox prioritize failing tests` |
| `/acp close`         | Zamknij sesję i usuń powiązania z celami wątków.                  | `/acp close`                                                  |
| `/acp status`        | Pokaż backend, tryb, stan, opcje runtime, możliwości. | `/acp status`                                                 |
| `/acp set-mode`      | Ustaw tryb runtime dla docelowej sesji.                      | `/acp set-mode plan`                                          |
| `/acp set`           | Ogólny zapis opcji konfiguracji runtime.                      | `/acp set model openai/gpt-5.4`                               |
| `/acp cwd`           | Ustaw nadpisanie katalogu roboczego runtime.                   | `/acp cwd /Users/user/Projects/repo`                          |
| `/acp permissions`   | Ustaw profil polityki zatwierdzeń.                              | `/acp permissions strict`                                     |
| `/acp timeout`       | Ustaw limit czasu runtime (sekundy).                            | `/acp timeout 120`                                            |
| `/acp model`         | Ustaw nadpisanie modelu runtime.                               | `/acp model anthropic/claude-opus-4-6`                        |
| `/acp reset-options` | Usuń nadpisania opcji runtime sesji.                  | `/acp reset-options`                                          |
| `/acp sessions`      | Wylistuj ostatnie sesje ACP z magazynu.                      | `/acp sessions`                                               |
| `/acp doctor`        | Stan backendu, możliwości, możliwe do wykonania poprawki.           | `/acp doctor`                                                 |
| `/acp install`       | Wyświetl deterministyczne kroki instalacji i włączenia.             | `/acp install`                                                |

`/acp sessions` odczytuje magazyn dla bieżącej powiązanej albo żądającej sesji. Polecenia, które akceptują tokeny `session-key`, `session-id` lub `session-label`, rozwiązują cele przez wykrywanie sesji gateway, w tym niestandardowe korzenie `session.store` per-agent.

## Mapowanie opcji runtime

`/acp` ma wygodne polecenia i ogólny setter.

Operacje równoważne:

- `/acp model <id>` mapuje się na klucz konfiguracji runtime `model`.
- `/acp permissions <profile>` mapuje się na klucz konfiguracji runtime `approval_policy`.
- `/acp timeout <seconds>` mapuje się na klucz konfiguracji runtime `timeout`.
- `/acp cwd <path>` bezpośrednio aktualizuje nadpisanie `cwd` runtime.
- `/acp set <key> <value>` to ogólna ścieżka.
  - Przypadek specjalny: `key=cwd` używa ścieżki nadpisania `cwd`.
- `/acp reset-options` czyści wszystkie nadpisania runtime dla docelowej sesji.

## Obsługa harnessów acpx (obecnie)

Obecne wbudowane aliasy harnessów acpx:

- `claude`
- `codex`
- `copilot`
- `cursor` (Cursor CLI: `cursor-agent acp`)
- `droid`
- `gemini`
- `iflow`
- `kilocode`
- `kimi`
- `kiro`
- `openclaw`
- `opencode`
- `pi`
- `qwen`

Gdy OpenClaw używa backendu acpx, preferuj te wartości dla `agentId`, chyba że konfiguracja acpx definiuje własne aliasy agentów.
Jeśli Twoja lokalna instalacja Cursor nadal udostępnia ACP jako `agent acp`, nadpisz polecenie agenta `cursor` w konfiguracji acpx zamiast zmieniać wbudowaną wartość domyślną.

Bezpośrednie użycie CLI acpx może też kierować do dowolnych adapterów przez `--agent <command>`, ale ta surowa furtka obejścia jest funkcją CLI acpx (a nie normalnej ścieżki `agentId` OpenClaw).

## Wymagana konfiguracja

Bazowa konfiguracja ACP w core:

```json5
{
  acp: {
    enabled: true,
    // Optional. Default is true; set false to pause ACP dispatch while keeping /acp controls.
    dispatch: { enabled: true },
    backend: "acpx",
    defaultAgent: "codex",
    allowedAgents: [
      "claude",
      "codex",
      "copilot",
      "cursor",
      "droid",
      "gemini",
      "iflow",
      "kilocode",
      "kimi",
      "kiro",
      "openclaw",
      "opencode",
      "pi",
      "qwen",
    ],
    maxConcurrentSessions: 8,
    stream: {
      coalesceIdleMs: 300,
      maxChunkChars: 1200,
    },
    runtime: {
      ttlMinutes: 120,
    },
  },
}
```

Konfiguracja powiązania z wątkiem zależy od adaptera kanału. Przykład dla Discord:

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
        spawnAcpSessions: true,
      },
    },
  },
}
```

Jeśli uruchamianie ACP z powiązaniem z wątkiem nie działa, najpierw sprawdź flagę funkcji adaptera:

- Discord: `channels.discord.threadBindings.spawnAcpSessions=true`

Powiązania bieżącej konwersacji nie wymagają tworzenia podrzędnego wątku. Wymagają aktywnego kontekstu konwersacji i adaptera kanału, który udostępnia powiązania konwersacji ACP.

Zobacz [Dokumentacja konfiguracji](/pl/gateway/configuration-reference).

## Konfiguracja pluginu dla backendu acpx

Świeże instalacje są dostarczane z domyślnie włączonym wbudowanym pluginem runtime `acpx`, więc ACP
zwykle działa bez ręcznego kroku instalacji pluginu.

Zacznij od:

```text
/acp doctor
```

Jeśli wyłączyłeś `acpx`, zablokowałeś go przez `plugins.allow` / `plugins.deny` albo chcesz
przełączyć się na lokalny checkout deweloperski, użyj jawnej ścieżki pluginu:

```bash
openclaw plugins install acpx
openclaw config set plugins.entries.acpx.enabled true
```

Instalacja lokalnego workspace podczas developmentu:

```bash
openclaw plugins install ./path/to/local/acpx-plugin
```

Następnie zweryfikuj stan backendu:

```text
/acp doctor
```

### Konfiguracja polecenia i wersji acpx

Domyślnie wbudowany plugin backendu acpx (`acpx`) używa przypiętego binarium lokalnego dla pluginu:

1. Polecenie domyślnie wskazuje na lokalne dla pluginu `node_modules/.bin/acpx` w pakiecie pluginu ACPX.
2. Oczekiwana wersja domyślnie jest równa wersji przypiętej dla rozszerzenia.
3. Przy uruchomieniu OpenClaw od razu rejestruje backend ACP jako niegotowy.
4. Zadanie ensure w tle sprawdza `acpx --version`.
5. Jeśli lokalne dla pluginu binarium brakuje albo nie zgadza się wersja, uruchamia:
   `npm install --omit=dev --no-save acpx@<pinned>` i ponownie weryfikuje.

Możesz nadpisać polecenie/wersję w konfiguracji pluginu:

```json
{
  "plugins": {
    "entries": {
      "acpx": {
        "enabled": true,
        "config": {
          "command": "../acpx/dist/cli.js",
          "expectedVersion": "any"
        }
      }
    }
  }
}
```

Uwagi:

- `command` akceptuje ścieżkę bezwzględną, względną albo nazwę polecenia (`acpx`).
- Ścieżki względne są rozwiązywane względem katalogu workspace OpenClaw.
- `expectedVersion: "any"` wyłącza ścisłe dopasowanie wersji.
- Gdy `command` wskazuje niestandardowe binarium/ścieżkę, automatyczna instalacja lokalna dla pluginu jest wyłączona.
- Uruchamianie OpenClaw pozostaje nieblokujące, gdy działa kontrola stanu backendu w tle.

Zobacz [Pluginy](/pl/tools/plugin).

### Automatyczna instalacja zależności

Gdy instalujesz OpenClaw globalnie przez `npm install -g openclaw`, zależności runtime `acpx`
(binaria zależne od platformy) są instalowane automatycznie
przez hook postinstall. Jeśli automatyczna instalacja się nie powiedzie, gateway nadal uruchomi się
normalnie i zgłosi brakującą zależność przez `openclaw acp doctor`.

### Most MCP dla narzędzi pluginów

Domyślnie sesje ACPX **nie** udostępniają harnessowi ACP narzędzi zarejestrowanych przez pluginy OpenClaw.

Jeśli chcesz, aby agenci ACP, tacy jak Codex lub Claude Code, mogli wywoływać zainstalowane
narzędzia pluginów OpenClaw, takie jak recall/store pamięci, włącz dedykowany most:

```bash
openclaw config set plugins.entries.acpx.config.pluginToolsMcpBridge true
```

Co to robi:

- Wstrzykuje wbudowany serwer MCP o nazwie `openclaw-plugin-tools` do bootstrapu sesji ACPX.
- Udostępnia narzędzia pluginów już zarejestrowane przez zainstalowane i włączone pluginy OpenClaw.
- Pozostawia tę funkcję jako jawną i domyślnie wyłączoną.

Uwagi dotyczące bezpieczeństwa i zaufania:

- To rozszerza powierzchnię narzędzi harnessu ACP.
- Agenci ACP dostają dostęp tylko do narzędzi pluginów już aktywnych w gateway.
- Traktuj to jako tę samą granicę zaufania, co zezwolenie tym pluginom na wykonywanie działań w samym OpenClaw.
- Przejrzyj zainstalowane pluginy przed włączeniem.

Niestandardowe `mcpServers` nadal działają jak wcześniej. Wbudowany most dla narzędzi pluginów to
dodatkowa wygoda typu opt-in, a nie zamiennik ogólnej konfiguracji serwera MCP.

## Konfiguracja uprawnień

Sesje ACP działają nieinteraktywnie — nie ma TTY do zatwierdzania ani odrzucania promptów uprawnień zapisu plików i wykonywania poleceń powłoki. Plugin acpx udostępnia dwa klucze konfiguracji sterujące obsługą uprawnień:

Te uprawnienia harnessu ACPX są oddzielne od zatwierdzeń `exec` w OpenClaw i oddzielne od flag obejścia dostawcy backendu CLI, takich jak Claude CLI `--permission-mode bypassPermissions`. ACPX `approve-all` jest przełącznikiem awaryjnym na poziomie harnessu dla sesji ACP.

### `permissionMode`

Steruje tym, jakie operacje agent harnessu może wykonywać bez promptu.

| Wartość           | Zachowanie                                                  |
| --------------- | --------------------------------------------------------- |
| `approve-all`   | Automatycznie zatwierdzaj wszystkie zapisy plików i polecenia powłoki.          |
| `approve-reads` | Automatycznie zatwierdzaj tylko odczyty; zapis i exec wymagają promptów. |
| `deny-all`      | Odrzucaj wszystkie prompty uprawnień.                              |

### `nonInteractivePermissions`

Steruje tym, co się dzieje, gdy pojawiłby się prompt uprawnień, ale nie ma interaktywnego TTY (co w przypadku sesji ACP zachodzi zawsze).

| Wartość  | Zachowanie                                                          |
| ------ | ----------------------------------------------------------------- |
| `fail` | Przerwij sesję z `AcpRuntimeError`. **(domyślnie)**           |
| `deny` | Cicho odrzuć uprawnienie i kontynuuj (łagodna degradacja). |

### Konfiguracja

Ustaw przez konfigurację pluginu:

```bash
openclaw config set plugins.entries.acpx.config.permissionMode approve-all
openclaw config set plugins.entries.acpx.config.nonInteractivePermissions fail
```

Uruchom ponownie gateway po zmianie tych wartości.

> **Ważne:** OpenClaw obecnie domyślnie używa `permissionMode=approve-reads` i `nonInteractivePermissions=fail`. W nieinteraktywnych sesjach ACP każdy zapis lub `exec`, który uruchomi prompt uprawnień, może zakończyć się błędem `AcpRuntimeError: Permission prompt unavailable in non-interactive mode`.
>
> Jeśli chcesz ograniczyć uprawnienia, ustaw `nonInteractivePermissions` na `deny`, aby sesje degradowały się łagodnie zamiast się zawieszać.

## Rozwiązywanie problemów

| Objaw                                                                     | Prawdopodobna przyczyna                                                                    | Naprawa                                                                                                                                                               |
| --------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ACP runtime backend is not configured`                                     | Brak pluginu backendu albo jest wyłączony.                                             | Zainstaluj i włącz plugin backendu, a następnie uruchom `/acp doctor`.                                                                                                        |
| `ACP is disabled by policy (acp.enabled=false)`                             | ACP jest globalnie wyłączone.                                                          | Ustaw `acp.enabled=true`.                                                                                                                                           |
| `ACP dispatch is disabled by policy (acp.dispatch.enabled=false)`           | Dispatch z normalnych wiadomości wątku jest wyłączony.                                  | Ustaw `acp.dispatch.enabled=true`.                                                                                                                                  |
| `ACP agent "<id>" is not allowed by policy`                                 | Agent nie znajduje się na allowliście.                                                         | Użyj dozwolonego `agentId` albo zaktualizuj `acp.allowedAgents`.                                                                                                              |
| `Unable to resolve session target: ...`                                     | Nieprawidłowy token klucza/id/etykiety.                                                         | Uruchom `/acp sessions`, skopiuj dokładny klucz/etykietę i spróbuj ponownie.                                                                                                                 |
| `--bind here requires running /acp spawn inside an active ... conversation` | `--bind here` użyto bez aktywnej konwersacji, którą można powiązać.                     | Przejdź do docelowego czatu/kanału i spróbuj ponownie albo użyj uruchomienia bez powiązania.                                                                                                  |
| `Conversation bindings are unavailable for <channel>.`                      | Adapter nie ma możliwości powiązań ACP bieżącej konwersacji.                      | Użyj `/acp spawn ... --thread ...`, jeśli jest obsługiwane, skonfiguruj najwyższego poziomu `bindings[]` albo przejdź do obsługiwanego kanału.                                              |
| `--thread here requires running /acp spawn inside an active ... thread`     | `--thread here` użyto poza kontekstem wątku.                                  | Przejdź do docelowego wątku albo użyj `--thread auto`/`off`.                                                                                                               |
| `Only <user-id> can rebind this channel/conversation/thread.`               | Inny użytkownik jest właścicielem aktywnego celu powiązania.                                    | Powiąż ponownie jako właściciel albo użyj innej konwersacji lub wątku.                                                                                                        |
| `Thread bindings are unavailable for <channel>.`                            | Adapter nie ma możliwości powiązań wątków.                                        | Użyj `--thread off` albo przejdź do obsługiwanego adaptera/kanału.                                                                                                          |
| `Sandboxed sessions cannot spawn ACP sessions ...`                          | Runtime ACP działa po stronie hosta; sesja żądająca jest w sandboxie.                       | Użyj `runtime="subagent"` z sesji sandboxowanych albo uruchom ACP z sesji bez sandboxa.                                                                  |
| `sessions_spawn sandbox="require" is unsupported for runtime="acp" ...`     | Zażądano `sandbox="require"` dla runtime ACP.                                  | Użyj `runtime="subagent"` dla wymaganego sandboxingu albo użyj ACP z `sandbox="inherit"` z sesji bez sandboxa.                                               |
| Missing ACP metadata for bound session                                      | Nieaktualne/usunięte metadane sesji ACP.                                             | Odtwórz przez `/acp spawn`, a następnie ponownie powiąż/skup wątek.                                                                                                             |
| `AcpRuntimeError: Permission prompt unavailable in non-interactive mode`    | `permissionMode` blokuje zapis/exec w nieinteraktywnej sesji ACP.             | Ustaw `plugins.entries.acpx.config.permissionMode` na `approve-all` i uruchom ponownie gateway. Zobacz [Konfiguracja uprawnień](#konfiguracja-uprawnień).                 |
| Sesja ACP kończy się wcześnie z niewielką ilością danych wyjściowych                                  | Prompty uprawnień są blokowane przez `permissionMode`/`nonInteractivePermissions`. | Sprawdź logi gateway pod kątem `AcpRuntimeError`. Dla pełnych uprawnień ustaw `permissionMode=approve-all`; dla łagodnej degradacji ustaw `nonInteractivePermissions=deny`. |
| Sesja ACP zawiesza się bez końca po ukończeniu pracy                       | Proces harnessu zakończył się, ale sesja ACP nie zgłosiła zakończenia.             | Monitoruj przez `ps aux \| grep acpx`; ręcznie zabij nieaktualne procesy.                                                                                                |
