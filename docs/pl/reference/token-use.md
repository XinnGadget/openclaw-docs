---
read_when:
    - Wyjaśnianie użycia tokenów, kosztów lub okien kontekstowych
    - Debugowanie wzrostu kontekstu lub zachowania Compaction
summary: Jak OpenClaw buduje kontekst promptu oraz raportuje użycie tokenów i koszty
title: Użycie tokenów i koszty
x-i18n:
    generated_at: "2026-04-12T09:34:14Z"
    model: gpt-5.4
    provider: openai
    source_hash: f8c856549cd28b8364a640e6fa9ec26aa736895c7a993e96cbe85838e7df2dfb
    source_path: reference/token-use.md
    workflow: 15
---

# Użycie tokenów i koszty

OpenClaw śledzi **tokeny**, a nie znaki. Tokeny są zależne od modelu, ale większość
modeli w stylu OpenAI daje średnio około 4 znaków na token dla tekstu angielskiego.

## Jak budowany jest prompt systemowy

OpenClaw składa własny prompt systemowy przy każdym uruchomieniu. Obejmuje on:

- listę narzędzi + krótkie opisy
- listę Skills (tylko metadane; instrukcje są ładowane na żądanie za pomocą `read`)
- instrukcje samodzielnej aktualizacji
- obszar roboczy + pliki bootstrapu (`AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`, `BOOTSTRAP.md` gdy nowe, a także `MEMORY.md`, jeśli istnieje, lub `memory.md` jako zapasowy wariant małymi literami). Duże pliki są obcinane przez `agents.defaults.bootstrapMaxChars` (domyślnie: 20000), a całkowite wstrzyknięcie bootstrapu jest ograniczone przez `agents.defaults.bootstrapTotalMaxChars` (domyślnie: 150000). Dzienne pliki `memory/*.md` nie są częścią zwykłego promptu bootstrapu; przy zwykłych turach pozostają dostępne na żądanie przez narzędzia pamięci, ale zwykłe `/new` i `/reset` mogą dodać na początku jednorazowy blok kontekstu startowego z ostatnią dzienną pamięcią dla tej pierwszej tury. Ten prelude startowy jest kontrolowany przez `agents.defaults.startupContext`.
- czas (UTC + strefa czasowa użytkownika)
- tagi odpowiedzi + zachowanie Heartbeat
- metadane runtime (host/OS/model/poziom myślenia)

Pełny podział znajdziesz w [Prompt systemowy](/pl/concepts/system-prompt).

## Co liczy się do okna kontekstowego

Wszystko, co model otrzymuje, liczy się do limitu kontekstu:

- prompt systemowy (wszystkie sekcje wymienione powyżej)
- historia rozmowy (wiadomości użytkownika + asystenta)
- wywołania narzędzi i wyniki narzędzi
- załączniki/transkrypcje (obrazy, audio, pliki)
- podsumowania Compaction i artefakty przycinania
- wrappery dostawcy lub nagłówki bezpieczeństwa (niewidoczne, ale nadal liczone)

Dla obrazów OpenClaw zmniejsza rozdzielczość ładunków obrazów w transkrypcjach/narzędziach przed wywołaniami dostawcy.
Użyj `agents.defaults.imageMaxDimensionPx` (domyślnie: `1200`), aby to dostroić:

- niższe wartości zwykle zmniejszają zużycie tokenów vision i rozmiar ładunku
- wyższe wartości zachowują więcej szczegółów wizualnych dla OCR/zrzutów ekranu z intensywnym UI

Aby zobaczyć praktyczny podział (na wstrzyknięty plik, narzędzia, Skills i rozmiar promptu systemowego), użyj `/context list` lub `/context detail`. Zobacz [Kontekst](/pl/concepts/context).

## Jak zobaczyć bieżące użycie tokenów

Użyj tych poleceń na czacie:

- `/status` → **bogata w emoji karta statusu** z modelem sesji, wykorzystaniem kontekstu,
  tokenami wejścia/wyjścia ostatniej odpowiedzi oraz **szacowanym kosztem** (tylko klucz API).
- `/usage off|tokens|full` → dodaje **stopkę użycia dla każdej odpowiedzi** do każdej odpowiedzi.
  - Utrzymuje się per sesja (zapisywane jako `responseUsage`).
  - Uwierzytelnianie OAuth **ukrywa koszt** (tylko tokeny).
- `/usage cost` → pokazuje lokalne podsumowanie kosztów z logów sesji OpenClaw.

Inne powierzchnie:

- **TUI/Web TUI:** obsługiwane są `/status` + `/usage`.
- **CLI:** `openclaw status --usage` i `openclaw channels list` pokazują
  znormalizowane okna limitów dostawcy (`X% left`, a nie koszty dla poszczególnych odpowiedzi).
  Obecni dostawcy okien użycia: Anthropic, GitHub Copilot, Gemini CLI,
  OpenAI Codex, MiniMax, Xiaomi i z.ai.

