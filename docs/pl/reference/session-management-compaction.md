---
read_when:
    - Musisz debugować identyfikatory sesji, JSONL transkryptu lub pola sessions.json
    - Zmieniasz zachowanie auto-kompaktowania lub dodajesz porządki „przed kompaktowaniem”
    - Chcesz zaimplementować opróżnianie pamięci lub ciche tury systemowe
summary: 'Szczegółowe omówienie: magazyn sesji + transkrypty, cykl życia i mechanizmy (auto)kompaktowania'
title: Szczegółowe omówienie zarządzania sesjami
x-i18n:
    generated_at: "2026-04-06T03:12:52Z"
    model: gpt-5.4
    provider: openai
    source_hash: e0d8c2d30be773eac0424f7a4419ab055fdd50daac8bc654e7d250c891f2c3b8
    source_path: reference/session-management-compaction.md
    workflow: 15
---

# Zarządzanie sesjami i kompaktowanie (szczegółowe omówienie)

Ten dokument wyjaśnia, jak OpenClaw zarządza sesjami od początku do końca:

- **Routing sesji** (jak wiadomości przychodzące mapują się na `sessionKey`)
- **Magazyn sesji** (`sessions.json`) i co śledzi
- **Trwałość transkryptu** (`*.jsonl`) i jego struktura
- **Higiena transkryptu** (poprawki specyficzne dla providera przed uruchomieniami)
- **Limity kontekstu** (okno kontekstu a śledzone tokeny)
- **Kompaktowanie** (kompaktowanie ręczne + automatyczne) i gdzie podpiąć pracę przed kompaktowaniem
- **Ciche porządki** (np. zapisy pamięci, które nie powinny generować widocznego dla użytkownika wyjścia)

Jeśli najpierw chcesz zacząć od przeglądu na wyższym poziomie, zacznij od:

- [/concepts/session](/pl/concepts/session)
- [/concepts/compaction](/pl/concepts/compaction)
- [/concepts/memory](/pl/concepts/memory)
- [/concepts/memory-search](/pl/concepts/memory-search)
- [/concepts/session-pruning](/pl/concepts/session-pruning)
- [/reference/transcript-hygiene](/pl/reference/transcript-hygiene)

---

## Źródło prawdy: Gateway

OpenClaw został zaprojektowany wokół pojedynczego **procesu Gateway**, który zarządza stanem sesji.

- Interfejsy UI (aplikacja macOS, web Control UI, TUI) powinny pytać Gateway o listy sesji i liczniki tokenów.
- W trybie zdalnym pliki sesji znajdują się na hoście zdalnym; „sprawdzanie lokalnych plików na Macu” nie odzwierciedli tego, czego używa Gateway.

---

## Dwie warstwy trwałości

OpenClaw zapisuje sesje w dwóch warstwach:

1. **Magazyn sesji (`sessions.json`)**
   - Mapa klucz/wartość: `sessionKey -> SessionEntry`
   - Mały, mutowalny, bezpieczny do edycji (lub usuwania wpisów)
   - Śledzi metadane sesji (bieżący identyfikator sesji, ostatnią aktywność, przełączniki, liczniki tokenów itd.)

2. **Transkrypt (`<sessionId>.jsonl`)**
   - Transkrypt tylko do dopisywania ze strukturą drzewa (wpisy mają `id` + `parentId`)
   - Przechowuje faktyczną rozmowę + wywołania narzędzi + podsumowania kompaktowania
   - Służy do odbudowy kontekstu modelu dla przyszłych tur

---

## Lokalizacje na dysku

Per agent, na hoście Gateway:

- Magazyn: `~/.openclaw/agents/<agentId>/sessions/sessions.json`
- Transkrypty: `~/.openclaw/agents/<agentId>/sessions/<sessionId>.jsonl`
  - Sesje tematów Telegram: `.../<sessionId>-topic-<threadId>.jsonl`

