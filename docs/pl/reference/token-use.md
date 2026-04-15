---
read_when:
    - Wyjaśnianie użycia tokenów, kosztów lub okien kontekstu
    - Debugowanie wzrostu kontekstu lub zachowania Compaction
summary: Jak OpenClaw buduje kontekst promptu oraz raportuje użycie tokenów i koszty
title: Użycie tokenów i koszty
x-i18n:
    generated_at: "2026-04-15T19:41:58Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9a706d3df8b2ea1136b3535d216c6b358e43aee2a31a4759824385e1345e6fe5
    source_path: reference/token-use.md
    workflow: 15
---

# Użycie tokenów i koszty

OpenClaw śledzi **tokeny**, a nie znaki. Tokeny są zależne od modelu, ale większość
modeli w stylu OpenAI ma średnio około 4 znaki na token dla tekstu angielskiego.

## Jak budowany jest prompt systemowy

OpenClaw składa własny prompt systemowy przy każdym uruchomieniu. Obejmuje on:

- Listę narzędzi + krótkie opisy
- Listę Skills (tylko metadane; instrukcje są ładowane na żądanie przez `read`).
  Zwięzły blok Skills jest ograniczony przez `skills.limits.maxSkillsPromptChars`,
  z opcjonalnym nadpisaniem per agent w
  `agents.list[].skillsLimits.maxSkillsPromptChars`.
- Instrukcje samoaktualizacji
- Pliki workspace + bootstrap (`AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`, `BOOTSTRAP.md` gdy są nowe, a także `MEMORY.md`, gdy występuje, lub `memory.md` jako wariant z małych liter). Duże pliki są przycinane przez `agents.defaults.bootstrapMaxChars` (domyślnie: 12000), a całkowity wstrzykiwany bootstrap jest ograniczony przez `agents.defaults.bootstrapTotalMaxChars` (domyślnie: 60000). Codzienne pliki `memory/*.md` nie są częścią zwykłego promptu bootstrap; pozostają dostępne na żądanie przez narzędzia pamięci w zwykłych turach, ale czyste `/new` i `/reset` mogą dodać jednorazowy blok kontekstu startowego z ostatnią dzienną pamięcią dla tej pierwszej tury. To wprowadzenie startowe jest kontrolowane przez `agents.defaults.startupContext`.
- Czas (UTC + strefa czasowa użytkownika)
- Tagi odpowiedzi + zachowanie Heartbeat
- Metadane runtime (host/OS/model/thinking)

Pełny podział znajdziesz w [Prompt systemowy](/pl/concepts/system-prompt).

## Co liczy się do okna kontekstu

Wszystko, co model otrzymuje, liczy się do limitu kontekstu:

- Prompt systemowy (wszystkie sekcje wymienione powyżej)
- Historia rozmowy (wiadomości użytkownika i asystenta)
- Wywołania narzędzi i wyniki narzędzi
- Załączniki/transkrypcje (obrazy, audio, pliki)
- Podsumowania Compaction i artefakty przycinania
- Opakowania dostawcy lub nagłówki bezpieczeństwa (niewidoczne, ale nadal liczone)

Niektóre powierzchnie runtime o dużym obciążeniu mają własne jawne limity:

- `agents.defaults.contextLimits.memoryGetMaxChars`
- `agents.defaults.contextLimits.memoryGetDefaultLines`
- `agents.defaults.contextLimits.toolResultMaxChars`
- `agents.defaults.contextLimits.postCompactionMaxChars`

Nadpisania per agent znajdują się w `agents.list[].contextLimits`. Te ustawienia
dotyczą ograniczonych fragmentów runtime i wstrzykiwanych bloków należących do runtime.
Są one oddzielone od limitów bootstrap, limitów kontekstu startowego i limitów
promptu Skills.

W przypadku obrazów OpenClaw skaluje w dół ładunki obrazów transkrypcji/narzędzi przed wywołaniami dostawcy.
Użyj `agents.defaults.imageMaxDimensionPx` (domyślnie: `1200`), aby to dostroić:

- Niższe wartości zwykle zmniejszają użycie tokenów vision i rozmiar ładunku.
- Wyższe wartości zachowują więcej szczegółów wizualnych dla zrzutów ekranu z dużą ilością OCR/UI.

