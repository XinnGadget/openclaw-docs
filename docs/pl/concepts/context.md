---
read_when:
    - Chcesz zrozumieć, co oznacza „kontekst” w OpenClaw
    - Debugujesz, dlaczego model „wie” coś (albo o tym zapomniał)
    - Chcesz zmniejszyć narzut kontekstu (`/context`, `/status`, `/compact`)
summary: 'Kontekst: co widzi model, jak jest zbudowany i jak go sprawdzić'
title: Kontekst
x-i18n:
    generated_at: "2026-04-12T23:28:04Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3620db1a8c1956d91a01328966df491388d3a32c4003dc4447197eb34316c77d
    source_path: concepts/context.md
    workflow: 15
---

# Kontekst

„Kontekst” to **wszystko, co OpenClaw wysyła do modelu dla danego uruchomienia**. Jest on ograniczony przez **okno kontekstowe** modelu (limit tokenów).

Model mentalny dla początkujących:

- **System prompt** (zbudowany przez OpenClaw): reguły, narzędzia, lista Skills, czas/środowisko uruchomieniowe oraz wstrzyknięte pliki workspace.
- **Historia rozmowy**: Twoje wiadomości + wiadomości asystenta dla tej sesji.
- **Wywołania/wyniki narzędzi + załączniki**: wyniki poleceń, odczyty plików, obrazy/audio itd.

Kontekst _nie jest tym samym_ co „pamięć”: pamięć może być zapisana na dysku i wczytana później; kontekst to to, co znajduje się w bieżącym oknie modelu.

## Szybki start (sprawdzanie kontekstu)

- `/status` → szybki widok „jak bardzo zapełnione jest moje okno?” + ustawienia sesji.
- `/context list` → co jest wstrzyknięte + przybliżone rozmiary (dla każdego pliku + łącznie).
- `/context detail` → głębszy rozkład: rozmiary dla każdego pliku, dla każdego schematu narzędzia, dla każdego wpisu Skills oraz rozmiar system promptu.
- `/usage tokens` → dołącza stopkę z użyciem tokenów do zwykłych odpowiedzi.
- `/compact` → podsumowuje starszą historię do zwartego wpisu, aby zwolnić miejsce w oknie.

Zobacz też: [Polecenia slash](/pl/tools/slash-commands), [Użycie tokenów i koszty](/pl/reference/token-use), [Compaction](/pl/concepts/compaction).

## Przykładowe dane wyjściowe

Wartości różnią się w zależności od modelu, dostawcy, polityki narzędzi i tego, co znajduje się w Twoim workspace.

### `/context list`

```
🧠 Rozkład kontekstu
Workspace: <workspaceDir>
Maks. bootstrap/plik: 20,000 chars
Sandbox: mode=non-main sandboxed=false
System prompt (uruchomienie): 38,412 chars (~9,603 tok) (Project Context 23,901 chars (~5,976 tok))

Wstrzyknięte pliki workspace:
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
Schematy narzędzi (JSON): 31,988 chars (~7,997 tok) (wliczają się do kontekstu; nie są pokazane jako tekst)
Narzędzia: (takie same jak powyżej)

Tokeny sesji (z cache): 14,250 łącznie / ctx=32,000
```

### `/context detail`

```
🧠 Rozkład kontekstu (szczegółowy)
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

## Co wlicza się do okna kontekstowego

Wlicza się wszystko, co otrzymuje model, w tym:

- System prompt (wszystkie sekcje).
- Historia rozmowy.
- Wywołania narzędzi + wyniki narzędzi.
- Załączniki/transkrypcje (obrazy/audio/pliki).
- Podsumowania Compaction i artefakty przycinania.
- „Opakowania” dostawcy lub ukryte nagłówki (niewidoczne, ale nadal liczone).

## Jak OpenClaw buduje system prompt

System prompt jest **własnością OpenClaw** i jest przebudowywany przy każdym uruchomieniu. Zawiera:

- Listę narzędzi + krótkie opisy.
- Listę Skills (tylko metadane; zobacz niżej).
- Lokalizację workspace.
- Czas (UTC + przeliczony czas użytkownika, jeśli skonfigurowano).
- Metadane środowiska uruchomieniowego (host/OS/model/myślenie).
- Wstrzyknięte pliki bootstrap workspace w sekcji **Project Context**.

Pełny opis: [System Prompt](/pl/concepts/system-prompt).

## Wstrzyknięte pliki workspace (Project Context)

Domyślnie OpenClaw wstrzykuje stały zestaw plików workspace (jeśli istnieją):

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md` (tylko przy pierwszym uruchomieniu)

Duże pliki są przycinane osobno dla każdego pliku zgodnie z `agents.defaults.bootstrapMaxChars` (domyślnie `20000` znaków). OpenClaw wymusza także łączny limit wstrzykiwania bootstrap dla wszystkich plików przez `agents.defaults.bootstrapTotalMaxChars` (domyślnie `150000` znaków). `/context` pokazuje rozmiary **raw vs injected** oraz to, czy wystąpiło przycięcie.

