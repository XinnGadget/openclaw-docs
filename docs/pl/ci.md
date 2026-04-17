---
read_when:
    - Musisz zrozumieć, dlaczego zadanie CI uruchomiło się lub nie uruchomiło
    - Diagnozujesz nieudane kontrole GitHub Actions
summary: Graf zadań CI, bramki zakresu i lokalne odpowiedniki poleceń
title: Potok CI
x-i18n:
    generated_at: "2026-04-09T09:45:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: d104f2510fadd674d7952aa08ad73e10f685afebea8d7f19adc1d428e2bdc908
    source_path: ci.md
    workflow: 15
---

# Potok CI

CI uruchamia się przy każdym wypchnięciu do `main` i dla każdego pull requestu. Używa inteligentnego określania zakresu, aby pomijać kosztowne zadania, gdy zmieniły się tylko niepowiązane obszary.

## Przegląd zadań

| Job                      | Cel                                                                                         | Kiedy się uruchamia                 |
| ------------------------ | ------------------------------------------------------------------------------------------- | ----------------------------------- |
| `preflight`              | Wykrywa zmiany tylko w dokumentacji, zmienione zakresy, zmienione rozszerzenia oraz buduje manifest CI | Zawsze dla wypchnięć i PR-ów, które nie są szkicami |
| `security-fast`          | Wykrywanie kluczy prywatnych, audyt workflow przez `zizmor`, audyt zależności produkcyjnych | Zawsze dla wypchnięć i PR-ów, które nie są szkicami |
| `build-artifacts`        | Buduje `dist/` i interfejs Control UI jeden raz, przesyła artefakty wielokrotnego użytku dla zadań zależnych | Zmiany istotne dla Node             |
| `checks-fast-core`       | Szybkie linuxowe ścieżki poprawności, takie jak sprawdzenia bundled/plugin-contract/protocol | Zmiany istotne dla Node             |
| `checks-fast-extensions` | Agreguje ścieżki shardów rozszerzeń po zakończeniu `checks-fast-extensions-shard`          | Zmiany istotne dla Node             |
| `extension-fast`         | Ukierunkowane testy tylko dla zmienionych bundled plugins                                   | Gdy wykryto zmiany w rozszerzeniach |
| `check`                  | Główna lokalna bramka w CI: `pnpm check` plus `pnpm build:strict-smoke`                     | Zmiany istotne dla Node             |
| `check-additional`       | Strażniki architektury, granic i cykli importów oraz harness regresji obserwacji gatewaya  | Zmiany istotne dla Node             |
| `build-smoke`            | Testy smoke zbudowanego CLI i smoke zużycia pamięci przy uruchamianiu                       | Zmiany istotne dla Node             |
| `checks`                 | Cięższe linuxowe ścieżki Node: pełne testy, testy kanałów i tylko dla wypchnięć zgodność z Node 22 | Zmiany istotne dla Node             |
| `check-docs`             | Formatowanie dokumentacji, lint i sprawdzanie niedziałających linków                        | Zmieniono dokumentację              |
| `skills-python`          | Ruff + pytest dla Skills opartych na Pythonie                                               | Zmiany istotne dla Python Skills    |
| `checks-windows`         | Ścieżki testowe specyficzne dla Windows                                                     | Zmiany istotne dla Windows          |
| `macos-node`             | Ścieżka testów TypeScript dla macOS z użyciem współdzielonych zbudowanych artefaktów       | Zmiany istotne dla macOS            |
| `macos-swift`            | Lint, build i testy Swift dla aplikacji macOS                                               | Zmiany istotne dla macOS            |
| `android`                | Macierz buildów i testów Androida                                                           | Zmiany istotne dla Androida         |

## Kolejność fail-fast

Zadania są uporządkowane tak, aby tańsze kontrole kończyły się niepowodzeniem przed uruchomieniem droższych:

1. `preflight` decyduje, które ścieżki w ogóle istnieją. Logika `docs-scope` i `changed-scope` to kroki wewnątrz tego zadania, a nie osobne zadania.
2. `security-fast`, `check`, `check-additional`, `check-docs` i `skills-python` kończą się szybko niepowodzeniem bez czekania na cięższe artefakty oraz zadania z macierzy platform.
3. `build-artifacts` nakłada się na szybkie ścieżki Linux, aby zadania zależne mogły rozpocząć się, gdy tylko współdzielony build będzie gotowy.
4. Następnie rozgałęziają się cięższe ścieżki platformowe i uruchomieniowe: `checks-fast-core`, `checks-fast-extensions`, `extension-fast`, `checks`, `checks-windows`, `macos-node`, `macos-swift` i `android`.

Logika zakresu znajduje się w `scripts/ci-changed-scope.mjs` i jest objęta testami jednostkowymi w `src/scripts/ci-changed-scope.test.ts`.
Oddzielny workflow `install-smoke` ponownie używa tego samego skryptu zakresu przez własne zadanie `preflight`. Oblicza `run_install_smoke` na podstawie węższego sygnału changed-smoke, więc Docker/install smoke uruchamia się tylko dla zmian istotnych dla instalacji, pakowania i kontenerów.

Przy wypchnięciach macierz `checks` dodaje ścieżkę `compat-node22`, uruchamianą tylko dla push. W pull requestach ta ścieżka jest pomijana, a macierz pozostaje skupiona na zwykłych ścieżkach testów i kanałów.

## Runners

| Runner                           | Zadania                                                                                             |
| -------------------------------- | --------------------------------------------------------------------------------------------------- |
| `blacksmith-16vcpu-ubuntu-2404`  | `preflight`, `security-fast`, `build-artifacts`, kontrole Linux, kontrole dokumentacji, Python Skills, `android` |
| `blacksmith-32vcpu-windows-2025` | `checks-windows`                                                                                    |
| `macos-latest`                   | `macos-node`, `macos-swift`                                                                         |

## Lokalne odpowiedniki

```bash
pnpm check          # typy + lint + formatowanie
pnpm build:strict-smoke
pnpm check:import-cycles
pnpm test:gateway:watch-regression
pnpm test           # testy vitest
pnpm test:channels
pnpm check:docs     # formatowanie dokumentacji + lint + niedziałające linki
pnpm build          # buduje dist, gdy mają znaczenie ścieżki artefaktów/build-smoke w CI
```
