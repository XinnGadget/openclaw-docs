---
read_when:
    - Chcesz trwałej wiedzy wykraczającej poza zwykłe notatki w `MEMORY.md`
    - Konfigurujesz dołączony Plugin memory-wiki
    - Chcesz zrozumieć `wiki_search`, `wiki_get` lub tryb bridge
summary: 'memory-wiki: skompilowany sejf wiedzy z proweniencją, twierdzeniami, dashboardami i trybem bridge'
title: Memory Wiki
x-i18n:
    generated_at: "2026-04-12T23:28:47Z"
    model: gpt-5.4
    provider: openai
    source_hash: 44d168a7096f744c56566ecac57499192eb101b4dd8a78e1b92f3aa0d6da3ad1
    source_path: plugins/memory-wiki.md
    workflow: 15
---

# Memory Wiki

`memory-wiki` to dołączony Plugin, który przekształca trwałą pamięć w skompilowany
sejf wiedzy.

Nie zastępuje on Pluginu Active Memory. Plugin Active Memory nadal
odpowiada za recall, promotion, indexing i Dreaming. `memory-wiki` działa obok niego
i kompiluje trwałą wiedzę do postaci nawigowalnego wiki z deterministycznymi stronami,
ustrukturyzowanymi twierdzeniami, proweniencją, dashboardami i odczytywalnymi maszynowo digestami.

Używaj go, gdy chcesz, aby pamięć zachowywała się bardziej jak utrzymywana warstwa wiedzy,
a mniej jak stos plików Markdown.

## Co dodaje

- Dedykowany sejf wiki z deterministycznym układem stron
- Ustrukturyzowane metadane twierdzeń i dowodów, a nie tylko proza
- Proweniencję, poziom pewności, sprzeczności i otwarte pytania na poziomie strony
- Skompilowane digests dla agentów i konsumentów runtime
- Natywne dla wiki narzędzia search/get/apply/lint
- Opcjonalny tryb bridge, który importuje publiczne artefakty z Pluginu Active Memory
- Opcjonalny tryb renderowania przyjazny dla Obsidian oraz integrację z CLI

## Jak to pasuje do pamięci

Pomyśl o tym podziale w ten sposób:

| Warstwa                                                 | Odpowiada za                                                                              |
| ------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Plugin Active Memory (`memory-core`, QMD, Honcho itp.)  | Recall, wyszukiwanie semantyczne, promotion, Dreaming, runtime pamięci                    |
| `memory-wiki`                                           | Skompilowane strony wiki, syntezy bogate w proweniencję, dashboardy, specyficzne dla wiki search/get/apply |

Jeśli Plugin Active Memory udostępnia współdzielone artefakty recall, OpenClaw może przeszukiwać
obie warstwy w jednym przebiegu za pomocą `memory_search corpus=all`.

Gdy potrzebujesz rankingu specyficznego dla wiki, proweniencji lub bezpośredniego dostępu do stron,
użyj zamiast tego narzędzi natywnych dla wiki.

## Zalecany wzorzec hybrydowy

Mocną domyślną konfiguracją dla lokalnych środowisk jest:

- QMD jako backend Active Memory dla recall i szerokiego wyszukiwania semantycznego
- `memory-wiki` w trybie `bridge` dla trwałych stron wiedzy syntetyzowanej

Ten podział działa dobrze, ponieważ każda warstwa pozostaje skoncentrowana na swoim zadaniu:

- QMD utrzymuje możliwość przeszukiwania surowych notatek, eksportów sesji i dodatkowych kolekcji
- `memory-wiki` kompiluje stabilne encje, twierdzenia, dashboardy i strony źródłowe

Praktyczna zasada:

- użyj `memory_search`, gdy chcesz wykonać jeden szeroki przebieg recall przez pamięć
- użyj `wiki_search` i `wiki_get`, gdy chcesz wyników wiki uwzględniających proweniencję
- użyj `memory_search corpus=all`, gdy chcesz, aby współdzielone wyszukiwanie obejmowało obie warstwy

