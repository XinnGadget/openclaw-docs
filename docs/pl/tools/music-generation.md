---
read_when:
    - Generujesz muzykę lub audio za pomocą agenta
    - Konfigurujesz dostawców i modele do generowania muzyki
    - Chcesz zrozumieć parametry narzędzia `music_generate`
summary: Generowanie muzyki za pomocą współdzielonych dostawców, w tym pluginów opartych na workflow
title: Generowanie muzyki
x-i18n:
    generated_at: "2026-04-06T03:14:17Z"
    model: gpt-5.4
    provider: openai
    source_hash: a03de8aa75cfb7248eb0c1d969fb2a6da06117967d097e6f6e95771d0f017ae1
    source_path: tools/music-generation.md
    workflow: 15
---

# Generowanie muzyki

Narzędzie `music_generate` pozwala agentowi tworzyć muzykę lub audio za pomocą
współdzielonej funkcji generowania muzyki z użyciem skonfigurowanych dostawców, takich jak Google,
MiniMax i skonfigurowane przez workflow ComfyUI.

W przypadku sesji agentów opartych na współdzielonych dostawcach OpenClaw uruchamia generowanie muzyki jako
zadanie w tle, śledzi je w rejestrze zadań, a następnie ponownie wybudza agenta, gdy
utwór jest gotowy, aby agent mógł opublikować ukończone audio z powrotem w
oryginalnym kanale.

<Note>
Wbudowane współdzielone narzędzie pojawia się tylko wtedy, gdy dostępny jest co najmniej jeden dostawca generowania muzyki. Jeśli nie widzisz `music_generate` w narzędziach agenta, skonfiguruj `agents.defaults.musicGenerationModel` lub ustaw klucz API dostawcy.
</Note>

## Szybki start

### Generowanie oparte na współdzielonych dostawcach

1. Ustaw klucz API dla co najmniej jednego dostawcy, na przykład `GEMINI_API_KEY` lub
   `MINIMAX_API_KEY`.
2. Opcjonalnie ustaw preferowany model:

```json5
{
  agents: {
    defaults: {
      musicGenerationModel: {
        primary: "google/lyria-3-clip-preview",
      },
    },
  },
}
```

3. Poproś agenta: _"Wygeneruj energiczny utwór synthpop o nocnej przejażdżce
   przez neonowe miasto."_

Agent automatycznie wywoła `music_generate`. Nie trzeba dodawać go do listy zezwoleń narzędzi.

W bezpośrednich synchronicznych kontekstach bez uruchomienia agenta opartego na sesji wbudowane
narzędzie nadal wraca do generowania inline i zwraca końcową ścieżkę mediów w
wyniku narzędzia.

Przykładowe prompty:

```text
Wygeneruj filmowy utwór fortepianowy z delikatnymi smyczkami i bez wokalu.
```

```text
Wygeneruj energetyczną pętlę chiptune o starcie rakiety o wschodzie słońca.
```

### Generowanie Comfy sterowane przez workflow

Dołączony plugin `comfy` podłącza się do współdzielonego narzędzia `music_generate` przez
rejestr dostawców generowania muzyki.

1. Skonfiguruj `models.providers.comfy.music` z workflow JSON oraz
   węzłami promptu/wyjścia.
2. Jeśli używasz Comfy Cloud, ustaw `COMFY_API_KEY` lub `COMFY_CLOUD_API_KEY`.
3. Poproś agenta o muzykę lub wywołaj narzędzie bezpośrednio.

Przykład:

```text
/tool music_generate prompt="Ciepła ambientowa pętla syntezatorowa z miękką taśmową teksturą"
```

## Obsługa współdzielonych dołączonych dostawców