Aby uzyskać praktyczny podział (na każdy wstrzyknięty plik, narzędzia, Skills i rozmiar promptu systemowego), użyj `/context list` lub `/context detail`. Zobacz [Kontekst](/pl/concepts/context).

## Jak zobaczyć bieżące użycie tokenów

Użyj tych poleceń na czacie:

- `/status` → **karta statusu bogata w emoji** z modelem sesji, użyciem kontekstu,
  tokenami wejścia/wyjścia ostatniej odpowiedzi oraz **szacowanym kosztem** (tylko klucz API).
- `/usage off|tokens|full` → dodaje **stopkę użycia dla każdej odpowiedzi** do każdej odpowiedzi.
  - Utrzymuje się per sesja (przechowywane jako `responseUsage`).
  - Autoryzacja OAuth **ukrywa koszt** (tylko tokeny).
- `/usage cost` → pokazuje lokalne podsumowanie kosztów z logów sesji OpenClaw.

Inne powierzchnie:

- **TUI/Web TUI:** obsługiwane są `/status` i `/usage`.
- **CLI:** `openclaw status --usage` i `openclaw channels list` pokazują
  znormalizowane okna limitów dostawców (`X% left`, a nie koszty per odpowiedź).
  Obecni dostawcy z oknami użycia: Anthropic, GitHub Copilot, Gemini CLI,
  OpenAI Codex, MiniMax, Xiaomi i z.ai.

Powierzchnie użycia normalizują popularne aliasy pól natywnych dla dostawców przed wyświetleniem.
Dla ruchu OpenAI-family Responses obejmuje to zarówno `input_tokens` /
`output_tokens`, jak i `prompt_tokens` / `completion_tokens`, więc nazwy pól
zależne od transportu nie zmieniają `/status`, `/usage` ani podsumowań sesji.
Użycie Gemini CLI JSON również jest normalizowane: tekst odpowiedzi pochodzi z `response`, a
`stats.cached` mapuje się na `cacheRead`, przy czym używane jest `stats.input_tokens - stats.cached`,
gdy CLI pomija jawne pole `stats.input`.
Dla natywnego ruchu OpenAI-family Responses aliasy użycia WebSocket/SSE są
normalizowane w ten sam sposób, a sumy całkowite wracają do znormalizowanego wejścia + wyjścia, gdy
`total_tokens` nie istnieje lub ma wartość `0`.
Gdy bieżący snapshot sesji jest ubogi, `/status` i `session_status` mogą
również odzyskać liczniki tokenów/cache oraz etykietę aktywnego modelu runtime z
najnowszego logu użycia transkrypcji. Istniejące niezerowe wartości live nadal mają
pierwszeństwo przed wartościami awaryjnie pobranymi z transkrypcji, a większe sumy
zorientowane na prompt z transkrypcji mogą wygrać, gdy zapisane sumy nie istnieją
lub są mniejsze.
Autoryzacja użycia dla okien limitów dostawców pochodzi z hooków specyficznych dla dostawcy, gdy są dostępne;
w przeciwnym razie OpenClaw wraca do dopasowywania poświadczeń OAuth/klucza API z
profili auth, env lub config.

## Szacowanie kosztów (gdy jest wyświetlane)

Koszty są szacowane na podstawie konfiguracji cen modelu:

```
models.providers.<provider>.models[].cost
```

Są to wartości **USD za 1M tokenów** dla `input`, `output`, `cacheRead` oraz
`cacheWrite`. Jeśli brakuje cen, OpenClaw pokazuje tylko tokeny. Tokeny OAuth
nigdy nie pokazują kosztu w dolarach.

## Wpływ TTL cache i przycinania

Cache promptów dostawcy działa tylko w obrębie okna TTL cache. OpenClaw może
opcjonalnie uruchamiać **przycinanie cache-ttl**: przycina sesję po wygaśnięciu
TTL cache, a następnie resetuje okno cache, aby kolejne żądania mogły ponownie użyć
świeżo zcache’owanego kontekstu zamiast ponownie cache’ować pełną historię. Dzięki temu koszty
zapisu cache pozostają niższe, gdy sesja pozostaje bezczynna dłużej niż TTL.