Jeśli tryb bridge zgłasza zero wyeksportowanych artefaktów, Plugin Active Memory
obecnie jeszcze nie udostępnia publicznych danych wejściowych bridge. Najpierw uruchom `openclaw wiki doctor`,
a następnie potwierdź, że Plugin Active Memory obsługuje publiczne artefakty.

## Tryby sejfu

`memory-wiki` obsługuje trzy tryby sejfu:

### `isolated`

Własny sejf, własne źródła, bez zależności od `memory-core`.

Użyj tego, gdy chcesz, aby wiki było własnym kuratorowanym magazynem wiedzy.

### `bridge`

Odczytuje publiczne artefakty pamięci i zdarzenia pamięci z Pluginu Active Memory
przez publiczne seamy Plugin SDK.

Użyj tego, gdy chcesz, aby wiki kompilowało i porządkowało wyeksportowane artefakty
Pluginu pamięci bez sięgania do prywatnych wnętrzności Pluginu.

Tryb bridge może indeksować:

- wyeksportowane artefakty pamięci
- raporty Dreaming
- notatki dzienne
- pliki główne pamięci
- logi zdarzeń pamięci

### `unsafe-local`

Jawna furtka awaryjna dla lokalnych prywatnych ścieżek na tym samym komputerze.

Ten tryb jest celowo eksperymentalny i nieprzenośny. Używaj go tylko wtedy, gdy
rozumiesz granicę zaufania i konkretnie potrzebujesz lokalnego dostępu do systemu plików,
którego tryb bridge nie może zapewnić.

## Układ sejfu

Plugin inicjalizuje sejf w taki sposób:

```text
<vault>/
  AGENTS.md
  WIKI.md
  index.md
  inbox.md
  entities/
  concepts/
  syntheses/
  sources/
  reports/
  _attachments/
  _views/
  .openclaw-wiki/
```

Zarządzana zawartość pozostaje wewnątrz wygenerowanych bloków. Bloki notatek tworzonych przez ludzi są zachowywane.

Główne grupy stron to:

- `sources/` dla zaimportowanych surowych materiałów i stron wspieranych przez bridge
- `entities/` dla trwałych rzeczy, osób, systemów, projektów i obiektów
- `concepts/` dla idei, abstrakcji, wzorców i polityk
- `syntheses/` dla skompilowanych podsumowań i utrzymywanych zestawień
- `reports/` dla wygenerowanych dashboardów

## Ustrukturyzowane twierdzenia i dowody

Strony mogą zawierać ustrukturyzowany frontmatter `claims`, a nie tylko tekst swobodny.

Każde twierdzenie może zawierać:

- `id`
- `text`
- `status`
- `confidence`
- `evidence[]`
- `updatedAt`

Wpisy dowodowe mogą zawierać:

- `sourceId`
- `path`
- `lines`
- `weight`
- `note`
- `updatedAt`

To właśnie sprawia, że wiki działa bardziej jak warstwa przekonań niż pasywny
zrzut notatek. Twierdzenia mogą być śledzone, oceniane, kwestionowane i rozstrzygane z powrotem do źródeł.

## Pipeline kompilacji

Krok kompilacji odczytuje strony wiki, normalizuje podsumowania i emituje stabilne
artefakty skierowane do maszyn w:

- `.openclaw-wiki/cache/agent-digest.json`
- `.openclaw-wiki/cache/claims.jsonl`

Te digests istnieją po to, aby agenci i kod runtime nie musieli analizować stron
Markdown.

Skompilowane dane wyjściowe zasilają także:

- indeksowanie wiki pierwszego przebiegu dla przepływów search/get
- wyszukiwanie `claim-id` z powrotem do strony właściciela
- kompaktowe uzupełnienia promptów
- generowanie raportów/dashboardów

## Dashboardy i raporty zdrowia

Gdy włączone jest `render.createDashboards`, kompilacja utrzymuje dashboardy w `reports/`.

Wbudowane raporty obejmują:

