---
read_when:
    - Devi capire perché un job CI è stato eseguito oppure no
    - Stai eseguendo il debug di controlli GitHub Actions non riusciti
summary: Grafico dei job CI, gate per ambito ed equivalenti locali dei comandi
title: Pipeline CI
x-i18n:
    generated_at: "2026-04-11T02:44:27Z"
    model: gpt-5.4
    provider: openai
    source_hash: ca7e355b7f73bfe8ea8c6971e78164b8b2e68cbb27966964955e267fed89fce6
    source_path: ci.md
    workflow: 15
---

# Pipeline CI

La CI viene eseguita a ogni push su `main` e per ogni pull request. Usa uno scoping intelligente per saltare i job costosi quando sono cambiate solo aree non correlate.

## Panoramica dei job

| Job                      | Scopo                                                                                   | Quando viene eseguito              |
| ------------------------ | --------------------------------------------------------------------------------------- | ---------------------------------- |
| `preflight`              | Rilevare modifiche solo alla documentazione, ambiti modificati, estensioni modificate e costruire il manifest CI | Sempre su push e PR non in bozza   |
| `security-fast`          | Rilevamento di chiavi private, audit dei workflow tramite `zizmor`, audit delle dipendenze di produzione | Sempre su push e PR non in bozza   |
| `build-artifacts`        | Eseguire la build di `dist/` e della Control UI una volta, caricare artifact riutilizzabili per i job downstream | Modifiche rilevanti per Node       |
| `checks-fast-core`       | Corsie Linux rapide di correttezza come controlli bundled/plugin-contract/protocol      | Modifiche rilevanti per Node       |
| `checks-node-extensions` | Shard completi dei test dei bundled plugin sull'intera suite di estensioni              | Modifiche rilevanti per Node       |
| `checks-node-core-test`  | Shard dei test core Node, escluse le corsie channel, bundled, contract ed extension     | Modifiche rilevanti per Node       |
| `extension-fast`         | Test mirati solo per i bundled plugin modificati                                        | Quando vengono rilevate modifiche alle estensioni |
| `check`                  | Gate locale principale nella CI: `pnpm check` più `pnpm build:strict-smoke`             | Modifiche rilevanti per Node       |
| `check-additional`       | Guardrail di architettura, boundary e cicli di import più l'harness di regressione del watch del gateway | Modifiche rilevanti per Node       |
| `build-smoke`            | Test smoke della CLI buildata e smoke della memoria all'avvio                           | Modifiche rilevanti per Node       |
| `checks`                 | Restanti corsie Linux Node: test dei channel e compatibilità Node 22 solo su push       | Modifiche rilevanti per Node       |
| `check-docs`             | Controlli di formattazione, lint e link rotti della documentazione                      | Documentazione modificata          |
| `skills-python`          | Ruff + pytest per le Skills basate su Python                                            | Modifiche rilevanti per le Skills Python |
| `checks-windows`         | Corsie di test specifiche per Windows                                                   | Modifiche rilevanti per Windows    |
| `macos-node`             | Corsia di test TypeScript su macOS che usa gli artifact buildati condivisi              | Modifiche rilevanti per macOS      |
| `macos-swift`            | Lint, build e test Swift per l'app macOS                                                | Modifiche rilevanti per macOS      |
| `android`                | Matrice di build e test Android                                                         | Modifiche rilevanti per Android    |

## Ordine fail-fast

I job sono ordinati in modo che i controlli economici falliscano prima che vengano eseguiti quelli costosi:

1. `preflight` decide quali corsie esistono davvero. La logica `docs-scope` e `changed-scope` è costituita da step interni a questo job, non da job separati.
2. `security-fast`, `check`, `check-additional`, `check-docs` e `skills-python` falliscono rapidamente senza aspettare i job più pesanti della matrice artifact e piattaforme.
3. `build-artifacts` si sovrappone alle corsie Linux rapide, così i consumer downstream possono iniziare non appena la build condivisa è pronta.
4. Le corsie più pesanti di piattaforma e runtime si distribuiscono dopo: `checks-fast-core`, `checks-node-extensions`, `checks-node-core-test`, `extension-fast`, `checks`, `checks-windows`, `macos-node`, `macos-swift` e `android`.

La logica di ambito si trova in `scripts/ci-changed-scope.mjs` ed è coperta da unit test in `src/scripts/ci-changed-scope.test.ts`.
Il workflow separato `install-smoke` riusa lo stesso script di ambito tramite il proprio job `preflight`. Calcola `run_install_smoke` dal segnale changed-smoke più ristretto, quindi lo smoke Docker/install viene eseguito solo per modifiche rilevanti per installazione, packaging e container.

Sui push, la matrice `checks` aggiunge la corsia `compat-node22` solo per i push. Sulle pull request, quella corsia viene saltata e la matrice resta concentrata sulle normali corsie di test/channel.

## Runner

| Runner                           | Job                                                                                                  |
| -------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `blacksmith-16vcpu-ubuntu-2404`  | `preflight`, `security-fast`, `build-artifacts`, controlli Linux, controlli docs, Skills Python, `android` |
| `blacksmith-32vcpu-windows-2025` | `checks-windows`                                                                                     |
| `macos-latest`                   | `macos-node`, `macos-swift`                                                                          |

## Equivalenti locali

```bash
pnpm check          # tipi + lint + formattazione
pnpm build:strict-smoke
pnpm check:import-cycles
pnpm test:gateway:watch-regression
pnpm test           # test vitest
pnpm test:channels
pnpm check:docs     # formattazione docs + lint + link rotti
pnpm build          # build di dist quando sono rilevanti le corsie CI artifact/build-smoke
```
