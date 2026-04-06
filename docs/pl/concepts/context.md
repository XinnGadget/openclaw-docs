---
read_when:
    - Chcesz zrozumieć, co oznacza „kontekst” w OpenClaw
    - Debugujesz, dlaczego model „wie” coś (albo o tym zapomniał)
    - Chcesz zmniejszyć narzut kontekstu (/context, /status, /compact)
summary: 'Kontekst: co widzi model, jak jest budowany i jak go sprawdzić'
title: Kontekst
x-i18n:
    generated_at: "2026-04-06T03:06:20Z"
    model: gpt-5.4
    provider: openai
    source_hash: fe7dfe52cb1a64df229c8622feed1804df6c483a6243e0d2f309f6ff5c9fe521
    source_path: concepts/context.md
    workflow: 15
---

# Kontekst

„Kontekst” to **wszystko, co OpenClaw wysyła do modelu na potrzeby uruchomienia**. Jest ograniczony przez **okno kontekstu** modelu (limit tokenów).

Prosty model myślowy dla początkujących:

- **System prompt** (budowany przez OpenClaw): reguły, narzędzia, lista Skills, czas/metadane środowiska uruchomieniowego i wstrzyknięte pliki obszaru roboczego.
- **Historia rozmowy**: Twoje wiadomości + wiadomości asystenta w tej sesji.
- **Wywołania/wyniki narzędzi + załączniki**: dane wyjściowe poleceń, odczyty plików, obrazy/audio itd.

Kontekst _to nie to samo_ co „pamięć”: pamięć może być zapisana na dysku i wczytana później; kontekst to to, co znajduje się w bieżącym oknie modelu.

## Szybki start (sprawdzanie kontekstu)

- `/status` → szybki widok „jak bardzo zapełnione jest moje okno?” + ustawienia sesji.
- `/context list` → co jest wstrzykiwane + przybliżone rozmiary (na plik + łącznie).
- `/context detail` → bardziej szczegółowy podział: rozmiary dla każdego pliku, schematu narzędzia, wpisu Skills i rozmiar system promptu.
- `/usage tokens` → dodaj stopkę z użyciem do zwykłych odpowiedzi.
- `/compact` → podsumuj starszą historię do zwartego wpisu, aby zwolnić miejsce w oknie.

Zobacz też: [Polecenia ukośnikowe](/pl/tools/slash-commands), [Użycie tokenów i koszty](/pl/reference/token-use), [Kompakcja](/pl/concepts/compaction).

## Przykładowe dane wyjściowe

Wartości różnią się zależnie od modelu, dostawcy, polityki narzędzi i tego, co znajduje się w Twoim obszarze roboczym.

### `/context list`

```
🧠 Podział kontekstu
Obszar roboczy: <workspaceDir>
Maks. bootstrap/pliku: 20,000 chars
Sandbox: mode=non-main sandboxed=false
System prompt (uruchomienie): 38,412 chars (~9,603 tok) (Project Context 23,901 chars (~5,976 tok))

Wstrzyknięte pliki obszaru roboczego:
- AGENTS.md: OK | raw 1,742 chars (~436 tok) | injected 1,742 chars (~436 tok)
- SOUL.md: OK | raw 912 chars (~228 tok) | injected 912 chars (~228 tok)
- TOOLS.md: TRUNCATED | raw 54,210 chars (~13,553 tok) | injected 20,962 chars (~5,241 tok)
- IDENTITY.md: OK | raw 211 chars (~53 tok) | injected 211 chars (~53 tok)
- USER.md: OK | raw 388 chars (~97 tok) | injected 388 chars (~97 tok)
- HEARTBEAT.md: MISSING | raw 0 | injected 0
- BOOTSTRAP.md: OK | raw 0 chars (~0 tok) | injected 0 chars (~0 tok)

Lista Skills (tekst system promptu): 2,184 chars (~546 tok) (12 skills)
Narzędzia: read, edit, write, exec, process, browser, message, sessions_send, …
Lista narzędzi (tekst system promptu): 1,032 chars (~258 tok)
Schematy narzędzi (JSON): 31,988 chars (~7,997 tok) (wliczają się do kontekstu; nie są pokazywane jako tekst)
Narzędzia: (takie same jak powyżej)

Tokeny sesji (z pamięci podręcznej): 14,250 total / ctx=32,000
```

### `/context detail`

```
🧠 Podział kontekstu (szczegółowy)
…
Największe Skills (rozmiar wpisu promptu):
- frontend-design: 412 chars (~103 tok)
- oracle: 401 chars (~101 tok)
… (+10 more skills)

Największe narzędzia (rozmiar schematu):
- browser: 9,812 chars (~2,453 tok)
- exec: 6,240 chars (~1,560 tok)
… (+N more tools)
```

## Co wlicza się do okna kontekstu

Wlicza się wszystko, co otrzymuje model, w tym:

- System prompt (wszystkie sekcje).
- Historia rozmowy.
- Wywołania narzędzi + wyniki narzędzi.
- Załączniki/transkrypcje (obrazy/audio/pliki).
- Podsumowania kompaktacji i artefakty przycinania.
- „Opakowania” dostawcy lub ukryte nagłówki (niewidoczne, ale nadal liczone).

## Jak OpenClaw buduje system prompt

System prompt jest **własnością OpenClaw** i jest przebudowywany przy każdym uruchomieniu. Zawiera:

- Listę narzędzi + krótkie opisy.
- Listę Skills (tylko metadane; zobacz niżej).
- Lokalizację obszaru roboczego.
- Czas (UTC + przeliczony czas użytkownika, jeśli skonfigurowano).
- Metadane środowiska uruchomieniowego (host/OS/model/thinking).
- Wstrzyknięte pliki bootstrap obszaru roboczego w sekcji **Project Context**.