- `reports/open-questions.md`
- `reports/contradictions.md`
- `reports/low-confidence.md`
- `reports/claim-health.md`
- `reports/stale-pages.md`

Raporty te śledzą takie rzeczy jak:

- klastry notatek o sprzecznościach
- klastry konkurujących twierdzeń
- twierdzenia bez ustrukturyzowanych dowodów
- strony i twierdzenia o niskim poziomie pewności
- nieaktualność lub nieznaną świeżość
- strony z nierozwiązanymi pytaniami

## Search i retrieval

`memory-wiki` obsługuje dwa backendy search:

- `shared`: użyj współdzielonego przepływu wyszukiwania pamięci, gdy jest dostępny
- `local`: przeszukuj wiki lokalnie

Obsługuje także trzy corpora:

- `wiki`
- `memory`
- `all`

Ważne zachowanie:

- `wiki_search` i `wiki_get` używają skompilowanych digestów jako pierwszego przebiegu, gdy to możliwe
- identyfikatory twierdzeń mogą być rozwiązywane z powrotem do strony właściciela
- kwestionowane/nieaktualne/świeże twierdzenia wpływają na ranking
- etykiety proweniencji mogą przetrwać do wyników

Praktyczna zasada:

- użyj `memory_search corpus=all` dla jednego szerokiego przebiegu recall
- użyj `wiki_search` + `wiki_get`, gdy zależy Ci na rankingu specyficznym dla wiki,
  proweniencji lub strukturze przekonań na poziomie strony

## Narzędzia agenta

Plugin rejestruje następujące narzędzia:

- `wiki_status`
- `wiki_search`
- `wiki_get`
- `wiki_apply`
- `wiki_lint`

Ich działanie:

- `wiki_status`: bieżący tryb sejfu, stan zdrowia, dostępność Obsidian CLI
- `wiki_search`: przeszukuje strony wiki i, gdy skonfigurowano, współdzielone corpora pamięci
- `wiki_get`: odczytuje stronę wiki według id/ścieżki lub wraca do współdzielonego corpus pamięci
- `wiki_apply`: wąskie mutacje syntez/metadanych bez swobodnej edycji strony
- `wiki_lint`: kontrole strukturalne, luki proweniencji, sprzeczności, otwarte pytania

Plugin rejestruje także niewyłączny supplement corpus pamięci, dzięki czemu współdzielone
`memory_search` i `memory_get` mogą sięgać do wiki, gdy Plugin Active Memory obsługuje wybór corpus.

## Zachowanie promptu i kontekstu

Gdy włączone jest `context.includeCompiledDigestPrompt`, sekcje promptów pamięci
dołączają kompaktowy skompilowany snapshot z `agent-digest.json`.

Ten snapshot jest celowo mały i bogaty w sygnał:

- tylko najważniejsze strony
- tylko najważniejsze twierdzenia
- liczba sprzeczności
- liczba pytań
- kwalifikatory confidence/freshness

Jest to opcjonalne, ponieważ zmienia kształt promptu i jest głównie przydatne dla
silników kontekstu lub starszego składania promptów, które jawnie korzystają z supplementów pamięci.

## Konfiguracja

Umieść konfigurację w `plugins.entries.memory-wiki.config`:

```json5
{
  plugins: {
    entries: {
      "memory-wiki": {
        enabled: true,
        config: {
          vaultMode: "isolated",
          vault: {
            path: "~/.openclaw/wiki/main",
            renderMode: "obsidian",
          },
          obsidian: {
            enabled: true,
            useOfficialCli: true,
            vaultName: "OpenClaw Wiki",
            openAfterWrites: false,
          },
          bridge: {
            enabled: false,
            readMemoryArtifacts: true,
            indexDreamReports: true,
            indexDailyNotes: true,
            indexMemoryRoot: true,
            followMemoryEvents: true,
          },
          ingest: {
            autoCompile: true,
            maxConcurrentJobs: 1,
            allowUrlIngest: true,
          },
          search: {
            backend: "shared",
            corpus: "wiki",
          },
          context: {
            includeCompiledDigestPrompt: false,
          },
          render: {
            preserveHumanBlocks: true,
            createBacklinks: true,
            createDashboards: true,
          },
        },
      },
    },
  },
}
```