OpenClaw rozwiązuje te ścieżki przez `src/config/sessions.ts`.

---

## Utrzymanie magazynu i kontrola dysku

Trwałość sesji ma automatyczne mechanizmy utrzymania (`session.maintenance`) dla `sessions.json` i artefaktów transkryptu:

- `mode`: `warn` (domyślnie) lub `enforce`
- `pruneAfter`: próg wieku dla nieaktualnych wpisów (domyślnie `30d`)
- `maxEntries`: limit wpisów w `sessions.json` (domyślnie `500`)
- `rotateBytes`: rotacja `sessions.json`, gdy plik jest zbyt duży (domyślnie `10mb`)
- `resetArchiveRetention`: czas przechowywania archiwów transkryptów `*.reset.<timestamp>` (domyślnie: taki sam jak `pruneAfter`; `false` wyłącza czyszczenie)
- `maxDiskBytes`: opcjonalny budżet katalogu sesji
- `highWaterBytes`: opcjonalny cel po czyszczeniu (domyślnie `80%` z `maxDiskBytes`)

Kolejność egzekwowania przy czyszczeniu budżetu dysku (`mode: "enforce"`):

1. Najpierw usuń najstarsze zarchiwizowane lub osierocone artefakty transkryptu.
2. Jeśli nadal jest powyżej celu, usuń najstarsze wpisy sesji i ich pliki transkryptu.
3. Kontynuuj, aż użycie spadnie do `highWaterBytes` lub poniżej.

W trybie `mode: "warn"` OpenClaw zgłasza potencjalne usunięcia, ale nie modyfikuje magazynu/plików.

Uruchom utrzymanie na żądanie:

```bash
openclaw sessions cleanup --dry-run
openclaw sessions cleanup --enforce
```

---

## Sesje cron i logi uruchomień

Odizolowane uruchomienia cron również tworzą wpisy sesji/transkrypty i mają dedykowane ustawienia retencji:

- `cron.sessionRetention` (domyślnie `24h`) usuwa stare sesje odizolowanych uruchomień cron z magazynu sesji (`false` wyłącza).
- `cron.runLog.maxBytes` + `cron.runLog.keepLines` przycinają pliki `~/.openclaw/cron/runs/<jobId>.jsonl` (domyślnie: `2_000_000` bajtów i `2000` wierszy).

---

## Klucze sesji (`sessionKey`)

`sessionKey` identyfikuje, *w którym koszyku konwersacji* się znajdujesz (routing + izolacja).

Typowe wzorce:

- Czat główny/bezpośredni (per agent): `agent:<agentId>:<mainKey>` (domyślnie `main`)
- Grupa: `agent:<agentId>:<channel>:group:<id>`
- Pokój/kanał (Discord/Slack): `agent:<agentId>:<channel>:channel:<id>` lub `...:room:<id>`
- Cron: `cron:<job.id>`
- Webhook: `hook:<uuid>` (chyba że nadpisano)

Kanoniczne zasady są opisane w [/concepts/session](/pl/concepts/session).

---

## Identyfikatory sesji (`sessionId`)

Każdy `sessionKey` wskazuje bieżący `sessionId` (plik transkryptu, który kontynuuje konwersację).

Zasady orientacyjne:

- **Reset** (`/new`, `/reset`) tworzy nowy `sessionId` dla tego `sessionKey`.
- **Reset dzienny** (domyślnie 4:00 czasu lokalnego na hoście gatewaya) tworzy nowy `sessionId` przy następnej wiadomości po przekroczeniu granicy resetu.
- **Wygaśnięcie bezczynności** (`session.reset.idleMinutes` lub starsze `session.idleMinutes`) tworzy nowy `sessionId`, gdy wiadomość nadejdzie po upływie okna bezczynności. Gdy skonfigurowane są jednocześnie reset dzienny i bezczynność, wygrywa to, co wygaśnie wcześniej.
- **Zabezpieczenie rozwidlenia od nadrzędnego wątku** (`session.parentForkMaxTokens`, domyślnie `100000`) pomija rozwidlanie transkryptu sesji nadrzędnej, gdy nadrzędna sesja jest już zbyt duża; nowy wątek zaczyna się od zera. Ustaw `0`, aby wyłączyć.