| Dostawca | Model domyślny         | Wejścia referencyjne | Obsługiwane kontrolki                                     | Klucz API                              |
| -------- | ---------------------- | -------------------- | --------------------------------------------------------- | -------------------------------------- |
| ComfyUI  | `workflow`             | Do 1 obrazu          | Muzyka lub audio zdefiniowane przez workflow              | `COMFY_API_KEY`, `COMFY_CLOUD_API_KEY` |
| Google   | `lyria-3-clip-preview` | Do 10 obrazów        | `lyrics`, `instrumental`, `format`                        | `GEMINI_API_KEY`, `GOOGLE_API_KEY`     |
| MiniMax  | `music-2.5+`           | Brak                 | `lyrics`, `instrumental`, `durationSeconds`, `format=mp3` | `MINIMAX_API_KEY`                      |

Użyj `action: "list"`, aby sprawdzić dostępnych współdzielonych dostawców i modele
w czasie działania:

```text
/tool music_generate action=list
```

Użyj `action: "status"`, aby sprawdzić aktywne zadanie muzyczne powiązane z sesją:

```text
/tool music_generate action=status
```

Przykład bezpośredniego generowania:

```text
/tool music_generate prompt="Marzycielski lo-fi hip hop z winylową teksturą i delikatnym deszczem" instrumental=true
```

## Parametry wbudowanego narzędzia

| Parametr          | Typ      | Opis                                                                                             |
| ----------------- | -------- | ------------------------------------------------------------------------------------------------ |
| `prompt`          | string   | Prompt generowania muzyki (wymagany dla `action: "generate"`)                                    |
| `action`          | string   | `"generate"` (domyślnie), `"status"` dla bieżącego zadania sesji lub `"list"` do sprawdzenia dostawców |
| `model`           | string   | Nadpisanie dostawcy/modelu, np. `google/lyria-3-pro-preview` lub `comfy/workflow`               |
| `lyrics`          | string   | Opcjonalny tekst utworu, gdy dostawca obsługuje jawne wejście tekstu                             |
| `instrumental`    | boolean  | Żądanie wyjścia wyłącznie instrumentalnego, gdy dostawca to obsługuje                            |
| `image`           | string   | Ścieżka lub URL pojedynczego obrazu referencyjnego                                               |
| `images`          | string[] | Wiele obrazów referencyjnych (do 10)                                                             |
| `durationSeconds` | number   | Docelowy czas trwania w sekundach, gdy dostawca obsługuje takie wskazówki                        |
| `format`          | string   | Wskazówka formatu wyjściowego (`mp3` lub `wav`), gdy dostawca to obsługuje                       |
| `filename`        | string   | Wskazówka nazwy pliku                                                                             |

Nie wszyscy dostawcy obsługują wszystkie parametry. OpenClaw nadal waliduje twarde limity,
takie jak liczba wejść, przed wysłaniem, ale nieobsługiwane opcjonalne wskazówki są
ignorowane z ostrzeżeniem, gdy wybrany dostawca lub model nie może ich uwzględnić.

## Zachowanie asynchroniczne dla ścieżki opartej na współdzielonych dostawcach

- Uruchomienia agentów powiązane z sesją: `music_generate` tworzy zadanie w tle, natychmiast zwraca odpowiedź started/task i później publikuje gotowy utwór w kolejnej wiadomości agenta.
- Zapobieganie duplikatom: dopóki to zadanie w tle ma stan `queued` lub `running`, kolejne wywołania `music_generate` w tej samej sesji zwracają status zadania zamiast uruchamiać kolejne generowanie.
- Sprawdzanie statusu: użyj `action: "status"`, aby sprawdzić aktywne zadanie muzyczne powiązane z sesją bez uruchamiania nowego.
- Śledzenie zadań: użyj `openclaw tasks list` lub `openclaw tasks show <taskId>`, aby sprawdzić status `queued`, `running` i terminalny dla generowania.
- Wybudzenie po zakończeniu: OpenClaw wstrzykuje wewnętrzne zdarzenie zakończenia z powrotem do tej samej sesji, aby model mógł sam napisać widoczną dla użytkownika wiadomość uzupełniającą.
- Wskazówka promptu: późniejsze tury użytkownika/ręczne w tej samej sesji dostają małą wskazówkę środowiska uruchomieniowego, gdy zadanie muzyczne jest już w toku, aby model nie wywoływał bezrefleksyjnie `music_generate` ponownie.
- Zapas bez sesji: bezpośrednie/lokalne konteksty bez rzeczywistej sesji agenta nadal działają inline i zwracają końcowy wynik audio w tej samej turze.