Powierzchnie użycia normalizują typowe aliasy pól natywnych dostawców przed wyświetleniem.
Dla ruchu OpenAI-family Responses obejmuje to zarówno `input_tokens` /
`output_tokens`, jak i `prompt_tokens` / `completion_tokens`, więc specyficzne dla transportu
nazwy pól nie zmieniają `/status`, `/usage` ani podsumowań sesji.
Użycie JSON Gemini CLI jest również normalizowane: tekst odpowiedzi pochodzi z `response`, a
`stats.cached` mapuje się na `cacheRead`, przy czym używane jest `stats.input_tokens - stats.cached`,
gdy CLI pomija jawne pole `stats.input`.
Dla natywnego ruchu OpenAI-family Responses aliasy użycia WebSocket/SSE są
normalizowane w ten sam sposób, a sumy całkowite wracają do znormalizowanego wejścia + wyjścia, gdy
`total_tokens` nie istnieje lub ma wartość `0`.
Gdy bieżąca migawka sesji jest uboga w dane, `/status` i `session_status` mogą
również odzyskać liczniki tokenów/cache oraz etykietę aktywnego modelu runtime z
najnowszego logu użycia transkryptu. Istniejące niezerowe wartości na żywo nadal mają
pierwszeństwo przed wartościami odzyskanymi z transkryptu, a większe sumy zorientowane na prompt
z transkryptu mogą wygrać, gdy zapisane sumy nie istnieją lub są mniejsze.
Uwierzytelnianie użycia dla okien limitów dostawcy pochodzi z hooków specyficznych dla dostawcy, gdy są dostępne;
w przeciwnym razie OpenClaw wraca do dopasowywania poświadczeń OAuth/klucza API
z profili uwierzytelniania, env lub konfiguracji.

## Szacowanie kosztów (gdy jest pokazywane)

Koszty są szacowane na podstawie konfiguracji cen modelu:

```
models.providers.<provider>.models[].cost
```

Są to wartości **USD za 1M tokenów** dla `input`, `output`, `cacheRead` i
`cacheWrite`. Jeśli brakuje cen, OpenClaw pokazuje tylko tokeny. Tokeny OAuth
nigdy nie pokazują kosztu w dolarach.

## Wpływ TTL cache i przycinania

Cache promptu dostawcy ma zastosowanie tylko w obrębie okna TTL cache. OpenClaw może
opcjonalnie uruchamiać **przycinanie cache-ttl**: przycina sesję po wygaśnięciu TTL
cache, a następnie resetuje okno cache, aby kolejne żądania mogły ponownie używać
świeżo zcache’owanego kontekstu zamiast ponownie cache’ować całą historię. Utrzymuje to
niższe koszty zapisu cache, gdy sesja pozostaje bezczynna po TTL.

Skonfiguruj to w [Konfiguracja Gateway](/pl/gateway/configuration), a szczegóły
działania znajdziesz w [Przycinanie sesji](/pl/concepts/session-pruning).

Heartbeat może utrzymywać cache **ciepły** podczas przerw bezczynności. Jeśli TTL cache modelu
wynosi `1h`, ustawienie interwału Heartbeat nieco poniżej tego czasu (np. `55m`) może zapobiec
ponownemu cache’owaniu całego promptu, zmniejszając koszty zapisu cache.

W konfiguracjach wieloagentowych możesz utrzymać jedną współdzieloną konfigurację modelu i dostrajać zachowanie cache
dla każdego agenta przez `agents.list[].params.cacheRetention`.

Pełny przewodnik po wszystkich ustawieniach znajdziesz w [Prompt Caching](/pl/reference/prompt-caching).

W przypadku cen API Anthropic odczyty cache są znacząco tańsze niż tokeny wejściowe,
podczas gdy zapisy cache są rozliczane według wyższego mnożnika. Najnowsze stawki i mnożniki TTL znajdziesz w cenniku prompt caching Anthropic:
[https://docs.anthropic.com/docs/build-with-claude/prompt-caching](https://docs.anthropic.com/docs/build-with-claude/prompt-caching)

### Przykład: utrzymanie 1h cache w cieple za pomocą Heartbeat

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
          cacheRetention: "long" # domyślna baza dla większości agentów
  list:
    - id: "research"
      default: true
      heartbeat:
        every: "55m" # utrzymuj długi cache w cieple dla głębokich sesji
    - id: "alerts"
      params:
        cacheRetention: "none" # unikaj zapisów cache dla skokowych powiadomień
```

`agents.list[].params` scala się na wierzchu `params` wybranego modelu, więc możesz
nadpisać tylko `cacheRetention` i pozostawić inne domyślne ustawienia modelu bez zmian.

### Przykład: włączenie nagłówka beta Anthropic 1M context

Okno kontekstowe 1M w Anthropic jest obecnie objęte bramką beta. OpenClaw może wstrzyknąć wymaganą
wartość `anthropic-beta`, gdy włączysz `context1m` w obsługiwanych modelach Opus
lub Sonnet.

```yaml
agents:
  defaults:
    models:
      "anthropic/claude-opus-4-6":
        params:
          context1m: true
```

To mapuje się na nagłówek beta Anthropic `context-1m-2025-08-07`.

Ma to zastosowanie tylko wtedy, gdy dla tego wpisu modelu ustawiono `context1m: true`.

Wymaganie: poświadczenie musi kwalifikować się do użycia długiego kontekstu. Jeśli nie,
Anthropic odpowie błędem limitu po stronie dostawcy dla tego żądania.

Jeśli uwierzytelniasz Anthropic tokenami OAuth/subskrypcyjnymi (`sk-ant-oat-*`),
OpenClaw pomija nagłówek beta `context-1m-*`, ponieważ Anthropic obecnie
odrzuca tę kombinację z HTTP 401.

## Wskazówki dotyczące zmniejszania presji tokenowej

- Użyj `/compact`, aby podsumować długie sesje.
- Przycinaj duże wyjścia narzędzi w swoich workflow.
- Obniż `agents.defaults.imageMaxDimensionPx` dla sesji z dużą liczbą zrzutów ekranu.
- Utrzymuj krótkie opisy Skills (lista Skills jest wstrzykiwana do promptu).
- Preferuj mniejsze modele do rozwlekłej, eksploracyjnej pracy.

Dokładny wzór narzutu listy Skills znajdziesz w [Skills](/pl/tools/skills).