Szczegół implementacyjny: decyzja zapada w `initSessionState()` w `src/auto-reply/reply/session.ts`.

---

## Schemat magazynu sesji (`sessions.json`)

Typ wartości magazynu to `SessionEntry` w `src/config/sessions.ts`.

Kluczowe pola (niepełna lista):

- `sessionId`: bieżący identyfikator transkryptu (nazwa pliku jest wyprowadzana z niego, chyba że ustawiono `sessionFile`)
- `updatedAt`: znacznik czasu ostatniej aktywności
- `sessionFile`: opcjonalne jawne nadpisanie ścieżki transkryptu
- `chatType`: `direct | group | room` (pomaga UI i zasadom wysyłki)
- `provider`, `subject`, `room`, `space`, `displayName`: metadane do etykiet grup/kanałów
- Przełączniki:
  - `thinkingLevel`, `verboseLevel`, `reasoningLevel`, `elevatedLevel`
  - `sendPolicy` (nadpisanie per sesja)
- Wybór modelu:
  - `providerOverride`, `modelOverride`, `authProfileOverride`
- Liczniki tokenów (best-effort / zależne od providera):
  - `inputTokens`, `outputTokens`, `totalTokens`, `contextTokens`
- `compactionCount`: jak często automatyczne kompaktowanie zostało ukończone dla tego klucza sesji
- `memoryFlushAt`: znacznik czasu ostatniego opróżnienia pamięci przed kompaktowaniem
- `memoryFlushCompactionCount`: liczba kompaktowań, przy której wykonano ostatnie opróżnienie

Magazyn można bezpiecznie edytować, ale Gateway jest źródłem prawdy: może przepisywać lub odtwarzać wpisy w trakcie działania sesji.

---

## Struktura transkryptu (`*.jsonl`)

Transkryptami zarządza `SessionManager` z `@mariozechner/pi-coding-agent`.

Plik ma format JSONL:

- Pierwszy wiersz: nagłówek sesji (`type: "session"`, zawiera `id`, `cwd`, `timestamp`, opcjonalne `parentSession`)
- Następnie: wpisy sesji z `id` + `parentId` (drzewo)

Istotne typy wpisów:

- `message`: wiadomości user/assistant/toolResult
- `custom_message`: wiadomości wstrzyknięte przez rozszerzenie, które *wchodzą* do kontekstu modelu (mogą być ukryte przed UI)
- `custom`: stan rozszerzenia, który *nie wchodzi* do kontekstu modelu
- `compaction`: zapisane podsumowanie kompaktowania z `firstKeptEntryId` i `tokensBefore`
- `branch_summary`: zapisane podsumowanie przy nawigacji po gałęzi drzewa

OpenClaw celowo **nie** „naprawia” transkryptów; Gateway używa `SessionManager` do ich odczytu/zapisu.

---

## Okna kontekstu a śledzone tokeny

Istotne są dwa różne pojęcia:

1. **Okno kontekstu modelu**: twardy limit per model (tokeny widoczne dla modelu)
2. **Liczniki magazynu sesji**: statystyki kroczące zapisywane do `sessions.json` (używane przez /status i dashboardy)

Jeśli dostrajasz limity:

- Okno kontekstu pochodzi z katalogu modeli (i może być nadpisane przez konfigurację).
- `contextTokens` w magazynie to wartość szacunkowa/raportowa z runtime; nie traktuj jej jako ścisłej gwarancji.

Więcej informacji znajdziesz w [/token-use](/pl/reference/token-use).

---