Gdy dochodzi do przycięcia, środowisko uruchomieniowe może wstrzyknąć ostrzeżenie bezpośrednio w prompt w sekcji Project Context. Skonfigurujesz to przez `agents.defaults.bootstrapPromptTruncationWarning` (`off`, `once`, `always`; domyślnie `once`).

## Skills: wstrzyknięte vs ładowane na żądanie

System prompt zawiera zwartą **listę Skills** (nazwa + opis + lokalizacja). Ta lista ma realny narzut.

Instrukcje Skills _nie są_ domyślnie dołączane. Oczekuje się, że model odczyta `SKILL.md` danej umiejętności przez `read` **tylko wtedy, gdy jest to potrzebne**.

## Narzędzia: są dwa koszty

Narzędzia wpływają na kontekst na dwa sposoby:

1. **Tekst listy narzędzi** w system prompcie (to, co widzisz jako „Tooling”).
2. **Schematy narzędzi** (JSON). Są wysyłane do modelu, aby mógł wywoływać narzędzia. Wliczają się do kontekstu, mimo że nie widzisz ich jako zwykłego tekstu.

`/context detail` rozbija największe schematy narzędzi, aby pokazać, co dominuje.

## Polecenia, dyrektywy i „skróty inline”

Polecenia slash są obsługiwane przez Gateway. Występuje tu kilka różnych zachowań:

- **Polecenia samodzielne**: wiadomość zawierająca wyłącznie `/...` jest uruchamiana jako polecenie.
- **Dyrektywy**: `/think`, `/verbose`, `/trace`, `/reasoning`, `/elevated`, `/model`, `/queue` są usuwane, zanim model zobaczy wiadomość.
  - Wiadomości zawierające wyłącznie dyrektywy utrwalają ustawienia sesji.
  - Dyrektywy inline w zwykłej wiadomości działają jako wskazówki dla tej konkretnej wiadomości.
- **Skróty inline** (tylko dla nadawców z allowlisty): niektóre tokeny `/...` w zwykłej wiadomości mogą zostać uruchomione natychmiast (na przykład: „hej /status”) i są usuwane, zanim model zobaczy pozostały tekst.

Szczegóły: [Polecenia slash](/pl/tools/slash-commands).

## Sesje, Compaction i przycinanie (co jest trwałe)

To, co pozostaje między wiadomościami, zależy od mechanizmu:

- **Zwykła historia** pozostaje w transkrypcie sesji, dopóki nie zostanie skompaktowana/przycięta zgodnie z polityką.
- **Compaction** zapisuje podsumowanie w transkrypcie i zachowuje nienaruszone ostatnie wiadomości.
- **Pruning** usuwa stare wyniki narzędzi z promptu _w pamięci_ dla danego uruchomienia, ale nie przepisuje transkryptu.

Dokumentacja: [Session](/pl/concepts/session), [Compaction](/pl/concepts/compaction), [Session pruning](/pl/concepts/session-pruning).

Domyślnie OpenClaw używa wbudowanego silnika kontekstu `legacy` do składania kontekstu i
Compaction. Jeśli zainstalujesz Plugin, który udostępnia `kind: "context-engine"` i
wybierzesz go za pomocą `plugins.slots.contextEngine`, OpenClaw przekaże temu
silnikowi składanie kontekstu, `/compact` oraz powiązane hooki cyklu życia
kontekstu subagenta. `ownsCompaction: false` nie powoduje automatycznego powrotu
do silnika `legacy`; aktywny silnik nadal musi poprawnie implementować `compact()`. Zobacz
[Context Engine](/pl/concepts/context-engine), aby poznać pełny
interfejs z możliwością podłączania, hooki cyklu życia i konfigurację.

## Co tak naprawdę raportuje `/context`

`/context` preferuje najnowszy raport system promptu **zbudowanego podczas uruchomienia**, jeśli jest dostępny:

- `System prompt (run)` = przechwycony z ostatniego osadzonego uruchomienia (z obsługą narzędzi) i utrwalony w magazynie sesji.
- `System prompt (estimate)` = obliczany na bieżąco, gdy nie istnieje raport z uruchomienia (lub gdy uruchamiasz przez backend CLI, który nie generuje raportu).

W obu przypadkach raportuje rozmiary i największe składniki; **nie** zrzuca pełnego system promptu ani schematów narzędzi.

## Powiązane

- [Context Engine](/pl/concepts/context-engine) — niestandardowe wstrzykiwanie kontekstu przez pluginy
- [Compaction](/pl/concepts/compaction) — podsumowywanie długich rozmów
- [System Prompt](/pl/concepts/system-prompt) — jak budowany jest system prompt
- [Agent Loop](/pl/concepts/agent-loop) — pełny cykl działania agenta