## Konfiguracja

### Wybór modelu

```json5
{
  agents: {
    defaults: {
      musicGenerationModel: {
        primary: "google/lyria-3-clip-preview",
        fallbacks: ["minimax/music-2.5+"],
      },
    },
  },
}
```

### Kolejność wyboru dostawcy

Podczas generowania muzyki OpenClaw próbuje dostawców w tej kolejności:

1. parametr `model` z wywołania narzędzia, jeśli agent go określi
2. `musicGenerationModel.primary` z konfiguracji
3. `musicGenerationModel.fallbacks` w podanej kolejności
4. automatyczne wykrywanie z użyciem tylko domyślnych dostawców opartych na uwierzytelnieniu:
   - najpierw bieżący dostawca domyślny
   - następnie pozostali zarejestrowani dostawcy generowania muzyki w kolejności identyfikatorów dostawców

Jeśli jeden dostawca zawiedzie, automatycznie próbowany jest kolejny kandydat. Jeśli zawiodą wszystkie,
błąd zawiera szczegóły każdej próby.

## Uwagi o dostawcach

- Google używa wsadowego generowania Lyria 3. Bieżący dołączony przepływ obsługuje
  prompt, opcjonalny tekst utworu i opcjonalne obrazy referencyjne.
- MiniMax używa wsadowego endpointu `music_generation`. Bieżący dołączony przepływ
  obsługuje prompt, opcjonalny tekst utworu, tryb instrumentalny, sterowanie czasem trwania i
  wyjście mp3.
- Obsługa ComfyUI jest sterowana przez workflow i zależy od skonfigurowanego grafu oraz
  mapowania węzłów dla pól promptu/wyjścia.

## Wybór właściwej ścieżki

- Użyj ścieżki opartej na współdzielonych dostawcach, gdy chcesz mieć wybór modelu, failover dostawców i wbudowany asynchroniczny przepływ zadań/statusu.
- Użyj ścieżki plugin, takiej jak ComfyUI, gdy potrzebujesz niestandardowego grafu workflow lub dostawcy, który nie jest częścią współdzielonej dołączonej funkcji generowania muzyki.
- Jeśli debugujesz zachowanie specyficzne dla ComfyUI, zobacz [ComfyUI](/providers/comfy). Jeśli debugujesz zachowanie współdzielonych dostawców, zacznij od [Google (Gemini)](/pl/providers/google) lub [MiniMax](/pl/providers/minimax).

## Testy live

Opcjonalny zakres testów live dla współdzielonych dołączonych dostawców:

```bash
OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/music-generation-providers.live.test.ts
```

Opcjonalny zakres testów live dla dołączonej ścieżki muzycznej ComfyUI:

```bash
OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts
```

Plik live dla Comfy obejmuje również workflow obrazów i wideo Comfy, gdy te
sekcje są skonfigurowane.

## Powiązane

- [Background Tasks](/pl/automation/tasks) - śledzenie zadań dla odłączonych uruchomień `music_generate`
- [Configuration Reference](/pl/gateway/configuration-reference#agent-defaults) - konfiguracja `musicGenerationModel`
- [ComfyUI](/providers/comfy)
- [Google (Gemini)](/pl/providers/google)
- [MiniMax](/pl/providers/minimax)
- [Models](/pl/concepts/models) - konfiguracja modeli i failover
- [Tools Overview](/pl/tools)