Kluczowe przełączniki:

- `vaultMode`: `isolated`, `bridge`, `unsafe-local`
- `vault.renderMode`: `native` lub `obsidian`
- `bridge.readMemoryArtifacts`: importuj publiczne artefakty Pluginu Active Memory
- `bridge.followMemoryEvents`: uwzględniaj logi zdarzeń w trybie bridge
- `search.backend`: `shared` lub `local`
- `search.corpus`: `wiki`, `memory` lub `all`
- `context.includeCompiledDigestPrompt`: dołącz kompaktowy snapshot digestu do sekcji promptów pamięci
- `render.createBacklinks`: generuj deterministyczne bloki powiązanych treści
- `render.createDashboards`: generuj strony dashboardów

### Przykład: QMD + tryb bridge

Użyj tego, gdy chcesz używać QMD do recall, a `memory-wiki` jako utrzymywanej
warstwy wiedzy:

```json5
{
  memory: {
    backend: "qmd",
      "memory-wiki": {
        enabled: true,
        config: {
          vaultMode: "bridge",
          bridge: {
            enabled: true,
            readMemoryArtifacts: true,
            indexDreamReports: true,
            indexDailyNotes: true,
            indexMemoryRoot: true,
            followMemoryEvents: true,
          },
          search: {
            backend: "shared",
            corpus: "all",
          },
          context: {
            includeCompiledDigestPrompt: false,
          },
        },
      },
    },
  },
}
```

Dzięki temu:

- QMD odpowiada za recall w Active Memory
- `memory-wiki` koncentruje się na skompilowanych stronach i dashboardach
- kształt promptu pozostaje niezmieniony, dopóki celowo nie włączysz promptów skompilowanego digestu

## CLI

`memory-wiki` udostępnia także powierzchnię najwyższego poziomu w CLI:

```bash
openclaw wiki status
openclaw wiki doctor
openclaw wiki init
openclaw wiki ingest ./notes/alpha.md
openclaw wiki compile
openclaw wiki lint
openclaw wiki search "alpha"
openclaw wiki get entity.alpha
openclaw wiki apply synthesis "Alpha Summary" --body "..." --source-id source.alpha
openclaw wiki bridge import
openclaw wiki obsidian status
```

Pełne odniesienie do komend znajdziesz w [CLI: wiki](/cli/wiki).

## Obsługa Obsidian

Gdy `vault.renderMode` ma wartość `obsidian`, Plugin zapisuje Markdown przyjazny dla Obsidian
i może opcjonalnie używać oficjalnego CLI `obsidian`.

Obsługiwane przepływy pracy obejmują:

- sprawdzanie statusu
- przeszukiwanie sejfu
- otwieranie strony
- wywoływanie komendy Obsidian
- przejście do notatki dziennej

Jest to opcjonalne. Wiki nadal działa w trybie natywnym bez Obsidian.

## Zalecany przepływ pracy

1. Zachowaj swój Plugin Active Memory dla recall/promotion/Dreaming.
2. Włącz `memory-wiki`.
3. Zacznij od trybu `isolated`, chyba że jawnie chcesz trybu bridge.
4. Używaj `wiki_search` / `wiki_get`, gdy proweniencja ma znaczenie.
5. Używaj `wiki_apply` do wąskich syntez lub aktualizacji metadanych.
6. Uruchamiaj `wiki_lint` po istotnych zmianach.
7. Włącz dashboardy, jeśli chcesz mieć widoczność nieaktualności/sprzeczności.

## Powiązana dokumentacja

- [Memory Overview](/pl/concepts/memory)
- [CLI: memory](/cli/memory)
- [CLI: wiki](/cli/wiki)
- [Plugin SDK overview](/pl/plugins/sdk-overview)