## Kompaktowanie: czym jest

Kompaktowanie podsumowuje starszą część rozmowy do zapisanego wpisu `compaction` w transkrypcie i zachowuje nienaruszone ostatnie wiadomości.

Po kompaktowaniu przyszłe tury widzą:

- Podsumowanie kompaktowania
- Wiadomości po `firstKeptEntryId`

Kompaktowanie jest **trwałe** (w przeciwieństwie do przycinania sesji). Zobacz [/concepts/session-pruning](/pl/concepts/session-pruning).

## Granice chunków kompaktowania i parowanie narzędzi

Gdy OpenClaw dzieli długi transkrypt na chunki do kompaktowania, zachowuje
sparowanie wywołań narzędzi asystenta z odpowiadającymi im wpisami `toolResult`.

- Jeśli podział według udziału tokenów wypada między wywołaniem narzędzia a jego wynikiem, OpenClaw
  przesuwa granicę do wiadomości asystenta z wywołaniem narzędzia zamiast rozdzielać tę parę.
- Jeśli końcowy blok wyników narzędzia w przeciwnym razie wypchnąłby chunk ponad cel,
  OpenClaw zachowuje ten oczekujący blok narzędzia i pozostawia niepodsumowany ogon bez zmian.
- Przerwane/blędne bloki wywołań narzędzi nie utrzymują oczekującego podziału.

---

## Kiedy następuje auto-kompaktowanie (runtime Pi)

W osadzonym agencie Pi automatyczne kompaktowanie uruchamia się w dwóch przypadkach:

1. **Odzyskiwanie po przepełnieniu**: model zwraca błąd przepełnienia kontekstu
   (`request_too_large`, `context length exceeded`, `input exceeds the maximum
number of tokens`, `input token count exceeds the maximum number of input
tokens`, `input is too long for the model`, `ollama error: context length
exceeded` i podobne warianty zależne od providera) → kompaktowanie → ponowna próba.
2. **Utrzymanie progu**: po udanej turze, gdy:

`contextTokens > contextWindow - reserveTokens`

Gdzie:

- `contextWindow` to okno kontekstu modelu
- `reserveTokens` to zapas zarezerwowany dla promptów + następnego wyjścia modelu

To semantyka runtime Pi (OpenClaw konsumuje zdarzenia, ale Pi decyduje, kiedy kompaktować).

---

## Ustawienia kompaktowania (`reserveTokens`, `keepRecentTokens`)

Ustawienia kompaktowania Pi znajdują się w ustawieniach Pi:

```json5
{
  compaction: {
    enabled: true,
    reserveTokens: 16384,
    keepRecentTokens: 20000,
  },
}
```

OpenClaw wymusza też minimalny próg bezpieczeństwa dla osadzonych uruchomień:

- Jeśli `compaction.reserveTokens < reserveTokensFloor`, OpenClaw go podnosi.
- Domyślny próg minimalny to `20000` tokenów.
- Ustaw `agents.defaults.compaction.reserveTokensFloor: 0`, aby wyłączyć ten próg.
- Jeśli wartość jest już wyższa, OpenClaw pozostawia ją bez zmian.

Dlaczego: trzeba zostawić wystarczający zapas na wieloturowe „porządki” (takie jak zapisy pamięci), zanim kompaktowanie stanie się nieuniknione.

Implementacja: `ensurePiCompactionReserveTokens()` w `src/agents/pi-settings.ts`
(wywoływane z `src/agents/pi-embedded-runner.ts`).

---

## Powierzchnie widoczne dla użytkownika

Możesz obserwować kompaktowanie i stan sesji przez:

- `/status` (w dowolnej sesji czatu)
- `openclaw status` (CLI)
- `openclaw sessions` / `sessions --json`
- Tryb verbose: `🧹 Auto-compaction complete` + liczba kompaktowań

---

## Ciche porządki (`NO_REPLY`)

