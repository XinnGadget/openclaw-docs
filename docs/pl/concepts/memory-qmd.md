---
read_when:
    - Chcesz skonfigurować QMD jako backend pamięci
    - Chcesz korzystać z zaawansowanych funkcji pamięci, takich jak reranking lub dodatkowe indeksowane ścieżki
summary: Lokalny sidecar wyszukiwania z podejściem local-first, z BM25, wektorami, rerankingiem i rozszerzaniem zapytań
title: Silnik pamięci QMD
x-i18n:
    generated_at: "2026-04-12T23:28:03Z"
    model: gpt-5.4
    provider: openai
    source_hash: 27afc996b959d71caed964a3cae437e0e29721728b30ebe7f014db124c88da04
    source_path: concepts/memory-qmd.md
    workflow: 15
---

# Silnik pamięci QMD

[QMD](https://github.com/tobi/qmd) to sidecar wyszukiwania local-first, który działa
obok OpenClaw. Łączy BM25, wyszukiwanie wektorowe i reranking w jednym
binarium, a także może indeksować treści wykraczające poza pliki pamięci w Twoim obszarze roboczym.

## Co dodaje w porównaniu z wbudowanym rozwiązaniem

- **Reranking i rozszerzanie zapytań** dla lepszego recall.
- **Indeksowanie dodatkowych katalogów** — dokumentacja projektu, notatki zespołu, wszystko na dysku.
- **Indeksowanie transkryptów sesji** — przywoływanie wcześniejszych rozmów.
- **W pełni lokalne** — działa przez Bun + node-llama-cpp, automatycznie pobiera modele GGUF.
- **Automatyczny fallback** — jeśli QMD jest niedostępne, OpenClaw płynnie przełącza się na
  wbudowany silnik.

## Pierwsze kroki

### Wymagania wstępne

- Zainstaluj QMD: `npm install -g @tobilu/qmd` lub `bun install -g @tobilu/qmd`
- Kompilacja SQLite, która pozwala na rozszerzenia (`brew install sqlite` na macOS).
- QMD musi znajdować się w `PATH` bramy.
- macOS i Linux działają od razu. Windows jest najlepiej wspierany przez WSL2.

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
— kolekcje, aktualizacje i uruchomienia osadzania są obsługiwane za Ciebie.
Preferuje bieżące kształty kolekcji QMD i zapytań MCP, ale nadal wraca do
starszych flag kolekcji `--mask` i starszych nazw narzędzi MCP, gdy jest to potrzebne.

## Jak działa sidecar

- OpenClaw tworzy kolekcje z plików pamięci Twojego obszaru roboczego oraz wszystkich
  skonfigurowanych `memory.qmd.paths`, a następnie uruchamia `qmd update` + `qmd embed` przy starcie
  i okresowo (domyślnie co 5 minut).
- Domyślna kolekcja obszaru roboczego śledzi `MEMORY.md` oraz drzewo `memory/`.
  Małe litery w `memory.md` pozostają fallbackiem bootstrapowym, a nie oddzielną kolekcją QMD.
- Odświeżanie przy starcie działa w tle, więc uruchamianie czatu nie jest blokowane.
- Wyszukiwania używają skonfigurowanego `searchMode` (domyślnie: `search`; obsługiwane są też
  `vsearch` i `query`). Jeśli dany tryb zawiedzie, OpenClaw ponawia próbę z `qmd query`.
- Jeśli QMD całkowicie zawiedzie, OpenClaw przełącza się na wbudowany silnik SQLite.

<Info>
Pierwsze wyszukiwanie może być wolne — QMD automatycznie pobiera modele GGUF (~2 GB) do
rerankingu i rozszerzania zapytań przy pierwszym uruchomieniu `qmd query`.
</Info>

## Nadpisania modeli

Zmienne środowiskowe modeli QMD są przekazywane bez zmian z procesu bramy,
więc możesz globalnie dostroić QMD bez dodawania nowej konfiguracji OpenClaw:

```bash
export QMD_EMBED_MODEL="hf:Qwen/Qwen3-Embedding-0.6B-GGUF/Qwen3-Embedding-0.6B-Q8_0.gguf"
export QMD_RERANK_MODEL="/absolute/path/to/reranker.gguf"
export QMD_GENERATE_MODEL="/absolute/path/to/generator.gguf"
```

Po zmianie modelu osadzania uruchom ponownie osadzanie, aby indeks pasował do
nowej przestrzeni wektorowej.

## Indeksowanie dodatkowych ścieżek

Skieruj QMD na dodatkowe katalogi, aby można było je przeszukiwać:

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
wynikach wyszukiwania. `memory_get` rozumie ten prefiks i odczytuje z poprawnego
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

Transkrypty są eksportowane jako oczyszczone tury User/Assistant do dedykowanej
kolekcji QMD w `~/.openclaw/agents/<id>/qmd/sessions/`.

## Zakres wyszukiwania

Domyślnie wyniki wyszukiwania QMD są udostępniane w sesjach bezpośrednich i kanałowych
(nie grupowych). Aby to zmienić, skonfiguruj `memory.qmd.scope`:

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

Gdy zakres zabrania wyszukiwania, OpenClaw zapisuje ostrzeżenie z wyliczonym kanałem i
typem czatu, dzięki czemu łatwiej diagnozować puste wyniki.

## Cytowania

Gdy `memory.citations` ma wartość `auto` lub `on`, fragmenty wyszukiwania zawierają
stopkę `Source: <path#line>`. Ustaw `memory.citations = "off"`, aby pominąć stopkę,
zachowując jednocześnie przekazywanie ścieżki wewnętrznie do agenta.

## Kiedy używać

Wybierz QMD, gdy potrzebujesz:

- Rerankingu dla wyników wyższej jakości.
- Przeszukiwać dokumentację projektu lub notatki poza obszarem roboczym.
- Przywoływać wcześniejsze rozmowy z sesji.
- W pełni lokalnego wyszukiwania bez kluczy API.

W prostszych konfiguracjach [wbudowany silnik](/pl/concepts/memory-builtin) sprawdza się dobrze
bez dodatkowych zależności.

## Rozwiązywanie problemów

**Nie znaleziono QMD?** Upewnij się, że binarium jest w `PATH` bramy. Jeśli OpenClaw
działa jako usługa, utwórz dowiązanie symboliczne:
`sudo ln -s ~/.bun/bin/qmd /usr/local/bin/qmd`.

**Pierwsze wyszukiwanie jest bardzo wolne?** QMD pobiera modele GGUF przy pierwszym użyciu. Rozgrzej je wcześniej
poleceniem `qmd query "test"` z użyciem tych samych katalogów XDG, których używa OpenClaw.

**Wyszukiwanie przekracza limit czasu?** Zwiększ `memory.qmd.limits.timeoutMs` (domyślnie: 4000 ms).
Ustaw `120000` dla wolniejszego sprzętu.

**Puste wyniki w czatach grupowych?** Sprawdź `memory.qmd.scope` — domyślnie
dozwolone są tylko sesje bezpośrednie i kanałowe.

**Tymczasowe repozytoria widoczne w obszarze roboczym powodują `ENAMETOOLONG` lub błędne indeksowanie?**
Przechodzenie przez drzewo w QMD obecnie podąża za zachowaniem bazowego skanera QMD zamiast
zasad dowiązań symbolicznych wbudowanych w OpenClaw. Trzymaj tymczasowe checkouty monorepo w
ukrytych katalogach takich jak `.tmp/` lub poza indeksowanymi katalogami głównymi QMD, dopóki QMD nie udostępni
bezpiecznego przechodzenia po cyklach albo jawnych mechanizmów wykluczania.

## Konfiguracja

Aby zobaczyć pełną powierzchnię konfiguracji (`memory.qmd.*`), tryby wyszukiwania, interwały aktualizacji,
reguły zakresu i wszystkie pozostałe ustawienia, zobacz
[Dokumentację konfiguracji pamięci](/pl/reference/memory-config).
