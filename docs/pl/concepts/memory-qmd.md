---
read_when:
    - Chcesz skonfigurować QMD jako backend pamięci
    - Chcesz korzystać z zaawansowanych funkcji pamięci, takich jak reranking lub dodatkowe indeksowane ścieżki
summary: Lokalny sidecar wyszukiwania z BM25, wektorami, rerankingiem i rozwijaniem zapytań
title: Silnik pamięci QMD
x-i18n:
    generated_at: "2026-04-06T03:06:19Z"
    model: gpt-5.4
    provider: openai
    source_hash: 36642c7df94b88f562745dd2270334379f2aeeef4b363a8c13ef6be42dadbe5c
    source_path: concepts/memory-qmd.md
    workflow: 15
---

# Silnik pamięci QMD

[QMD](https://github.com/tobi/qmd) to lokalny sidecar wyszukiwania, który działa
obok OpenClaw. Łączy BM25, wyszukiwanie wektorowe i reranking w jednym
pliku binarnym oraz może indeksować treści wykraczające poza pliki pamięci w obszarze roboczym.

## Co dodaje względem wbudowanego rozwiązania

- **Reranking i rozwijanie zapytań** dla lepszego recall.
- **Indeksowanie dodatkowych katalogów** -- dokumentacji projektu, notatek zespołu, wszystkiego na dysku.
- **Indeksowanie transkryptów sesji** -- przywoływanie wcześniejszych rozmów.
- **W pełni lokalne** -- działa przez Bun + node-llama-cpp, automatycznie pobiera modele GGUF.
- **Automatyczny fallback** -- jeśli QMD jest niedostępne, OpenClaw płynnie wraca do
  wbudowanego silnika.

## Pierwsze kroki

### Wymagania wstępne

- Zainstaluj QMD: `npm install -g @tobilu/qmd` lub `bun install -g @tobilu/qmd`
- Kompilacja SQLite, która pozwala na rozszerzenia (`brew install sqlite` na macOS).
- QMD musi być dostępne w `PATH` bramy.
- macOS i Linux działają od razu. Windows jest najlepiej obsługiwany przez WSL2.

### Włączanie

```json5
{
  memory: {
    backend: "qmd",
  },
}
```

OpenClaw tworzy samowystarczalny katalog domowy QMD w
`~/.openclaw/agents/<agentId>/qmd/` i automatycznie zarządza cyklem życia sidecara
-- kolekcje, aktualizacje i uruchomienia osadzania są obsługiwane automatycznie.
Preferuje bieżące kształty kolekcji QMD i zapytań MCP, ale w razie potrzeby nadal wraca do
starszych flag kolekcji `--mask` i starszych nazw narzędzi MCP.

## Jak działa sidecar

- OpenClaw tworzy kolekcje z plików pamięci w obszarze roboczym oraz ze wszystkich
  skonfigurowanych `memory.qmd.paths`, a następnie uruchamia `qmd update` + `qmd embed` przy starcie
  i okresowo (domyślnie co 5 minut).
- Odświeżanie przy starcie działa w tle, więc uruchamianie czatu nie jest blokowane.
- Wyszukiwania używają skonfigurowanego `searchMode` (domyślnie: `search`; obsługuje też
  `vsearch` i `query`). Jeśli dany tryb zawiedzie, OpenClaw ponawia próbę za pomocą `qmd query`.
- Jeśli QMD całkowicie zawiedzie, OpenClaw wraca do wbudowanego silnika SQLite.

<Info>
Pierwsze wyszukiwanie może być wolne -- QMD automatycznie pobiera modele GGUF (~2 GB) do
rerankingu i rozwijania zapytań przy pierwszym uruchomieniu `qmd query`.
</Info>

## Nadpisania modeli

Zmienne środowiskowe modeli QMD są przekazywane bez zmian z procesu bramy,
więc możesz globalnie dostrajać QMD bez dodawania nowej konfiguracji OpenClaw:

```bash
export QMD_EMBED_MODEL="hf:Qwen/Qwen3-Embedding-0.6B-GGUF/Qwen3-Embedding-0.6B-Q8_0.gguf"
export QMD_RERANK_MODEL="/absolute/path/to/reranker.gguf"
export QMD_GENERATE_MODEL="/absolute/path/to/generator.gguf"
```

Po zmianie modelu osadzania uruchom ponownie osadzanie, aby indeks odpowiadał
nowej przestrzeni wektorowej.

## Indeksowanie dodatkowych ścieżek

Skieruj QMD na dodatkowe katalogi, aby stały się przeszukiwalne:

```json5
{
  memory: {
    backend: "qmd",
    qmd: {
      paths: [{ name: "docs", path: "~/notes", pattern: "**/*.md" }],
    },
  },
}
```

Fragmenty z dodatkowych ścieżek pojawiają się jako `qmd/<collection>/<relative-path>` w
wynikach wyszukiwania. `memory_get` rozumie ten prefiks i odczytuje z właściwego
katalogu głównego kolekcji.

## Indeksowanie transkryptów sesji

Włącz indeksowanie sesji, aby przywoływać wcześniejsze rozmowy:

```json5
{
  memory: {
    backend: "qmd",
    qmd: {
      sessions: { enabled: true },
    },
  },
}
```

Transkrypty są eksportowane jako oczyszczone tury Użytkownik/Asystent do dedykowanej
kolekcji QMD w `~/.openclaw/agents/<id>/qmd/sessions/`.

## Zakres wyszukiwania

Domyślnie wyniki wyszukiwania QMD są udostępniane tylko w sesjach DM (nie w grupach ani
kanałach). Skonfiguruj `memory.qmd.scope`, aby to zmienić:

```json5
{
  memory: {
    qmd: {
      scope: {
        default: "deny",
        rules: [{ action: "allow", match: { chatType: "direct" } }],
      },
    },
  },
}
```

Gdy zakres odrzuca wyszukiwanie, OpenClaw zapisuje ostrzeżenie z wyprowadzonym kanałem i
typem czatu, aby łatwiej było diagnozować puste wyniki.

## Cytowania

Gdy `memory.citations` ma wartość `auto` lub `on`, fragmenty wyszukiwania zawierają
stopkę `Source: <path#line>`. Ustaw `memory.citations = "off"`, aby pominąć stopkę,
jednocześnie nadal przekazując ścieżkę agentowi wewnętrznie.

## Kiedy używać

Wybierz QMD, gdy potrzebujesz:

- Rerankingu dla wyników wyższej jakości.
- Przeszukiwania dokumentacji projektu lub notatek poza obszarem roboczym.
- Przywoływania wcześniejszych rozmów z sesji.
- W pełni lokalnego wyszukiwania bez kluczy API.

W prostszych konfiguracjach [wbudowany silnik](/pl/concepts/memory-builtin) sprawdza się dobrze
bez dodatkowych zależności.

## Rozwiązywanie problemów

**Nie znaleziono QMD?** Upewnij się, że plik binarny jest w `PATH` bramy. Jeśli OpenClaw
działa jako usługa, utwórz dowiązanie symboliczne:
`sudo ln -s ~/.bun/bin/qmd /usr/local/bin/qmd`.

**Pierwsze wyszukiwanie jest bardzo wolne?** QMD pobiera modele GGUF przy pierwszym użyciu. Wstępnie rozgrzej
je poleceniem `qmd query "test"` z użyciem tych samych katalogów XDG, których używa OpenClaw.

**Wyszukiwanie przekracza limit czasu?** Zwiększ `memory.qmd.limits.timeoutMs` (domyślnie: 4000ms).
Ustaw `120000` dla wolniejszego sprzętu.

**Puste wyniki w czatach grupowych?** Sprawdź `memory.qmd.scope` -- domyślna konfiguracja
zezwala tylko na sesje DM.

**Tymczasowe repozytoria widoczne w obszarze roboczym powodują `ENAMETOOLONG` lub błędne indeksowanie?**
Przechodzenie QMD obecnie podąża za bazowym zachowaniem skanera QMD zamiast
wbudowanych reguł dowiązań symbolicznych OpenClaw. Trzymaj tymczasowe checkouty monorepo w
ukrytych katalogach, takich jak `.tmp/`, lub poza indeksowanymi katalogami głównymi QMD, dopóki QMD nie udostępni
odpornego na cykle przechodzenia lub jawnych mechanizmów wykluczania.

## Konfiguracja

Pełny opis powierzchni konfiguracji (`memory.qmd.*`), trybów wyszukiwania, interwałów aktualizacji,
reguł zakresu i wszystkich pozostałych ustawień znajdziesz w
[referencji konfiguracji pamięci](/pl/reference/memory-config).