Skonfiguruj to w [Konfiguracja Gateway](/pl/gateway/configuration), a szczegóły
zachowania znajdziesz w [Przycinanie sesji](/pl/concepts/session-pruning).

Heartbeat może utrzymywać cache **warm** w przerwach bezczynności. Jeśli TTL cache
Twojego modelu wynosi `1h`, ustawienie interwału Heartbeat tuż poniżej tej wartości
(np. `55m`) może zapobiec ponownemu cache’owaniu pełnego promptu, zmniejszając koszty
zapisu cache.

W konfiguracjach wieloagentowych możesz utrzymać jedną współdzieloną konfigurację modelu i dostrajać zachowanie cache
per agent za pomocą `agents.list[].params.cacheRetention`.

Pełny przewodnik po wszystkich ustawieniach znajdziesz w [Prompt Caching](/pl/reference/prompt-caching).

W przypadku cen API Anthropic odczyty cache są znacznie tańsze niż tokeny
wejściowe, natomiast zapisy cache są rozliczane z wyższym mnożnikiem. Aktualne stawki i mnożniki TTL znajdziesz w cenniku prompt caching Anthropic:
[https://docs.anthropic.com/docs/build-with-claude/prompt-caching](https://docs.anthropic.com/docs/build-with-claude/prompt-caching)

### Przykład: utrzymywanie cache 1h w stanie warm za pomocą Heartbeat

```yaml
agents:
  defaults:
    model:
      primary: "anthropic/claude-opus-4-6"
    models:
      "anthropic/claude-opus-4-6":
        params:
          cacheRetention: "long"
    heartbeat:
      every: "55m"
```

### Przykład: ruch mieszany ze strategią cache per agent

```yaml
agents:
  defaults:
    model:
      primary: "anthropic/claude-opus-4-6"
    models:
      "anthropic/claude-opus-4-6":
        params:
          cacheRetention: "long" # default baseline for most agents
  list:
    - id: "research"
      default: true
      heartbeat:
        every: "55m" # keep long cache warm for deep sessions
    - id: "alerts"
      params:
        cacheRetention: "none" # avoid cache writes for bursty notifications
```

`agents.list[].params` scala się na wierzchu `params` wybranego modelu, więc możesz
nadpisać tylko `cacheRetention` i odziedziczyć pozostałe domyślne ustawienia modelu bez zmian.

### Przykład: włączenie nagłówka beta Anthropic 1M context

Okno kontekstu 1M Anthropic jest obecnie objęte bramką beta. OpenClaw może wstrzyknąć
wymaganą wartość `anthropic-beta`, gdy włączysz `context1m` w obsługiwanych modelach Opus
lub Sonnet.

```yaml
agents:
  defaults:
    models:
      "anthropic/claude-opus-4-6":
        params:
          context1m: true
```

Mapuje się to na nagłówek beta Anthropic `context-1m-2025-08-07`.

Ma to zastosowanie tylko wtedy, gdy `context1m: true` jest ustawione w tym wpisie modelu.

Wymaganie: poświadczenie musi kwalifikować się do użycia długiego kontekstu. Jeśli nie,
Anthropic odpowie błędem limitu po stronie dostawcy dla tego żądania.

Jeśli uwierzytelniasz Anthropic za pomocą tokenów OAuth/subscription (`sk-ant-oat-*`),
OpenClaw pomija nagłówek beta `context-1m-*`, ponieważ Anthropic obecnie
odrzuca tę kombinację z HTTP 401.

## Wskazówki, jak zmniejszyć presję tokenów

- Użyj `/compact`, aby podsumować długie sesje.
- Ograniczaj duże wyniki narzędzi w swoich workflow.
- Obniż `agents.defaults.imageMaxDimensionPx` dla sesji z dużą liczbą zrzutów ekranu.
- Utrzymuj krótkie opisy Skills (lista Skills jest wstrzykiwana do promptu).
- W przypadku rozwlekłej, eksploracyjnej pracy preferuj mniejsze modele.

Zobacz [Skills](/pl/tools/skills), aby poznać dokładny wzór narzutu listy Skills.