OpenClaw obsługuje „ciche” tury dla zadań w tle, w których użytkownik nie powinien widzieć pośredniego wyjścia.

Konwencja:

- Asystent zaczyna swoje wyjście dokładnie od cichego tokena `NO_REPLY` /
  `no_reply`, aby wskazać „nie dostarczaj odpowiedzi użytkownikowi”.
- OpenClaw usuwa/tłumi to w warstwie dostarczania.
- Tłumienie dokładnego cichego tokena jest nieczułe na wielkość liter, więc `NO_REPLY` i
  `no_reply` są liczone, gdy cały payload jest tylko tym cichym tokenem.
- Służy to wyłącznie do prawdziwych tur w tle/bez dostarczenia; nie jest skrótem dla
  zwykłych żądań użytkownika wymagających działania.

Od wersji `2026.1.10` OpenClaw tłumi również **streaming szkicu/wskaźnika pisania**, gdy
częściowy chunk zaczyna się od `NO_REPLY`, aby ciche operacje nie ujawniały częściowego
wyjścia w trakcie tury.

---

## „Opróżnianie pamięci” przed kompaktowaniem (zaimplementowane)

Cel: zanim nastąpi automatyczne kompaktowanie, uruchomić cichą turę agentową, która zapisze trwały
stan na dysku (np. `memory/YYYY-MM-DD.md` w workspace agenta), aby kompaktowanie nie mogło
usunąć krytycznego kontekstu.

OpenClaw używa podejścia **opróżnienia przed progiem**:

1. Monitoruj użycie kontekstu sesji.
2. Gdy przekroczy „miękki próg” (poniżej progu kompaktowania Pi), uruchom cichą
   dyrektywę „zapisz pamięć teraz” dla agenta.
3. Użyj dokładnie cichego tokena `NO_REPLY` / `no_reply`, aby użytkownik niczego
   nie zobaczył.

Konfiguracja (`agents.defaults.compaction.memoryFlush`):

- `enabled` (domyślnie: `true`)
- `softThresholdTokens` (domyślnie: `4000`)
- `prompt` (wiadomość użytkownika dla tury opróżnienia)
- `systemPrompt` (dodatkowy prompt systemowy dołączany dla tury opróżnienia)

Uwagi:

- Domyślny prompt/systemPrompt zawiera wskazówkę `NO_REPLY`, aby tłumić
  dostarczanie.
- Opróżnienie uruchamia się raz na cykl kompaktowania (śledzone w `sessions.json`).
- Opróżnienie działa tylko dla osadzonych sesji Pi.
- Opróżnienie jest pomijane, gdy workspace sesji jest tylko do odczytu (`workspaceAccess: "ro"` lub `"none"`).
- Zobacz [Pamięć](/pl/concepts/memory), aby poznać układ plików workspace i wzorce zapisu.

Pi udostępnia również hook `session_before_compact` w API rozszerzeń, ale logika
opróżniania OpenClaw znajduje się dziś po stronie Gateway.

---

## Lista kontrolna rozwiązywania problemów

- Nieprawidłowy klucz sesji? Zacznij od [/concepts/session](/pl/concepts/session) i potwierdź `sessionKey` w `/status`.
- Niezgodność magazynu i transkryptu? Potwierdź host Gateway i ścieżkę magazynu z `openclaw status`.
- Spam kompaktowania? Sprawdź:
  - okno kontekstu modelu (zbyt małe)
  - ustawienia kompaktowania (`reserveTokens` zbyt wysokie względem okna modelu mogą powodować wcześniejsze kompaktowanie)
  - nadmiar wyników narzędzi: włącz/skonfiguruj przycinanie sesji
- Ciche tury przeciekają? Upewnij się, że odpowiedź zaczyna się od `NO_REPLY` (dokładny token, bez rozróżniania wielkości liter) i że używasz wersji zawierającej poprawkę tłumienia streamingu.