Pełny opis: [System Prompt](/pl/concepts/system-prompt).

## Wstrzyknięte pliki obszaru roboczego (Project Context)

Domyślnie OpenClaw wstrzykuje stały zestaw plików obszaru roboczego (jeśli są obecne):

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md` (tylko przy pierwszym uruchomieniu)

Duże pliki są obcinane osobno dla każdego pliku zgodnie z `agents.defaults.bootstrapMaxChars` (domyślnie `20000` znaków). OpenClaw wymusza też łączny limit wstrzykiwania bootstrap dla wszystkich plików za pomocą `agents.defaults.bootstrapTotalMaxChars` (domyślnie `150000` znaków). `/context` pokazuje rozmiary **raw vs injected** oraz informację, czy doszło do obcięcia.

Gdy dochodzi do obcięcia, środowisko uruchomieniowe może wstrzyknąć blok ostrzeżenia bezpośrednio do promptu w sekcji Project Context. Skonfigurujesz to przez `agents.defaults.bootstrapPromptTruncationWarning` (`off`, `once`, `always`; domyślnie `once`).

## Skills: wstrzykiwane vs ładowane na żądanie

System prompt zawiera zwartą **listę Skills** (nazwa + opis + lokalizacja). Ta lista ma rzeczywisty narzut.

Instrukcje Skills _nie_ są domyślnie dołączane. Oczekuje się, że model odczyta `SKILL.md` danej umiejętności za pomocą `read` **tylko wtedy, gdy będzie to potrzebne**.

## Narzędzia: są dwa koszty

Narzędzia wpływają na kontekst na dwa sposoby:

1. **Tekst listy narzędzi** w system promptcie (to, co widzisz jako „Tooling”).
2. **Schematy narzędzi** (JSON). Są wysyłane do modelu, aby mógł wywoływać narzędzia. Wliczają się do kontekstu, mimo że nie widzisz ich jako zwykłego tekstu.

`/context detail` rozbija największe schematy narzędzi, aby pokazać, co dominuje.

## Polecenia, dyrektywy i „skróty inline”

Polecenia ukośnikowe są obsługiwane przez Gateway. Występuje tu kilka różnych zachowań:

- **Polecenia samodzielne**: wiadomość zawierająca wyłącznie `/...` jest uruchamiana jako polecenie.
- **Dyrektywy**: `/think`, `/verbose`, `/reasoning`, `/elevated`, `/model`, `/queue` są usuwane, zanim model zobaczy wiadomość.
  - Wiadomości zawierające wyłącznie dyrektywy utrwalają ustawienia sesji.
  - Dyrektywy inline w zwykłej wiadomości działają jako wskazówki tylko dla tej wiadomości.
- **Skróty inline** (tylko nadawcy z listy dozwolonych): określone tokeny `/...` wewnątrz zwykłej wiadomości mogą zostać uruchomione od razu (na przykład: „hej /status”) i są usuwane, zanim model zobaczy pozostały tekst.

Szczegóły: [Polecenia ukośnikowe](/pl/tools/slash-commands).

## Sesje, kompaktacja i przycinanie (co się utrzymuje)

To, co utrzymuje się między wiadomościami, zależy od mechanizmu:

- **Zwykła historia** utrzymuje się w transkrypcji sesji, dopóki nie zostanie skompaktowana/przycięta zgodnie z polityką.
- **Kompaktacja** zapisuje podsumowanie w transkrypcji i zachowuje nienaruszone ostatnie wiadomości.
- **Przycinanie** usuwa stare wyniki narzędzi z promptu _w pamięci_ dla danego uruchomienia, ale nie przepisuje transkrypcji.

Dokumentacja: [Sesja](/pl/concepts/session), [Kompaktacja](/pl/concepts/compaction), [Przycinanie sesji](/pl/concepts/session-pruning).

Domyślnie OpenClaw używa wbudowanego silnika kontekstu `legacy` do składania
i kompaktacji. Jeśli zainstalujesz plugin udostępniający `kind: "context-engine"` i
wybierzesz go przez `plugins.slots.contextEngine`, OpenClaw przekaże składanie
kontekstu, `/compact` i powiązane hooki cyklu życia kontekstu subagentów temu
silnikowi. `ownsCompaction: false` nie powoduje automatycznego powrotu do
silnika legacy; aktywny silnik nadal musi poprawnie implementować `compact()`. Zobacz
[Context Engine](/pl/concepts/context-engine), aby poznać pełny
interfejs rozszerzalny, hooki cyklu życia i konfigurację.

## Co faktycznie raportuje `/context`

`/context` preferuje najnowszy raport system promptu **zbudowany podczas uruchomienia**, gdy jest dostępny:

- `System prompt (run)` = przechwycony z ostatniego osadzonego uruchomienia (obsługującego narzędzia) i zapisany w magazynie sesji.
- `System prompt (estimate)` = obliczony na bieżąco, gdy raport z uruchomienia nie istnieje jeszcze.

W obu przypadkach raportuje rozmiary i największe składniki; **nie** zrzuca pełnego system promptu ani schematów narzędzi.

## Powiązane

- [Context Engine](/pl/concepts/context-engine) — niestandardowe wstrzykiwanie kontekstu przez pluginy
- [Kompaktacja](/pl/concepts/compaction) — podsumowywanie długich rozmów
- [System Prompt](/pl/concepts/system-prompt) — jak budowany jest system prompt
- [Pętla agenta](/pl/concepts/agent-loop) — pełny cykl wykonywania agenta
